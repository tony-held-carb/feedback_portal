#!/bin/bash

# ----------------------------------------------------------------------
# launch_with_screen.sh
#
# Launches a persistent background Flask or Gunicorn server using screen.
#
# USAGE:
#   ./launch_with_screen.sh                 # Defaults to flask mode
#   ./launch_with_screen.sh flask          # Flask dev mode
#   ./launch_with_screen.sh gunicorn       # Gunicorn production mode
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

echo "🔍 Launching '$MODE' in screen session '$SESSION_NAME'..."
echo "📁 Project root:      $PROJECT_ROOT"
echo "📁 Source directory:  $SOURCE_ROOT"
echo "📄 Log file:          $LOG_FILE"
echo "🐍 Conda environment: $CONDA_ENV"
echo "🌐 Host/Port:         $HOST:$PORT"
echo "🐞 Debug enabled:     $DEBUG"

mkdir -p "$LOG_DIR"

# Check that source dir exists
if [[ ! -d "$SOURCE_ROOT" ]]; then
  echo "❌ ERROR: Source directory not found: $SOURCE_ROOT"
  exit 1
fi

cd "$SOURCE_ROOT" || {
  echo "❌ ERROR: Failed to cd into $SOURCE_ROOT"
  exit 1
}

# Construct command
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

echo
echo "🚀 Command to run:"
echo "$CMD"
echo

# Wrap command for screen
SCREEN_CMD="bash -c \"$CMD | tee -a '$LOG_FILE'\""

echo "🖥️ Launching in screen with:"
echo "screen -S \"$SESSION_NAME\" -dm $SCREEN_CMD"
echo

# Actually run it
screen -S "$SESSION_NAME" -dm bash -c "$CMD | tee -a \"$LOG_FILE\""

# Verify
sleep 2
if screen -list | grep -q "$SESSION_NAME"; then
  echo "✅ Screen session '$SESSION_NAME' is running."
else
  echo "❌ Screen session did not start properly. Please check:"
  echo "  - Your conda environment"
  echo "  - Flask or Gunicorn installation"
  echo "  - The log file for error output: $LOG_FILE"
fi

echo
echo "To reattach:  screen -r $SESSION_NAME"
echo "To list all:  screen -ls"
echo "To stop:      ./stop_with_screen.sh"
