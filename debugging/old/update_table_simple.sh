#!/bin/bash

echo "Updating table with commit 1 timestamps (simplified)..."

# Get the commit hash
commit1=$(git log --oneline | grep "Initial pycharm CRLF" | head -1 | awk '{print $1}')
echo "Checking out commit: $commit1"

# Checkout the commit
git checkout $commit1 --quiet

echo "Getting timestamps from commit 1..."
# Create a simple list of files and their timestamps
grep "|" file_matches.txt | grep -v "|----" | grep -v "Table 1" | grep -v "| ID |" | while IFS= read -r line; do
    file_path=$(echo "$line" | sed 's/|//g' | awk '{print $2}')
    if [ -n "$file_path" ] && [ -f "$file_path" ]; then
        mod_time=$(stat -c "%y" "$file_path" | cut -d' ' -f1,2 | sed 's/ / /')
        echo "$file_path|$mod_time" >> commit1_times.txt
        echo -n "."  # Progress indicator
    fi
done

echo ""
echo "Got timestamps for $(wc -l < commit1_times.txt) files"

# Go back to current commit
git checkout HEAD --quiet

echo "Creating updated table..."
# Create updated table
cat > file_matches_updated.txt << 'EOF'
# Table 1: Current files that match pattern (with commit 1 timestamps)

| ID | Full File Path | Current Modified Time | Commit 1 Modified Time |
|----|----------------|----------------------|------------------------|
EOF

# Process each line and add commit 1 timestamp
id=1
while IFS= read -r line; do
    if [[ "$line" == *"|"* ]] && [[ "$line" != *"|----"* ]] && [[ "$line" != *"Table 1"* ]] && [[ "$line" != *"| ID |"* ]]; then
        file_path=$(echo "$line" | sed 's/|//g' | awk '{print $2}')
        current_time=$(echo "$line" | sed 's/|//g' | awk '{print $3, $4}')
        
        if [ -n "$file_path" ]; then
            commit1_time=$(grep "^$file_path|" commit1_times.txt | cut -d'|' -f2)
            if [ -z "$commit1_time" ]; then
                commit1_time="N/A"
            fi
            printf "| %d | %s | %s | %s |\n" "$id" "$file_path" "$current_time" "$commit1_time" >> file_matches_updated.txt
            id=$((id + 1))
        fi
    fi
done < file_matches.txt

# Clean up
rm commit1_times.txt

echo "Done! Updated table saved to file_matches_updated.txt"
echo "Total files in updated table: $((id - 1))" 