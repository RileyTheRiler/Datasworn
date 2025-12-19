@echo off
cd /d %~dp0
title Starforged Backend
echo ==========================================
echo    STARFORGED AI GAME MASTER - SERVER
echo ==========================================
echo.
echo Starting backend...
python main.py
echo.
echo Server stopped.
pause
