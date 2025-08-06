#!/bin/bash

echo "=== Resetting Git Index to Force Line Ending Detection ==="

echo "1. Temporarily changing core.autocrlf to false..."
git config core.autocrlf false

echo ""
echo "2. Resetting Git index..."
git reset

echo ""
echo "3. Re-adding all files..."
git add .

echo ""
echo "4. Checking how many files are now staged..."
git diff --cached --name-only | wc -l

echo ""
echo "5. Sample of staged files:"
git diff --cached --name-only | head -10

echo ""
echo "6. Restoring core.autocrlf to input..."
git config core.autocrlf input

echo ""
echo "Done! Now Git should detect all the line ending changes."
echo "Run: git commit -m 'Convert all text files from CRLF to LF'" 