import json
import os
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "config.json"
HISTORY_FILE = BASE_DIR / "history.json"
CACHE_FILE = BASE_DIR / "task_cache.json"
PAUSE_LOG_FILE = BASE_DIR / "pause_log.json"
EVENT_LOG_FILE = BASE_DIR / "event_log.json"

DEFAULT_CONFIG = {
    "categories": [
        {"id": "cat_1", "name": "Work", "target_hours": 20, "priority": 1},
        {"id": "cat_2", "name": "Personal", "target_hours": 10, "priority": 2}
    ],
    "free_time_chance": 0.05
}

def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        _save_json(path, default)
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default

def _save_json(path: Path, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_config() -> Dict[str, Any]:
    return _load_json(CONFIG_FILE, DEFAULT_CONFIG)

def save_config(data: Dict[str, Any]) -> None:
    _save_json(CONFIG_FILE, data)

def get_history() -> List[Dict[str, Any]]:
    return _load_json(HISTORY_FILE, [])

def append_history(entry: Dict[str, Any]) -> None:
    history = get_history()
    history.append(entry)
    _save_json(HISTORY_FILE, history)

def load_task_cache() -> Dict[str, str]:
    return _load_json(CACHE_FILE, {})

def save_task_cache(data: Dict[str, str]) -> None:
    _save_json(CACHE_FILE, data)

def append_pause_log(entry: Dict[str, Any]) -> None:
    logs = _load_json(PAUSE_LOG_FILE, [])
    logs.append(entry)
    _save_json(PAUSE_LOG_FILE, logs)

def append_event_log(entry: Dict[str, Any]) -> None:
    logs = _load_json(EVENT_LOG_FILE, [])
    logs.append(entry)
    _save_json(EVENT_LOG_FILE, logs)
