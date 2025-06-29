@echo off
REM ========================================
REM GitHub CLI Availability Check
REM ========================================
REM
REM This script checks if GitHub CLI is available
REM and provides installation instructions.
REM
REM ========================================

echo ========================================
echo GitHub CLI Availability Check
echo ========================================
echo.

echo [1/3] Checking if GitHub CLI is installed...
gh --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ GitHub CLI is installed!
    gh --version
    echo.
    echo [2/3] Checking authentication status...
    gh auth status
    echo.
    echo [3/3] Testing GitHub connectivity...
    gh api user
    echo.
    echo ========================================
    echo RECOMMENDATION: Use GitHub CLI for Cursor auth
    echo ========================================
    echo.
    echo Since GitHub CLI is working, try:
    echo 1. Open Cursor
    echo 2. Attempt GitHub authentication
    echo 3. Cursor should detect existing GitHub CLI auth
    echo.
) else (
    echo ❌ GitHub CLI is not installed
    echo.
    echo ========================================
    echo INSTALLATION INSTRUCTIONS
    echo ========================================
    echo.
    echo Option 1: Using winget (Windows Package Manager)
    echo ------------------------------------------------
    echo winget install GitHub.cli
    echo.
    echo Option 2: Manual Download
    echo -------------------------
    echo 1. Go to: https://cli.github.com/
    echo 2. Download Windows installer
    echo 3. Run installer as normal user (no admin needed)
    echo.
    echo Option 3: Using Chocolatey (if available)
    echo -----------------------------------------
    echo choco install gh
    echo.
    echo ========================================
    echo AFTER INSTALLATION
    echo ========================================
    echo 1. Open new Command Prompt
    echo 2. Run: gh auth login
    echo 3. Follow browser authentication
    echo 4. Test: gh auth status
    echo 5. Try Cursor authentication
    echo.
)

echo ========================================
echo ALTERNATIVE: Manual Token Method
echo ========================================
echo.
echo If GitHub CLI doesn't work, try manual token:
echo.
echo 1. Go to GitHub.com → Settings → Developer settings
echo 2. Personal access tokens → Tokens (classic)
echo 3. Generate new token (classic)
echo 4. Select scopes: repo, workflow, write:packages, read:packages
echo 5. Copy token and use in Cursor as password
echo.

pause 