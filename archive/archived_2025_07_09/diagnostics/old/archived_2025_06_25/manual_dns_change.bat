@echo off
REM ========================================
REM Manual DNS Change Script
REM ========================================
REM
REM This script attempts to change DNS settings
REM to bypass corporate DNS blocking.
REM
REM WARNING: May require admin rights
REM
REM ========================================

echo ========================================
echo Manual DNS Change Script
echo ========================================
echo.
echo This script will attempt to change your DNS settings.
echo.
echo WARNING: This may require admin rights and could affect
echo your network connectivity. Proceed with caution.
echo.

set /p CONFIRM="Do you want to continue? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo Operation cancelled.
    pause
    exit /b
)

echo.
echo [STEP 1] Checking current DNS settings...
echo Current DNS settings:
ipconfig /all | findstr "DNS Servers"
echo.

echo [STEP 2] Testing current Cursor domain access...
echo Testing cursor.sh with current DNS:
nslookup cursor.sh
echo.

echo [STEP 3] Attempting to change DNS to Google DNS...
echo Attempting to change Wi-Fi DNS to 8.8.8.8...
netsh interface ip set dns "Wi-Fi" static 8.8.8.8
if %errorlevel% equ 0 (
    echo ✅ DNS change successful!
    echo Adding secondary DNS 8.8.4.4...
    netsh interface ip add dns "Wi-Fi" 8.8.4.4 index=2
) else (
    echo ❌ DNS change failed - likely requires admin rights
    echo.
    echo [ALTERNATIVE] Trying Ethernet adapter...
    netsh interface ip set dns "Ethernet" static 8.8.8.8
    if %errorlevel% equ 0 (
        echo ✅ DNS change successful on Ethernet!
    ) else (
        echo ❌ DNS change failed on both adapters
        echo Admin rights required for DNS changes.
        pause
        exit /b
    )
)

echo.
echo [STEP 4] Verifying DNS change...
echo New DNS settings:
ipconfig /all | findstr "DNS Servers"
echo.

echo [STEP 5] Testing Cursor domains with new DNS...
echo Testing cursor.sh with new DNS:
nslookup cursor.sh
echo.

echo Testing api.github.com with new DNS:
nslookup api.github.com
echo.

echo [STEP 6] Testing Cursor authentication...
echo.
echo If DNS resolution works above, try Cursor authentication now.
echo.
echo [IMPORTANT] To revert DNS changes later, run:
echo netsh interface ip set dns "Wi-Fi" dhcp
echo.

echo ========================================
echo NEXT STEPS
echo ========================================
echo.
echo 1. Try to authenticate in Cursor
echo 2. If it works, you can use Cursor at work!
echo 3. If it doesn't work, revert DNS and use hybrid approach
echo 4. Remember to revert DNS when done: netsh interface ip set dns "Wi-Fi" dhcp
echo.

pause 