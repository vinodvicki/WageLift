@echo off
echo Starting WageLift Frontend (Debug Mode)...
echo ========================================

cd frontend

echo Installing dependencies...
call npm install

echo.
echo Starting Next.js development server...
call npm run dev

echo.
echo Press any key to exit...
pause 