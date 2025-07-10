# Hybrid Workflow Guide: Cursor at Home + VS Code at Work

## Overview
Since Cursor is blocked at work but you want to use its AI features, this guide outlines a hybrid approach:
- **Home**: Use Cursor for AI-assisted development
- **Work**: Use VS Code for basic editing and testing
- **Sync**: Git repository for code synchronization

## Workflow Strategy

### **Home Computer (Cursor)**
- Primary development with AI assistance
- Complex refactoring and new features
- AI-powered code generation and debugging
- Full Git operations and commits

### **Work Computer (VS Code)**
- Code review and testing
- Bug fixes and minor changes
- Running and debugging applications
- Documentation updates

## Setup Instructions

### **Home Computer Setup**

#### **1. Install Cursor**
```bash
# Download from https://cursor.sh/
# Install normally (no corporate restrictions)
```

#### **2. Configure Git**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@arb.ca.gov"
```

#### **3. Clone Repository**
```bash
git clone https://github.com/tony-held-carb/feedback_portal.git
cd feedback_portal
```

#### **4. Set Up Python Environment**
```bash
# Create conda environment
conda create -n feedback_portal python=3.9
conda activate feedback_portal

# Install dependencies
pip install -r requirements.txt
```

### **Work Computer Setup**

#### **1. Install VS Code**
- Download from https://code.visualstudio.com/
- Install for current user (no admin rights needed)

#### **2. Install Essential Extensions**
```json
{
    "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "eamodio.gitlens",
        "GitHub.vscode-pull-request-github"
    ]
}
```

#### **3. Configure Python Environment**
- Point to your conda environment
- Install required packages

## Daily Workflow

### **Morning Routine (Work)**

#### **1. Pull Latest Changes**
```bash
git pull origin refactor_20
```

#### **2. Review Changes**
- Check what was done at home
- Review AI-generated code
- Test functionality

#### **3. Make Minor Changes**
- Bug fixes
- Documentation updates
- Testing

### **Evening Routine (Home)**

#### **1. Pull Work Changes**
```bash
git pull origin refactor_20
```

#### **2. Continue Development**
- Use Cursor's AI features
- Implement new features
- Refactor code

#### **3. Commit and Push**
```bash
git add .
git commit -m "Feature: [description]"
git push origin refactor_20
```

## Best Practices

### **Git Workflow**

#### **Branch Strategy**
```bash
# Main development branch
git checkout refactor_20

# Feature branches (when needed)
git checkout -b feature/new-feature
git push origin feature/new-feature
```

#### **Commit Messages**
```bash
# Use descriptive commit messages
git commit -m "Feature: Add user authentication system"
git commit -m "Fix: Resolve database connection timeout"
git commit -m "Refactor: Improve code organization"
```

#### **Regular Syncing**
- Pull before starting work each day
- Push before ending work each day
- Use meaningful commit messages

### **Code Organization**

#### **File Structure**
```
feedback_portal/
├── source/production/arb/     # Main application
├── diagnostics/              # Troubleshooting tools
├── documentation/            # Project docs
├── README.md                 # Project overview
└── requirements.txt          # Dependencies
```

#### **Development Guidelines**
- Keep work and home environments in sync
- Document major changes
- Test thoroughly before pushing
- Use consistent coding standards

## Communication Between Environments

### **Work Notes (Work Computer)**
Create a `work_notes.md` file for communication:
```markdown
# Work Notes

## Today's Tasks
- [ ] Review AI-generated auth refactor
- [ ] Test database connections
- [ ] Update documentation

## Issues Found
- Database timeout on work network
- Need to update requirements.txt

## Questions for Home Development
- Should we add more error handling?
- Consider adding logging to auth module
```

### **Home Notes (Home Computer)**
Create a `home_notes.md` file:
```markdown
# Home Development Notes

## Completed Today
- ✅ Refactored authentication system
- ✅ Added comprehensive error handling
- ✅ Updated documentation

## Next Steps
- [ ] Implement user profile management
- [ ] Add password reset functionality
- [ ] Optimize database queries

## Issues to Address
- Need to handle corporate proxy settings
- Consider adding offline mode
```

## Troubleshooting

### **Common Issues**

#### **Merge Conflicts**
```bash
# If conflicts occur
git status
git diff
# Resolve conflicts manually
git add .
git commit -m "Resolve merge conflicts"
```

#### **Environment Differences**
- Keep `requirements.txt` updated
- Document environment-specific settings
- Use relative paths when possible

#### **Large Files**
```bash
# Check for large files
git ls-files | xargs ls -la | sort -k5 -nr | head -10

# Add to .gitignore if needed
echo "large_file.dat" >> .gitignore
```

### **Backup Strategy**

#### **Regular Backups**
```bash
# Create backup branch
git checkout -b backup/$(date +%Y%m%d)
git push origin backup/$(date +%Y%m%d)
```

#### **Cloud Backup**
- Consider using GitHub for code backup
- Use cloud storage for large files
- Keep local backups of important data

## Productivity Tips

### **Cursor at Home**
- Use AI for code generation
- Leverage chat for debugging
- Take advantage of refactoring tools
- Generate documentation with AI

### **VS Code at Work**
- Focus on testing and validation
- Use integrated terminal for running apps
- Leverage Git integration
- Use extensions for productivity

### **Synchronization**
- Commit frequently with clear messages
- Pull before starting work
- Push before ending work
- Use branches for major features

## Security Considerations

### **Corporate Compliance**
- Don't store sensitive data in Git
- Use environment variables for secrets
- Follow corporate security policies
- Don't sync personal data

### **Data Protection**
- Keep work and personal data separate
- Use appropriate .gitignore files
- Don't commit credentials or keys
- Regular security reviews

## Alternative Tools

### **If Git Sync Becomes Problematic**
- **GitHub Desktop**: Visual Git interface
- **SourceTree**: Advanced Git client
- **VS Code Git**: Integrated Git in VS Code
- **Cloud Storage**: For non-code files

### **For Large Files**
- **Git LFS**: Large file storage
- **Cloud Storage**: Google Drive, OneDrive
- **USB Drives**: For very large files

## Success Metrics

### **Track Progress**
- Regular commits and pushes
- Reduced merge conflicts
- Faster development cycles
- Better code quality

### **Continuous Improvement**
- Refine workflow based on experience
- Optimize sync frequency
- Improve communication between environments
- Enhance automation where possible

## Conclusion

This hybrid approach allows you to:
- ✅ Use Cursor's AI features at home
- ✅ Comply with corporate policies at work
- ✅ Maintain code synchronization
- ✅ Leverage the best of both environments

The key is establishing a consistent workflow and maintaining good communication between your development environments. 