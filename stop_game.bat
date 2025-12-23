@echo off
echo ===========================================
echo   Stopping Starforged Game Servers
echo ===========================================
echo.

echo Stopping Backend Server...
taskkill /FI "WINDOWTITLE eq Starforged Backend*" /T /F >nul 2>&1

echo Stopping Frontend Server...
taskkill /FI "WINDOWTITLE eq Starforged Client*" /T /F >nul 2>&1

echo.
echo All servers stopped.
echo.
pause
