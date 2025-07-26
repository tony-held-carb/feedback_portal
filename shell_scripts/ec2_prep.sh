#!/bin/bash
# -----------------------------------------------------------------------------
# ec2_prep.sh
#
# Prepare the EC2 system for running the Flask feedback portal.
# This script:
#   - Cleans log and upload files
#   - Fetches remote branches
#   - Checks out the most recently updated remote branch
#   - Pulls the latest commits
#
# Usage:
#   source ~/code/git_repos/feedback_portal/scripts/ec2_prep.sh
#
# Aliased usage (recommended):
#   alias ec2_prep='source ~/code/git_repos/feedback_portal/scripts/ec2_prep.sh'
#
# Dependencies:
#   - Requires 'checkout_latest_remote_branch' to be defined in your shell
#     (e.g., in .bashrc or .bash_profile)
# -----------------------------------------------------------------------------

repo="$HOME/code/git_repos"

echo "🛠️  Prepping system for Flask run"
echo "📁 Git repo location: $repo"

set -x  # Start command tracing

cd "$repo/feedback_portal"

# Clean previous logs and uploads
rm "$repo/feedback_portal/logs"/*.log
rm "$repo/feedback_portal/portal_uploads"/*.json
rm "$repo/feedback_portal/portal_uploads"/*.xlsx

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
