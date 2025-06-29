@echo off
REM ========================================
REM Cursor Live Authentication Diagnostics
REM ========================================
REM
REM This script monitors Cursor processes and captures
REM real-time authentication attempts and errors.
REM
REM SAFETY: Read-only monitoring - no system changes
REM
REM ========================================

echo ========================================
echo Cursor Live Authentication Diagnostics
echo ========================================
echo.
echo SAFETY: Read-only monitoring - no system changes
echo.
echo This script will monitor Cursor processes and capture
echo authentication attempts and errors in real-time.
echo.
echo Instructions:
echo 1. Keep this window open
echo 2. Try to authenticate in Cursor
echo 3. Watch for any error messages below
echo 4. Press Ctrl+C to stop monitoring
echo.
echo ========================================
echo.

REM Create output file
set OUTPUT_FILE=diagnostics\cursor_live_auth_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt
set OUTPUT_FILE=%OUTPUT_FILE: =0%

echo Cursor Live Authentication Diagnostics > "%OUTPUT_FILE%"
echo Started: %date% %time% >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo [INFO] Starting Cursor process monitoring...
echo [INFO] Starting Cursor process monitoring... >> "%OUTPUT_FILE%"

REM Monitor Cursor processes and network connections
:monitor_loop
echo.
echo [%time%] Checking Cursor processes and network activity...
echo [%time%] Checking Cursor processes and network activity... >> "%OUTPUT_FILE%"

REM Check if Cursor is running
tasklist /fi "imagename eq Cursor.exe" 2>&1 | find "Cursor.exe" >nul
if %errorlevel% equ 0 (
    echo [%time%] Cursor.exe is running
    echo [%time%] Cursor.exe is running >> "%OUTPUT_FILE%"
    
    REM Get Cursor process details
    tasklist /fi "imagename eq Cursor.exe" /v >> "%OUTPUT_FILE%" 2>&1
    
    REM Check network connections for Cursor
    echo [%time%] Checking Cursor network connections... >> "%OUTPUT_FILE%"
    netstat -ano | find "Cursor.exe" >> "%OUTPUT_FILE%" 2>&1
    
    REM Check for any new network connections to auth-related domains
    echo [%time%] Checking connections to auth domains... >> "%OUTPUT_FILE%"
    netstat -ano | find "cursor.sh" >> "%OUTPUT_FILE%" 2>&1
    netstat -ano | find "github.com" >> "%OUTPUT_FILE%" 2>&1
    netstat -ano | find "api.github.com" >> "%OUTPUT_FILE%" 2>&1
    netstat -ano | find "oauth" >> "%OUTPUT_FILE%" 2>&1
    
) else (
    echo [%time%] Cursor.exe is not running
    echo [%time%] Cursor.exe is not running >> "%OUTPUT_FILE%"
)

REM Check for any error messages in Windows Event Log (user-level only)
echo [%time%] Checking recent application errors... >> "%OUTPUT_FILE%"
wevtutil qe Application /c:5 /f:text | find "Cursor" >> "%OUTPUT_FILE%" 2>&1
wevtutil qe Application /c:5 /f:text | find "Error" >> "%OUTPUT_FILE%" 2>&1

REM Check DNS resolution for auth domains
echo [%time%] Testing DNS resolution... >> "%OUTPUT_FILE%"
nslookup cursor.sh >> "%OUTPUT_FILE%" 2>&1
nslookup api.github.com >> "%OUTPUT_FILE%" 2>&1

REM Check if any new files were created in Cursor directories
echo [%time%] Checking for new files in Cursor directories... >> "%OUTPUT_FILE%"
dir "C:\Users\%USERNAME%\AppData\Roaming\Cursor" /od | find "06/25/2025" >> "%OUTPUT_FILE%" 2>&1

echo [%time%] Waiting 10 seconds before next check...
echo [%time%] Waiting 10 seconds before next check... >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"

REM Wait 10 seconds before next check
timeout /t 10 /nobreak >nul

REM Continue monitoring
goto monitor_loop 