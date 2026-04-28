@echo off
setlocal
cd /d "%~dp0"

python --version >nul 2>&1
if %errorlevel% neq 0 goto install_python
goto check_ffmpeg

:install_python
echo Python not found. Attempting auto-install via winget...
winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
if %errorlevel% neq 0 goto install_python_fail
echo Python installed. Restart this script to pick up PATH.
pause
exit /b 0

:install_python_fail
echo Auto-install failed. Get Python 3.10+ from https://python.org
pause
exit /b 1

:check_ffmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 goto install_ffmpeg
goto setup_venv

:install_ffmpeg
echo ffmpeg not found. Attempting auto-install via winget...
winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
if %errorlevel% neq 0 goto install_ffmpeg_fail
echo ffmpeg installed. Restart this script to pick up PATH.
pause
exit /b 0

:install_ffmpeg_fail
echo Auto-install failed. Install ffmpeg manually.
pause
exit /b 1

:setup_venv
if exist "venv\Scripts\python.exe" goto install_deps
echo Creating virtual environment...
python -m venv venv

:install_deps
call venv\Scripts\activate.bat
echo Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 goto install_deps_fail
echo Python dependencies installed.
goto check_llama

:install_deps_fail
echo pip install failed.
pause
exit /b 1

:check_llama
set CACHE_DIR=%USERPROFILE%\.cache\legal-dictation
if not exist "%CACHE_DIR%" mkdir "%CACHE_DIR%"
if exist "%CACHE_DIR%\llama-cli.exe" goto launch
echo Downloading llama-cli binary (~16 MB)...
curl -L -o "%CACHE_DIR%\llama.zip" "https://github.com/ggml-org/llama.cpp/releases/download/b8953/llama-b8953-bin-win-cpu-x64.zip" --progress-bar
if %errorlevel% neq 0 goto download_llama_fail
echo Extracting...
python extract_llama.py "%CACHE_DIR%\llama.zip" "%CACHE_DIR%"
if %errorlevel% neq 0 goto extract_llama_fail
if exist "%CACHE_DIR%\llama.zip" del "%CACHE_DIR%\llama.zip" >nul
if not exist "%CACHE_DIR%\llama-cli.exe" goto extract_llama_fail
echo llama-cli ready.
goto launch

:download_llama_fail
echo Download failed. Check your internet connection.
pause
exit /b 1

:extract_llama_fail
echo Could not find llama-cli.exe in the archive.
pause
exit /b 1

:launch
echo.
echo Setup complete. Launching...
python main.py
if %errorlevel% neq 0 goto launch_fail
goto end

:launch_fail
echo.
echo Application exited with error.
pause

:end
