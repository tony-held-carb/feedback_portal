#!/bin/bash
# run_batch_commands.sh: Run a batch of commands using command_wrapper.sh, with progress and error handling.

# List your commands here (one per array element)
COMMANDS=(
  "git status"
  "git branch -a"
  "ls -l"
)

NUM_COMMANDS=${#COMMANDS[@]}
OUTPUT_FILES=()
EXIT_STATUSES=()

for ((i=0; i<NUM_COMMANDS; i++)); do
  CMD="${COMMANDS[$i]}"
  echo "Executing command $((i+1)) of $NUM_COMMANDS: $CMD"

  # Call command_wrapper.sh and capture its output
  WRAPPER_OUTPUT=$(bash "$(dirname "$0")/command_wrapper.sh" ${CMD})
  STATUS=$?

  # Extract output file name from wrapper output
  OUTPUT_FILE=$(echo "$WRAPPER_OUTPUT" | grep '^OUTPUT_FILE=' | cut -d'=' -f2-)
  OUTPUT_FILES+=("$OUTPUT_FILE")
  EXIT_STATUSES+=("$STATUS")

  # Print wrapper output
  echo "$WRAPPER_OUTPUT"

  if [ $STATUS -ne 0 ]; then
    echo "ERROR: Command '$CMD' failed with exit status $STATUS. See $OUTPUT_FILE for details."
  fi

done

# echo "\n===== BATCH COMMAND SUMMARY ====="
# for ((i=0; i<NUM_COMMANDS; i++)); do
#   CMD="${COMMANDS[$i]}"
#   FILE="${OUTPUT_FILES[$i]}"
#   STATUS="${EXIT_STATUSES[$i]}"
#   echo "Command $((i+1)): $CMD"
#   echo "  Output File: $FILE"
#   echo "  Exit Status: $STATUS"
#   if [ "$STATUS" -ne 0 ]; then
#     echo "  ERROR: Command failed."
#   fi
#   echo

# done
echo "BATCH_COMMANDS_DONE" 