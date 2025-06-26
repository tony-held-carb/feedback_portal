# VS Code Setup Guide (IT Approved Alternative to Cursor)

## Situation Summary
- **IT Response**: VS Code is approved, Cursor is not
- **Issue**: Corporate DNS blocks `cursor.sh` and `api.github.com`
- **Solution**: Use VS Code with AI coding extensions

## VS Code Installation

### **Step 1: Install VS Code**
1. Download from: https://code.visualstudio.com/
2. Run installer (no admin rights required)
3. Install for current user only

### **Step 2: Install Essential Extensions**

#### **AI Coding Extensions (Cursor Alternatives):**
1. **GitHub Copilot** (Most Popular)
   - Extension ID: `GitHub.copilot`
   - Features: AI code completion, chat, inline suggestions
   - Cost: $10/month (or free for students/teachers)

2. **Amazon CodeWhisperer** (Free Alternative)
   - Extension ID: `AmazonWebServices.aws-toolkit-vscode`
   - Features: AI code suggestions, security scanning
   - Cost: Free for individual use

3. **Tabnine** (Free Alternative)
   - Extension ID: `TabNine.tabnine-vscode`
   - Features: AI code completion
   - Cost: Free tier available

4. **Kite** (Free Alternative)
   - Extension ID: `kiteco.kite`
   - Features: AI code completion
   - Cost: Free

#### **GitHub Integration:**
1. **GitHub Pull Requests and Issues**
   - Extension ID: `GitHub.vscode-pull-request-github`
   - Features: Manage PRs and issues directly in VS Code

2. **GitLens** (Enhanced Git Features)
   - Extension ID: `eamodio.gitlens`
   - Features: Advanced Git history, blame, etc.

#### **Python Development (For Your Project):**
1. **Python**
   - Extension ID: `ms-python.python`
   - Features: Python language support, debugging

2. **Pylance**
   - Extension ID: `ms-python.vscode-pylance`
   - Features: Fast Python language server

## GitHub CLI Integration

### **Step 1: Verify GitHub CLI**
```cmd
gh --version
gh auth status
```

### **Step 2: Authenticate (if needed)**
```cmd
gh auth login
```

### **Step 3: Test GitHub Integration**
```cmd
gh api user
```

## VS Code Configuration

### **Settings (Ctrl+,)**
```json
{
    "editor.suggestSelection": "first",
    "editor.acceptSuggestionOnCommitCharacter": false,
    "editor.acceptSuggestionOnEnter": "on",
    "editor.tabCompletion": "on",
    "editor.wordBasedSuggestions": "off",
    "editor.quickSuggestions": {
        "other": true,
        "comments": true,
        "strings": true
    },
    "python.defaultInterpreterPath": "C:\\Users\\theld\\miniconda3\\envs\\mini_conda_01\\python.exe",
    "python.terminal.activateEnvironment": true
}
```

### **Keybindings (Ctrl+K Ctrl+S)**
- `Ctrl+Shift+P`: Command Palette
- `Ctrl+,`: Settings
- `Ctrl+Shift+X`: Extensions
- `Ctrl+Shift+G`: Source Control

## GitHub Copilot Setup

### **Step 1: Install Extension**
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "GitHub Copilot"
4. Install the extension

### **Step 2: Authenticate**
1. Sign in with GitHub account
2. Authorize VS Code to use Copilot
3. Verify activation in status bar

### **Step 3: Usage**
- **Inline Suggestions**: Code appears as you type
- **Accept**: Tab or Ctrl+Enter
- **Reject**: Esc
- **Next Suggestion**: Alt+] or Alt+[
- **Previous Suggestion**: Alt+[

## Alternative AI Extensions Setup

### **Amazon CodeWhisperer**
1. Install AWS Toolkit extension
2. Sign in with AWS account (free tier)
3. Enable CodeWhisperer in settings

### **Tabnine**
1. Install Tabnine extension
2. Create free account
3. Configure in settings

## Git Integration

### **Step 1: Configure Git**
```cmd
git config --global user.name "Your Name"
git config --global user.email "your.email@arb.ca.gov"
```

### **Step 2: VS Code Git Features**
- Source Control panel (Ctrl+Shift+G)
- Git commands in Command Palette
- Integrated terminal for Git operations

## Project Setup

### **Step 1: Open Your Project**
```cmd
code D:\local\cursor\feedback_portal
```

### **Step 2: Select Python Interpreter**
1. Ctrl+Shift+P
2. "Python: Select Interpreter"
3. Choose your conda environment

### **Step 3: Install Python Dependencies**
```cmd
pip install -r requirements.txt
```

## Comparison: VS Code vs Cursor

### **VS Code Advantages:**
- ✅ IT approved
- ✅ Extensive extension ecosystem
- ✅ Stable and mature
- ✅ Works with corporate DNS
- ✅ GitHub Copilot integration

### **VS Code Limitations:**
- ❌ Less integrated AI features than Cursor
- ❌ Requires multiple extensions for full functionality
- ❌ More setup required

### **Cursor Advantages:**
- ✅ Integrated AI features
- ✅ Better AI code completion
- ✅ Built-in chat interface
- ✅ Streamlined experience

### **Cursor Limitations:**
- ❌ Not IT approved
- ❌ Blocked by corporate DNS
- ❌ Requires authentication servers

## Troubleshooting

### **Extension Issues:**
1. Reload VS Code (Ctrl+Shift+P → "Developer: Reload Window")
2. Check extension logs
3. Reinstall problematic extensions

### **GitHub Integration Issues:**
1. Verify GitHub CLI authentication
2. Check network connectivity
3. Clear VS Code cache

### **Python Issues:**
1. Verify Python interpreter path
2. Check conda environment activation
3. Install missing packages

## Next Steps

1. **Install VS Code** and essential extensions
2. **Set up GitHub Copilot** for AI assistance
3. **Configure Python environment** for your project
4. **Test Git integration** with your repository
5. **Customize settings** for optimal workflow

## Resources

- [VS Code Documentation](https://code.visualstudio.com/docs)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [VS Code Python Guide](https://code.visualstudio.com/docs/languages/python)
- [GitHub CLI Documentation](https://cli.github.com/)

## Notes

- VS Code is a mature, stable alternative to Cursor
- GitHub Copilot provides similar AI capabilities
- All extensions work within corporate network restrictions
- Setup may take longer but provides more flexibility 