#!/bin/bash
# -----------------------------------------------------------------------------
# run_all.sh
#
# Executes a batch of shell commands listed in a user-defined file, using the
# run.sh script to log output and capture diagnostics for each command.
#
# Each command's stdout/stderr is saved to a timestamped log file under:
#   debugging/
# The wrapper script (run.sh) also prints completion markers, including:
#   - OUTPUT_FILE
#   - EXIT_STATUS
#   - COMMAND_DONE
#
# This batch runner adds:
#   - Progress indicators (e.g. "Executing command 2 of 5")
#   - Error handling (non-zero exit status warnings)
#   - Batch summary markers
#
# USAGE:
#   1. Create or edit 'run_all_commands.txt' in the same directory as this script.
#      - One command per line
#      - Blank lines and lines beginning with # are ignored
#
#   2. Run the batch runner:
#        bash path/to/run_all.sh
#      Or, if aliased:
#        run_all
#
#   Example 'run_all_commands.txt':
#     # Build reports
#     python build_report.py
#
#     # Compress output
#     tar -czf report.tar.gz output/
#
#   Note: 'run_all_commands.txt' is gitignored so each user can customize it freely.
#
# OUTPUT:
#   - Prints real-time progress and results for each command
#   - Summarizes any failed commands
#   - Logs are saved to diagnostics/cursor/output_<timestamp>.txt
#
# DEPENDENCIES:
#   - run.sh must be located in the same directory as this script
#   - debugging/ must be writable or creatable from the current user
#
# END MARKER:
#   - Upon successful completion of the loop, the script prints:
#       BATCH_COMMANDS_DONE
# -----------------------------------------------------------------------------

COMMANDS_FILE="$(dirname "$0")/run_all_commands.txt"

if [ ! -f "$COMMANDS_FILE" ]; then
  echo "Commands file not found: $COMMANDS_FILE"
  echo "Create this file and add one command per line."
  exit 1
fi

# Read commands from the file, ignoring empty lines and comments
mapfile -t COMMANDS < <(grep -vE '^\s*#|^\s*$' "$COMMANDS_FILE")

NUM_COMMANDS=${#COMMANDS[@]}
OUTPUT_FILES=()
EXIT_STATUSES=()
FAILED_COMMANDS=()

for ((i=0; i<NUM_COMMANDS; i++)); do
  CMD="${COMMANDS[$i]}"
  echo
  echo "🟢 Executing command $((i+1)) of $NUM_COMMANDS:"
  echo "    $CMD"

  # Use eval to properly handle quoted args and spaces
  WRAPPER_OUTPUT=$(eval bash "$(dirname "$0")/run.sh" "$CMD")
  STATUS=$?

  # Extract output file name from wrapper output
  OUTPUT_FILE=$(echo "$WRAPPER_OUTPUT" | grep '^OUTPUT_FILE=' | cut -d'=' -f2-)
  OUTPUT_FILES+=("$OUTPUT_FILE")
  EXIT_STATUSES+=("$STATUS")

  # Print wrapper output
  echo "$WRAPPER_OUTPUT"

  if [ $STATUS -ne 0 ]; then
    echo "❌ ERROR: Command failed with exit status $STATUS"
    echo "   ↳ Log: $OUTPUT_FILE"
    FAILED_COMMANDS+=("$CMD")
  else
    echo "✅ Success"
    echo "   ↳ Log: $OUTPUT_FILE"
  fi
done

echo
echo "📋 Batch Summary:"
for ((i=0; i<NUM_COMMANDS; i++)); do
  CMD="${COMMANDS[$i]}"
  STATUS="${EXIT_STATUSES[$i]}"
  FILE="${OUTPUT_FILES[$i]}"
  STATUS_MSG=$( [ "$STATUS" -eq 0 ] && echo "Success" || echo "Failed ")
  printf "  [%02d/%02d] %-7s → %s\n" "$((i+1))" "$NUM_COMMANDS" "$STATUS_MSG" "$FILE"
done

echo
if [ ${#FAILED_COMMANDS[@]} -eq 0 ]; then
  echo "✅ All commands completed successfully."
  echo "BATCH_COMMANDS_DONE"
  exit 0
else
  echo "⚠️  ${#FAILED_COMMANDS[@]} command(s) failed:"
  for cmd in "${FAILED_COMMANDS[@]}"; do
    echo "   - $cmd"
  done
  exit 1
fi
