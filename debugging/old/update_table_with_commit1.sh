#!/bin/bash

echo "Updating table with commit 1 timestamps..."

# Get the commit hash
commit1=$(git log --oneline | grep "Initial pycharm CRLF" | head -1 | awk '{print $1}')
echo "Checking out commit: $commit1"

# Checkout the commit
git checkout $commit1 --quiet

# Create a temporary file to store commit 1 timestamps
> commit1_timestamps.txt

# Get timestamps for all files in the current table
while IFS= read -r line; do
    # Skip header lines
    if [[ "$line" == *"|----"* ]] || [[ "$line" == *"Table 1"* ]] || [[ "$line" == *"| ID |"* ]]; then
        continue
    fi
    
    # Extract file path from the line (column 2)
    file_path=$(echo "$line" | sed 's/|//g' | awk '{print $2}')
    
    if [ -n "$file_path" ] && [ -f "$file_path" ]; then
        mod_time=$(stat -c "%y" "$file_path" | cut -d' ' -f1,2 | sed 's/ / /')
        echo "$file_path|$mod_time" >> commit1_timestamps.txt
    fi
done < file_matches.txt

echo "Got timestamps for $(wc -l < commit1_timestamps.txt) files from commit 1"

# Go back to current commit
git checkout HEAD --quiet

# Create updated table
cat > file_matches_updated.txt << 'EOF'
# Table 1: Current files that match pattern (with commit 1 timestamps)

| ID | Full File Path | Current Modified Time | Commit 1 Modified Time |
|----|----------------|----------------------|------------------------|
EOF

# Update the table with both timestamps
id=1
while IFS= read -r line; do
    # Skip header lines
    if [[ "$line" == *"|----"* ]] || [[ "$line" == *"Table 1"* ]] || [[ "$line" == *"| ID |"* ]]; then
        continue
    fi
    
    # Extract file path from the line (column 2)
    file_path=$(echo "$line" | sed 's/|//g' | awk '{print $2}')
    
    if [ -n "$file_path" ] && [ -f "$file_path" ]; then
        current_time=$(stat -c "%y" "$file_path" | cut -d' ' -f1,2 | sed 's/ / /')
        commit1_time=$(grep "^$file_path|" commit1_timestamps.txt | cut -d'|' -f2)
        
        # If we don't have commit1_time, use "N/A"
        if [ -z "$commit1_time" ]; then
            commit1_time="N/A"
        fi
        
        printf "| %d | %s | %s | %s |\n" "$id" "$file_path" "$current_time" "$commit1_time" >> file_matches_updated.txt
        id=$((id + 1))
    fi
done < file_matches.txt

# Clean up
rm commit1_timestamps.txt

echo "Done! Updated table saved to file_matches_updated.txt"
echo "Total files in updated table: $((id - 1))" 