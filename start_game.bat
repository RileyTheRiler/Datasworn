@echo off
echo ========================================================
echo       Starforged AI Game Master - Launcher
echo ========================================================

echo.
echo [1/2] Starting Backend Server...
start "Starforged_Backend" cmd /k "python src/server.py"

echo.
echo [2/2] Starting Frontend Server...
cd frontend
start "Starforged_Frontend" cmd /k "npm run dev"
cd ..

echo.
echo Waiting for servers to initialize...
timeout /t 5 > nul
start http://localhost:5173

echo.
echo ========================================================
echo Game is running! 
echo.
echo 1. The backend should be running on port 8000
echo 2. The frontend should open in your browser automatically
echo    (If not, go to http://localhost:5173)
echo.
echo PRESS ANY KEY TO STOP SERVERS AND EXIT
echo ========================================================
pause > nul

echo.
echo Stopping servers...
taskkill /FI "WINDOWTITLE eq Starforged_Backend*" /T /F
taskkill /FI "WINDOWTITLE eq Starforged_Frontend*" /T /F

echo Done.
timeout /t 2 > nul
