#!/bin/bash

echo "=== Simple Git Status Check ==="

echo "1. Current Git status:"
git status --porcelain | head -10

echo ""
echo "2. Number of modified files:"
git status --porcelain | wc -l

echo ""
echo "3. Adding all files (simple approach):"
git add .

echo ""
echo "4. Checking staged files:"
git diff --cached --name-only | wc -l

echo ""
echo "5. Sample of staged files:"
git diff --cached --name-only | head -10

echo ""
echo "Done! Run 'git commit -m \"Convert line endings to LF\"' to commit changes." 