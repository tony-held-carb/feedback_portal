@echo off
echo Testing Scenario 1: Token-based authentication with Git commands only
echo.

echo Step 1: Check current Git configuration
echo.
echo Current Git user:
git config --global user.name
git config --global user.email
echo.
echo Current credential helper:
git config --global credential.helper
echo.

echo Step 2: Generate GitHub Token (Manual Step)
echo.
echo Please do this manually:
echo 1. Go to https://github.com
echo 2. Sign in as: tony-held-carb
echo 3. Go to Settings ^> Developer settings ^> Personal access tokens
echo 4. Generate new token with 'repo' and 'workflow' permissions
echo 5. Copy the token
echo.
echo Repository: tony-held-carb/feedback_portal
echo Username: tony-held-carb
echo.
pause

echo Step 3: Configure Git to store credentials
echo.
git config --global credential.helper store
echo Credential helper set to 'store'
echo.

echo Step 4: Trigger authentication with a test push
echo.
echo Making a small test change to trigger authentication...
echo # Test commit for authentication setup - %date% %time% >> README.md
git add README.md
git commit -m "Test commit for authentication setup"
echo.

echo Step 5: Push to trigger authentication prompt
echo.
echo When prompted for credentials:
echo - Username: tony-held-carb
echo - Password: paste your personal access token (not your GitHub password)
echo.
echo Pushing to: https://github.com/tony-held-carb/feedback_portal
git push
echo.

echo Step 6: Verify token is stored
echo.
if exist "%USERPROFILE%\.git-credentials" (
    echo SUCCESS: Token stored in .git-credentials
    echo File location: %USERPROFILE%\.git-credentials
    echo.
    echo Checking if token is for correct repository:
    findstr "github.com" "%USERPROFILE%\.git-credentials"
) else (
    echo WARNING: No .git-credentials file found
)
echo.

echo Step 7: Test Git operations work without prompts
echo.
echo Testing git pull (should work without prompts)...
git pull
echo.

echo Step 8: Test another Git operation
echo.
echo Testing git status and remote info...
git status
git remote -v
echo.

echo Step 9: Restart Cursor
echo.
echo Now restart Cursor completely and test:
echo 1. Open Cursor
echo 2. Try using GitHub features (Sync, Push buttons)
echo 3. See if login button still appears
echo.
pause

echo Step 10: Results Analysis
echo.
echo If Cursor no longer shows login button: SCENARIO 1 SUCCESS!
echo If Cursor still shows login button: Try Scenario 3 (Git commands work)
echo.
echo Repository: tony-held-carb/feedback_portal
echo Username: tony-held-carb
echo Token should be stored for: https://github.com
echo.
pause 