@echo off
REM Quick IoT Device Connection Test Script for Windows
REM Copy this to c:\appdev\fast-api\ and run: test_device_connection.bat

echo.
echo ============================================================
echo IoT Device Connection Test
echo ============================================================
echo.

setlocal enabledelayedexpansion

REM Configuration
set BACKEND_URL=http://172.22.231.200:8001
set DEVICE_ID=esp32-plant-01

echo [1] Testing Backend Connectivity...
echo.
curl -s -o nul -w "Backend Health: %%{http_code}\n" %BACKEND_URL%/health
echo.

echo [2] Fetching Telemetry for Device: %DEVICE_ID%
echo.
echo URL: %BACKEND_URL%/api/iot/telemetry/?device_id=%DEVICE_ID%^&limit=5
echo.
curl -s "%BACKEND_URL%/api/iot/telemetry/?device_id=%DEVICE_ID%&limit=5" | python -m json.tool 2>nul || (
    echo Failed to parse JSON response
)
echo.

echo [3] Running Python Diagnostic...
echo.
python check_device_connection.py %DEVICE_ID%
echo.

echo ============================================================
echo Test Complete
echo ============================================================
echo.
