#!/bin/bash

echo "=== Forcing Git to Re-evaluate All Converted Files ==="

echo "1. Temporarily changing core.autocrlf to false..."
git config core.autocrlf false

echo ""
echo "2. Resetting Git index to force re-evaluation..."
git reset

echo ""
echo "3. Re-adding all text files..."
find . -type f -not -path "./.git/*" -not -path "./.idea/*" \( -name "*.py" -o -name "*.txt" -o -name "*.md" -o -name "*.json" -o -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.xml" -o -name "*.sql" -o -name "*.ini" -o -name "*.cfg" -o -name "*.conf" \) -exec git add {} \;

echo ""
echo "4. Adding the 15 files without extensions..."
extensionless_files=(
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

for file in "${extensionless_files[@]}"; do
    if [ -f "$file" ]; then
        git add "$file"
    fi
done

echo ""
echo "5. Checking how many files are now staged..."
git diff --cached --name-only | wc -l
echo "files are now staged for commit"

echo ""
echo "6. Restoring core.autocrlf to input..."
git config core.autocrlf input

echo ""
echo "7. Sample of staged files:"
git diff --cached --name-only | head -10

echo ""
echo "Done! Now run:"
echo "git commit -m 'Convert all text files from CRLF to LF'"
echo "git push" 