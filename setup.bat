@echo off
setlocal
cd /d "%~dp0"

:: Check / Install Python via winget
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Attempting auto-install via winget...
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
    if %errorlevel% neq 0 (
        echo Auto-install failed. Get Python 3.10+ from https://python.org
        pause
        exit /b 1
    )
    echo Python installed. Restart this script to pick up PATH.
    pause
    exit /b 0
)

:: Check / Install ffmpeg via winget
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo ffmpeg not found. Attempting auto-install via winget...
    winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
    if %errorlevel% neq 0 (
        echo Auto-install failed. Install ffmpeg manually.
        pause
        exit /b 1
    )
    echo ffmpeg installed. Restart this script to pick up PATH.
    pause
    exit /b 0
)

:: Create venv if missing
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

:: Install Python deps (route to log to avoid parsing issues with > and < in pip output)
echo Installing Python dependencies...
pip install -r requirements.txt > "%TEMP%\pip_install.log" 2>&1
set PIPEXIT=%errorlevel%
if "%PIPEXIT%" neq "0" (
    echo.
    echo pip install failed. Last lines of output:
    type "%TEMP%\pip_install.log"
    del "%TEMP%\pip_install.log" >nul 2>&1
    pause
    exit /b 1
)
del "%TEMP%\pip_install.log" >nul 2>&1
echo Python dependencies installed.

:: Check for llama-cli binary
set CACHE_DIR=%USERPROFILE%\.cache\legal-dictation
if not exist "%CACHE_DIR%" mkdir "%CACHE_DIR%"
if not exist "%CACHE_DIR%\llama-cli.exe" (
    echo Downloading llama-cli binary (~30 MB)...
    cmd /c curl -L -o "%CACHE_DIR%\llama.zip" "https://github.com/ggml-org/llama.cpp/releases/download/b4822/llama-b4822-bin-win-cuda-cu12.6-x64.zip" --progress-bar
    if %errorlevel% neq 0 (
        echo Download failed.
        pause
        exit /b 1
    )
    echo Extracting...
    powershell -Command "try { Expand-Archive -Path '%CACHE_DIR%\\llama.zip' -DestinationPath '%CACHE_DIR%' -Force; Write-Host ok } catch { exit 1 }" >nul
    if %errorlevel% neq 0 (
        echo Extract failed.
        pause
        exit /b 1
    )
    :: Move llama-cli.exe to cache root if nested in subfolders
    if exist "%CACHE_DIR%\build\bin\Release\llama-cli.exe" (
        move /Y "%CACHE_DIR%\build\bin\Release\llama-cli.exe" "%CACHE_DIR%\llama-cli.exe" >nul
    )
    if not exist "%CACHE_DIR%\llama-cli.exe" (
        dir /s /b "%CACHE_DIR%\llama-cli.exe" 2>nul > "%TEMP%\llama_find.txt"
        for /f "usebackq delims=" %%f in ("%TEMP%\llama_find.txt") do move /Y "%%f" "%CACHE_DIR%\llama-cli.exe" >nul 2>&1
        del "%TEMP%\llama_find.txt" >nul 2>&1
    )
    :: Cleanup
    if exist "%CACHE_DIR%\build" rmdir /s /q "%CACHE_DIR%\build" >nul 2>&1
    if exist "%CACHE_DIR%\llama.zip" del "%CACHE_DIR%\llama.zip" >nul
    if not exist "%CACHE_DIR%\llama-cli.exe" (
        echo Could not find llama-cli.exe in the archive.
        pause
        exit /b 1
    )
    echo llama-cli ready.
)

echo.
echo Setup complete. Launching...
python main.py
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error.
    pause
)
