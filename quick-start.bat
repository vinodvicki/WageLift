@echo off
title WageLift Development Servers
echo ========================================
echo Starting WageLift Development Servers
echo ========================================
echo.

echo Installing dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo ERROR: Frontend dependencies failed to install
    pause
    exit /b 1
)

echo.
echo Starting Frontend Server (localhost:3000)...
start "WageLift Frontend" cmd /k "cd /d %~dp0frontend && npx next dev"

echo.
echo Waiting 3 seconds...
timeout /t 3 /nobreak >nul

echo Starting Backend Server (localhost:8000)...
cd ..\backend
start "WageLift Backend" cmd /k "cd /d %~dp0backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo ========================================
echo Servers are starting...
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo ========================================
echo.
echo Press any key to close this window...
pause >nul 
