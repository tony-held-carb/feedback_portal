@echo off
REM ========================================
REM Cursor Authentication Diagnostics Script
REM ========================================
REM
REM SAFETY NOTICE:
REM --------------
REM This script is READ-ONLY and SAFE to run.
REM - Only collects system information and diagnostics
REM - Does NOT modify any system settings
REM - Does NOT change system performance
REM - Does NOT install or uninstall software
REM - Does NOT modify registry values
REM - Does NOT change network configuration
REM - Only creates a text file with diagnostic information
REM - Designed to work WITHOUT admin rights
REM
REM PURPOSE:
REM --------
REM Collects comprehensive system information to help troubleshoot
REM Cursor authentication issues, especially in corporate environments
REM with VPN, proxy, or security software.
REM
REM ========================================

echo ========================================
echo Cursor Authentication Diagnostics Script
echo ========================================
echo.
echo SAFETY: This script only collects information - no changes made
echo NOTE: Running without admin rights - some info may be limited
echo.
echo Collecting system information...
echo.

REM Create diagnostics directory if it doesn't exist
if not exist "diagnostics" mkdir diagnostics

REM Set output file
set OUTPUT_FILE=diagnostics\cursor_auth_diagnostics_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt
set OUTPUT_FILE=%OUTPUT_FILE: =0%

echo Cursor Authentication Diagnostics Report > "%OUTPUT_FILE%"
echo Generated: %date% %time% >> "%OUTPUT_FILE%"
echo SAFETY: Read-only diagnostics - no system changes made >> "%OUTPUT_FILE%"
echo NOTE: Run without admin rights - some information may be limited >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo [1/8] System Information...
echo ======================================== >> "%OUTPUT_FILE%"
echo SYSTEM INFORMATION >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
systeminfo >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo [2/8] Network Configuration...
echo ======================================== >> "%OUTPUT_FILE%"
echo NETWORK CONFIGURATION >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
ipconfig /all >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo [3/8] DNS Configuration...
echo ======================================== >> "%OUTPUT_FILE%"
echo DNS CONFIGURATION >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
nslookup cursor.sh >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"
nslookup github.com >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo [4/8] VPN Status and Configuration...
echo ======================================== >> "%OUTPUT_FILE%"
echo VPN STATUS AND CONFIGURATION >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
echo Checking for Cisco VPN processes... >> "%OUTPUT_FILE%"
tasklist /fi "imagename eq vpnui.exe" >> "%OUTPUT_FILE%" 2>&1
tasklist /fi "imagename eq vpncli.exe" >> "%OUTPUT_FILE%" 2>&1
tasklist /fi "imagename eq cisco*" >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo Checking VPN registry entries (user-level only)... >> "%OUTPUT_FILE%"
reg query "HKCU\SOFTWARE\Cisco Systems" /s 2>nul >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo [5/8] Proxy Configuration...
echo ======================================== >> "%OUTPUT_FILE%"
echo PROXY CONFIGURATION >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable >> "%OUTPUT_FILE%" 2>&1
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer >> "%OUTPUT_FILE%" 2>&1
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyOverride >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo [6/8] Security Software...
echo ======================================== >> "%OUTPUT_FILE%"
echo SECURITY SOFTWARE >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
echo Checking for common antivirus/security software... >> "%OUTPUT_FILE%"
tasklist /fi "imagename eq msseces.exe" >> "%OUTPUT_FILE%" 2>&1
tasklist /fi "imagename eq mcshield.exe" >> "%OUTPUT_FILE%" 2>&1
tasklist /fi "imagename eq avast.exe" >> "%OUTPUT_FILE%" 2>&1
tasklist /fi "imagename eq avgui.exe" >> "%OUTPUT_FILE%" 2>&1
tasklist /fi "imagename eq norton.exe" >> "%OUTPUT_FILE%" 2>&1
tasklist /fi "imagename eq kav.exe" >> "%OUTPUT_FILE%" 2>&1
tasklist /fi "imagename eq kavsvc.exe" >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo [7/8] Cursor Installation and Data...
echo ======================================== >> "%OUTPUT_FILE%"
echo CURSOR INSTALLATION AND DATA >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
echo Checking Cursor installation... >> "%OUTPUT_FILE%"
dir "C:\Users\%USERNAME%\AppData\Local\Programs\Cursor" 2>nul >> "%OUTPUT_FILE%"
dir "C:\Users\%USERNAME%\AppData\Roaming\Cursor" 2>nul >> "%OUTPUT_FILE%"
dir "C:\Users\%USERNAME%\AppData\Local\Cursor" 2>nul >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo [8/8] Browser Information...
echo ======================================== >> "%OUTPUT_FILE%"
echo BROWSER INFORMATION >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
echo Checking installed browsers... >> "%OUTPUT_FILE%"
reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" 2>nul >> "%OUTPUT_FILE%"
reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe" 2>nul >> "%OUTPUT_FILE%"
reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe" 2>nul >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo ======================================== >> "%OUTPUT_FILE%"
echo CONNECTIVITY TESTS >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
echo Testing connectivity to Cursor and GitHub... >> "%OUTPUT_FILE%"
ping -n 1 cursor.sh >> "%OUTPUT_FILE%" 2>&1
ping -n 1 github.com >> "%OUTPUT_FILE%" 2>&1
ping -n 1 api.github.com >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo ======================================== >> "%OUTPUT_FILE%"
echo ENVIRONMENT VARIABLES >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
echo Checking relevant environment variables... >> "%OUTPUT_FILE%"
echo HTTP_PROXY: %HTTP_PROXY% >> "%OUTPUT_FILE%"
echo HTTPS_PROXY: %HTTPS_PROXY% >> "%OUTPUT_FILE%"
echo NO_PROXY: %NO_PROXY% >> "%OUTPUT_FILE%"
echo. >> "%OUTPUT_FILE%"

echo ======================================== >> "%OUTPUT_FILE%"
echo FIREWALL STATUS (Limited - No Admin Rights) >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
echo Note: Firewall information limited without admin rights >> "%OUTPUT_FILE%"
netsh advfirewall show allprofiles >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo ======================================== >> "%OUTPUT_FILE%"
echo USER-LEVEL REGISTRY INFORMATION >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"
echo Checking user-level registry for additional info... >> "%OUTPUT_FILE%"
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer" /v Shell Folders >> "%OUTPUT_FILE%" 2>&1
echo. >> "%OUTPUT_FILE%"

echo ======================================== >> "%OUTPUT_FILE%"
echo END OF REPORT >> "%OUTPUT_FILE%"
echo ======================================== >> "%OUTPUT_FILE%"

echo.
echo Diagnostics complete!
echo Output saved to: %OUTPUT_FILE%
echo.
echo SAFETY: No system changes were made - read-only diagnostics only.
echo NOTE: Some information may be limited without admin rights.
echo.
echo Please share this file for analysis.
echo.
pause 