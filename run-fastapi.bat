@echo off
REM FastAPI Startup Script for Smart Plant Watering System
REM Run this file to start the FastAPI backend on port 8001 (Independent)

cd /d "%~dp0"
echo.
echo ========================================
echo FastAPI Backend - Smart Plant Watering
echo ========================================
echo.
echo Starting FastAPI on http://localhost:8001
echo API Docs: http://localhost:8001/docs
echo.

REM Use virtual environment Python
set VENV_PYTHON=..\.venv\Scripts\python.exe

REM Check if venv exists
if not exist "%VENV_PYTHON%" (
    echo ERROR: Virtual environment not found!
    echo Please ensure .venv is installed in the parent directory.
    pause
    exit /b 1
)

REM Start FastAPI with auto-reload
"%VENV_PYTHON%" -m uvicorn main:app --reload --port 8001 --host 0.0.0.0

pause
