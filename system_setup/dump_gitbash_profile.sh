#!/bin/bash

# Output destination
#OUTPUT_FILE=dump_gitbash_profile_work.txt
OUTPUT_FILE=dump_gitbash_profile_home.txt
HOME_DIR="$HOME"

# Start fresh
echo "Git Bash Profile Dump - $(date)" > "$OUTPUT_FILE"
echo "Home Directory: $HOME_DIR" >> "$OUTPUT_FILE"
echo "==========================================" >> "$OUTPUT_FILE"

# List all files in home directory
echo -e "\n📁 Files in ~/" >> "$OUTPUT_FILE"
ls -al "$HOME_DIR" >> "$OUTPUT_FILE"

# List of profile files to check
FILES=(.bashrc .bash_profile .profile .inputrc .git-prompt.sh .bash_aliases .condarc)

# Dump contents of each if it exists
for file in "${FILES[@]}"; do
  FULL="$HOME_DIR/$file"
  if [[ -f "$FULL" ]]; then
    echo -e "\n\n🔧 ==== Contents of $file ====\n" >> "$OUTPUT_FILE"
    cat "$FULL" >> "$OUTPUT_FILE"
  else
    echo -e "\n\n⛔ $file not found" >> "$OUTPUT_FILE"
  fi
done

echo -e "\n✅ Done. Output saved to $OUTPUT_FILE"
