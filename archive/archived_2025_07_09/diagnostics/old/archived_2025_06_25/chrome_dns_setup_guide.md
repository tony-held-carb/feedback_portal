# Chrome DNS-over-HTTPS Setup Guide

## What is DNS-over-HTTPS (DoH)?
DNS-over-HTTPS encrypts DNS queries and sends them over HTTPS, bypassing traditional DNS servers. This can help you access GitHub and Cursor even when corporate DNS blocks these domains.

## Step-by-Step Setup

### 1. Open Chrome Settings
- Open Chrome
- Click the three dots menu (⋮) in the top-right corner
- Select "Settings"

### 2. Navigate to Privacy and Security
- In the left sidebar, click "Privacy and security"
- Scroll down to find "Security"

### 3. Enable DNS-over-HTTPS
- In the Security section, find "Use secure DNS"
- Toggle it ON
- Select "With" from the dropdown
- Choose one of these providers:
  - **Google (Public DNS)** - `https://dns.google/dns-query`
  - **Cloudflare** - `https://cloudflare-dns.com/dns-query`
  - **Quad9** - `https://dns.quad9.net/dns-query`

### 4. Test the Connection
1. Open a new tab in Chrome
2. Go to `chrome://net-internals/#dns`
3. Click "Clear host cache"
4. Try accessing: https://github.com
5. Go back to `chrome://net-internals/#dns` and check if GitHub resolves

### 5. Authenticate with GitHub
1. Go to https://github.com in Chrome
2. Sign in to your GitHub account
3. Go to GitHub Settings → Developer settings → Personal access tokens
4. Generate a new token with appropriate permissions
5. Copy the token

### 6. Use Token in Cursor
Once you have the token, you can use it in Cursor:
- Open Cursor
- Go to Settings → Extensions → GitHub
- Enter your GitHub username and the personal access token

## Alternative: GitHub CLI in Chrome
If the above doesn't work, you can try:
1. Open Chrome
2. Go to https://cli.github.com/
3. Follow the web-based authentication flow
4. Copy the generated token for use in Cursor

## Troubleshooting
- If Chrome still can't access GitHub, try a different DNS provider
- Clear Chrome's DNS cache: `chrome://net-internals/#dns`
- Check if your corporate firewall blocks HTTPS traffic to DNS providers
- Try using a mobile hotspot temporarily to test if it's a network issue

## Benefits
- Bypasses corporate DNS restrictions
- Encrypted DNS queries for privacy
- Works without admin rights
- One-time setup for persistent access 