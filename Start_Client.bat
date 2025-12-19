@echo off
cd /d %~dp0
title Starforged Game Client
echo ==========================================
echo    STARFORGED AI GAME MASTER - CLIENT
echo ==========================================
echo.
echo Starting frontend...
cd frontend
npm run dev
echo.
echo Client stopped.
pause
