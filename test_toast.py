
import time
import threading
from windows_toasts import WindowsToaster, Toast

# Mock Session
class MockSession:
    def __init__(self, name, duration):
        self.task_name = name
        self.category = "Test"
        self.duration_minutes = duration
        self.start_time = time.time()
        self.notified = False

# Mock Monitor
def test_monitor():
    print("Test monitor started...")
    toaster = WindowsToaster('Kairos Test')
    
    session = MockSession("Test Notification Task", 0.1) # 6 seconds
    
    print(f"Session started: {session.task_name} for 6 seconds")
    
    while True:
        now = time.time()
        elapsed = now - session.start_time
        duration_sec = session.duration_minutes * 60
        
        if elapsed >= duration_sec and not session.notified:
            print("Session expired!")
            new_toast = Toast()
            new_toast.text_fields = [f"Time's up! {session.task_name} is done."]
            try:
                toaster.show_toast(new_toast)
                print("Toast Sent!")
                return
            except Exception as e:
                print(f"Error: {e}")
                return
        
        time.sleep(1)

if __name__ == "__main__":
    test_monitor()
