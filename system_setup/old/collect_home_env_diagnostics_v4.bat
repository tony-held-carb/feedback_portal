@echo off
setlocal EnableDelayedExpansion

rem === DEFINE FALLBACK IDE PATHS ===
set "home_pycharm_path=C:\tony_apps\PyCharm_2025\bin\pycharm64.exe"
set "home_cursor_path=C:\Users\tonyh\AppData\Local\Programs\cursor\Cursor.exe"
set "home_code_path=C:\Users\tonyh\AppData\Local\Programs\Microsoft VS Code\Code.exe"

set "work_pycharm_path=C:\Program Files\JetBrains\PyCharm 2025.1\bin\pycharm64.exe"
set "work_cursor_path=C:\Users\theld\AppData\Local\Programs\cursor\Cursor.exe"
set "work_code_path=C:\Users\theld\AppData\Local\Programs\Microsoft VS Code\Code.exe"

set "OUTPUT=home_env_diagnostics_v4.txt"
echo ==== Environment Diagnostics: %DATE% %TIME% ==== > %OUTPUT%
echo --------------------------------------------- >> %OUTPUT%
echo. >> %OUTPUT%

rem === ENVIRONMENT VARIABLES ===
echo ==== ENVIRONMENT VARIABLES (set) ==== >> %OUTPUT%
set >> %OUTPUT%
echo. >> %OUTPUT%

rem === SYSTEMINFO ===
echo ==== SYSTEMINFO ==== >> %OUTPUT%
systeminfo >> %OUTPUT% 2>&1
echo. >> %OUTPUT%

rem === CONDA ===
echo ==== CONDA INFO ==== >> %OUTPUT%
conda info >> %OUTPUT% 2>&1
echo. >> %OUTPUT%

rem Ensure CONDA does not hang future sections
ping -n 2 127.0.0.1 > nul

rem === CONDA LIST ===
echo ==== CONDA LIST ==== >> %OUTPUT%
conda list >> %OUTPUT% 2>&1
echo. >> %OUTPUT%

rem === CONDA ENV LIST ===
echo ==== CONDA ENV LIST ==== >> %OUTPUT%
conda env list >> %OUTPUT% 2>&1
echo. >> %OUTPUT%

rem === PYTHON ===
echo ==== PYTHON INFO ==== >> %OUTPUT%
where python >> %OUTPUT% 2>&1
python --version >> %OUTPUT% 2>&1
echo. >> %OUTPUT%

rem === GIT ===
echo ==== GIT INFO ==== >> %OUTPUT%
where git >> %OUTPUT% 2>&1
git --version >> %OUTPUT% 2>&1
git config --list >> %OUTPUT% 2>&1
echo. >> %OUTPUT%

rem === .condarc ===
echo ==== .condarc ==== >> %OUTPUT%
if exist "%USERPROFILE%\.condarc" (
  type "%USERPROFILE%\.condarc" >> %OUTPUT%
) else (
  echo (no .condarc file found) >> %OUTPUT%
)
echo. >> %OUTPUT%

rem === PYCHARM ===
echo ==== PYCHARM ==== >> %OUTPUT%
where pycharm >> %OUTPUT% 2>&1
if not errorlevel 1 (
  for /f "delims=" %%f in ('where pycharm 2^>nul') do (
    echo ---- Found: %%f ---- >> %OUTPUT%
    type "%%f" >> %OUTPUT% 2>&1
  )
) else if exist "%home_pycharm_path%" (
  echo ---- Using fallback: %home_pycharm_path% ---- >> %OUTPUT%
  type "%home_pycharm_path%" >> %OUTPUT% 2>&1
) else if exist "%work_pycharm_path%" (
  echo ---- Using fallback: %work_pycharm_path% ---- >> %OUTPUT%
  type "%work_pycharm_path%" >> %OUTPUT% 2>&1
) else (
  echo (PyCharm not found) >> %OUTPUT%
)
echo. >> %OUTPUT%

rem JetBrains Directory
if exist "%APPDATA%\JetBrains" (
  echo ---- JetBrains ---- >> %OUTPUT%
  dir "%APPDATA%\JetBrains" >> %OUTPUT% 2>&1
)
if exist "%APPDATA%\JetBrains\PyCharm2025.1" (
  echo ---- PyCharm2025.1 ---- >> %OUTPUT%
  dir "%APPDATA%\JetBrains\PyCharm2025.1" >> %OUTPUT% 2>&1
)
echo. >> %OUTPUT%

rem === CURSOR ===
echo ==== CURSOR ==== >> %OUTPUT%
where cursor >> %OUTPUT% 2>&1
if exist "%home_cursor_path%" (
  echo ---- Using fallback: %home_cursor_path% ---- >> %OUTPUT%
) else if exist "%work_cursor_path%" (
  echo ---- Using fallback: %work_cursor_path% ---- >> %OUTPUT%
) else (
  echo (Cursor not found) >> %OUTPUT%
)
echo. >> %OUTPUT%

if exist "%APPDATA%\Cursor" (
  echo ---- Cursor Directory ---- >> %OUTPUT%
  dir "%APPDATA%\Cursor" >> %OUTPUT% 2>&1
)
if exist "%APPDATA%\Code\User" (
  echo ---- Code\User ---- >> %OUTPUT%
  dir "%APPDATA%\Code\User" >> %OUTPUT% 2>&1
  if exist "%APPDATA%\Code\User\snippets" (
    dir "%APPDATA%\Code\User\snippets" >> %OUTPUT% 2>&1
  )
  if exist "%APPDATA%\Code\User\settings.json" (
    type "%APPDATA%\Code\User\settings.json" >> %OUTPUT% 2>&1
  )
)
echo. >> %OUTPUT%

rem === VS CODE ===
echo ==== VS CODE ==== >> %OUTPUT%
if exist "%home_code_path%" (
  echo ---- Using fallback: %home_code_path% ---- >> %OUTPUT%
) else if exist "%work_code_path%" (
  echo ---- Using fallback: %work_code_path% ---- >> %OUTPUT%
) else (
  echo (VS Code not found) >> %OUTPUT%
)
if exist "%APPDATA%\Code - Insiders\User" (
  echo ---- VS Code Insiders ---- >> %OUTPUT%
  dir "%APPDATA%\Code - Insiders\User" >> %OUTPUT% 2>&1
)
if exist "%APPDATA%\Code\User" (
  echo ---- VS Code User Settings ---- >> %OUTPUT%
  dir "%APPDATA%\Code\User" >> %OUTPUT% 2>&1
  dir "%APPDATA%\Code\User\snippets" >> %OUTPUT% 2>&1
  type "%APPDATA%\Code\User\settings.json" >> %OUTPUT% 2>&1
)
echo. >> %OUTPUT%
echo Diagnostics written to: %OUTPUT%
pause
