@echo off
setlocal enabledelayedexpansion

set OUTPUT=home_env_diagnostics_full_v2.txt
set TMPDIR=%TEMP%\env_diag_temp
mkdir "%TMPDIR%" >nul 2>&1

echo Collecting environment diagnostics...
echo ------------------------------------- > %OUTPUT%

:: Function to run a command and log to subfile
set INDEX=0
for %%L in (
  "==== SYSTEMINFO ====" "systeminfo"
  "==== CONDA INFO ====" "conda info"
  "==== CONDA LIST ====" "conda list"
  "==== CONDA ENV LIST ====" "conda env list"
  "==== PYTHON INFO ====" "where python && python --version"
  "==== GIT INFO ====" "where git && git --version && git config --list"
  "==== .condarc ====" "if exist \"%USERPROFILE%\.condarc\" (type \"%USERPROFILE%\.condarc\") else (echo (no .condarc file found))"
  "==== PYCHARM ====" "where pycharm"
  "==== CURSOR ====" "where cursor"
  "==== APPDATA LISTING ====" "dir \"%APPDATA%\""
) do (
  set /a INDEX+=1
  set HEADER=%%~L
  set CMD=%%~L
  if "!INDEX!"=="2" (
    echo !HEADER! >> %OUTPUT%
    call cmd /c !CMD! > "%TMPDIR%\out!INDEX!.txt" 2>&1
    type "%TMPDIR%\out!INDEX!.txt" >> %OUTPUT%
    echo. >> %OUTPUT%
  )
)

:: Manual sections not suited for loop
echo ==== PYCHARM FILES ==== >> %OUTPUT%
for /f "delims=" %%f in ('where pycharm 2^>nul') do (
  echo ---- Contents of: %%f ---- >> %OUTPUT%
  type "%%f" >> %OUTPUT% 2>&1
)

echo ---- JetBrains directory ---- >> %OUTPUT%
dir "%APPDATA%\JetBrains" >> %OUTPUT% 2>&1

if exist "%APPDATA%\JetBrains\PyCharm2025.1" (
  echo ---- PyCharm2025.1 ---- >> %OUTPUT%
  dir "%APPDATA%\JetBrains\PyCharm2025.1" >> %OUTPUT% 2>&1
)

echo ==== CURSOR DIRS ==== >> %OUTPUT%
if exist "%APPDATA%\Cursor" (
  echo ---- Cursor Directory ---- >> %OUTPUT%
  dir "%APPDATA%\Cursor" >> %OUTPUT% 2>&1
)

if exist "%APPDATA%\Code\User" (
  echo ---- Cursor Code\User ---- >> %OUTPUT%
  dir "%APPDATA%\Code\User" >> %OUTPUT% 2>&1

  echo ---- Cursor Code\User\snippets ---- >> %OUTPUT%
  dir "%APPDATA%\Code\User\snippets" >> %OUTPUT% 2>&1

  echo ---- Cursor settings.json ---- >> %OUTPUT%
  type "%APPDATA%\Code\User\settings.json" >> %OUTPUT% 2>&1
)

echo ==== VS CODE ==== >> %OUTPUT%
if exist "%APPDATA%\Code - Insiders\User" (
  echo ---- VS Code Insiders ---- >> %OUTPUT%
  dir "%APPDATA%\Code - Insiders\User" >> %OUTPUT% 2>&1
)

if exist "%APPDATA%\Code\User" (
  echo ---- VS Code ---- >> %OUTPUT%
  dir "%APPDATA%\Code\User" >> %OUTPUT% 2>&1

  echo ---- VS Code snippets ---- >> %OUTPUT%
  dir "%APPDATA%\Code\User\snippets" >> %OUTPUT% 2>&1

  echo ---- VS Code settings ---- >> %OUTPUT%
  type "%APPDATA%\Code\User\settings.json" >> %OUTPUT% 2>&1
)

echo Cleanup...
rd /s /q "%TMPDIR%" >nul 2>&1

echo Diagnostics written to: %OUTPUT%
pause
