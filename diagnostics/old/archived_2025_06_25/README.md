# Cursor Authentication Troubleshooting Guide

## Problem Description
Cursor authentication is failing on a work computer (CARB domain environment) with Cisco VPN and corporate network policies.

## Diagnostic Results Summary

### System Information
- **OS**: Windows 11 Enterprise (Build 22631)
- **Domain**: ad.arb.ca.gov (CARB corporate domain)
- **Computer**: HP EliteBook 840 14 inch G9 Notebook PC
- **User**: theld

### Network Configuration
- **Primary DNS**: 10.77.94.22 (CARB corporate)
- **Secondary DNS**: 10.77.64.22 (CARB corporate)
- **VPN**: Cisco AnyConnect Virtual Miniport Adapter (IP: 10.94.23.2)
- **Wi-Fi**: Intel(R) Wi-Fi 6E AX211 (IP: 192.168.1.167)

### Connectivity Tests
✅ **All connectivity tests passed:**
- cursor.sh: 10ms ping
- github.com: 30ms ping  
- api.github.com: 30ms ping

### Cursor Installation
✅ **Cursor properly installed:**
- Location: `C:\Users\theld\AppData\Local\Programs\Cursor`
- Version: Recent installation (06/21/2025)
- All required files present

### Security Environment
- **Proxy**: Disabled (ProxyEnable: 0x0)
- **VPN**: Not currently active
- **Antivirus**: No common security software detected
- **Firewall**: GPO-controlled (corporate managed)

## Root Cause Analysis

### Primary Issue: Corporate DNS Interference
The main problem is the use of CARB corporate DNS servers (`10.77.94.22`, `10.77.64.22`) which are likely:
- Blocking authentication requests to Cursor servers
- Redirecting requests to internal servers
- Implementing corporate content filtering

### Secondary Issues
1. **Corporate Domain Policies**: Group Policy Objects (GPO) may restrict external tool access
2. **SSL/Certificate Issues**: Corporate SSL inspection could interfere with authentication
3. **Network Segmentation**: Corporate network may isolate development tools

## Solutions (In Order of Priority)

### 🎯 **Option 1: GitHub CLI Authentication (RECOMMENDED)**
**Why this works best in corporate environments:**
- Bypasses OAuth flow issues
- Uses browser-based authentication
- Better handles corporate proxy/SSL restrictions
- Cursor can detect existing GitHub CLI authentication

**Steps:**
1. **Install GitHub CLI** (if not already installed):
   ```cmd
   winget install GitHub.cli
   ```
   Or download from: https://cli.github.com/

2. **Authenticate via CLI**:
   ```cmd
   gh auth login
   ```
   - Choose "GitHub.com"
   - Choose "HTTPS"
   - Choose "Yes" to authenticate Git operations
   - Choose "Login with a web browser"
   - Follow the browser authentication

3. **Verify authentication**:
   ```cmd
   gh auth status
   ```

4. **Test Cursor authentication** - Cursor should now pick up the GitHub CLI authentication

### 🔑 **Option 2: Manual Token Authentication**
**Why this works:**
- Bypasses OAuth flow entirely
- Uses simple username/password authentication
- Less likely to be blocked by corporate policies

**Steps:**
1. **Generate Personal Access Token**:
   - Go to GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Select scopes: `repo`, `workflow`, `write:packages`, `read:packages`
   - Copy the token (you won't see it again!)

2. **Use token in Cursor**:
   - When Cursor asks for authentication
   - Use your GitHub username
   - Use the token as your password

### 🌐 **Option 3: DNS Configuration Change**
**Steps:**
1. Open Network Settings
2. Navigate to Wi-Fi adapter properties
3. Change DNS settings to:
   - Primary: `8.8.8.8` (Google DNS)
   - Secondary: `8.8.4.4` (Google DNS)
4. Test Cursor authentication

**Alternative DNS Options:**
- Cloudflare: `1.1.1.1`, `1.0.0.1`
- OpenDNS: `208.67.222.222`, `208.67.220.220`

### 🔄 **Option 4: DNS Cache Flush**
**Safe command (no admin rights required):**
```cmd
ipconfig /flushdns
```
**What it does:**
- Clears DNS cache (temporary stored domain resolutions)
- Forces fresh DNS lookups
- **Does NOT change DNS settings**
- Completely safe and reversible

### 📞 **Option 5: Contact IT Support**
**Request the following:**
- Whitelist `cursor.sh` and `api.github.com` domains
- Allow Cursor authentication through corporate firewall
- Check corporate policies on development tools
- Verify SSL inspection settings

## Diagnostic Scripts

### Available Scripts
1. **`cursor_auth_diagnostics.bat`** - Comprehensive system diagnostics
2. **`cursor_auth_live_diagnostics.bat`** - Real-time monitoring during authentication attempts
3. **`cursor_auth_error_check.bat`** - Analysis and troubleshooting steps
4. **`check_github_cli.bat`** - Check GitHub CLI availability and provide installation help

### How to Use Live Diagnostics
1. Run `cursor_auth_live_diagnostics.bat`
2. Keep the window open
3. Attempt Cursor authentication
4. Watch for error messages
5. Press Ctrl+C to stop monitoring

## Troubleshooting Steps

### Step 1: Check GitHub CLI (Recommended)
1. Run `check_github_cli.bat`
2. If not installed, install GitHub CLI
3. Authenticate: `gh auth login`
4. Test Cursor authentication

### Step 2: Try Manual Token
1. Generate GitHub personal access token
2. Use token as password in Cursor
3. Test authentication

### Step 3: DNS Cache Flush
1. Run: `ipconfig /flushdns`
2. Test Cursor authentication
3. If successful, document for IT

### Step 4: Live Monitoring
1. Run live diagnostics script
2. Attempt authentication
3. Capture any error messages
4. Share results with IT

### Step 5: IT Escalation
If other methods don't work:
1. Contact IT department
2. Share diagnostic results
3. Request domain whitelisting
4. Ask about corporate development tool policies

## Expected Outcomes

### Success Indicators
- Cursor authentication completes without errors
- No network connection failures
- Normal login flow proceeds

### Failure Indicators
- Authentication timeout errors
- Network connection refused
- SSL certificate errors
- Corporate policy blocking messages

## Files Generated
- `cursor_auth_diagnostics_YYYYMMDD_HHMMSS.txt` - System diagnostics
- `cursor_live_auth_YYYYMMDD_HHMMSS.txt` - Real-time monitoring results
- `Cursor/` directory - Cursor application data (if copied)

## Notes
- All diagnostic scripts are read-only and safe to run
- No admin rights required for most operations
- Corporate environment may require IT approval for changes
- Document all changes and results for IT support
- GitHub CLI method is most reliable in corporate environments

## Contact Information
For additional support, share diagnostic results and this README with IT department. 