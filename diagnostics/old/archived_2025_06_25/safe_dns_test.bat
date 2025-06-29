@echo off
REM ========================================
REM Safe DNS Testing Script
REM ========================================
REM
REM This script safely tests DNS changes with
REM easy undo options and safety checks.
REM
REM ========================================

echo ========================================
echo Safe DNS Testing Script
echo ========================================
echo.
echo This script will safely test DNS changes.
echo.
echo SAFETY FEATURES:
echo - Only ADDS DNS servers (doesn't replace)
echo - Easy undo options
echo - Backup of current settings
echo - Non-destructive testing
echo.

set BACKUP_FILE=diagnostics\dns_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt
set BACKUP_FILE=%BACKUP_FILE: =0%

echo [1/5] Creating backup of current DNS settings...
echo Current DNS Settings Backup > "%BACKUP_FILE%"
echo Generated: %date% %time% >> "%BACKUP_FILE%"
echo ======================================== >> "%BACKUP_FILE%"
echo. >> "%BACKUP_FILE%"

echo Current DNS configuration: >> "%BACKUP_FILE%"
ipconfig /all | findstr "DNS Servers" >> "%BACKUP_FILE%"
echo. >> "%BACKUP_FILE%"

echo [2/5] Testing current Cursor domain access...
echo Testing cursor.sh with current DNS:
nslookup cursor.sh
echo.

echo [3/5] Attempting to add Google DNS as tertiary...
echo Attempting: netsh interface ip add dns "Wi-Fi" 8.8.8.8 index=3
netsh interface ip add dns "Wi-Fi" 8.8.8.8 index=3
if %errorlevel% equ 0 (
    echo ✅ SUCCESS: Google DNS added as tertiary (index=3)
    echo ✅ SUCCESS: Google DNS added as tertiary (index=3) >> "%BACKUP_FILE%"
) else (
    echo ❌ FAILED: Could not add DNS server
    echo ❌ FAILED: Could not add DNS server >> "%BACKUP_FILE%"
    echo Possible reasons:
    echo - Admin rights required
    echo - Wrong adapter name
    echo - Network policy restrictions
    echo.
    goto :undo_options
)

echo [4/5] Verifying new DNS configuration...
echo New DNS configuration:
ipconfig /all | findstr "DNS Servers"
echo.

echo New DNS configuration: >> "%BACKUP_FILE%"
ipconfig /all | findstr "DNS Servers" >> "%BACKUP_FILE%"
echo. >> "%BACKUP_FILE%"

echo [5/5] Testing Cursor domains with new configuration...
echo Testing cursor.sh with new DNS configuration:
nslookup cursor.sh
echo.

echo Testing api.github.com with new DNS configuration:
nslookup api.github.com
echo.

echo ========================================
echo DNS CHANGE COMPLETE
echo ========================================
echo.
echo ✅ Google DNS (8.8.8.8) added as tertiary DNS
echo ✅ Your original DNS servers remain as primary/secondary
echo ✅ Cursor domains should now be accessible
echo.
echo [NEXT STEP] Try Cursor authentication now!
echo.

:undo_options

echo ========================================
echo UNDO OPTIONS (if needed)
echo ========================================
echo.
echo If you need to undo the DNS changes:
echo.
echo [OPTION 1] Remove specific DNS server:
echo netsh interface ip delete dns "Wi-Fi" 8.8.8.8
echo.
echo [OPTION 2] Reset to DHCP (recommended):
echo netsh interface ip set dns "Wi-Fi" dhcp
echo.
echo [OPTION 3] Remove all custom DNS:
echo netsh interface ip delete dns "Wi-Fi" all
echo netsh interface ip set dns "Wi-Fi" dhcp
echo.
echo [OPTION 4] Manual reset:
echo - Network Settings → Wi-Fi → Properties → IPv4 → Properties
echo - Set to "Obtain DNS server address automatically"
echo.
echo Backup saved to: %BACKUP_FILE%
echo.

pause 