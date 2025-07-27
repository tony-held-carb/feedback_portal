#!/bin/bash
# ----------------------------------------------------------------------
# portal_run.sh
#
# Prepare and launch the Flask feedback portal using screen.
# This script:
#   - Stops any existing screen session
#   - Launches the Flask app in a new screen session
#
# Usage:
#   # Use default repo path ($HOME/code/git_repos)
#   source ~/code/git_repos/feedback_portal/scripts/portal_run.sh
#
#   # Specify custom repo path
#   source ~/code/git_repos/feedback_portal/scripts/portal_run.sh /path/to/your/repos
#
#   # With alias (recommended)
#   alias portal_run='source ~/code/git_repos/feedback_portal/scripts/portal_run.sh'
#   portal_run                    # Use default path
#   portal_run /custom/repo/path  # Use custom path
#
# Arguments:
#   $1 - Optional: Repository base path (defaults to $HOME/code/git_repos)
#
# Dependencies:
#   - Requires shell_scripts/stop_with_screen.sh
#   - Requires shell_scripts/launch_with_screen.sh
# ----------------------------------------------------------------------

# Set repo_path from argument or use default
repo_path="${1:-$HOME/code/git_repos}"

echo "Stopping Screen if already running"
echo "📁 Git repo location: $repo_path"

# Validate that the repo path exists
if [ ! -d "$repo_path" ]; then
    echo "❌ Error: Repository path '$repo_path' does not exist"
    exit 1
fi

# Validate that feedback_portal directory exists
if [ ! -d "$repo_path/feedback_portal" ]; then
    echo "❌ Error: feedback_portal directory not found at '$repo_path/feedback_portal'"
    exit 1
fi

# Validate that required shell scripts exist
if [ ! -f "$repo_path/feedback_portal/scripts/portal_screen_stop.sh" ]; then
    echo "❌ Error: portal_screen_stop.sh not found at '$repo_path/feedback_portal/scripts/portal_screen_stop.sh'"
    exit 1
fi

if [ ! -f "$repo_path/feedback_portal/scripts/portal_screen_launch.sh" ]; then
    echo "❌ Error: portal_screen_launch.sh not found at '$repo_path/feedback_portal/scripts/portal_screen_launch.sh'"
    exit 1
fi

source "$repo_path/feedback_portal/scripts/portal_screen_stop.sh"
echo
source "$repo_path/feedback_portal/scripts/portal_screen_launch.sh"
