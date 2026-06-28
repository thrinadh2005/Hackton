@echo off
echo ===================================================
echo   Starting EdgeIntel-AM Unified Dashboard Services
echo ===================================================

:: Ensure python venv exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo Virtual environment already exists.
)

:: Run model training once to ensure models exist
echo Pre-training machine learning models...
venv\Scripts\python backend\train_models.py

:: Launch services in separate windows
echo Starting FastAPI Backend...
start cmd /k "title FastAPI Backend && venv\Scripts\python -m uvicorn backend.main:app --reload"

echo Starting Telemetry Simulator...
start cmd /k "title Telemetry Simulator && venv\Scripts\python backend\simulator.py"

echo Starting React Frontend...
start cmd /k "title React Frontend && cd frontend && npm install && npm run dev"

echo All services launched! Opening browser at http://localhost:5173
timeout /t 5
start http://localhost:5173
