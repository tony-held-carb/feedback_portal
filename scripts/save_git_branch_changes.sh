# Create a temporary directory for changed files
mkdir -p /tmp/refactor_36_changes

# Get list of changed files between main and refactor_36
git diff --name-only main..refactor_36 > /tmp/changed_files.txt

# Copy only the changed files to temp directory
while IFS= read -r file; do
    if [ -f "$file" ]; then
        # Create directory structure
        mkdir -p "/tmp/refactor_36_changes/$(dirname "$file")"
        # Copy file
        cp "$file" "/tmp/refactor_36_changes/$file"
    fi
done < /tmp/changed_files.txt

# Create zip archive
# cd /tmp
# zip -r refactor_36_changes.zip refactor_36_changes/

# # Move to your workspace
# mv refactor_36_changes.zip /home/tonyh/git_repos/feedback_portal/

# # Cleanup
# rm -rf /tmp/refactor_36_changes /tmp/changed_files.txt