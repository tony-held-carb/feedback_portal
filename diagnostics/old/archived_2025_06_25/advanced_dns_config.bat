@echo off
REM ========================================
REM Advanced DNS Configuration Script
REM ========================================
REM
REM This script demonstrates multiple DNS server configurations
REM with different index values for maximum reliability.
REM
REM ========================================

echo ========================================
echo Advanced DNS Configuration Script
echo ========================================
echo.
echo This script will configure multiple DNS servers for:
echo - Maximum reliability
echo - Bypass corporate DNS blocking
echo - Fallback options
echo.

set OUTPUT_FILE=diagnostics\advanced_dns_test_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt
set OUTPUT_FILE=%OUTPUT_FILE: =0%

echo Advanced DNS Configuration Test > "%OUTPUT_FILE%"
echo Started: %date% %time% >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo [1/6] Checking current DNS configuration...
echo [1/6] Checking current DNS configuration... >> "%OUTPUT_FILE%"
echo Current DNS settings: >> "%OUTPUT_FILE%"
ipconfig /all | findstr "DNS Servers" >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo [2/6] Testing current Cursor domain access...
echo [2/6] Testing current Cursor domain access... >> "%OUTPUT_FILE%"
echo Testing cursor.sh with current DNS: >> "%OUTPUT_FILE%"
nslookup cursor.sh >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo [3/6] Testing individual DNS servers...
echo [3/6] Testing individual DNS servers... >> "%OUTPUT_FILE%"

echo Testing Google DNS (8.8.8.8): >> "%OUTPUT_FILE%"
nslookup cursor.sh 8.8.8.8 >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo Testing Google DNS Secondary (8.8.4.4): >> "%OUTPUT_FILE%"
nslookup cursor.sh 8.8.4.4 >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo Testing Cloudflare DNS (1.1.1.1): >> "%OUTPUT_FILE%"
nslookup cursor.sh 1.1.1.1 >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo Testing Cloudflare DNS Secondary (1.0.0.1): >> "%OUTPUT_FILE%"
nslookup cursor.sh 1.0.0.1 >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo Testing OpenDNS (208.67.222.222): >> "%OUTPUT_FILE%"
nslookup cursor.sh 208.67.222.222 >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo [4/6] Attempting advanced DNS configuration...
echo [4/6] Attempting advanced DNS configuration... >> "%OUTPUT_FILE%"

echo Setting up 5 DNS servers for maximum reliability: >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo Step 1: Setting primary DNS (Google)...
echo Step 1: Setting primary DNS (Google)... >> "%OUTPUT_FILE%"
netsh interface ip set dns "Wi-Fi" static 8.8.8.8 >> "%OUTPUT_FILE%" 2>&1
if %errorlevel% equ 0 (
    echo ✅ Primary DNS set to 8.8.8.8
    echo ✅ Primary DNS set to 8.8.8.8 >> "%OUTPUT_FILE%"
) else (
    echo ❌ Failed to set primary DNS - admin rights required
    echo ❌ Failed to set primary DNS - admin rights required >> "%OUTPUT_FILE%"
    goto :end
)

echo Step 2: Adding secondary DNS (Google backup)...
echo Step 2: Adding secondary DNS (Google backup)... >> "%OUTPUT_FILE%"
netsh interface ip add dns "Wi-Fi" 8.8.4.4 index=2 >> "%OUTPUT_FILE%" 2>&1
if %errorlevel% equ 0 (
    echo ✅ Secondary DNS added: 8.8.4.4 (index=2)
    echo ✅ Secondary DNS added: 8.8.4.4 (index=2) >> "%OUTPUT_FILE%"
) else (
    echo ⚠️ Secondary DNS failed, continuing with primary only
    echo ⚠️ Secondary DNS failed, continuing with primary only >> "%OUTPUT_FILE%"
)

echo Step 3: Adding tertiary DNS (Cloudflare)...
echo Step 3: Adding tertiary DNS (Cloudflare)... >> "%OUTPUT_FILE%"
netsh interface ip add dns "Wi-Fi" 1.1.1.1 index=3 >> "%OUTPUT_FILE%" 2>&1
if %errorlevel% equ 0 (
    echo ✅ Tertiary DNS added: 1.1.1.1 (index=3)
    echo ✅ Tertiary DNS added: 1.1.1.1 (index=3) >> "%OUTPUT_FILE%"
) else (
    echo ⚠️ Tertiary DNS failed
    echo ⚠️ Tertiary DNS failed >> "%OUTPUT_FILE%"
)

echo Step 4: Adding quaternary DNS (Cloudflare backup)...
echo Step 4: Adding quaternary DNS (Cloudflare backup)... >> "%OUTPUT_FILE%"
netsh interface ip add dns "Wi-Fi" 1.0.0.1 index=4 >> "%OUTPUT_FILE%" 2>&1
if %errorlevel% equ 0 (
    echo ✅ Quaternary DNS added: 1.0.0.1 (index=4)
    echo ✅ Quaternary DNS added: 1.0.0.1 (index=4) >> "%OUTPUT_FILE%"
) else (
    echo ⚠️ Quaternary DNS failed
    echo ⚠️ Quaternary DNS failed >> "%OUTPUT_FILE%"
)

echo Step 5: Adding quinary DNS (OpenDNS)...
echo Step 5: Adding quinary DNS (OpenDNS)... >> "%OUTPUT_FILE%"
netsh interface ip add dns "Wi-Fi" 208.67.222.222 index=5 >> "%OUTPUT_FILE%" 2>&1
if %errorlevel% equ 0 (
    echo ✅ Quinary DNS added: 208.67.222.222 (index=5)
    echo ✅ Quinary DNS added: 208.67.222.222 (index=5) >> "%OUTPUT_FILE%"
) else (
    echo ⚠️ Quinary DNS failed
    echo ⚠️ Quinary DNS failed >> "%OUTPUT_FILE%"
)

echo [5/6] Verifying new DNS configuration...
echo [5/6] Verifying new DNS configuration... >> "%OUTPUT_FILE%"
echo New DNS configuration: >> "%OUTPUT_FILE%"
ipconfig /all | findstr "DNS Servers" >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo [6/6] Testing Cursor domains with new configuration...
echo [6/6] Testing Cursor domains with new configuration... >> "%OUTPUT_FILE%"

echo Testing cursor.sh with new DNS configuration: >> "%OUTPUT_FILE%"
nslookup cursor.sh >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo Testing api.github.com with new DNS configuration: >> "%OUTPUT_FILE%"
nslookup api.github.com >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo Testing github.com with new DNS configuration: >> "%OUTPUT_FILE%"
nslookup github.com >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

:end

echo ======================================== >> "%OUTPUT_FILE%"
echo DNS INDEX EXPLANATION >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"
echo DNS Index Priority Order: >> "%OUTPUT_FILE%"
echo Index 1 (Primary): 8.8.8.8 - Google DNS >> "%OUTPUT_FILE%"
echo Index 2 (Secondary): 8.8.4.4 - Google DNS Backup >> "%OUTPUT_FILE%"
echo Index 3 (Tertiary): 1.1.1.1 - Cloudflare DNS >> "%OUTPUT_FILE%"
echo Index 4 (Quaternary): 1.0.0.1 - Cloudflare Backup >> "%OUTPUT_FILE%"
echo Index 5 (Quinary): 208.67.222.222 - OpenDNS >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"
echo Resolution Process: >> "%OUTPUT_FILE%"
echo 1. Try Index 1 (8.8.8.8) >> "%OUTPUT_FILE%"
echo 2. If Index 1 fails, try Index 2 (8.8.4.4) >> "%OUTPUT_FILE%"
echo 3. If Index 2 fails, try Index 3 (1.1.1.1) >> "%OUTPUT_FILE%"
echo 4. If Index 3 fails, try Index 4 (1.0.0.1) >> "%OUTPUT_FILE%"
echo 5. If Index 4 fails, try Index 5 (208.67.222.222) >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo ========================================
echo DNS CONFIGURATION COMPLETE
echo ========================================
echo.
echo DNS servers configured in priority order:
echo.
echo Index 1 (Primary):    8.8.8.8     - Google DNS
echo Index 2 (Secondary):  8.8.4.4     - Google DNS Backup
echo Index 3 (Tertiary):   1.1.1.1     - Cloudflare DNS
echo Index 4 (Quaternary): 1.0.0.1     - Cloudflare Backup
echo Index 5 (Quinary):    208.67.222.222 - OpenDNS
echo.
echo Resolution Process:
echo 1. Try primary DNS first
echo 2. If primary fails, try secondary
echo 3. Continue through all DNS servers until one works
echo.
echo [IMPORTANT] To revert to original DNS:
echo netsh interface ip set dns "Wi-Fi" dhcp
echo.
echo [NEXT STEP] Try Cursor authentication now!
echo.

pause 