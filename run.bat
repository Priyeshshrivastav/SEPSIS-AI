@echo off
echo ===================================================
echo 🚀 Starting Sepsis AI System
echo ===================================================

echo [1/2] Launching FastAPI Backend (Port 8000)...
start cmd /k "python main.py"

timeout /t 3 /nobreak > nul

echo [2/2] Launching Streamlit UI (Browser should open automatically)...
start cmd /k "python -m streamlit run ui.py"
