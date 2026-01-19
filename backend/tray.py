import os
import sys
import threading
import uvicorn
import subprocess
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

# Flag to control server loop
server_process = None

def create_image(width=64, height=64, color1="orange", color2="black"):
    # Generate an orange icon
    image = Image.new("RGB", (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image

def start_server():
    # Run uvicorn programmatically or as subprocess
    # Using subprocess allows cleaner termination usually
    global server_process
    # Assuming the current directory is root or backend parent
    # We want to run: python -m uvicorn backend.main:app --port 55544
    # Adjust path as necessary
    cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "55544"]
    server_process = subprocess.Popen(cmd, cwd=os.path.dirname(os.path.dirname(__file__)))

def stop_server():
    global server_process
    if server_process:
        server_process.terminate()
        server_process = None

def on_quit(icon, item):
    icon.stop()
    stop_server()
    sys.exit()

def on_open(icon, item):
    # Open frontend in browser or configured window
    # For now, just print
    print("Opening Dashboard...")
    # Try to open as an app window with specific size (Chrome/Edge)
    # This is a best-effort attempt to set the size.
    try:
        # Check standard paths or just run command assuming it's in path
        # 'start' is cmd specific
        cmd = 'start msedge --app=http://localhost:55544 --window-size=450,910'
        subprocess.Popen(cmd, shell=True)
    except:
        subprocess.Popen(["start", "http://localhost:55544"], shell=True)

def setup_tray():
    icon_image = create_image()
    menu = (
        item('Open Dashboard', on_open),
        item('Exit', on_quit)
    )
    icon = pystray.Icon("Kairos", icon_image, "Kairos Decider", menu)
    
    start_server()
    icon.run()

if __name__ == "__main__":
    setup_tray()
