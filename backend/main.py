import os
import subprocess
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from .database import load_config, save_config, append_history, get_history, load_task_cache, save_task_cache, append_pause_log
from .taskade import fetch_taskade_tasks

# Define generic result type
Result = Dict[str, Any]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Backend started.")
    yield
    # Shutdown
    print("Backend shutting down.")

app = FastAPI(lifespan=lifespan)

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:55545"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Kairos Backend Running"}

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

@app.post("/tasks")
async def fetch_tasks_endpoint():
    """
    Fetch tasks from Taskade, check cache, and prioritize.
    """
    # 1. Fetch from Taskade
    try:
        tasks = await fetch_taskade_tasks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # 2. Load Cache
    cache = load_task_cache()
    
    # 3. Process/Categorize (Placeholder for now)
    # TODO: Implement categorization logic here using Gemini CLI if needed
    
    return {"tasks": tasks}

@app.post("/categorize")
async def categorize_task(task_title: str = Body(..., embed=True), categories: List[str] = Body(..., embed=True)):
    """
    Calls local Gemini CLI via subprocess to categorize a task.
    Current implementation is a stub to be fleshed out.
    """
    # TODO: Implement subprocess call to "gemini"
    # prompt = f"Classify: '{task_title}' into {categories}. Return ONLY the category name."
    return {"category": "Uncategorized"}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=55544, reload=True)
