import asyncio
import os
from dotenv import load_dotenv

# Force load .env from parent dir
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from backend.todoist_client import TodoistManager

async def test():
    print("Testing TodoistManager...")
    manager = TodoistManager()
    if not manager.api:
        print("API not initialized (Key missing?)")
        return

    print("Fetching projects...")
    projects_result = await manager.fetch_active_tasks()
    print(projects_result)
    

if __name__ == "__main__":
    asyncio.run(test())
