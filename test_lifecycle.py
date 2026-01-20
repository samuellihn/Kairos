
import requests
import time

BASE_URL = "http://localhost:55544"

def test_session_lifecycle():
    print("Testing Session Lifecycle...")
    
    # 1. Start Session
    print("1. Starting Session...")
    res = requests.post(f"{BASE_URL}/session/start", json={
        "task_name": "Lifecycle Test",
        "category": "Test",
        "duration_minutes": 0.05, # 3 seconds
        "start_time": time.time()
    })
    print(res.json())
    
    # 2. Check Active
    res = requests.get(f"{BASE_URL}/session/current")
    data = res.json()
    print(f"2. Current Session: Active={data.get('active')}, Notified={data.get('session', {}).get('notified')}")
    
    # 3. Simulate Timeout (Frontend would call this)
    print("3. Calling /session/timeout...")
    res = requests.post(f"{BASE_URL}/session/timeout")
    print(res.json())
    
    # 4. Check Still Active but Notified
    res = requests.get(f"{BASE_URL}/session/current")
    data = res.json()
    print(f"4. Current Session: Active={data.get('active')}, Notified={data.get('session', {}).get('notified')}")
    
    # 5. Stop (Discard)
    print("5. Calling /session/stop...")
    res = requests.post(f"{BASE_URL}/session/stop")
    print(res.json())
    
    # 6. Check Gone
    res = requests.get(f"{BASE_URL}/session/current")
    data = res.json()
    print(f"6. Current Session: Active={data.get('active')}")

if __name__ == "__main__":
    try:
        test_session_lifecycle()
    except Exception as e:
        print(f"Failed: {e}")
