@echo off
cd /d %~dp0
title Sprite Slicer Tool
echo ==========================================
echo          SPRITE SLICER TOOL
echo ==========================================
echo.
echo This tool will split a sprite sheet into individual images.
echo.

:ask_file
set /p img="> Drag and drop your image file here: "
:: Remove quotes if they exist
set img=%img:"=%

if not exist "%img%" (
    echo File not found! Please try again.
    goto ask_file
)

echo.
echo Enter grid details (e.g., for that character sheet: 6 cols, 4 rows)
set /p cols="> Columns: "
set /p rows="> Rows: "
set /p pad="> Padding (pixels to trim, default 0): "
if "%pad%"=="" set pad=0

echo.
echo Slicing...
python src/sprite_slicer.py "%img%" --cols %cols% --rows %rows% --padding %pad%
echo.
pause
