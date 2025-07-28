#!/bin/bash

# ----------------------------------------------------------------------
# portal_screen_stop.sh
#
# Stop a running screen session for the feedback portal.
#
# Usage:
#   cd ~/code/git_repos/feedback_portal/scripts
#   ./portal_screen_stop.sh                      # stops 'feedback_portal'
#   ./portal_screen_stop.sh custom_session_name  # stops custom session
#
# Arguments:
#   $1 - Optional: Screen session name (defaults to 'feedback_portal')
#
# Dependencies:
#   - Requires screen utility
#
# Notes:
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
