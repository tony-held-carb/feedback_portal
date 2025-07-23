@echo off
setlocal enabledelayedexpansion

:: Output file
set "OUT=conda_work_config_dump.txt"
echo Collecting Conda/Miniconda diagnostics... > "%OUT%"
echo. >> "%OUT%"

:: Conda Info
echo ===================== conda info ===================== >> "%OUT%"
conda info >> "%OUT%" 2>&1
echo. >> "%OUT%"

:: Conda Config
echo ================ conda config --show ================ >> "%OUT%"
conda config --show >> "%OUT%" 2>&1
echo. >> "%OUT%"

:: Conda List (Explicit)
echo ============== conda list --explicit ================ >> "%OUT%"
conda list --explicit >> "%OUT%" 2>&1
echo. >> "%OUT%"

:: Conda Environments
echo ================== conda env list =================== >> "%OUT%"
conda env list >> "%OUT%" 2>&1
echo. >> "%OUT%"

:: .condarc (User config file)
echo ===================== .condarc ======================= >> "%OUT%"
if exist "%USERPROFILE%\.condarc" (
  type "%USERPROFILE%\.condarc" >> "%OUT%"
) else (
  echo (no .condarc file found) >> "%OUT%"
)
echo. >> "%OUT%"

echo ✅ Done. Output saved to %OUT%
pause
