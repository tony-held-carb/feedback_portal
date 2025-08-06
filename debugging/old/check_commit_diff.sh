#!/bin/bash

echo "=== Checking Files Modified Between Commits ==="

echo "Looking for files changed between:"
echo "- 'Initial pycharm CRLF to LF batch.'"
echo "- 'converted many more files from crlf to lf. system files should all be using linux style file endings now'"
echo ""

# Get the commit hashes
commit1=$(git log --oneline | grep "Initial pycharm CRLF" | head -1 | awk '{print $1}')
commit2=$(git log --oneline | grep "converted many more files from crlf to lf" | head -1 | awk '{print $1}')

echo "Commit 1 (Initial pycharm): $commit1"
echo "Commit 2 (converted many more): $commit2"
echo ""

echo "=== Files changed between these commits ==="
git diff --name-only $commit1..$commit2 | head -20

echo ""
echo "=== Count of files changed ==="
git diff --name-only $commit1..$commit2 | wc -l
echo "files were changed between these commits"

echo ""
echo "=== Files by extension ==="
git diff --name-only $commit1..$commit2 | sed 's/.*\.//' | sort | uniq -c | sort -nr

echo ""
echo "=== Sample of changed files ==="
git diff --name-only $commit1..$commit2 | head -10 