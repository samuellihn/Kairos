import os
import sys
from dotenv import load_dotenv

# Explicitly load .env from parent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(env_path)

from backend.gemini_client import categorize_task

def test():
    print("Testing Gemma 3 API...")
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY not found in env.")
        return

    # Clear cache for this test key to ensure fresh API call
    # We can pass an empty dict as cache to simulate fresh state and capture result
    dummy_cache = {}
    
    task = "Prepare quarterly financial report for board meeting"
    categories = ["Work", "Personal", "Health"]
    
    print(f"Task: {task}")
    print(f"Categories: {categories}")
    
    cat = categorize_task(task, categories, cache=dummy_cache)
    print(f"Result: {cat}")
    
    if cat in categories:
        print("SUCCESS: Valid category returned.")
    else:
        print(f"WARNING: Returned category '{cat}' not in list (or 'Uncategorized').")

if __name__ == "__main__":
    test()
