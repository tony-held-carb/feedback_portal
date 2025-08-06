#!/bin/bash

echo "=== Counting Files with CRLF Line Endings ==="

echo "Looking for files that currently have CRLF line endings:"
echo ""

extensions=("py" "txt" "md" "json" "html" "css" "js" "sh" "yml" "yaml" "xml" "sql" "ini" "cfg" "conf")

total_files=0
for ext in "${extensions[@]}"; do
    count=$(find . -type f -not -path "./.git/*" -not -path "./.idea/*" -name "*.$ext" | xargs file | grep "CRLF" | wc -l)
    echo "$ext: $count files with CRLF"
    total_files=$((total_files + count))
done

echo ""
echo "Total files with CRLF line endings: $total_files"

echo ""
echo "=== Files without extensions that have CRLF ==="
find . -type f -not -path "./.git/*" -not -path "./.idea/*" | grep -v '\.[^/]*$' | xargs file | grep "CRLF" | wc -l
echo "files without extensions have CRLF"

echo ""
echo "=== Sample of files with CRLF ==="
find . -type f -not -path "./.git/*" -not -path "./.idea/*" \( -name "*.py" -o -name "*.txt" -o -name "*.md" -o -name "*.json" -o -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.xml" -o -name "*.sql" -o -name "*.ini" -o -name "*.cfg" -o -name "*.conf" \) | xargs file | grep "CRLF" | head -5 