@echo off
setlocal enabledelayedexpansion

:: ========================
:: Set fallback IDE paths
:: ========================
set "home_pycharm_path=C:\tony_apps\PyCharm_2025\bin\pycharm64.exe"
set "home_cursor_path=C:\Users\tonyh\AppData\Local\Programs\cursor\Cursor.exe"
set "home_code_path=C:\Users\tonyh\AppData\Local\Programs\Microsoft VS Code\Code.exe"

set "work_pycharm_path=C:\Program Files\JetBrains\PyCharm 2025.1\bin\pycharm64.exe"
set "work_cursor_path=C:\Users\theld\AppData\Local\Programs\cursor\Cursor.exe"
set "work_code_path=C:\Users\theld\AppData\Local\Programs\Microsoft VS Code\Code.exe"

:: ========================
:: Set output file
:: ========================
set "OUTPUT=collect_env_diagnostics_v5_work.txt"
echo Collecting home environment diagnostics... > %OUTPUT%
echo ------------------------------------------- >> %OUTPUT%

:: ========================
:: Helper: run + flush
:: ========================
set "TMP=temp_diag.txt"
del "%TMP%" >nul 2>&1

call :run_and_log "set"
call :run_and_log "systeminfo"

:: ========================
:: Conda diagnostics
:: ========================
call :run_and_log "conda info"
call :run_and_log "conda list"
call :run_and_log "conda env list"

:: ========================
:: Python diagnostics
:: ========================
call :run_and_log "where python"
call :run_and_log "python --version"

:: ========================
:: Git diagnostics
:: ========================
call :run_and_log "where git"
call :run_and_log "git --version"
call :run_and_log "git config --list"

:: ========================
:: .condarc
:: ========================
echo ==== .condarc ==== >> %OUTPUT%
if exist "%USERPROFILE%\.condarc" (
  type "%USERPROFILE%\.condarc" >> %OUTPUT%
) else (
  echo (no .condarc file found) >> %OUTPUT%
)

:: ========================
:: PyCharm diagnostics
:: ========================
call :run_and_log "where pycharm"
if errorlevel 1 (
  echo Fallback used: home_pycharm_path = %home_pycharm_path% >> %OUTPUT%
  if exist "%home_pycharm_path%" type "%home_pycharm_path%" >> %OUTPUT%
)

call :run_and_log "dir ""%APPDATA%\JetBrains"""
call :run_and_log "dir ""%APPDATA%\JetBrains\PyCharm2025.1"""

:: ========================
:: Cursor diagnostics
:: ========================
call :run_and_log "where cursor"
if errorlevel 1 (
  echo Fallback used: home_cursor_path = %home_cursor_path% >> %OUTPUT%
  if exist "%home_cursor_path%" type "%home_cursor_path%" >> %OUTPUT%
)

call :run_and_log "dir ""%APPDATA%\Cursor"""
call :run_and_log "dir ""%APPDATA%\Code\User"""
call :run_and_log "dir ""%APPDATA%\Code\User\snippets"""
call :run_and_log "type ""%APPDATA%\Code\User\settings.json"""

:: ========================
:: VS Code diagnostics
:: ========================
call :run_and_log "dir ""%APPDATA%\Code - Insiders\User"""
call :run_and_log "dir ""%APPDATA%\Code\User"""
call :run_and_log "dir ""%APPDATA%\Code\User\snippets"""
call :run_and_log "type ""%APPDATA%\Code\User\settings.json"""

echo ------------------------------------------- >> %OUTPUT%
echo Diagnostics complete. Output written to: %OUTPUT%
pause
exit /b

:: ========================
:: Function to run and flush each section
:: ========================
:run_and_log
echo ==== %~1 ==== >> %OUTPUT%
cmd /c %~1 > "%TMP%" 2>&1
type "%TMP%" >> %OUTPUT%
echo. >> %OUTPUT%
exit /b
