@echo off
echo Testing Cursor Authentication Options...
echo.

echo Step 1: Generate GitHub Token
echo - Go to https://github.com
echo - Settings ^> Developer settings ^> Personal access tokens
echo - Generate new token with repo and workflow permissions
echo - Copy the token
echo.

echo Step 2: Check Cursor Settings
echo - Open Cursor
echo - Go to Settings (Ctrl+,)
echo - Look for:
echo   * Extensions ^> GitHub
echo   * Git settings
echo   * Authentication options
echo.

echo Step 3: Try Git Configuration
echo - Open terminal in Cursor
echo - Run: git config --global user.name "YourUsername"
echo - Run: git config --global user.email "your-email@example.com"
echo - Run: git config --global credential.helper store
echo.

echo Step 4: Test Authentication
echo - Try to clone a repo or push changes
echo - When prompted for password, use the token instead
echo - Should work without browser prompts
echo.

echo If Cursor still tries browser auth:
echo - Look for "Use token" or "Skip OAuth" options
echo - Check if there's an "Advanced" authentication mode
echo - Try configuring Git credentials first
echo.

pause 