@echo off
REM Admin Setup Tool for FastAPI
REM Use this to create admin users and sample data

cd /d "%~dp0"

echo.
echo ========================================
echo FastAPI Admin Setup Tool
echo ========================================
echo.

REM Use virtual environment Python
set VENV_PYTHON=..\.venv\Scripts\python.exe

if not exist "%VENV_PYTHON%" (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

"%VENV_PYTHON%" admin_setup.py

pause
