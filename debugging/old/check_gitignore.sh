#!/bin/bash

echo "=== Checking Git Ignore Status ==="
echo ""

echo "1. Files that are ignored by Git:"
git status --ignored | grep "ignored" | head -20

echo ""
echo "2. Number of ignored files:"
git status --ignored | grep "ignored" | wc -l

echo ""
echo "3. Files that are tracked by Git:"
git ls-files | head -20

echo ""
echo "4. Number of tracked files:"
git ls-files | wc -l

echo ""
echo "5. Checking .gitignore files:"
find . -name ".gitignore" -type f

echo ""
echo "6. Content of root .gitignore:"
if [ -f ".gitignore" ]; then
    cat .gitignore
else
    echo "No .gitignore in root directory"
fi

echo ""
echo "7. Files in archive directories (likely ignored):"
find ./archive -type f -name "*.py" -o -name "*.txt" -o -name "*.md" -o -name "*.json" | head -10

echo ""
echo "8. Checking if archive directories are in .gitignore:"
if [ -f ".gitignore" ]; then
    grep -i "archive" .gitignore || echo "archive not found in .gitignore"
fi 