#!/bin/bash
echo "=== Fast File Finder for Specific Extensions ==="
echo "Finding files with specified extensions..."

# Create output file with header
cat > file_extension_matches.txt << 'EOF'
# Files matching specified extensions in feedback_portal
# Excluding .git and .idea directories
EOF

# Use globbing to find files quickly - this is much faster than find
# We'll use multiple glob patterns to catch all extensions
for ext in py txt md json html css js sh yml yaml xml sql ini cfg conf; do
    # Use globstar to search recursively, but exclude .git and .idea
    for file in **/*.$ext; do
        # Check if file exists (glob might not match anything)
        if [[ -f "$file" ]]; then
            # Skip files in .git and .idea directories
            if [[ "$file" != .git/* && "$file" != .idea/* ]]; then
                echo "$file" >> file_extension_matches.txt
            fi
        fi
    done
done

# Sort and remove duplicates
sort -u file_extension_matches.txt > temp_sorted.txt
mv temp_sorted.txt file_extension_matches.txt

# Count total files
total_files=$(wc -l < file_extension_matches.txt)
echo "Total files found: $total_files"
echo "Results saved to file_extension_matches.txt"

# Show first 10 files as sample
echo ""
echo "=== Sample of found files ==="
head -10 file_extension_matches.txt 