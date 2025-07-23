@echo off
setlocal enabledelayedexpansion

:: Output file
set "OUT=git_vscode_work_config_dump.txt"
echo Collecting Git and VS Code diagnostics... > "%OUT%"
echo. >> "%OUT%"

:: ----------------------
:: Git Global Config
:: ----------------------
echo ================ git config --list --show-origin ================ >> "%OUT%"
git config --list --show-origin >> "%OUT%" 2>&1
echo. >> "%OUT%"

:: Git Version
echo ======================= git --version ========================== >> "%OUT%"
git --version >> "%OUT%" 2>&1
echo. >> "%OUT%"

:: ----------------------
:: VS Code Extensions
:: ----------------------
echo ===================== VS Code Extensions ======================== >> "%OUT%"
where code >nul 2>&1
if %errorlevel%==0 (
  code --list-extensions --show-versions >> "%OUT%" 2>&1
) else (
  echo 'code' command not found in PATH. >> "%OUT%"
)
echo. >> "%OUT%"

:: VS Code User Settings File
echo ================ VS Code settings.json (if exists) ============== >> "%OUT%"
set "VSCODE_SETTINGS=%APPDATA%\Code\User\settings.json"
if exist "!VSCODE_SETTINGS!" (
  type "!VSCODE_SETTINGS!" >> "%OUT%"
) else (
  echo No settings.json file found. >> "%OUT%"
)
echo. >> "%OUT%"

echo ✅ Done. Output saved to %OUT%
pause
