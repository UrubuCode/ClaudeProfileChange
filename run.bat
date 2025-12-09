@echo off
REM Claude Profile Manager - Windows Launcher
echo Starting Claude Profile Manager...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Run the application
python main.py

REM Pause if there was an error
if errorlevel 1 (
    echo.
    echo Application exited with error. Press any key to close...
    pause >nul
)