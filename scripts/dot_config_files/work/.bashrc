echo ">>> .bashrc loaded at $(date) <<<"

# Custom prompt
PS1='$(basename "$PWD")\$ '

# Environment variables common to all environments
export PATH=$PATH:$HOME/bin

# Use the machine name to customize different environments
echo "MACHINE_NAME=$MACHINE_NAME"

case "$MACHINE_NAME" in
  "TONY_WORK")
    CONDA_HOME="/c/Users/theld/AppData/Local/miniconda3"
    export portal="/c/tony_local/pycharm/feedback_portal"
    ;;
  "TONY_HOME")
    CONDA_HOME="/c/Users/tonyh/miniconda3"
    export portal="/d/local/cursor/feedback_portal"

    # --- BEGIN: Optional settings to try and reduce Cursor hanging ---
    export GIT_PAGER=cat
    export PAGER=cat
    export LESS=F
#    export TERM=dumb
    export GIT_TERMINAL_PROMPT=0
    # --- END: Optional settings to try and reduce Cursor hanging ---
    ;;
  "TONY_EC2")
    echo "EC2 not set up yet"
    ;;
  *)
    echo "⚠️  Unknown MACHINE_NAME='$MACHINE_NAME'."
    ;;
esac

# Derived Environmental Variables
export prod="$portal/source/production"
export PATH="$PATH:$portal/diagnostics/cursor"

# Additional Settings
export TERM=xterm-256color

# initialize conda and activate default environment
if [[ -n "$CONDA_HOME" && -f "$CONDA_HOME/Scripts/conda.exe" ]]; then
  # echo ">>> .bashrc found conda.exe at $(date) <<<"
  eval "$("$CONDA_HOME/Scripts/conda.exe" 'shell.bash' 'hook')"
  # echo ">>> .bashrc finished conda eval at $(date) <<<"
else
  echo ">>> .bashrc did NOT find conda.exe at expected location: $CONDA_HOME/Scripts/conda.exe <<<"
fi
conda activate mini_conda_02

# Aliases
alias ll='ls -la --color=auto'
alias gs='git status'
alias py='python'
alias run="$portal/scripts/run"
alias run_all="$portal/scripts/run_all"

# start in the portal directory
cd $portal

# Diagnostics
echo -e "\nportal=$portal (your pwd)"
echo "prod=$prod"
echo 'to run flask: cd $prod, flask --app arb/wsgi run --debug --no-reload'


# Custom Functions

# -------------------------------------------------------------------
# copy_to_clipboard() — Cross-platform clipboard copy utility
#
# This function attempts to copy piped input to the system clipboard
# across various platforms. It silently does nothing if no supported
# clipboard tool is found.
#
# SUPPORTED ENGINES (in order of priority):
#   - Windows:   clip
#   - macOS:     pbcopy
#   - Linux:     xclip (must be installed)
#   - WSL:       clip.exe
#
# USAGE:
#   echo "text" | copy_to_clipboard
#   some_command_output | copy_to_clipboard
#
# RETURNS:
#   0 if copy was attempted, 1 if silently skipped (no tool found)
#
# NOTES:
# - If xclip is used, it requires X11 to be running.
# - This function is silent by design (no warnings on failure).
# -------------------------------------------------------------------

copy_to_clipboard() {

  if command -v clip &>/dev/null; then
    tr -d '\n' | clip
  elif command -v pbcopy &>/dev/null; then
    tr -d '\n' | pbcopy
  elif command -v xclip &>/dev/null; then
    tr -d '\n' | xclip -selection clipboard
  elif command -v clip.exe &>/dev/null; then
    tr -d '\n' | clip.exe
  else
    return 1  # Fail silently
  fi
}


# -------------------------------------------------------------------
# wpath() — Convert a Windows-style path to a Git Bash–compatible path
#
# This function takes a single Windows-style path as an argument and
# prints both the original Windows path and its equivalent Unix-style
# path for use in Git Bash.
#
# It uses `cygpath -u` internally to perform the conversion.
#
# USAGE:
#   wpath 'C:\Users\tonyh\Desktop\file.txt'
#   wpath 'D:\local\cursor\feedback_portal\scripts\compare_yml.txt'
#
# OUTPUT:
#   windows path: 'D:\local\cursor\feedback_portal\scripts\compare_yml.txt'
#   linux path:   '/d/local/cursor/feedback_portal/scripts/compare_yml.txt'
#
# LIMITATIONS:
# - Requires Git Bash with `cygpath` available (default in Git for Windows).
# - Must pass the path as a single argument (quoted if it contains spaces or backslashes).
# - Only converts string literals — does not validate whether the path exists.
# - Accepts only one argument. Extra arguments will be ignored.
# -------------------------------------------------------------------

wpath() {
  if [ -z "$1" ]; then
    echo "Usage: wpath 'C:\\path\\to\\file_or_directory'"
    return 1
  fi

  local win_path="$1"
  local unix_path
  unix_path=$(cygpath -u "$win_path" 2>/dev/null)

  if [ -z "$unix_path" ]; then
    echo "Error: Could not convert path '$win_path'"
    return 1
  fi

  echo "windows path: '$win_path'"
  echo "linux path:   '$unix_path'"
  echo "$unix_path" | copy_to_clipboard
}

# -------------------------------------------------------------------
# lpath() — Convert a Git Bash–style linux path to a Windows-style path
#
# This function takes a single Unix-style linux path as an argument and
# prints both the original Unix-style path and its equivalent
# Windows-style path.
#
# It uses `cygpath -w` internally to perform the conversion.
#
# USAGE:
#   lpath '/d/local/cursor/feedback_portal/scripts/compare_yml.txt'
#
# OUTPUT:
#   linux path:   '/d/local/cursor/feedback_portal/scripts/compare_yml.txt'
#   windows path: 'D:\local\cursor\feedback_portal\scripts\compare_yml.txt'
#
# LIMITATIONS:
# - Requires Git Bash with `cygpath` (included in Git for Windows).
# - Must pass a single argument (quoted if it contains spaces).
# - Does not validate whether the path exists.
# -------------------------------------------------------------------

lpath() {
  if [ -z "$1" ]; then
    echo "Usage: lpath '/c/path/to/file_or_directory'"
    return 1
  fi

  local unix_path="$1"
  local win_path
  win_path=$(cygpath -w "$unix_path" 2>/dev/null)

  if [ -z "$win_path" ]; then
    echo "Error: Could not convert path '$unix_path'"
    return 1
  fi

  echo "linux path:   '$unix_path'"
  echo "windows path: '$win_path'"
  echo "$win_path" | copy_to_clipboard
}

# -------------------------------------------------------------------
# path() — Route to wpath or lpath depending on slash type
#
# Behavior:
# - If the argument contains a backslash (\), treat it as a Windows path
#   and call wpath().
# - Else if it contains a forward slash (/), treat it as a Linux-style
#   path and call lpath().
# - Else (no slashes), assume the path is the same in both styles.
#   Print both and copy to clipboard.
#
# USAGE:
#   path 'C:\Users\tonyh\Desktop\file.txt'     → calls wpath
#   path '/c/Users/tonyh/Desktop/file.txt'     → calls lpath
#   path 'myfile'                              → same in both styles
#
# OUTPUT:
#   Prints both Windows and Linux interpretations.
#   Always copies the converted (or original) path to clipboard.
# -------------------------------------------------------------------

path() {
  if [ -z "$1" ]; then
    echo "Usage: path <path>"
    return 1
  fi

  local input="$1"

  if [[ "$input" == *\\* ]]; then
    wpath "$input"
  elif [[ "$input" == */* ]]; then
    lpath "$input"
  else
    echo "windows path: '$input'"
    echo "linux path:   '$input'"
    echo "$input" | copy_to_clipboard
  fi
}
