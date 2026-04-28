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
goto launch

:install_deps_fail
echo pip install failed.
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
