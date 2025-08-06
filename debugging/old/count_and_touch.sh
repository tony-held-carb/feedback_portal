#!/bin/bash

echo "=== Counting Files by Extension ==="

# Count files by extension
echo "Counting files with specific extensions:"
echo ""

extensions=("py" "txt" "md" "json" "html" "css" "js" "sh" "yml" "yaml" "xml" "sql" "ini" "cfg" "conf")

total_files=0
for ext in "${extensions[@]}"; do
    count=$(find . -type f -not -path "./.git/*" -not -path "./.idea/*" -name "*.$ext" | wc -l)
    echo "$ext: $count files"
    total_files=$((total_files + count))
done

echo ""
echo "Total files with these extensions: $total_files"

# echo ""
# echo "=== Touching Files to Force Git Recognition ==="
# 
# # List of the 15 files without extensions that we converted
# extensionless_files=(
#     "./.pytest_cache/v/cache/lastfailed"
#     "./.pytest_cache/v/cache/nodeids"
#     "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Local State"
#     "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Local Storage/leveldb/CURRENT"
#     "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Local Storage/leveldb/LOCK"
#     "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Local Storage/leveldb/LOG"
#     "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/machineid"
#     "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Network/Cookies-journal"
#     "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Network/Network Persistent State"
#     "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Network/NetworkDataMigrated"
#     "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Network/Trust Tokens-journal"
#     "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Preferences"
#     "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Session Storage/CURRENT"
#     "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Session Storage/LOCK"
#     "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Session Storage/LOG"
#     "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Shared Dictionary/db-journal"
#     "./archive/script_backups/run"
#     "./archive/script_backups/run_all"
#     "./source/production/.pytest_cache/v/cache/nodeids"
# )
# 
# echo "Touching extensionless files..."
# for file in "${extensionless_files[@]}"; do
#     if [ -f "$file" ]; then
#         touch "$file"
#         echo "Touched: $file"
#     fi
# done
# 
# echo ""
# echo "Touching files with extensions..."
# find . -type f -not -path "./.git/*" -not -path "./.idea/*" \( -name "*.py" -o -name "*.txt" -o -name "*.md" -o -name "*.json" -o -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.xml" -o -name "*.sql" -o -name "*.ini" -o -name "*.cfg" -o -name "*.conf" \) -exec touch {} \;
# 
# echo ""
# echo "Adding all touched files to Git..."
# git add .
# 
# echo ""
# echo "Checking staged files..."
# git diff --cached --name-only | wc -l
# echo "files are now staged for commit"
# 
# echo ""
# echo "Done! Run: git commit -m 'Convert all text files from CRLF to LF'" 