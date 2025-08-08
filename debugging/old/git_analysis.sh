#!/bin/bash

echo "=== Git Analysis: Line Ending Changes ==="
echo ""

echo "1. Current Git status:"
git status --porcelain | head -20

echo ""
echo "2. Number of modified files:"
git status --porcelain | wc -l

echo ""
echo "3. Git core.autocrlf setting:"
git config core.autocrlf

echo ""
echo "4. Git core.eol setting:"
git config core.eol

echo ""
echo "5. Recent commits:"
git log --oneline -3

echo ""
echo "6. Files that were actually changed in the last commit:"
git show --name-only HEAD | head -20

echo ""
echo "7. Number of files in last commit:"
git show --name-only HEAD | wc -l

echo ""
echo "8. Check if any files still have CRLF:"
find . -type f -not -path "./.git/*" -not -path "./.idea/*" \( -name "*.py" -o -name "*.txt" -o -name "*.md" -o -name "*.json" -o -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.xml" -o -name "*.sql" -o -name "*.ini" -o -name "*.cfg" -o -name "*.conf" \) | xargs file | grep "CRLF" | head -10

echo ""
echo "9. Total files with CRLF remaining:"
find . -type f -not -path "./.git/*" -not -path "./.idea/*" \( -name "*.py" -o -name "*.txt" -o -name "*.md" -o -name "*.json" -o -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.xml" -o -name "*.sql" -o -name "*.ini" -o -name "*.cfg" -o -name "*.conf" \) | xargs file | grep "CRLF" | wc -l 