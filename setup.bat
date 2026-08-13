@echo off
REM 2048 local setup (Windows)

echo.
echo 2048 Game Setup
echo ===============
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Installation failed
    pause
    exit /b 1
)

echo.
echo SUCCESS. Run:
echo   .venv\Scripts\activate
echo   python main.py
echo.
pause
