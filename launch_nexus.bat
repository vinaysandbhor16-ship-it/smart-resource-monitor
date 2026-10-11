@echo off
title NEXUS Smart Resource Monitor
cd /d "%~dp0"
echo Launching NEXUS Resource Monitor...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with an error or Python was not found in PATH.
    pause
)
