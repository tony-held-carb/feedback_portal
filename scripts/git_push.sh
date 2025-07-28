#!/bin/bash

# git_push.sh
# ============
#
# A bash script for automated git operations that adds files, commits them,
# and pushes to the remote repository with either a default message or a 
# custom message provided via argument.
#
# Usage:
#   ./git_push.sh file1 file2 file3
#   ./git_push.sh --commit_message "Custom commit message" file1 file2
#   ./git_push.sh -m "Custom commit message" file1 file2
#
# Arguments:
#   --commit_message, -m: Custom commit message (optional)
#   file1, file2, ...: Files to add, commit, and push
#
# Examples:
#   ./git_push.sh admin/mini_conda_02.yml
#   ./git_push.sh --commit_message "Update conda environment" admin/mini_conda_02.yml
#   ./git_push.sh -m "Fix E2E test issues" tests/e2e/test_*.py
#
# Requirements:
#   - Git must be installed and configured
#   - Script must be run from a git repository
#   - User must have write permissions to the repository

set -e  # Exit on any error

# Default values
COMMIT_MESSAGE="Auto commit"
FILES=()

# Function to display usage information
show_usage() {
    echo "Usage: $0 [OPTIONS] file1 [file2 ...]"
    echo ""
    echo "Options:"
    echo "  --commit_message, -m    Custom commit message (default: 'Auto commit')"
    echo "  --help, -h             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 file1.txt file2.py"
    echo "  $0 --commit_message 'Update configuration' config.yml"
    echo "  $0 -m 'Fix bug in module' src/module.py"
    echo ""
    echo "Note: If no files are specified, the script will exit with an error."
}

# Function to check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "Error: Not in a git repository. Please run this script from a git repository."
        exit 1
    fi
}

# Function to check if git is configured
check_git_config() {
    if ! git config --get user.name > /dev/null 2>&1; then
        echo "Error: Git user.name is not configured. Please run:"
        echo "  git config --global user.name 'Your Name'"
        exit 1
    fi
    
    if ! git config --get user.email > /dev/null 2>&1; then
        echo "Error: Git user.email is not configured. Please run:"
        echo "  git config --global user.email 'your.email@example.com'"
        exit 1
    fi
}

# Function to validate files exist
validate_files() {
    local missing_files=()
    
    for file in "${FILES[@]}"; do
        if [[ ! -e "$file" ]]; then
            missing_files+=("$file")
        fi
    done
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        echo "Error: The following files do not exist:"
        printf '  %s\n' "${missing_files[@]}"
        exit 1
    fi
}

# Function to check if files have changes
check_for_changes() {
    local changed_files=()
    
    for file in "${FILES[@]}"; do
        if git status --porcelain "$file" | grep -q .; then
            changed_files+=("$file")
        fi
    done
    
    if [[ ${#changed_files[@]} -eq 0 ]]; then
        echo "Warning: No changes detected in the specified files."
        echo "Files checked: ${FILES[*]}"
        exit 0
    fi
}

# Function to perform git operations
perform_git_operations() {
    echo "Adding files to git..."
    git add "${FILES[@]}"
    
    echo "Committing with message: '$COMMIT_MESSAGE'"
    git commit -m "$COMMIT_MESSAGE"
    
    echo "✅ Successfully committed ${#FILES[@]} file(s):"
    printf '  %s\n' "${FILES[@]}"
    
    echo "Pushing to remote repository..."
    git push
    
    echo "✅ Successfully pushed to remote repository"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --commit_message|-m)
            if [[ -n "$2" && "$2" != --* ]]; then
                COMMIT_MESSAGE="$2"
                shift 2
            else
                echo "Error: --commit_message requires a value"
                exit 1
            fi
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        --*)
            echo "Error: Unknown option $1"
            show_usage
            exit 1
            ;;
        *)
            FILES+=("$1")
            shift
            ;;
    esac
done

# Check if files were provided
if [[ ${#FILES[@]} -eq 0 ]]; then
    echo "Error: No files specified."
    show_usage
    exit 1
fi

# Main execution
echo "=== Git Push Script ==="
echo "Commit message: $COMMIT_MESSAGE"
echo "Files to process: ${FILES[*]}"
echo ""

# Run checks
check_git_repo
check_git_config
validate_files
check_for_changes

# Perform git operations
perform_git_operations

echo ""
echo "🎉 Git add, commit, and push completed successfully!" 