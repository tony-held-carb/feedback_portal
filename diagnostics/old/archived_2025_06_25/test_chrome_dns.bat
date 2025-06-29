@echo off
echo Testing Chrome DNS-over-HTTPS access to GitHub...
echo.

echo Step 1: Check if Chrome is running
tasklist /FI "IMAGENAME eq chrome.exe" 2>NUL | find /I /N "chrome.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Chrome is running - please close it first
    echo Then enable DNS-over-HTTPS in Chrome settings
    echo.
    echo Instructions:
    echo 1. Open Chrome
    echo 2. Go to Settings ^> Privacy and security ^> Security
    echo 3. Enable "Use secure DNS" and select Google or Cloudflare
    echo 4. Close Chrome
    echo 5. Run this script again
    pause
    exit /b
)

echo Step 2: Testing DNS resolution with Chrome's DoH
echo.
echo Attempting to access GitHub via Chrome...
start chrome --incognito --disable-web-security --user-data-dir="%TEMP%\chrome_test" https://github.com

echo.
echo Step 3: Check if GitHub loaded successfully
echo.
echo If GitHub loaded in the incognito window:
echo - You can now authenticate with GitHub
echo - Generate a personal access token
echo - Use that token in Cursor
echo.
echo If GitHub failed to load:
echo - Try a different DNS provider (Cloudflare, Quad9)
echo - Check if corporate firewall blocks HTTPS DNS
echo.
pause 