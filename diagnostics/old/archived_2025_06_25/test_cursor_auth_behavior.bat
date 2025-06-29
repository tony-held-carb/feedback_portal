@echo off
echo Testing Cursor Authentication Behavior...
echo.

echo Step 1: Check current Git credentials
echo.
git config --list | findstr credential
echo.

echo Step 2: Check if any GitHub tokens are stored
echo.
if exist "%USERPROFILE%\.git-credentials" (
    echo Found .git-credentials file
    type "%USERPROFILE%\.git-credentials"
) else (
    echo No .git-credentials file found
)
echo.

echo Step 3: Test Git authentication directly
echo.
echo Testing git push to trigger authentication...
echo This will help determine if Git auth works with stored tokens
echo.

echo Step 4: Cursor Authentication Test
echo.
echo Now test Cursor's login behavior:
echo 1. Open Cursor
echo 2. Try to use GitHub features (Sync, Push, etc.)
echo 3. See if it shows login button or uses stored credentials
echo.

echo Step 5: Check Cursor Settings
echo.
echo Look for GitHub settings in Cursor:
echo - Press Ctrl+, to open settings
echo - Search for "GitHub" or "git"
echo - Look for authentication options
echo.

echo Step 6: Alternative Approaches
echo.
echo If Cursor still shows login button:
echo - Look for "Use token" or "Skip OAuth" options
echo - Check if there's a GitHub extension to install
echo - Try configuring Git credentials first, then test Cursor
echo.

pause 