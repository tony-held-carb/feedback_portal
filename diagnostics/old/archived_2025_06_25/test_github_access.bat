@echo off
echo Testing GitHub access via Chrome DNS-over-HTTPS...
echo.

echo IMPORTANT: Make sure you've enabled DNS-over-HTTPS in Chrome first:
echo 1. Open Chrome
echo 2. Go to Settings ^> Privacy and security ^> Security
echo 3. Enable "Use secure DNS" and select Google or Cloudflare
echo 4. Close Chrome completely
echo.

echo Press any key when you've enabled DoH in Chrome...
pause >nul

echo.
echo Testing GitHub access...
echo Opening Chrome in incognito mode to test GitHub...

start chrome --incognito --disable-web-security --user-data-dir="%TEMP%\github_test" https://github.com

echo.
echo Check if GitHub loaded successfully in the incognito window.
echo.
echo If GitHub loaded:
echo - You can now generate a personal access token
echo - Go to GitHub ^> Settings ^> Developer settings ^> Personal access tokens
echo - Generate a new token with repo and workflow permissions
echo - Copy the token for use in Cursor
echo.
echo If GitHub failed to load:
echo - Try a different DNS provider (Cloudflare, Quad9)
echo - Check if corporate firewall blocks HTTPS DNS traffic
echo - Consider using mobile hotspot temporarily
echo.
pause 