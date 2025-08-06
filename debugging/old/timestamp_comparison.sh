#!/bin/bash

echo "=== Timestamp Comparison Between Commits ===" > timestamp_analysis.txt
echo "Starting analysis..." >> timestamp_analysis.txt

# Get the commit hashes
commit1=$(git log --oneline | grep "Initial pycharm CRLF" | head -1 | awk '{print $1}')
commit2=$(git log --oneline | grep "converted many more files from crlf to lf" | head -1 | awk '{print $1}')

echo "Commit 1 (Initial pycharm): $commit1" >> timestamp_analysis.txt
echo "Commit 2 (converted many more): $commit2" >> timestamp_analysis.txt
echo "" >> timestamp_analysis.txt

echo "1. Creating list of files with target extensions..." >> timestamp_analysis.txt
find . -type f -not -path "./.git/*" -not -path "./.idea/*" \( -name "*.py" -o -name "*.txt" -o -name "*.md" -o -name "*.json" -o -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.xml" -o -name "*.sql" -o -name "*.ini" -o -name "*.cfg" -o -name "*.conf" \) > temp_files.txt

echo "Found $(wc -l < temp_files.txt) files to check" >> timestamp_analysis.txt
echo "" >> timestamp_analysis.txt

echo "2. Checking out commit 1 and getting timestamps..." >> timestamp_analysis.txt
git checkout $commit1 --quiet
echo "Getting timestamps for commit 1..." >> timestamp_analysis.txt
while IFS= read -r file; do
    if [ -f "$file" ]; then
        stat -c "%Y %n" "$file" >> timestamps_commit1.txt
    fi
done < temp_files.txt

echo "3. Checking out commit 2 and getting timestamps..." >> timestamp_analysis.txt
git checkout $commit2 --quiet
echo "Getting timestamps for commit 2..." >> timestamp_analysis.txt
while IFS= read -r file; do
    if [ -f "$file" ]; then
        stat -c "%Y %n" "$file" >> timestamps_commit2.txt
    fi
done < temp_files.txt

echo "4. Comparing timestamps..." >> timestamp_analysis.txt
echo "Files with different timestamps (modified between commits):" >> timestamp_analysis.txt
while IFS= read -r file; do
    if [ -f "$file" ]; then
        ts1=$(grep "$file" timestamps_commit1.txt | awk '{print $1}')
        ts2=$(grep "$file" timestamps_commit2.txt | awk '{print $1}')
        if [ "$ts1" != "$ts2" ] && [ -n "$ts1" ] && [ -n "$ts2" ]; then
            echo "$file" >> modified_files.txt
        fi
    fi
done < temp_files.txt

echo "" >> timestamp_analysis.txt
echo "5. Results:" >> timestamp_analysis.txt
echo "Total files checked: $(wc -l < temp_files.txt)" >> timestamp_analysis.txt
echo "Files with different timestamps: $(wc -l < modified_files.txt)" >> timestamp_analysis.txt

echo "" >> timestamp_analysis.txt
echo "6. Sample of modified files:" >> timestamp_analysis.txt
head -10 modified_files.txt >> timestamp_analysis.txt

echo "" >> timestamp_analysis.txt
echo "7. Cleaning up..." >> timestamp_analysis.txt
rm temp_files.txt timestamps_commit1.txt timestamps_commit2.txt

echo "Done! Check timestamp_analysis.txt for results and modified_files.txt for the list of modified files." 