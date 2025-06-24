@echo off
cls
echo.
echo =============================================
echo         WageLift Server Startup
echo =============================================
echo.

REM Change to project directory
cd /d "%~dp0"

echo [1/4] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [2/4] Installing frontend dependencies...
cd frontend
npm install --silent
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [3/4] Starting Frontend Server...
start "WageLift Frontend - http://localhost:3000" cmd /c "npm run dev"

echo [4/4] Starting Backend Server...
cd ..\backend
start "WageLift Backend - http://localhost:8000" cmd /c "uvicorn app.main:app --reload --port 8000"

echo.
echo =============================================
echo   SERVERS STARTED SUCCESSFULLY!
echo.
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo   Wait 10-15 seconds for servers to start
echo   then open: http://localhost:3000
echo =============================================
echo.

timeout /t 15 /nobreak
start http://localhost:3000

echo Opening browser...
echo Press any key to exit
pause >nul 