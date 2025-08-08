#!/bin/bash

echo "=== Forcing Git to recognize all line ending changes (Safe Mode) ==="

# Redirect all output to files
exec 1>git_force_output.txt 2>git_force_errors.txt

echo "1. Temporarily changing core.autocrlf to false..."
git config core.autocrlf false

echo ""
echo "2. Adding all text files to Git index..."
find . -type f -not -path "./.git/*" -not -path "./.idea/*" \( -name "*.py" -o -name "*.txt" -o -name "*.md" -o -name "*.json" -o -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.xml" -o -name "*.sql" -o -name "*.ini" -o -name "*.cfg" -o -name "*.conf" \) -exec git add {} \;

echo ""
echo "3. Checking how many files are now staged..."
git diff --cached --name-only | wc -l

echo ""
echo "4. Restoring core.autocrlf to input..."
git config core.autocrlf input

echo ""
echo "5. Final status check..."
git status --porcelain | wc -l
echo "files are now staged for commit"

echo ""
echo "=== Next steps ==="
echo "Run: git commit -m 'Convert all text files from CRLF to LF'"
echo "Run: git push"
echo ""
echo "This will ensure all ~600+ files are properly committed with LF line endings"

# Close the redirects
exec 1>&1 2>&2

echo "Script completed. Check git_force_output.txt and git_force_errors.txt for details." 