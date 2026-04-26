# FastAPI Startup Script for Smart Plant Watering System
# Run this file to start the FastAPI backend on port 8001 (Independent)

# Navigate to FastAPI directory
$fastAPIPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $fastAPIPath

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FastAPI Backend - Smart Plant Watering" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting FastAPI on http://localhost:8001" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8001/docs" -ForegroundColor Green
Write-Host ""

# Use virtual environment Python
$pythonExe = '..\.venv\Scripts\python.exe'

# Check if venv exists
if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please ensure .venv is installed in the parent directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Get Python version
$pythonVersion = &$pythonExe --version

Write-Host "Using Python: $pythonVersion" -ForegroundColor Yellow
Write-Host ""

# Start FastAPI
Write-Host "Database: SQLite (fastapi.db)" -ForegroundColor Yellow
Write-Host ""
&$pythonExe -m uvicorn main:app --reload --port 8001 --host 0.0.0.0

