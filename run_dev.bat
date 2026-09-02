@echo off
echo =======================================================
echo Starting RazorShield AI - Backend & Frontend SOC Servers
echo =======================================================

start cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
start cmd /k "cd frontend && npm run dev"

echo.
echo Backend API Docs: http://localhost:8000/docs
echo Frontend SOC Dashboard: http://localhost:5173
echo =======================================================
