import os
import subprocess
from dotenv import load_dotenv

# Explicitly load .env from parent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(env_path)

from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import threading
import time
from windows_toasts import WindowsToaster, Toast

from .database import load_config, save_config, append_history, get_history, load_task_cache, save_task_cache, append_pause_log, append_event_log
from .todoist_client import TodoistManager
from .gemini_client import categorize_task

# Define generic result type
Result = Dict[str, Any]

# Initialize clients
todoist_manager = TodoistManager()

# --- Session State Management ---
from pydantic import BaseModel

class ActiveSession(BaseModel):
    task_name: str
    category: str
    duration_minutes: float
    start_time: float # Unix timestamp
    task_due_date: Optional[str] = None
    related_tasks: List[Dict[str, Any]] = []
    notified: bool = False

current_session: Optional[ActiveSession] = None

def monitor_sessions():
    """
    Background thread to check for expired sessions and trigger notifications.
    """
    print("Session monitor thread started.")
    toaster = WindowsToaster('Kairos')
    
    while True:
        try:
            global current_session
            if current_session:
                now = time.time()
                elapsed = now - current_session.start_time
                duration_sec = current_session.duration_minutes * 60
                
                # Check if expired and not yet notified
                if elapsed >= duration_sec and not current_session.notified:
                    print(f"Session expired: {current_session.task_name}")
                    
                    # Trigger Toast
                    new_toast = Toast()
                    new_toast.text_fields = [f"Time's up! {current_session.task_name} is done."]
                    try:
                        toaster.show_toast(new_toast)
                        print("Notification sent.")
                    except Exception as e:
                        print(f"Failed to send notification: {e}")
                    
                    # Mark as notified so we don't spam
                    current_session.notified = True
            
            time.sleep(5) # Check every 5 seconds
        except Exception as e:
            print(f"Error in monitor thread: {e}")
            time.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Backend started.")
    
    # Start Monitor Thread
    monitor_thread = threading.Thread(target=monitor_sessions, daemon=True)
    monitor_thread.start()
    
    yield
    # Shutdown
    print("Backend shutting down.")

app = FastAPI(lifespan=lifespan)

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"message": "Kairos Backend Running"}

# Serve frontend build if it exists


@app.get("/config")
async def get_config_endpoint():
    return load_config()

@app.post("/config")
async def update_config_endpoint(config: Dict[str, Any] = Body(...)):
    save_config(config)
    return {"status": "success"}

@app.get("/history")
async def get_history_endpoint():
    return get_history()

@app.post("/history")
async def append_history_endpoint(entry: Dict[str, Any] = Body(...)):
    append_history(entry)
    return {"status": "success"}

@app.post("/pause_log")
async def append_pause_log_endpoint(entry: Dict[str, Any] = Body(...)):
    append_pause_log(entry)
    return {"status": "success"}

@app.post("/log_event")
async def log_event_endpoint(entry: Dict[str, Any] = Body(...)):
    append_event_log(entry)
    return {"status": "success"}

@app.post("/tasks")
async def fetch_tasks_endpoint():
    """
    Fetch tasks from Todoist, check cache for categories, and invoke Gemini for uncategorized ones.
    """
    # 1. Fetch from Todoist
    tasks = await todoist_manager.fetch_active_tasks()
    
    # 2. Categorize
    config = load_config()
    categories = [c["name"] for c in config.get("categories", [])]
    
    # Load cache ONCE
    cache = load_task_cache()
    original_cache_size = len(cache)
    
    # Identify miss
    tasks_to_categorize = []
    
    for task in tasks:
        if task["content"] in cache:
            task["category"] = cache[task["content"]]
        else:
            tasks_to_categorize.append(task["content"])
            # Temporarily mark as Uncategorized until batch returns
            task["category"] = "Uncategorized"
    
    # Batch Process
    if tasks_to_categorize:
        print(f"Batch categorizing {len(tasks_to_categorize)} tasks...")
        from .gemini_client import categorize_tasks_batch
        new_categories = categorize_tasks_batch(tasks_to_categorize, categories)
        
        # Merge results back
        for task in tasks:
            if task["content"] in new_categories:
                task["category"] = new_categories[task["content"]]
                cache[task["content"]] = new_categories[task["content"]]
            elif task["category"] == "Uncategorized" and task["content"] in cache:
                 # Fallback if batch missed it but it was in cache (unlikely here but safety)
                 task["category"] = cache[task["content"]]
    
    # Save cache if changed
    if len(cache) > original_cache_size:
        save_task_cache(cache)
    
    return {"tasks": tasks}

@app.post("/tasks/{task_id}/complete")
async def complete_task_endpoint(task_id: str):
    """
    Completes a task in Todoist.
    """
    success = await todoist_manager.close_task(task_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to close task in Todoist")
    return {"status": "success", "task_id": task_id}

@app.post("/categorize")
async def categorize_task_endpoint(task_title: str = Body(..., embed=True), categories: List[str] = Body(..., embed=True)):
    """
    Direct endpoint to categorize a task.
    """
    category = categorize_task(task_title, categories)
    return {"category": category}

@app.post("/session/start")
async def start_session_endpoint(session: ActiveSession = Body(...)):
    global current_session
    # If start_time is not provided or 0, set it to now
    if not session.start_time:
        session.start_time = time.time()
    current_session = session
    print(f"Session started provided: {session.task_name} at {session.start_time}")
    return {"status": "success", "session": current_session}

@app.get("/session/current")
async def get_current_session_endpoint():
    global current_session
    if current_session:
        # Calculate elapsed/remaining logic if needed, or just return the static data
        # The frontend can calculate remaining time based on start_time and duration
        return {"active": True, "session": current_session, "server_time": time.time()}
    return {"active": False}

@app.post("/session/stop")
async def stop_session_endpoint():
    global current_session
    current_session = None
    print("Session stopped/cleared.")
    return {"status": "success"}

@app.post("/session/timeout")
async def timeout_session_endpoint():
    """
    Called when the frontend timer finishes. 
    Triggers immediate notification (if not already sent) but keeps the session active (so feedback can be entered).
    Marks session as notified.
    """
    global current_session
    if current_session:
        # 1. Trigger Notification Immediately (if not yet)
        if not current_session.notified:
             print(f"Session timeout triggered via endpoint: {current_session.task_name}")
             toaster = WindowsToaster('Kairos')
             new_toast = Toast()
             new_toast.text_fields = [f"Time's up! {current_session.task_name} is done."]
             try:
                toaster.show_toast(new_toast)
             except Exception as e:
                print(f"Failed to send notification: {e}")
             current_session.notified = True

        return {"status": "success", "message": "Session marked as timed out but kept active."}
    
    return {"status": "error", "message": "No active session"}


# Serve frontend build if it exists
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "out")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
else:
    @app.get("/")
    async def root():
        return {"message": "Frontend not found. Run 'npm run build' in frontend/"}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=55544, reload=True)
