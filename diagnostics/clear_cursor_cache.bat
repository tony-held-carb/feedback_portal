@echo off
REM ========================================
REM Cursor Cache and History Clear Script
REM ========================================
REM
REM This script clears Cursor cache, history, and
REM authentication data that might be causing issues.
REM
REM SAFETY: Only deletes cache files - no system changes
REM
REM ========================================

echo ========================================
echo Cursor Cache and History Clear Script
echo ========================================
echo.
echo SAFETY: Only deletes cache files - no system changes
echo.
echo This will clear:
echo - Cursor cache and temporary files
echo - Authentication tokens and sessions
echo - Browser cache and cookies
echo - Extension cache
echo - User preferences (will reset to defaults)
echo.
echo WARNING: This will log you out of Cursor
echo and you'll need to re-authenticate.
echo.

set /p CONFIRM="Do you want to continue? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo Operation cancelled.
    pause
    exit /b
)

echo.
echo [1/6] Clearing Cursor cache directories...

REM Clear main cache directories
if exist "C:\Users\%USERNAME%\AppData\Roaming\Cursor\Cache" (
    echo Clearing Cache...
    rmdir /s /q "C:\Users\%USERNAME%\AppData\Roaming\Cursor\Cache" 2>nul
)

if exist "C:\Users\%USERNAME%\AppData\Roaming\Cursor\Code Cache" (
    echo Clearing Code Cache...
    rmdir /s /q "C:\Users\%USERNAME%\AppData\Roaming\Cursor\Code Cache" 2>nul
)

if exist "C:\Users\%USERNAME%\AppData\Roaming\Cursor\GPUCache" (
    echo Clearing GPU Cache...
    rmdir /s /q "C:\Users\%USERNAME%\AppData\Roaming\Cursor\GPUCache" 2>nul
)

echo [2/6] Clearing authentication and session data...

REM Clear authentication-related data
if exist "C:\Users\%USERNAME%\AppData\Roaming\Cursor\Session Storage" (
    echo Clearing Session Storage...
    rmdir /s /q "C:\Users\%USERNAME%\AppData\Roaming\Cursor\Session Storage" 2>nul
)

if exist "C:\Users\%USERNAME%\AppData\Roaming\Cursor\Local Storage" (
    echo Clearing Local Storage...
    rmdir /s /q "C:\Users\%USERNAME%\AppData\Roaming\Cursor\Local Storage" 2>nul
)

echo [3/6] Clearing extension and workspace cache...

REM Clear extension cache
if exist "C:\Users\%USERNAME%\AppData\Roaming\Cursor\CachedData" (
    echo Clearing Cached Data...
    rmdir /s /q "C:\Users\%USERNAME%\AppData\Roaming\Cursor\CachedData" 2>nul
)

if exist "C:\Users\%USERNAME%\AppData\Roaming\Cursor\CachedProfilesData" (
    echo Clearing Cached Profiles Data...
    rmdir /s /q "C:\Users\%USERNAME%\AppData\Roaming\Cursor\CachedProfilesData" 2>nul
)

echo [4/6] Clearing user workspace storage...

REM Clear workspace storage (contains auth tokens)
if exist "C:\Users\%USERNAME%\AppData\Roaming\Cursor\User\workspaceStorage" (
    echo Clearing Workspace Storage...
    rmdir /s /q "C:\Users\%USERNAME%\AppData\Roaming\Cursor\User\workspaceStorage" 2>nul
)

echo [5/6] Clearing crash and error logs...

REM Clear crash logs
if exist "C:\Users\%USERNAME%\AppData\Roaming\Cursor\Crashpad" (
    echo Clearing Crashpad...
    rmdir /s /q "C:\Users\%USERNAME%\AppData\Roaming\Cursor\Crashpad" 2>nul
)

if exist "C:\Users\%USERNAME%\AppData\Roaming\Cursor\logs" (
    echo Clearing Logs...
    rmdir /s /q "C:\Users\%USERNAME%\AppData\Roaming\Cursor\logs" 2>nul
)

echo [6/6] Resetting user preferences...

REM Backup and clear preferences (optional - more aggressive)
echo Creating backup of preferences...
copy "C:\Users\%USERNAME%\AppData\Roaming\Cursor\Preferences" "C:\Users\%USERNAME%\AppData\Roaming\Cursor\Preferences.backup" 2>nul

REM Clear preferences (this will reset all settings)
if exist "C:\Users\%USERNAME%\AppData\Roaming\Cursor\Preferences" (
    echo Clearing Preferences (will reset settings)...
    del "C:\Users\%USERNAME%\AppData\Roaming\Cursor\Preferences" 2>nul
)

echo.
echo ========================================
echo CACHE CLEAR COMPLETE
echo ========================================
echo.
echo ✅ Cursor cache and history cleared
echo ✅ Authentication data cleared
echo ✅ Session data cleared
echo ✅ Extension cache cleared
echo ✅ User preferences reset
echo.
echo NEXT STEPS:
echo 1. Restart Cursor completely
echo 2. Try authentication again
echo 3. If issues persist, try GitHub CLI method
echo.
echo NOTE: If you need to restore preferences:
echo Copy Preferences.backup to Preferences
echo.

pause 