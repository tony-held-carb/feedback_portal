#!/bin/bash

# ----------------------------------------------------------------------
# prep system for flask run
#
# Usage:
# source ~/code/git_repos/feedback_portal/shell_scripts/ec2_prep.sh
# or just ec2_prep if it is aliased with: alias ec2_prep='source ~/code/git_repos/feedback_portal/shell_scripts/ec2_prep.sh'
# ----------------------------------------------------------------------

echo "Prepping system for flask run"
set -x  # Start command tracing

cd /home/theld/code/git_repos/feedback_portal
rm /home/theld/code/git_repos/feedback_portal/logs/*.log
rm /home/theld/code/git_repos/feedback_portal/portal_uploads/*.json
rm /home/theld/code/git_repos/feedback_portal/portal_uploads/*.xlsx
git branch -a
git fetch --all --prune
git branch -a
echo "checking out the most recent branch updated on github"
git for-each-ref --sort=-committerdate --format='%(refname:short)' refs/remotes/origin/ | grep -v '^origin/HEAD$' | head -n 1 | xargs -I{} git checkout --track {}
git pull
git status


set +x  # Stop command tracing
echo "System prep complete"
