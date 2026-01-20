import os
from typing import List, Dict, Optional
from google import genai
from .database import load_task_cache, save_task_cache

def categorize_task(task_title: str, categories: List[str], cache: Optional[Dict[str, str]] = None) -> str:
    """
    Categorizes a task into one of the provided categories using Gemma 3 API via google-genai SDK.
    Checks cache first.
    """
    # 1. Check Cache
    use_external_cache = cache is not None
    if not use_external_cache:
        cache = load_task_cache()
    
    if task_title in cache:
        return cache[task_title]
    
    # 2. Call Gemma 3 API
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found.")
        return "Uncategorized"

    try:
        client = genai.Client(api_key=api_key)
        
        category_list_str = ", ".join(categories)
        prompt = f"Classify the task '{task_title}' into exactly one of these categories: [{category_list_str}]. Return ONLY the category name. If unsure or none match, return 'Uncategorized'."
        
        # Using 'gemma-2-9b-it' or 'gemini-1.5-flash' if 3 is not out yet, but user asked for 'gemma-3-12b'
        # Current google-genai SDK maps models. 
        # Attempting user's requested model string.
        response = client.models.generate_content(
            model="gemma-3-4b-it", 
            contents=prompt
        )
        
        if response.text:
            category = response.text.strip()
            # Basic cleanup
            category = category.replace("```", "").replace("\n", "").strip()
        else:
            category = "Uncategorized"

        # 3. Update Cache
        # Validation: check if response loosely matches a category (optional)
        
        cache[task_title] = category
        
        if not use_external_cache:
            save_task_cache(cache)
        
        return category

    except Exception as e:
        print(f"Error calling Gemma 3 API: {e}")
        return "Uncategorized"

def categorize_tasks_batch(tasks: List[str], categories: List[str]) -> Dict[str, str]:
    """
    Categorizes a list of tasks in a single API call using Gemma 3.
    Returns a dictionary mapping task_title -> category.
    """
    if not tasks:
        return {}

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found.")
        return {t: "Uncategorized" for t in tasks}

    try:
        client = genai.Client(api_key=api_key)
        
        category_list_str = ", ".join(categories)
        # Construct a clear JSON instruction prompt
        prompt = (
            f"You are a task management assistant. Classify the following tasks into exactly one of these categories: [{category_list_str}].\n"
            f"Tasks: {tasks}\n"
            f"Return ONLY a valid JSON object where keys are the task titles and values are the assigned categories.\n"
            f"If a task does not fit well, pick the best match or 'Uncategorized'.\n"
            f"JSON Format Example: {{ \"Buy milk\": \"Personal\", \"Finish code\": \"Work\" }}"
        )
        
        response = client.models.generate_content(
            model="gemma-3-4b-it", 
            contents=prompt
        )
        
        import json
        if response.text:
            cleaned_text = response.text.strip()
            # Remove markdown code blocks if present (though response_mime_type might handle this, safety first)
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
                
            results = json.loads(cleaned_text)
            return results
        else:
            return {t: "Uncategorized" for t in tasks}

    except Exception as e:
        print(f"Error calling Gemma 3 Batch API: {e}")
        return {t: "Uncategorized" for t in tasks}
