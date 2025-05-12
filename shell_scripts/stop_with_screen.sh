#!/bin/bash

# ----------------------------------------------------------------------
# stop_with_screen.sh
#
# Stops the named screen session used to run your Flask or Gunicorn app.
#
# NOTES:
#   - you may have to make this script executable with
#       chmod +x stop_with_screen.sh
#
# ----------------------------------------------------------------------

SESSION_NAME="feedback_portal"

if screen -list | grep -q "$SESSION_NAME"; then
  screen -S "$SESSION_NAME" -X quit
  echo "🛑 Stopped screen session: $SESSION_NAME"
else
  echo "ℹ️  No running screen session named: $SESSION_NAME"
fi
