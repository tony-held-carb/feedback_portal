#!/bin/bash

# ----------------------------------------------------------------------
# launch_with_screen.sh
#
# This launches a Flask or Gunicorn server in a detached screen session
# using the conda environment and logs all output to LOG_DIR="$PROJECT_ROOT/logs"
#
# USAGE:
#   cd ~/code/git_repos/feedback_portal/shell_scripts
#   ./launch_with_screen.sh                        # defaults to flask, 0.0.0.0:2113, debug=true
#   ./launch_with_screen.sh gunicorn               # gunicorn with defaults
#   ./launch_with_screen.sh flask 0.0.0.0 5000 true
#   ./launch_with_screen.sh gunicorn 127.0.0.1 8000 false
#
# ARGS:
#   $1 = MODE      (flask | gunicorn)       [default: flask]
#   $2 = HOST      (IP or hostname)         [default: 0.0.0.0]
#   $3 = PORT      (port number)            [default: 2113]
#   $4 = DEBUG     (true | false)           [default: true — flask only]
#
# NOTES:
#   - may need to run chmod +x on this file to make it executable
#   - if you wanted to run directly from the command line without shell closing issues:
#     - flask --app wsgi run --host=0.0.0.0 -p 2113 --debug &    # & runs in the background

# ----------------------------------------------------------------------

# Args with defaults
MODE="${1:-flask}"
HOST="${2:-0.0.0.0}"
PORT="${3:-2113}"
DEBUG="${4:-true}"

# Config
SESSION_NAME="feedback_portal"
CONDA_ENV="mini_conda_01"
REPOT_ROOT="$HOME/code/git_repos"
PROJECT_ROOT="$REPOT_ROOT/feedback_portal"
WSGI_DIR="$PROJECT_ROOT/source/production/arb"
PYTHON_ROOT="$PROJECT_ROOT/source/production"
LOG_DIR="$PROJECT_ROOT/logs"
TIMESTAMP=$(date +"%Y_%m_%d_%H_%M_%S")
LOG_FILE="$LOG_DIR/screen_${MODE}_$TIMESTAMP.log"

mkdir -p "$LOG_DIR"

echo "🔍 Launching $MODE in screen session '$SESSION_NAME'"
echo "📁 WSGI directory:  $WSGI_DIR"
echo "🐍 Conda env:       $CONDA_ENV"
echo "🌐 Host:Port        $HOST:$PORT"
echo "🐞 Debug mode:      $DEBUG"
echo "📄 Log file:        $LOG_FILE"

# Build command
if [[ "$MODE" == "flask" ]]; then
  CMD="cd $WSGI_DIR && conda activate $CONDA_ENV && PYTHONPATH=$PYTHON_ROOT flask --app wsgi run --host=$HOST --port=$PORT"
  [[ "$DEBUG" == "true" ]] && CMD="$CMD --debug"
elif [[ "$MODE" == "gunicorn" ]]; then
  CMD="cd $WSGI_DIR && conda activate $CONDA_ENV && PYTHONPATH=$PYTHON_ROOT gunicorn --bind $HOST:$PORT wsgi:app"
else
  echo "❌ Unknown mode: $MODE"
  exit 1
fi

echo
echo "🛠️ Final command:"
echo "bash -l -c \"$CMD >> $LOG_FILE 2>&1\""
echo

# Launch in screen
screen -S "$SESSION_NAME" -dm bash -l -c "$CMD >> \"$LOG_FILE\" 2>&1"

sleep 2
if screen -list | grep -q "$SESSION_NAME"; then
  echo "✅ Screen session '$SESSION_NAME' is running."
else
  echo "❌ Screen session failed to launch. Check the log:"
fi

echo "📄 Log file: $LOG_FILE"
echo
echo "To reattach:  screen -r $SESSION_NAME"
echo "To list all:  screen -ls"
echo "To stop:      screen -S $SESSION_NAME -X quit"
