@echo off
cls
echo.
echo =============================================
echo       WageLift Phase 2 - CLEAN START
echo =============================================
echo.

REM Ensure we're in the right directory
cd /d "%~dp0"

echo [1/3] Frontend Setup...
cd frontend
if not exist node_modules (
    echo Installing dependencies...
    npm install --silent
)

echo [2/3] Starting Frontend (Next.js)...
start "WageLift Frontend" cmd /k "npm run dev"

echo [3/3] Starting Backend (FastAPI)...
cd ..\backend
start "WageLift Backend" cmd /k "python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo.
echo =============================================
echo   ✅ SERVERS STARTING...
echo.
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo   Opening browser in 10 seconds...
echo =============================================
echo.

timeout /t 10 /nobreak
start http://localhost:3000

echo.
echo ✅ WageLift is running!
echo Press any key to continue...
pause >nul 