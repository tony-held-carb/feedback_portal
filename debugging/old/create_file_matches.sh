#!/bin/bash

echo "Creating file_matches.txt with Table 1..."

# Create the header
cat > file_matches.txt << 'EOF'
# Table 1: Current files that match pattern

| ID | Full File Path | Last Modified (as of 3:00pm) |
|----|----------------|------------------------------|
EOF

# Counter for ID
id=1

# Find all files with target extensions and get their modification times
find . -type f -not -path "./.git/*" -not -path "./.idea/*" \( -name "*.py" -o -name "*.txt" -o -name "*.md" -o -name "*.json" -o -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.xml" -o -name "*.sql" -o -name "*.ini" -o -name "*.cfg" -o -name "*.conf" \) | while IFS= read -r file; do
    if [ -f "$file" ]; then
        # Get modification time in readable format
        mod_time=$(stat -c "%y" "$file" | cut -d' ' -f1,2 | sed 's/ / /')
        # Output in table format with full path
        printf "| %d | %s | %s |\n" "$id" "$file" "$mod_time" >> file_matches.txt
        id=$((id + 1))
    fi
done

# Add the 15 files without extensions
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
        mod_time=$(stat -c "%y" "$file" | cut -d' ' -f1,2 | sed 's/ / /')
        printf "| %d | %s | %s |\n" "$id" "$file" "$mod_time" >> file_matches.txt
        id=$((id + 1))
    fi
done

echo "Done! Created file_matches.txt with Table 1"
echo "Total files in table: $((id - 1))" 