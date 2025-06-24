@echo off
echo === WageLift Dependency Check ===
echo.

echo Checking Python...
python --version
echo.

echo Checking Node.js...
node --version
echo.

echo Checking npm...
npm --version
echo.

echo Checking Backend Dependencies...
cd backend
pip list | findstr "fastapi uvicorn pydantic"
echo.

echo Checking Frontend Dependencies...
cd ../frontend
dir node_modules 2>nul | find "Directory" | find /c "Directory"
echo.

echo === Environment Files ===
echo Backend .env exists:
if exist "../backend/.env" (echo YES) else (echo NO)

echo Frontend .env.local exists:
if exist ".env.local" (echo YES) else (echo NO)

echo.
echo === Port Check ===
netstat -an | findstr ":3000 :8000"
echo.

pause 