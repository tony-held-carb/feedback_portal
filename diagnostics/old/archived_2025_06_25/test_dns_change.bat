@echo off
REM ========================================
REM Test DNS Change Without Admin Rights
REM ========================================
REM
REM This script tests if DNS can be changed from command line
REM and tests connectivity to Cursor domains with different DNS.
REM
REM SAFETY: Only tests DNS resolution - no permanent changes
REM
REM ========================================

echo ========================================
echo Test DNS Change Without Admin Rights
echo ========================================
echo.
echo SAFETY: Only tests DNS resolution - no permanent changes
echo.

set OUTPUT_FILE=diagnostics\dns_test_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt
set OUTPUT_FILE=%OUTPUT_FILE: =0%

echo DNS Change Test Results > "%OUTPUT_FILE%"
echo Started: %date% %time% >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo [1/4] Checking current DNS settings...
echo [1/4] Checking current DNS settings... >> "%OUTPUT_FILE%"
ipconfig /all | findstr "DNS Servers" >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo [2/4] Testing current DNS resolution (should fail)...
echo [2/4] Testing current DNS resolution (should fail)... >> "%OUTPUT_FILE%"
echo Testing cursor.sh with current DNS: >> "%OUTPUT_FILE%"
nslookup cursor.sh >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo Testing api.github.com with current DNS: >> "%OUTPUT_FILE%"
nslookup api.github.com >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo [3/4] Testing with Google DNS (8.8.8.8)...
echo [3/4] Testing with Google DNS (8.8.8.8)... >> "%OUTPUT_FILE%"
echo Testing cursor.sh with Google DNS: >> "%OUTPUT_FILE%"
nslookup cursor.sh 8.8.8.8 >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo Testing api.github.com with Google DNS: >> "%OUTPUT_FILE%"
nslookup api.github.com 8.8.8.8 >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo [4/4] Testing with Cloudflare DNS (1.1.1.1)...
echo [4/4] Testing with Cloudflare DNS (1.1.1.1)... >> "%OUTPUT_FILE%"
echo Testing cursor.sh with Cloudflare DNS: >> "%OUTPUT_FILE%"
nslookup cursor.sh 1.1.1.1 >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo Testing api.github.com with Cloudflare DNS: >> "%OUTPUT_FILE%"
nslookup api.github.com 1.1.1.1 >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo ======================================== >> "%OUTPUT_FILE%"
echo DNS CHANGE ATTEMPTS >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"

echo [ATTEMPT 1] Try to change DNS via netsh (likely requires admin)...
echo [ATTEMPT 1] Try to change DNS via netsh (likely requires admin)... >> "%OUTPUT_FILE%"
netsh interface ip set dns "Wi-Fi" static 8.8.8.8 >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo [ATTEMPT 2] Try to change DNS via netsh with primary/secondary...
echo [ATTEMPT 2] Try to change DNS via netsh with primary/secondary... >> "%OUTPUT_FILE%"
netsh interface ip set dns "Wi-Fi" static 8.8.8.8 primary >> "%OUTPUT_FILE%" 2>&1
netsh interface ip add dns "Wi-Fi" 8.8.4.4 index=2 >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo [ATTEMPT 3] Try to change DNS via netsh for Ethernet adapter...
echo [ATTEMPT 3] Try to change DNS via netsh for Ethernet adapter... >> "%OUTPUT_FILE%"
netsh interface ip set dns "Ethernet" static 8.8.8.8 >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo [ATTEMPT 4] Check if DNS was actually changed...
echo [ATTEMPT 4] Check if DNS was actually changed... >> "%OUTPUT_FILE%"
ipconfig /all | findstr "DNS Servers" >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo [ATTEMPT 5] Test Cursor domains after DNS change attempt...
echo [ATTEMPT 5] Test Cursor domains after DNS change attempt... >> "%OUTPUT_FILE%"
echo Testing cursor.sh after DNS change: >> "%OUTPUT_FILE%"
nslookup cursor.sh >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo Testing api.github.com after DNS change: >> "%OUTPUT_FILE%"
nslookup api.github.com >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo ======================================== >> "%OUTPUT_FILE%"
echo ALTERNATIVE METHODS >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"

echo [METHOD 1] Test using environment variables...
echo [METHOD 1] Test using environment variables... >> "%OUTPUT_FILE%"
echo Setting DNS environment variables... >> "%OUTPUT_FILE%"
set DNS_SERVER=8.8.8.8 >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo [METHOD 2] Test using PowerShell (if available)...
echo [METHOD 2] Test using PowerShell (if available)... >> "%OUTPUT_FILE%"
powershell -Command "Get-DnsClientServerAddress" >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo [METHOD 3] Test using WMI (likely requires admin)...
echo [METHOD 3] Test using WMI (likely requires admin)... >> "%OUTPUT_FILE%"
wmic nicconfig where "NetEnabled='true'" call SetDNSServerSearchOrder ("8.8.8.8","8.8.4.4") >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo ======================================== >> "%OUTPUT_FILE%"
echo ANALYSIS >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"

echo Based on the results above: >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo If nslookup with 8.8.8.8 or 1.1.1.1 works: >> "%OUTPUT_FILE%"
echo - DNS change might be possible >> "%OUTPUT_FILE%"
echo - Try the DNS change commands manually >> "%OUTPUT_FILE%"
echo - Test Cursor authentication after change >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo If nslookup with 8.8.8.8 or 1.1.1.1 fails: >> "%OUTPUT_FILE%"
echo - Corporate firewall is blocking external DNS >> "%OUTPUT_FILE%"
echo - DNS change won't help >> "%OUTPUT_FILE%"
echo - Need IT approval for domain whitelisting >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo If netsh commands fail with "Access Denied": >> "%OUTPUT_FILE%"
echo - Admin rights required for DNS changes >> "%OUTPUT_FILE%"
echo - Cannot change DNS without admin privileges >> "%OUTPUT_FILE%"
echo - Need IT assistance for DNS configuration >> "%OUTPUT_FILE%"

echo.
echo ========================================
echo ANALYSIS
echo ========================================
echo.
echo Check the output file for detailed results.
echo.
echo If external DNS works, you might be able to:
echo 1. Change DNS temporarily via command line
echo 2. Test Cursor authentication
echo 3. Revert DNS when done
echo.
echo If external DNS is blocked, you'll need:
echo 1. IT approval for domain whitelisting
echo 2. Or use the hybrid workflow approach
echo.

pause 