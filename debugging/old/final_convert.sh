#!/bin/bash

echo "=== Converting the last remaining file with CRLF ==="

# Convert the remaining file
file="./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/cursor_live_auth_20250625_174344.txt"

echo "Converting: $file"
dos2unix "$file"

echo ""
echo "=== Verification ==="
echo "Checking if any files still have CRLF:"
find . -type f -not -path "./.git/*" -not -path "./.idea/*" \( -name "*.py" -o -name "*.txt" -o -name "*.md" -o -name "*.json" -o -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.xml" -o -name "*.sql" -o -name "*.ini" -o -name "*.cfg" -o -name "*.conf" \) | xargs file | grep "CRLF"

echo ""
echo "Total files with CRLF remaining:"
find . -type f -not -path "./.git/*" -not -path "./.idea/*" \( -name "*.py" -o -name "*.txt" -o -name "*.md" -o -name "*.json" -o -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.xml" -o -name "*.sql" -o -name "*.ini" -o -name "*.cfg" -o -name "*.conf" \) | xargs file | grep "CRLF" | wc -l 