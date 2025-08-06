#!/bin/bash

echo "=== Simple Git Add for Line Ending Changes ==="

# Create a temporary file list
echo "Creating file list..."
find . -type f -not -path "./.git/*" -not -path "./.idea/*" \( -name "*.py" -o -name "*.txt" -o -name "*.md" -o -name "*.json" -o -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.xml" -o -name "*.sql" -o -name "*.ini" -o -name "*.cfg" -o -name "*.conf" \) > temp_files.txt

echo "Found $(wc -l < temp_files.txt) files to process"

echo ""
echo "Adding files to Git (this may take a while)..."
while IFS= read -r file; do
    if [ -f "$file" ]; then
        git add "$file" 2>/dev/null
        echo -n "."  # Progress indicator
    fi
done < temp_files.txt

echo ""
echo "Checking staged files..."
git diff --cached --name-only | wc -l

echo ""
echo "Cleaning up..."
rm temp_files.txt

echo "Done! Check git status to see staged files." 