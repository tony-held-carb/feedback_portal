#!/bin/bash

echo "=== Converting 15 safe files from CRLF to LF ==="

# List of 15 files safe to convert (based on Table 1 analysis)
safe_files=(
    "./.pytest_cache/v/cache/lastfailed"
    "./.pytest_cache/v/cache/nodeids"
    "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Local State"
    "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Local Storage/leveldb/CURRENT"
    "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Local Storage/leveldb/LOCK"
    "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Local Storage/leveldb/LOG"
    "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/machineid"
    "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Network/Cookies-journal"
    "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Network/Network Persistent State"
    "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Network/NetworkDataMigrated"
    "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Network/Trust Tokens-journal"
    "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Preferences"
    "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Session Storage/CURRENT"
    "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Session Storage/LOCK"
    "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Session Storage/LOG"
    "./archive/archived_2025_07_09/diagnostics/old/archived_2025_06_25/diagnostics/Cursor/Shared Dictionary/db-journal"
    "./archive/script_backups/run"
    "./archive/script_backups/run_all"
    "./source/production/.pytest_cache/v/cache/nodeids"
)

# echo "=== Opening files for visual inspection ==="
# for file in "${safe_files[@]}"; do
#     if [ -f "$file" ]; then
#         echo "Opening: $file"
#         # Open in editor (assuming you're using Cursor)
#         cursor "$file" &
#         sleep 1  # Small delay to prevent overwhelming the editor
#     else
#         echo "File not found: $file"
#     fi
# done

echo ""
echo "=== Converting files to LF ==="
for file in "${safe_files[@]}"; do
    if [ -f "$file" ]; then
        echo "Converting: $file"
        dos2unix "$file"
    fi
done

echo ""
echo "=== Conversion complete ==="
echo "Converted $(echo "${safe_files[@]}" | wc -w) files from CRLF to LF"