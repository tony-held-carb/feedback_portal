# Cursor Authentication Flow Analysis

## The Problem
When Cursor asks you to "log in" and offers email, Google, or GitHub options, it launches a browser window for authentication. However, this browser window will still be subject to the same corporate DNS restrictions that prevent access to GitHub.

## Cursor's Authentication Methods

### 1. Browser-Based OAuth (What you're seeing)
- Cursor opens a browser window
- Browser tries to access GitHub's OAuth endpoints
- **FAILS** because corporate DNS blocks GitHub domains
- This is the current flow you're experiencing

### 2. Personal Access Token (What we need)
- Bypasses browser-based OAuth entirely
- Uses direct API authentication
- **WORKS** even with DNS restrictions (once you have the token)

## The Solution: Get Token First, Then Configure Cursor

### Step 1: Enable Chrome DNS-over-HTTPS
1. Open Chrome
2. Settings → Privacy and security → Security
3. Enable "Use secure DNS" with Google or Cloudflare
4. Test: https://github.com should work in Chrome

### Step 2: Generate GitHub Token in Chrome
1. Go to https://github.com in Chrome (should work with DoH)
2. Sign in to your GitHub account
3. Go to Settings → Developer settings → Personal access tokens → Tokens (classic)
4. Generate new token with these scopes:
   - `repo` (full control of private repositories)
   - `workflow` (update GitHub Action workflows)
   - `write:packages` (upload packages to GitHub Package Registry)
   - `delete:packages` (delete packages from GitHub Package Registry)

### Step 3: Configure Cursor to Use Token
**Method A: Direct Configuration**
- Open Cursor
- Go to Settings → Extensions → GitHub
- Enter your GitHub username
- Enter the personal access token (not password)

**Method B: Skip Browser Auth**
- When Cursor prompts for login, look for "Use token" or "Advanced" options
- Enter username and token directly

**Method C: Manual Git Configuration**
- Open terminal in Cursor
- Run: `git config --global user.name "Your GitHub Username"`
- Run: `git config --global user.email "your-email@example.com"`
- Run: `git config --global credential.helper store`
- When prompted for password, use the token instead

## Why This Works
- **Chrome DoH** bypasses DNS restrictions to get the token
- **Token authentication** doesn't require ongoing DNS resolution
- **Git operations** use the token directly, not browser OAuth

## Alternative: Offline Token Generation
If Chrome DoH doesn't work, you can:
1. Use your phone's hotspot temporarily
2. Generate the token on a different network
3. Copy the token to your work machine
4. Configure Cursor with the token

## Testing the Setup
Once configured, test with:
```bash
git clone https://github.com/your-username/test-repo.git
```
Should work without browser prompts. 