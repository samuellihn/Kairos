import os
from typing import List, Dict, Any, Optional
from todoist_api_python.api_async import TodoistAPIAsync

class TodoistManager:
    def __init__(self):
        token = os.environ.get("TODOIST_API_KEY")
        if not token:
            print("Warning: TODOIST_API_KEY not found in environment variables.")
            self.api = None
        else:
            self.api = TodoistAPIAsync(token)

    async def flatten_deep_async(self, nested_iterable):
        flat_list = []
        if hasattr(nested_iterable, '__aiter__'):
            async for item in nested_iterable:
                if isinstance(item, list):
                    flat_list.extend(await self.flatten_deep_async(item))
                else:
                    flat_list.append(item)
        if hasattr(nested_iterable, '__iter__'):
            for item in nested_iterable:
                if isinstance(item, list):
                    flat_list.extend(self.flatten_deep_async(item))
                else:
                    flat_list.append(item)
        return flat_list

    async def fetch_active_tasks(self) -> List[Dict[str, Any]]:
        if not self.api:
            return []
        
        try:
            tasks_result = await self.api.get_tasks()
            
            # Handle potential async generator (based on observation)
            if hasattr(tasks_result, '__aiter__'):
                tasks = await self.flatten_deep_async(tasks_result)
            else:
                tasks = tasks_result

            # Transform to a simpler format for our frontend
            simplified_tasks = []
            for task in tasks:
                simplified_tasks.append({
                    "id": task.id,
                    "content": task.content,
                    "due": task.due.string if task.due else None,
                    "priority": task.priority,
                    "provider": "todoist" # Tag source
                })
            return simplified_tasks
        except Exception as e:
            print(f"Error fetching Todoist tasks: {e}")
            with open("server_debug_error.txt", "a") as f:
                f.write(f"Server Fetch Error: {type(e)} - {e}\n")
            return []

    async def close_task(self, task_id: str) -> bool:
        if not self.api:
            return False
        
        try:
            is_success = await self.api.close_task(task_id=task_id)
            return is_success
        except Exception as e:
            print(f"Error closing Todoist task {task_id}: {e}")
            return False
