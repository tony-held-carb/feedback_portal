#!/bin/bash

# ----------------------------------------------------------------------
# portal_screen_launch.sh
#
# Launch a Flask or Gunicorn server in a detached screen session
# using the conda environment and logs all output to LOG_DIR="$PROJECT_ROOT/logs"
#
# Usage:
#   cd ~/code/git_repos/feedback_portal/scripts
#   ./portal_screen_launch.sh                        # defaults to flask, 0.0.0.0:2113, debug=true
#   ./portal_screen_launch.sh gunicorn               # gunicorn with defaults
#   ./portal_screen_launch.sh flask 0.0.0.0 5000 true
#   ./portal_screen_launch.sh gunicorn 127.0.0.1 8000 false
#
# Arguments:
#   $1 = MODE      (flask | gunicorn)       [default: flask]
#   $2 = HOST      (IP or hostname)         [default: 0.0.0.0]
#   $3 = PORT      (port number)            [default: 2113]
#   $4 = DEBUG     (true | false)           [default: true — flask only]
# ----------------------------------------------------------------------

# Args with defaults
MODE="${1:-flask}"
HOST="${2:-0.0.0.0}"
PORT="${3:-2113}"
DEBUG="${4:-true}"

# Config
SESSION_NAME="feedback_portal"
CONDA_ENV="mini_conda_02"
REPO_ROOT="$HOME/code/git_repos"
PROJECT_ROOT="$REPO_ROOT/feedback_portal"
PRODUCTION_DIR="$PROJECT_ROOT/source/production"
LOG_DIR="$PROJECT_ROOT/logs"
TIMESTAMP=$(date +"%Y_%m_%d_%H_%M_%S")
LOG_FILE="$LOG_DIR/screen_${MODE}_$TIMESTAMP.log"

echo "🔍 Launching $MODE in screen session '$SESSION_NAME'"
echo "📁 Production directory: $PRODUCTION_DIR"
echo "🐍 Conda env: $CONDA_ENV"
echo "🌐 Host:Port $HOST:$PORT"
echo "🐞 Debug mode: $DEBUG"
echo "📄 Log file: $LOG_FILE"
echo

# Step 1: Check if production directory exists
echo "Step 1: Checking production directory..."
if [[ ! -d "$PRODUCTION_DIR" ]]; then
  echo "❌ Production directory does not exist: $PRODUCTION_DIR"
  exit 1
fi
echo "✅ Production directory exists"

# Step 2: Create log directory
echo "Step 2: Creating log directory..."
mkdir -p "$LOG_DIR"
if [[ ! -d "$LOG_DIR" ]]; then
  echo "❌ Failed to create log directory: $LOG_DIR"
  exit 1
fi
echo "✅ Log directory ready"

# Step 3: Kill existing screen session if it exists
echo "Step 3: Checking for existing screen session..."
if screen -list | grep -q "$SESSION_NAME"; then
  echo "🔄 Killing existing screen session '$SESSION_NAME'"
  screen -S "$SESSION_NAME" -X quit
  sleep 1
  echo "✅ Existing session killed"
else
  echo "✅ No existing session found"
fi

# Step 4: Build the command based on mode
echo "Step 4: Building launch command..."
if [[ "$MODE" == "flask" ]]; then
  LAUNCH_CMD="flask --app arb/wsgi run --host=$HOST --port=$PORT"
  [[ "$DEBUG" == "true" ]] && LAUNCH_CMD="$LAUNCH_CMD --debug"
elif [[ "$MODE" == "gunicorn" ]]; then
  LAUNCH_CMD="gunicorn --bind $HOST:$PORT arb.wsgi:app"
else
  echo "❌ Unknown mode: $MODE"
  exit 1
fi
echo "✅ Command: $LAUNCH_CMD"

# Step 5: Launch screen session with direct commands
echo "Step 5: Launching screen session..."
SCREEN_CMD="cd $PRODUCTION_DIR && conda activate $CONDA_ENV && $LAUNCH_CMD >> $LOG_FILE 2>&1"
echo "SCREEN_CMD: $SCREEN_CMD"

screen -S "$SESSION_NAME" -dm bash -c "$SCREEN_CMD"
SCREEN_EXIT_CODE=$?

if [[ $SCREEN_EXIT_CODE -ne 0 ]]; then
  echo "❌ Screen command failed with exit code: $SCREEN_EXIT_CODE"
  exit 1
fi
echo "✅ Screen session launched"

# Step 6: Verify session is running
echo "Step 6: Verifying session is running..."
sleep 2
if screen -list | grep -q "$SESSION_NAME"; then
  echo "✅ Screen session '$SESSION_NAME' is running"
  echo "📄 Log file: $LOG_FILE"
  echo
  echo "To reattach:  screen -r $SESSION_NAME"
  echo "To list all:  screen -ls"
  echo "To stop:      screen -S $SESSION_NAME -X quit"
else
  echo "❌ Screen session failed to start"
  echo "📄 Log file: $LOG_FILE"
  echo
  echo "🔍 Debugging steps:"
  echo "1. Check if log file was created:"
  echo "   ls -la $LOG_FILE"
  echo "2. If log file exists, check contents:"
  echo "   cat $LOG_FILE"
  echo "3. Check screen sessions:"
  echo "   screen -ls"
  echo "4. Test command manually:"
  echo "   cd $PRODUCTION_DIR && conda activate $CONDA_ENV && $LAUNCH_CMD"
fi 