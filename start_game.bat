@echo off
setlocal enabledelayedexpansion

echo ===========================================
echo       Starforged AI Game Master
echo ===========================================
echo Starting services...
echo.

:: 1. Start Backend Server
echo [1/2] Starting Backend (Port 8000)...
start "Starforged Backend" cmd /k "cd /d %~dp0 && venv\Scripts\activate && uvicorn src.server:app --reload --host 0.0.0.0 --port 8000"

:: Wait and check if backend is responding
echo Waiting for backend to start...
set /a attempts=0
:check_backend
set /a attempts+=1
if %attempts% gtr 30 (
    echo ERROR: Backend failed to start after 30 seconds!
    echo Please check if Python and dependencies are installed correctly.
    pause
    exit /b 1
)

timeout /t 1 >nul
curl -s http://localhost:8000/api/health >nul 2>&1
if errorlevel 1 (
    echo Still waiting... (%attempts%/30^)
    goto check_backend
)

echo Backend is ready!
echo.

:: 2. Start Frontend Client
echo [2/2] Starting Frontend (Port 5173)...
cd frontend
start "Starforged Client" cmd /k "npm run dev"
cd ..

:: Wait for frontend
echo Waiting for frontend to build...
timeout /t 5 >nul

:: 3. Open Application in Default Browser
echo Opening game in browser...
start http://localhost:5173

echo.
echo ===========================================
echo   GAME IS RUNNING!
echo ===========================================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo ===========================================
echo.
echo Press CTRL+C or close this window to stop all servers.
echo You can also use the Exit button in the game menu.
echo.
pause

:: Cleanup on exit
echo.
echo Shutting down servers...
taskkill /FI "WINDOWTITLE eq Starforged Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Starforged Client*" /T /F >nul 2>&1
echo Servers stopped.
timeout /t 2 >nul
