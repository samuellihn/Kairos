This refined **GEMINI.md** is optimized for "vibe coding" with tools like Google Antigravity or local LLMs. It incorporates your feedback on security, UI-based configuration, and intelligent token-saving through persistent caching.

---
# GEMINI.md: The Decider Project (Refined)

## 1. Project Architecture

A hybrid desktop system designed for low-friction productivity.

* **Backend:** Python (FastAPI) + System Tray (Pystray).
* **Frontend:** Next.js PWA (Static Export) running in Vivaldi standalone window.
* **Intelligence:** Gemini CLI (Local subprocess) for task classification and "Free Time" ideation.
* **Data Persistence:** Local JSON files for configuration, analytics, and categorization caching.

---

## 2. Environment & Security

All sensitive tokens must live in a `.env` file in the project root. The Python backend and Next.js (if using server-side envs) will load these at runtime.

**File: `.env**`

```bash
TASKADE_PAT=your_taskade_token_here
GEMINI_API_KEY=your_google_api_key_here  # If the CLI requires it
BASE_URL=http://localhost:8000

```

---

## 3. Data & Cache Schema

### `config.json` (Managed via Next.js UI)

Stores your category preferences and weekly goals.

```json
{
  "categories": [
    { "id": "cat_1", "name": "Homework", "target_hours": 20, "priority": 1 },
    { "id": "cat_2", "name": "Research", "target_hours": 15, "priority": 2 }
  ],
  "free_time_chance": 0.05
}

```

### `task_cache.json` (Token Optimizer)

Prevents re-categorizing the same task twice.

```json
{
  "Finish MechE PSET 4": "Homework",
  "Satellite simulation update": "Research"
}

```

---

## 4. Feature Specifications

### A. Configuration UI (Next.js)

* **Route:** `/settings`
* **Functionality:** A dynamic form built with Tailwind CSS.
* **Logic:** * Fetch `config.json` from the Python backend on load.
* Allow users to add/edit/delete categories (Name, Target Hours, Priority).
* "Save" button sends a POST request to the Python backend to overwrite `config.json`.



### B. Intelligent Categorization (Python Sidecar)

To minimize Gemini CLI calls:

1. **Check Cache:** Before calling Gemini, check if `task_title` exists in `task_cache.json`.
2. **Call Gemini:** If not found, run: `gemini "Classify: [Task] into [Categories]. Return ONLY the category name."`
3. **Update Cache:** Save the result to `task_cache.json` immediately.

### C. The Decision Engine & Timer

1. **Selection:** Weighted random pick. `Weight = (Goal - Spent) * Priority`.
2. **Interval:** * If "Time Available" > 60 min: Set timer for a random duration between 20–60 min.
* If "Time Available" < 60 min: Set timer for exactly "Time Available".


3. **Priority Sorting:** If multiple tasks exist in a category, sort by `Taskade Priority` -> `Due Date`.

### D. Feedback & Analytics Loop

When a timer ends or is stopped early, show a **Feedback Modal**:

* **Question:** "What did you accomplish?" (Text input).
* **Time Check:** "Actual time spent?" (Auto-populated with timer data, but editable).
* **Action:** Append data to `history.json` with a timestamp.
* **Extenders:** Buttons for +5m, +15m, +30m, +1h.

### E. "Free Time" Engine

* **Trigger:** Occasional "Free Time" option appears in the Decider based on `free_time_chance`.
* **Sync:** A background task reads `context.md` (personal project ideas/docs) once a week.
* **Generation:** Gemini CLI generates 3 fresh build ideas based on your recent activity and context.

---

## 5. Developer Prompt for Scaffolding

> "Using this GEMINI.md, build the FastAPI backend first. Ensure it serves `config.json` and `history.json` endpoints. Then, create the Next.js frontend with a `/settings` page for category management and a `/timer` page for the Pomodoro logic. Use a sidecar pattern where the Python script manages the Windows tray icon and launches the local server."

---

### Next Step for the App

I can generate the **React code for the Configuration Dashboard** (using Tailwind) so you can start setting up your categories and goals in a clean UI. Would you like to start there?