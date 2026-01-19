@echo off
echo Starting Kairos...
cd frontend
echo Building Frontend...
call npm run build
cd ..
echo "Starting Backend & Tray..."
python backend/tray.py
