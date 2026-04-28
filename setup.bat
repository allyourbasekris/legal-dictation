@echo off
setlocal
cd /d "%~dp0"

:: Check / Install Python via winget
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Attempting auto-install via winget...
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
    if %errorlevel% neq 0 (
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
    if %errorlevel% neq 0 (
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
    if %errorlevel% neq 0 (
        echo Failed to create venv
        pause
        exit /b 1
    )
) else (
    echo Virtual environment found.
)

:: Activate and install Python deps
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo pip install failed
    pause
    exit /b 1
)

:: Check for llama-cli binary
set "CACHE_DIR=%USERPROFILE%\.cache\legal-dictation"
if not exist "%CACHE_DIR%" mkdir "%CACHE_DIR%"
if not exist "%CACHE_DIR%\llama-cli.exe" (
    echo.
    echo Downloading llama-cli (llama.cpp binary, ~30 MB)...
    set "ZIP_URL=https://github.com/ggml-org/llama.cpp/releases/download/b4822/llama-b4822-bin-win-cuda-cu12.6-x64.zip"
    set "ZIP_FILE=%CACHE_DIR%\llama.zip"
    curl -L -o "%CACHE_DIR%\llama.zip" "%ZIP_URL%" --progress-bar
    if %errorlevel% neq 0 (
        echo Failed to download llama-cli. Check your internet connection.
        pause
        exit /b 1
    )
    echo Extracting...
    powershell -Command "& {try { $z='%CACHE_DIR:\=\\%\\llama.zip'; Expand-Archive -Path $z -DestinationPath '%CACHE_DIR%\\llama_extract' -Force -ErrorAction Stop; Write-Host 'ok' } catch { Write-Host 'extract failed'; exit 1 }}" >nul
    if %errorlevel% neq 0 (
        echo Extract failed.
        pause
        exit /b 1
    )
    :: Move llama-cli.exe from wherever it landed to cache root
    if exist "%CACHE_DIR%\llama_extract\build\bin\Release\llama-cli.exe" (
        move /Y "%CACHE_DIR%\llama_extract\build\bin\Release\llama-cli.exe" "%CACHE_DIR%\llama-cli.exe" >nul
    )
    :: If not in the expected path, search recursively
    if not exist "%CACHE_DIR%\llama-cli.exe" (
        dir /s /b "%CACHE_DIR%\llama_extract\llama-cli.exe" > "%CACHE_DIR%\find_result.txt" 2>nul
        for /f "usebackq delims=" %%f in ("%CACHE_DIR%\find_result.txt") do (
            move /Y "%%f" "%CACHE_DIR%\llama-cli.exe" >nul 2>&1
        )
        del "%CACHE_DIR%\find_result.txt" >nul 2>&1
    )
    :: Cleanup
    if exist "%CACHE_DIR%\llama_extract" rmdir /S /Q "%CACHE_DIR%\llama_extract" >nul 2>&1
    del "%CACHE_DIR%\llama.zip" >nul 2>&1

    if not exist "%CACHE_DIR%\llama-cli.exe" (
        echo Could not find llama-cli.exe in the extracted archive.
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
    echo Application exited with error. Press any key to close.
    pause
)

deactivate
