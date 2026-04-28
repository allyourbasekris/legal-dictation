@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

:: Check / Install Python via winget
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Attempting auto-install via winget...
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
    if !errorlevel! neq 0 (
        echo.
        echo Auto-install failed. Install Python 3.10+ manually from https://python.org
        echo Make sure to check "Add Python to PATH" during installation.
        pause
        exit /b 1
    )
    echo.
    echo Python installed. Restart this script to pick up PATH changes.
    pause
    exit /b 0
)

:: Check / Install ffmpeg via winget
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo ffmpeg not found. Attempting auto-install via winget...
    winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
    if !errorlevel! neq 0 (
        echo Auto-install failed. Install ffmpeg manually from https://ffmpeg.org
        pause
        exit /b 1
    )
    echo.
    echo ffmpeg installed. Restart this script to pick up PATH changes.
    pause
    exit /b 0
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
