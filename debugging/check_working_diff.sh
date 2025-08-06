#!/bin/bash

echo "=== Checking Working Directory Changes Between Commits ==="

echo "Looking for files that were actually modified between:"
echo "- 'Initial pycharm CRLF to LF batch.'"
echo "- 'converted many more files from crlf to lf. system files should all be using linux style file endings now'"
echo ""

# Get the commit hashes
commit1=$(git log --oneline | grep "Initial pycharm CRLF" | head -1 | awk '{print $1}')
commit2=$(git log --oneline | grep "converted many more files from crlf to lf" | head -1 | awk '{print $1}')

echo "Commit 1 (Initial pycharm): $commit1"
echo "Commit 2 (converted many more): $commit2"
echo ""

echo "=== Checking what files exist in commit2 but not in commit1 ==="
git diff --name-only $commit1..$commit2 --diff-filter=A | head -10

echo ""
echo "=== Checking what files were modified in commit2 vs commit1 ==="
git diff --name-only $commit1..$commit2 --diff-filter=M | head -10

echo ""
echo "=== Alternative: Check what files have different content between commits ==="
echo "This might show files that were converted but Git didn't track as changed:"
git diff $commit1..$commit2 --name-only | head -10

echo ""
echo "=== Total files with any changes between commits ==="
git diff $commit1..$commit2 --name-only | wc -l
echo "files have any differences between these commits"

echo ""
echo "=== Note ==="
echo "If this still shows only ~22 files, it means Git's core.autocrlf setting"
echo "prevented Git from seeing the line ending changes as modifications."
echo "We may need to force Git to re-evaluate all files." 