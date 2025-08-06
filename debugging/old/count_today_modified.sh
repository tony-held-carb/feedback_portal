#!/bin/bash

echo "=== Counting Files Modified Today by Extension ==="

# Get today's date in the format that find uses
today=$(date +%Y-%m-%d)

echo "Looking for files modified today ($today):"
echo ""

extensions=("py" "txt" "md" "json" "html" "css" "js" "sh" "yml" "yaml" "xml" "sql" "ini" "cfg" "conf")

total_files=0
for ext in "${extensions[@]}"; do
    count=$(find . -type f -not -path "./.git/*" -not -path "./.idea/*" -name "*.$ext" -newermt "$today" | wc -l)
    echo "$ext: $count files"
    total_files=$((total_files + count))
done

echo ""
echo "Total files modified today with these extensions: $total_files"

echo ""
echo "=== Files without extensions modified today ==="
find . -type f -not -path "./.git/*" -not -path "./.idea/*" -newermt "$today" | grep -v '\.[^/]*$' | wc -l
echo "files without extensions modified today"

echo ""
echo "=== Sample of files modified today ==="
find . -type f -not -path "./.git/*" -not -path "./.idea/*" -newermt "$today" \( -name "*.py" -o -name "*.txt" -o -name "*.md" -o -name "*.json" -o -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.xml" -o -name "*.sql" -o -name "*.ini" -o -name "*.cfg" -o -name "*.conf" \) | head -10 