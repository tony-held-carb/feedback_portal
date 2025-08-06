#!/bin/bash
echo "=== Ultra Fast File Finder ==="
echo "Finding files with specified extensions..."

# Create output file with header
cat > file_extension_matches.txt << 'EOF'
# Files matching specified extensions in feedback_portal
# Excluding .git and .idea directories
EOF

# Use a single command with all wildcards - this is much faster than loops
# Find all files with specified extensions in one go
find . -type f \( -name "*.py" -o -name "*.txt" -o -name "*.md" -o -name "*.json" -o -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.xml" -o -name "*.sql" -o -name "*.ini" -o -name "*.cfg" -o -name "*.conf" \) -not -path "./.git/*" -not -path "./.idea/*" | sed 's|^\./||' >> file_extension_matches.txt

# Count total files
total_files=$(wc -l < file_extension_matches.txt)
echo "Total files found: $total_files"
echo "Results saved to file_extension_matches.txt"

# Show first 10 files as sample
echo ""
echo "=== Sample of found files ==="
head -10 file_extension_matches.txt 