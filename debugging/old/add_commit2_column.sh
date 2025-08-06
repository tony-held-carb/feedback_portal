#!/bin/bash

echo "Adding commit 2 timestamps to the table..."

# Get the commit hash
commit2=$(git log --oneline | grep "converted many more files from crlf to lf" | head -1 | awk '{print $1}')
echo "Checking out commit: $commit2"

# Checkout the commit
git checkout $commit2 --quiet

echo "Getting timestamps from commit 2..."
# Create a simple list of files and their timestamps
grep "|" file_matches_updated.txt | grep -v "|----" | grep -v "Table 1" | grep -v "| ID |" | while IFS= read -r line; do
    file_path=$(echo "$line" | sed 's/|//g' | awk '{print $2}')
    if [ -n "$file_path" ] && [ -f "$file_path" ]; then
        mod_time=$(stat -c "%y" "$file_path" | cut -d' ' -f1,2 | sed 's/ / /')
        echo "$file_path|$mod_time" >> commit2_times.txt
        echo -n "."  # Progress indicator
    fi
done

echo ""
echo "Got timestamps for $(wc -l < commit2_times.txt) files"

# Go back to current commit (branch head)
echo "Returning to branch head..."
git checkout HEAD --quiet

echo "Creating final table with all timestamps..."
# Create final table with all timestamps
cat > file_matches_final.txt << 'EOF'
# Table 1: Current files that match pattern (with all commit timestamps)

| ID | Full File Path | Current Modified Time | Commit 1 Modified Time | Commit 2 Modified Time |
|----|----------------|----------------------|------------------------|------------------------|
EOF

# Process each line and add commit 2 timestamp
id=1
while IFS= read -r line; do
    if [[ "$line" == *"|"* ]] && [[ "$line" != *"|----"* ]] && [[ "$line" != *"Table 1"* ]] && [[ "$line" != *"| ID |"* ]]; then
        file_path=$(echo "$line" | sed 's/|//g' | awk '{print $2}')
        current_time=$(echo "$line" | sed 's/|//g' | awk '{print $3, $4}')
        commit1_time=$(echo "$line" | sed 's/|//g' | awk '{print $5, $6}')
        
        if [ -n "$file_path" ]; then
            commit2_time=$(grep "^$file_path|" commit2_times.txt | cut -d'|' -f2)
            if [ -z "$commit2_time" ]; then
                commit2_time="N/A"
            fi
            printf "| %d | %s | %s | %s | %s |\n" "$id" "$file_path" "$current_time" "$commit1_time" "$commit2_time" >> file_matches_final.txt
            id=$((id + 1))
        fi
    fi
done < file_matches_updated.txt

# Clean up
rm commit2_times.txt

echo "Done! Final table saved to file_matches_final.txt"
echo "Total files in final table: $((id - 1))"
echo "Successfully returned to branch head" 