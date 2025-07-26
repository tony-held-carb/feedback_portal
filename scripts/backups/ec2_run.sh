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

echo "Stopping Screen if already running"
source /home/theld/code/git_repos/feedback_portal/shell_scripts/stop_with_screen.sh

echo
source /home/theld/code/git_repos/feedback_portal/shell_scripts/launch_with_screen.sh
