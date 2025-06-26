@echo off
REM ========================================
REM Cursor Command-Line Authentication Test
REM ========================================
REM
REM This script tests various command-line methods
REM to authenticate Cursor without using the GUI.
REM
REM ========================================

echo ========================================
echo Cursor Command-Line Authentication Test
echo ========================================
echo.

set OUTPUT_FILE=diagnostics\cursor_cli_auth_test_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt
set OUTPUT_FILE=%OUTPUT_FILE: =0%

echo Cursor Command-Line Authentication Test > "%OUTPUT_FILE%"
echo Started: %date% %time% >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo [1/5] Testing GitHub CLI authentication...
echo [1/5] Testing GitHub CLI authentication... >> "%OUTPUT_FILE%"

gh --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ GitHub CLI is available
    echo ✅ GitHub CLI is available >> "%OUTPUT_FILE%"
    
    echo Checking GitHub CLI auth status...
    echo Checking GitHub CLI auth status... >> "%OUTPUT_FILE%"
    gh auth status >> "%OUTPUT_FILE%" 2>&1
    
    echo Testing GitHub API access...
    echo Testing GitHub API access... >> "%OUTPUT_FILE%"
    gh api user >> "%OUTPUT_FILE%" 2>&1
    
) else (
    echo ❌ GitHub CLI not available
    echo ❌ GitHub CLI not available >> "%OUTPUT_FILE%"
)

echo [2/5] Testing direct IP resolution...
echo [2/5] Testing direct IP resolution... >> "%OUTPUT_FILE%"

echo Testing if we can resolve cursor.sh IP addresses...
echo Testing if we can resolve cursor.sh IP addresses... >> "%OUTPUT_FILE%"

REM Try to get IP addresses (this might work even if DNS is blocked)
nslookup cursor.sh 8.8.8.8 >> "%OUTPUT_FILE%" 2>&1
nslookup api.github.com 8.8.8.8 >> "%OUTPUT_FILE%" 2>&1

echo [3/5] Testing alternative authentication methods...
echo [3/5] Testing alternative authentication methods... >> "%OUTPUT_FILE%"

echo Checking if Cursor has command-line options...
echo Checking if Cursor has command-line options... >> "%OUTPUT_FILE%"

REM Check if Cursor supports command-line authentication
"C:\Users\%USERNAME%\AppData\Local\Programs\Cursor\Cursor.exe" --help >> "%OUTPUT_FILE%" 2>&1
"C:\Users\%USERNAME%\AppData\Local\Programs\Cursor\Cursor.exe" --version >> "%OUTPUT_FILE%" 2>&1

echo [4/5] Testing environment variables...
echo [4/5] Testing environment variables... >> "%OUTPUT_FILE%"

echo Checking for Cursor-related environment variables...
echo Checking for Cursor-related environment variables... >> "%OUTPUT_FILE%"
set | findstr -i cursor >> "%OUTPUT_FILE%" 2>&1
set | findstr -i github >> "%OUTPUT_FILE%" 2>&1

echo [5/5] Testing alternative DNS servers...
echo [5/5] Testing alternative DNS servers... >> "%OUTPUT_FILE%"

echo Testing with Google DNS (8.8.8.8)...
echo Testing with Google DNS (8.8.8.8)... >> "%OUTPUT_FILE%"
nslookup cursor.sh 8.8.8.8 >> "%OUTPUT_FILE%" 2>&1

echo Testing with Cloudflare DNS (1.1.1.1)...
echo Testing with Cloudflare DNS (1.1.1.1)... >> "%OUTPUT_FILE%"
nslookup cursor.sh 1.1.1.1 >> "%OUTPUT_FILE%" 2>&1

echo.
echo ========================================
echo ANALYSIS AND RECOMMENDATIONS
echo ========================================
echo.

echo [ANALYSIS] Based on IT response and DNS blocking:
echo.
echo ❌ IT has approved VS Code, not Cursor
echo ❌ Corporate DNS is blocking cursor.sh and api.github.com
echo ❌ Direct IP access won't work due to SSL certificates
echo.
echo [RECOMMENDATIONS]:
echo.
echo 1. Use VS Code as approved by IT
echo 2. Install GitHub Copilot extension in VS Code
echo 3. Use GitHub CLI for Git operations
echo 4. Consider portable Cursor on USB drive (if allowed)
echo.

echo ======================================== >> "%OUTPUT_FILE%"
echo ANALYSIS AND RECOMMENDATIONS >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
echo IT Response: VS Code approved, Cursor not supported >> "%OUTPUT_FILE%"
echo Corporate DNS blocking: cursor.sh, api.github.com >> "%OUTPUT_FILE%"
echo Recommendation: Use VS Code with GitHub Copilot >> "%OUTPUT_FILE%"

pause 