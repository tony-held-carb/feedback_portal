#!/bin/bash
# -----------------------------------------------------------------------------
# portal_prep.sh
#
# Prepare the system for running the Flask feedback portal.
# This script:
#   - Cleans log and upload files
#   - Fetches remote branches
#   - Checks out the most recently updated remote branch
#   - Pulls the latest commits
#
# Usage:
#   # Use default repo path ($HOME/code/git_repos)
#   source ~/code/git_repos/feedback_portal/scripts/portal_prep.sh
#
#   # Specify custom repo path
#   source ~/code/git_repos/feedback_portal/scripts/portal_prep.sh /path/to/your/repos
#
#   # With alias (recommended)
#   alias portal_prep='source ~/code/git_repos/feedback_portal/scripts/portal_prep.sh'
#   portal_prep                    # Use default path
#   portal_prep /custom/repo/path  # Use custom path
#
# Arguments:
#   $1 - Optional: Repository base path (defaults to $HOME/code/git_repos)
#
# Dependencies:
#   - Requires 'checkout_latest_remote_branch' to be defined in your shell
#     (e.g., in .bashrc or .bash_profile)
# -----------------------------------------------------------------------------

# Set repo_path from argument or use default
repo_path="${1:-$HOME/code/git_repos}"

echo "🛠️  Prepping system for Flask run"
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

set -x  # Start command tracing

cd "$repo_path/feedback_portal"

# Clean previous logs and uploads
rm "$repo_path/feedback_portal/logs"/*.log
rm "$repo_path/feedback_portal/portal_uploads"/*.json
rm "$repo_path/feedback_portal/portal_uploads"/*.xlsx

# Show and sync remote branches
git branch -a
git fetch --all --prune
git branch -a

# Check out the most recently updated remote branch
echo "🌿 Checking out the most recent branch updated on GitHub"
checkout_latest_remote_branch --force-create

# Pull latest changes and show status
git pull
git status

set +x  # Stop command tracing
echo "✅ System prep complete"
