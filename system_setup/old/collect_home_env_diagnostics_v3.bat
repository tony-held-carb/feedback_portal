@echo off
setlocal enabledelayedexpansion

set OUTPUT=home_env_diagnostics_v3.txt
echo === Environment Diagnostics (%DATE% %TIME%) === > %OUTPUT%
echo Working Directory: %CD% >> %OUTPUT%
echo --------------------------------------------- >> %OUTPUT%

rem ==== ENVIRONMENT VARIABLES ====
echo ==== ENVIRONMENT VARIABLES (set) ==== >> %OUTPUT%
set >> %OUTPUT% 2>&1

rem ==== SYSTEM INFO ====
echo ==== SYSTEMINFO ==== >> %OUTPUT%
systeminfo >> %OUTPUT% 2>&1

rem ==== CONDA INFO ====
echo ==== CONDA INFO ==== >> %OUTPUT%
conda info >> %OUTPUT% 2>&1

echo ==== CONDA LIST ==== >> %OUTPUT%
conda list >> %OUTPUT% 2>&1

echo ==== CONDA ENV LIST ==== >> %OUTPUT%
conda env list >> %OUTPUT% 2>&1

rem ==== PYTHON ====
echo ==== PYTHON INFO ==== >> %OUTPUT%
where python >> %OUTPUT% 2>&1
python --version >> %OUTPUT% 2>&1

rem ==== GIT ====
echo ==== GIT INFO ==== >> %OUTPUT%
where git >> %OUTPUT% 2>&1
git --version >> %OUTPUT% 2>&1
git config --list >> %OUTPUT% 2>&1

rem ==== .condarc ====
echo ==== .condarc ==== >> %OUTPUT%
if exist "%USERPROFILE%\.condarc" (
  type "%USERPROFILE%\.condarc" >> %OUTPUT%
) else (
  echo (no .condarc file found) >> %OUTPUT%
)

rem ==== PYCHARM ====
echo ==== PYCHARM DETECTION ==== >> %OUTPUT%
where pycharm >> %OUTPUT% 2>&1
if exist "C:\tony_apps\PyCharm_2025\bin\pycharm64.exe" (
  echo Found PyCharm manually at C:\tony_apps\PyCharm_2025\bin\pycharm64.exe >> %OUTPUT%
  echo Version info: >> %OUTPUT%
  "C:\tony_apps\PyCharm_2025\bin\pycharm64.exe" --version >> %OUTPUT% 2>&1
)

echo ---- JetBrains directory ---- >> %OUTPUT%
dir "%APPDATA%\JetBrains" >> %OUTPUT% 2>&1

if exist "%APPDATA%\JetBrains\PyCharm2025.1" (
  echo ---- PyCharm2025.1 ---- >> %OUTPUT%
  dir "%APPDATA%\JetBrains\PyCharm2025.1" >> %OUTPUT% 2>&1
)

rem ==== CURSOR ====
echo ==== CURSOR DETECTION ==== >> %OUTPUT%
where cursor >> %OUTPUT% 2>&1
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\cursor\Cursor.exe" (
  echo Found Cursor at C:\Users\%USERNAME%\AppData\Local\Programs\cursor\Cursor.exe >> %OUTPUT%
)

if exist "%APPDATA%\Cursor" (
  echo ---- Cursor Data ---- >> %OUTPUT%
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

rem ==== VSCODE ====
echo ==== VS CODE DETECTION ==== >> %OUTPUT%
where code >> %OUTPUT% 2>&1
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe" (
  echo Found VS Code at C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe >> %OUTPUT%
)

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

echo === End of Diagnostics (%DATE% %TIME%) === >> %OUTPUT%
echo.
echo ✅ Diagnostics written to: %OUTPUT%
pause
