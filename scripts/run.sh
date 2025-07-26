#!/bin/bash
# -----------------------------------------------------------------------------
# run.sh
#
# A lightweight wrapper to execute any shell command, capture its output
# (both stdout and stderr), and save it to a timestamped diagnostics file
# in the `diagnostics/cursor/` directory (relative to this script).
#
# This is useful for logging the results of diagnostics or automation tasks
# in a consistent and traceable format.
#
# Time Behavior:
#   - Timestamps are recorded in UTC-7 to align with Pacific Daylight Time (PDT).
#   - The timestamp format includes milliseconds when supported, otherwise falls
#     back to appending the process ID (`$$`) for uniqueness.
#
# Output Format:
#   - The script creates a file named: output_<timestamp>.txt
#   - Includes a diagnostic header with:
#       - Command run
#       - Working directory
#       - UTC-7 timestamp
#   - Appends full stdout and stderr of the command.
#
# Echoed Completion Markers:
#   - OUTPUT_FILE=<path>    — Full path to the generated output file.
#   - EXIT_STATUS=<code>    — The numeric exit code from the command.
#   - COMMAND_DONE          — A static marker to help external tools parse completion.
#
# Usage:
#   run.sh <command> [args...]
#
# Examples:
#   run.sh ls -l /tmp
#   run.sh python my_script.py --flag
#
# Notes:
#   - Must be run using `source run` or made executable and placed in $PATH.
#   - The output directory will be created if it does not exist.
#   - Intended for EC2 or dev environments where tracking diagnostic runs is important.
# -----------------------------------------------------------------------------

if [ $# -eq 0 ]; then
  echo "Usage: $0 <command> [args...]"
  exit 1
fi

# Always write output to diagnostics/cursor (sibling to scripts directory)
OUTPUT_DIR="$(dirname "$0")/../diagnostics/cursor"
mkdir -p "$OUTPUT_DIR"

# Try to get milliseconds; fallback to PID if not supported
if date +"%N" | grep -q '[0-9]'; then
  TIMESTAMP=$(date -u -d "-7 hours" +"%Y_%m_%d_%H_%M_%S_%3N")
else
  TIMESTAMP=$(date -u -d "-7 hours" +"%Y_%m_%d_%H_%M_%S")_$$
fi
OUTPUT_FILE="$OUTPUT_DIR/output_${TIMESTAMP}.txt"

# Gather diagnostic info
CMD_RUN="$@"
PWD_RUN="$(pwd)"
DATE_RUN=$(date -u -d "-7 hours")

# Write header to output file
{
  echo "===== RUN SCRIPT DIAGNOSTICS ====="
  echo "Command: $CMD_RUN"
  echo "Working Directory: $PWD_RUN"
  echo "Timestamp: $DATE_RUN (UTC-7, Pacific Daylight Time)"
  echo "========================================"
  echo
} > "$OUTPUT_FILE"

# Run the command, appending stdout and stderr to the output file
"$@" >> "$OUTPUT_FILE" 2>&1
STATUS=$?

echo "OUTPUT_FILE=$OUTPUT_FILE"
echo "EXIT_STATUS=$STATUS"
echo "COMMAND_DONE"
exit $STATUS