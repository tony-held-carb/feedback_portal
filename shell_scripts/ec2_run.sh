#!/bin/bash

# ----------------------------------------------------------------------
# prep system for flask run
#
# Usage:
# source ~/code/git_repos/feedback_portal/shell_scripts/ec2_run.sh
# or just ec2_run if it is aliased with: alias ec2_run='source ~/code/git_repos/feedback_portal/shell_scripts/ec2_run.sh'

#
# Notes:
# ----------------------------------------------------------------------

echo "Running the Flask Feedback Portal"
set -x  # Start command tracing

source /home/theld/code/git_repos/feedback_portal/shell_scripts/stop_with_screen.sh
source /home/theld/code/git_repos/feedback_portal/shell_scripts/launch_with_screen.sh

set +x  # Stop command tracing
echo "Flask should be running"