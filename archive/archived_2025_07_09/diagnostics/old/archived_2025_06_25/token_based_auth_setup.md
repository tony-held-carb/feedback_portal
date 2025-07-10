# Token-Based Authentication Setup for Cursor

## Since GitHub is Already Accessible

If you can access GitHub on your work computer, you can generate a personal access token directly:

### Step 1: Generate GitHub Token
1. Go to https://github.com (should work fine)
2. Click your profile picture → Settings
3. Scroll down to "Developer settings" (bottom left)
4. Click "Personal access tokens" → "Tokens (classic)"
5. Click "Generate new token" → "Generate new token (classic)"
6. Give it a descriptive name like "Cursor Work Computer"
7. Set expiration (90 days recommended)
8. Select these scopes:
   - `repo` (full control of private repositories)
   - `workflow` (update GitHub Action workflows)
   - `write:packages` (upload packages)
   - `delete:packages` (delete packages)
9. Click "Generate token"
10. **IMPORTANT**: Copy the token immediately (you won't see it again)

### Step 2: Configure Cursor to Use Token

**Option A: Cursor Settings (Preferred)**
- Open Cursor
- Go to Settings → Extensions → GitHub
- Enter your GitHub username
- Enter the personal access token (not your password)

**Option B: Git Configuration**
- Open terminal in Cursor
- Run these commands:
```bash
git config --global user.name "Your GitHub Username"
git config --global user.email "your-email@example.com"
git config --global credential.helper store
```
- When Cursor prompts for password during Git operations, use the token instead

**Option C: Skip Browser Auth**
- When Cursor asks to "log in", look for:
  - "Use token" option
  - "Advanced" or "Manual" authentication
  - "Skip browser authentication"
- Enter username and token directly

### Step 3: Test the Setup
1. Try cloning a repository in Cursor
2. Try pushing/pulling changes
3. Should work without browser prompts

## How This Works
- **Token is stored locally** (in Git credential helper or Cursor settings)
- **No browser OAuth needed** - bypasses the failing web login
- **Direct API authentication** - uses token for all GitHub operations
- **Persistent access** - works until token expires

## Security Notes
- Keep the token secure (don't share it)
- Set appropriate expiration (90 days recommended)
- Use minimal required permissions
- You can revoke tokens anytime on GitHub

## Troubleshooting
If Cursor still tries browser auth:
- Check if there's a "Use token" option in the login dialog
- Try configuring Git credentials first
- Look for "Skip OAuth" or "Manual authentication" options 