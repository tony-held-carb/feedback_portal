@echo off
REM time_wrapper.bat - Accurate wall-clock timing wrapper for Python script

echo ----------------------------------------
echo [INFO] Starting outer timer...

REM Capture start time in float seconds using PowerShell
for /f %%i in ('powershell -NoProfile -Command "[decimal](Get-Date).ToUniversalTime().Subtract([datetime]::UnixEpoch).TotalSeconds"') do set "START_TS=%%i"

echo [INFO] System start time: %TIME%

REM Run the Python script
python time_launch.py

REM Capture end time in float seconds
for /f %%i in ('powershell -NoProfile -Command "[decimal](Get-Date).ToUniversalTime().Subtract([datetime]::UnixEpoch).TotalSeconds"') do set "END_TS=%%i"

echo [INFO] System end time: %TIME%

REM Compute and round duration using PowerShell (FULLY quoted to avoid + bug)
for /f %%i in ('powershell -NoProfile -Command "[math]::Round([decimal](%END_TS%) - [decimal](%START_TS%), 3)"') do set "ELAPSED=%%i"

echo [RESULT] Wall time from OS (Python + launch overhead): %ELAPSED% seconds
echo ----------------------------------------
