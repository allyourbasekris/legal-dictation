@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

:: Check ffmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo ffmpeg not found. Install from https://ffmpeg.org or via winget:
    echo   winget install ffmpeg
    pause
    exit /b 1
)

:: Create venv if missing
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo Failed to create venv
        pause
        exit /b 1
    )
) else (
    echo Virtual environment found.
)

:: Activate and install
call venv\Scripts\activate.bat

echo Installing dependencies (first run downloads ~1.5 GB of models)...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo pip install failed
    pause
    exit /b 1
)

echo.
echo Setup complete. Launching...
python main.py
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error. Press any key to close.
    pause
)

deactivate
