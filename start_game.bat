@echo off
echo ===========================================
echo       Starforged AI Game Master
echo ===========================================
echo Starting services...

:: 1. Start Backend Server
echo Starting Backend (Port 8000)...
start "Starforged Backend" cmd /k "venv\Scripts\activate && uvicorn src.server:app --reload"

:: 2. Start Frontend Client
echo Starting Frontend...
cd frontend
start "Starforged Client" cmd /k "npm run dev"
cd ..

:: 3. Wait for services to spin up
echo Waiting for servers to initialize...
timeout /t 5 >nul

:: 4. Open Application in Default Browser
echo Opening Launch Interface...
start http://localhost:5173

echo.
echo ===========================================
echo   Game Running!
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:5173
echo ===========================================
echo.
pause
