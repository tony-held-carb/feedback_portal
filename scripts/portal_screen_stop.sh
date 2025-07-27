#!/bin/bash

# ----------------------------------------------------------------------
# portal_screen_stop.sh — Stops a running screen session for the feedback portal.
#
# USAGE:
#   cd ~/code/git_repos/feedback_portal/scripts
#   ./portal_screen_stop.sh                      # stops 'feedback_portal'
#   ./portal_screen_stop.sh custom_session_name  # stops custom session
#
# ARGS:
#   $1 - Optional: Screen session name (defaults to 'feedback_portal')
#
# NOTES:
#   - You can verify it's stopped using:
#       screen -ls
#   - You may need to run chmod +x on this file to make it executable

# ----------------------------------------------------------------------

SESSION_NAME="${1:-feedback_portal}"

echo "🛑 Attempting to stop screen session: $SESSION_NAME"

if screen -list | grep -q "\.${SESSION_NAME}"; then
  screen -S "$SESSION_NAME" -X quit
  echo "✅ Stopped screen session: $SESSION_NAME"
else
  echo "⚠️  No active screen session found with name: $SESSION_NAME"
  echo "ℹ️  Use 'screen -ls' to list available sessions."
fi
