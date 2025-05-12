#!/bin/bash

# ----------------------------------------------------------------------
# launch_with_screen.sh
#
# Launches a persistent background Flask or Gunicorn server using screen.
#
# USAGE:
#   ./launch_with_screen.sh                # Defaults to flask mode
#   ./launch_with_screen.sh flask          # Flask dev mode
#   ./launch_with_screen.sh gunicorn       # Gunicorn production mode
#
# BEHAVIOR:
#   - Creates a detached screen session named "feedback_portal"
#   - Logs stdout/stderr to a timestamped file in ./logs/
#   - Uses the conda environment: mini_conda_01
#
# MANAGING THE SCREEN SESSION:
#   - List all sessions:     screen -ls
#   - Reattach to session:   screen -r feedback_portal
#   - Detach (if attached):  Ctrl-A then D (only needed if manually attached)
#   - Kill the session:      ./stop_with_screen.sh
#
# CONFIGURATION:
#   - You can edit HOST, PORT, and DEBUG variables below.
#   - Flask mode honors --debug if DEBUG=true
#   - Gunicorn mode ignores DEBUG (intended for production)
#
# DEFAULTS:
#   - Mode:    flask
#   - Host:    0.0.0.0
#   - Port:    2113
#   - Debug:   true
# ----------------------------------------------------------------------

SESSION_NAME="feedback_portal"
MODE="${1:-flask}"  # default to 'flask' mode if not specified

# --- Configurable options ---
CONDA_ENV="mini_conda_01"
CONDA_BASE="$HOME/miniconda3"
HOST="0.0.0.0"
PORT="2113"
DEBUG="true"
# -----------------------------

PROJECT_ROOT="$HOME/code/git_repos/feedback_portal"
SOURCE_ROOT="$PROJECT_ROOT/source/production"
LOG_DIR="$PROJECT_ROOT/logs"
TIMESTAMP=$(date +"%Y_%m_%d_%H_%M_%S")
LOG_FILE="$LOG_DIR/${SESSION_NAME}_${MODE}_$TIMESTAMP.log"

mkdir -p "$LOG_DIR"

cd "$SOURCE_ROOT" || exit 1

# Construct command for screen session
if [[ "$MODE" == "flask" ]]; then
  CMD="source $CONDA_BASE/etc/profile.d/conda.sh && conda activate $CONDA_ENV && flask --app wsgi run --host=$HOST --port=$PORT"
  if [[ "$DEBUG" == "true" ]]; then
    CMD="$CMD --debug"
  fi
elif [[ "$MODE" == "gunicorn" ]]; then
  CMD="source $CONDA_BASE/etc/profile.d/conda.sh && conda activate $CONDA_ENV && gunicorn --bind $HOST:$PORT wsgi:app"
else
  echo "❌ Unknown mode: $MODE. Use 'flask' or 'gunicorn'."
  exit 1
fi

# Launch in detached screen session
screen -S "$SESSION_NAME" -dm bash -c "$CMD | tee -a \"$LOG_FILE\""

echo "✅ Started '$MODE' server in detached screen session: $SESSION_NAME"
echo "   Logging to: $LOG_FILE"
echo
echo "To reattach:  screen -r $SESSION_NAME"
echo "To list all:  screen -ls"
echo "To stop:      ./stop_with_screen.sh"
