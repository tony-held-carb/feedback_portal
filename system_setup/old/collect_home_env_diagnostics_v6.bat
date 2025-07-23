@echo off
setlocal enabledelayedexpansion

rem === DEFINE IDE FALLBACK PATHS ===
set "home_pycharm_path=C:\tony_apps\PyCharm_2025\bin\pycharm64.exe"
set "home_cursor_path=C:\Users\tonyh\AppData\Local\Programs\cursor\Cursor.exe"
set "home_code_path=C:\Users\tonyh\AppData\Local\Programs\Microsoft VS Code\Code.exe"

set "work_pycharm_path=C:\Users\theld\AppData\Local\JetBrains\PyCharm2025.1\bin\pycharm64.exe"
set "work_cursor_path=C:\Users\theld\AppData\Local\Programs\cursor\Cursor.exe"
set "work_code_path=C:\Users\theld\AppData\Local\Programs\Microsoft VS Code\Code.exe"

set "OUTPUT=home_env_diagnostics_v6.txt"
set "TMP_DIR=%TEMP%\env_diag_parts"
if exist "%TMP_DIR%" rd /s /q "%TMP_DIR%"
mkdir "%TMP_DIR%"

set COUNT=0

rem === HELPER FUNCTION ===
:write_section
set /a COUNT+=1
set "TMP_FILE=%TMP_DIR%\%COUNT%_%~1.txt"
echo ==== %~1 ==== > "%TMP_FILE%"
echo Running: %~1
cmd /c %~2 >> "%TMP_FILE%" 2>&1
goto :eof

rem === RUN DIAGNOSTIC SECTIONS ===
call :write_section "SYSTEM INFO" "systeminfo"
call :write_section "SET ENVIRONMENT VARIABLES" "set"
call :write_section "CONDA INFO" "conda info"
call :write_section "CONDA LIST" "conda list"
call :write_section "CONDA ENV LIST" "conda env list"
call :write_section "PYTHON INFO" "where python && python --version"
call :write_section "GIT INFO" "where git && git --version && git config --list"
call :write_section "CONDARC" "if exist %USERPROFILE%\.condarc (type %USERPROFILE%\.condarc) else (echo (no .condarc found))"
call :write_section "PYCHARM PATH" "where pycharm || (echo Using fallback: %home_pycharm_path% & if exist \"%home_pycharm_path%\" echo (exists) & if not exist \"%home_pycharm_path%\" echo (missing))"
call :write_section "CURSOR PATH" "where cursor || (echo Using fallback: %home_cursor_path% & if exist \"%home_cursor_path%\" echo (exists) & if not exist \"%home_cursor_path%\" echo (missing))"
call :write_section "VSCODE PATH" "where code || (echo Using fallback: %home_code_path% & if exist \"%home_code_path%\" echo (exists) & if not exist \"%home_code_path%\" echo (missing))"
call :write_section "USERPROFILE DIRECTORY" "dir /a %USERPROFILE%"
call :write_section "APPDATA DIRECTORY" "dir /a %APPDATA%"
call :write_section "JETBRAINS DIR" "dir /a \"%APPDATA%\JetBrains\" && dir /a \"%APPDATA%\JetBrains\PyCharm2025.1\""
call :write_section "CURSOR CONFIG" "dir /a \"%APPDATA%\Cursor\" && dir /a \"%APPDATA%\Code\User\" && dir /a \"%APPDATA%\Code\User\snippets\" && type \"%APPDATA%\Code\User\settings.json\""
call :write_section "VSCODE CONFIG" "dir /a \"%APPDATA%\Code - Insiders\User\" && dir /a \"%APPDATA%\Code\User\" && dir /a \"%APPDATA%\Code\User\snippets\" && type \"%APPDATA%\Code\User\settings.json\""

rem === MERGE ALL OUTPUT ===
del "%OUTPUT%" >nul 2>&1
for %%F in ("%TMP_DIR%\*.txt") do (
  type "%%~F" >> "%OUTPUT%"
  echo. >> "%OUTPUT%"
  echo ----------------------------- >> "%OUTPUT%"
  echo. >> "%OUTPUT%"
)

echo ✅ Diagnostics written to: %OUTPUT%
pause
