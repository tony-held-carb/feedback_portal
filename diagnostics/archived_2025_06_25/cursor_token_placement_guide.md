# Where to Place GitHub Token for Cursor

## Method 1: Git Credential Helper (Most Reliable)

This is the most reliable method - Git will store the token and Cursor will use it automatically.

### Step 1: Configure Git
Open terminal in Cursor and run:
```bash
git config --global user.name "Your GitHub Username"
git config --global user.email "your-email@example.com"
git config --global credential.helper store
```

### Step 2: Trigger Token Storage
The first time you do a Git operation that requires authentication:
```bash
git clone https://github.com/your-username/test-repo.git
```
When prompted:
- **Username**: your GitHub username
- **Password**: paste your personal access token (not your GitHub password)

### Step 3: Verify Storage
The token is now stored in: `%USERPROFILE%\.git-credentials`
You can check this file exists and contains your token.

## Method 2: Cursor Settings (If Available)

### Step 1: Open Cursor Settings
- Press `Ctrl+,` or go to File → Preferences → Settings
- Search for "GitHub" or "git"

### Step 2: Look for GitHub Extension Settings
Common locations:
- Extensions → GitHub
- Git → GitHub
- Authentication → GitHub
- Source Control → GitHub

### Step 3: Enter Token
- Username: your GitHub username
- Password/Token: paste your personal access token

## Method 3: Windows Credential Manager

### Step 1: Open Credential Manager
- Press `Win+R`, type `control keymgr.dll`, press Enter
- Or search "Credential Manager" in Start menu

### Step 2: Add GitHub Credentials
- Click "Windows Credentials" → "Add a generic credential"
- Internet or network address: `git:https://github.com`
- User name: your GitHub username
- Password: paste your personal access token

## Method 4: Environment Variables

### Step 1: Set Environment Variables
Open terminal in Cursor and run:
```bash
setx GITHUB_TOKEN "your-personal-access-token"
setx GITHUB_USERNAME "your-github-username"
```

### Step 2: Restart Cursor
Close and reopen Cursor for the environment variables to take effect.

## Method 5: Git Config Direct Token

### Step 1: Configure Git with Token
```bash
git config --global github.token "your-personal-access-token"
git config --global github.user "your-github-username"
```

## Testing the Setup

### Test 1: Clone Repository
```bash
git clone https://github.com/your-username/test-repo.git
```
Should work without prompts.

### Test 2: Push Changes
```bash
cd test-repo
echo "test" > test.txt
git add test.txt
git commit -m "test commit"
git push
```
Should work without prompts.

## Troubleshooting

### If Cursor Still Prompts for Web Auth:
1. Check if token is properly stored: `git config --list | findstr github`
2. Verify credential helper: `git config --global credential.helper`
3. Check Windows Credential Manager for conflicting entries
4. Try Method 1 (Git credential helper) as it's most reliable

### If Token Doesn't Work:
1. Verify token has correct permissions (repo, workflow)
2. Check if token is expired
3. Generate a new token and try again

## Security Notes
- The token is stored in plain text in credential files
- Keep your computer secure
- Set appropriate token expiration (90 days recommended)
- You can revoke tokens anytime on GitHub 