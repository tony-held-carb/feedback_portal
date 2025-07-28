# echo ">>> .bashrc loaded at $(date) <<<"
# Custom prompt
PS1='$(basename "$PWD")\$ '

# Aliases
alias ll='ls -la --color=auto'
alias gs='git status'
alias py='python'

# Environment variables
export PATH=$PATH:$HOME/bin

# --- BEGIN: Prevent CLI Hanging and Prompts ---
# Prevent git and other tools from using pagers or interactive prompts
export GIT_PAGER=cat
export PAGER=cat
export LESS=F
export TERM=dumb
export GIT_TERMINAL_PROMPT=0
# --- END: Prevent CLI Hanging and Prompts ---

# echo ">>> .bashrc about to check for conda init at $(date) <<<"
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
if [ -f '/c/Users/tonyh/miniconda3/Scripts/conda.exe' ]; then
    # echo ">>> .bashrc found conda.exe at $(date) <<<"
    eval "$('/c/Users/tonyh/miniconda3/Scripts/conda.exe' 'shell.bash' 'hook')"
    # echo ">>> .bashrc finished conda eval at $(date) <<<"
else
    echo ">>> .bashrc did NOT find conda.exe at $(date) <<<"
fi
# <<< conda initialize <<<


# Add feedback_portal diagnostics scripts to PATH
export PATH="$PATH:/d/local/cursor/feedback_portal/diagnostics/cursor"

alias run='/d/local/cursor/feedback_portal/scripts/run'
alias run_all='/d/local/cursor/feedback_portal/scripts/run_all'

export portal="/d/local/cursor/feedback_portal"
export prod="/d/local/cursor/feedback_portal/source/production"
echo -e "\nportal=$portal"
echo "prod=$prod"

cd $portal
echo "pwd=$portal"

echo 'to run flask: cd $prod, flask --app arb/wsgi run --debug --no-reload'

echo -e "\nGo get 'em tiger\n"

conda activate mini_conda_02

# git bash windows will assume a dumb terminal unless you export the term after conda activation
export TERM=xterm-256color



wcd() {
  # cd using a windows path to unix directory
  # example: wcd 'C:\Users\tonyh\miniconda3'
  # note: the single quotes are required
  cd "$(cygpath -u "$1")"
}

w() {
  # w is a wrapper for cd that converts windows paths to unix paths
  # example: w cd 'C:\Users\tonyh\miniconda3'
  # note: the single quotes are required
  local args=()
  for arg in "$@"; do
    # If it looks like a Windows path (starts with drive letter + :\), convert it
    if [[ "$arg" =~ ^[A-Za-z]:\\ ]]; then
      # Remove trailing backslash and convert to Unix
      arg="${arg%\\}"
      arg="$(cygpath -u "$arg")"
    fi
    args+=("$arg")
  done
  "${args[@]}"
}

# -------------------------------------------------------------------
# path() — Convert a Windows-style path to a Git Bash–compatible path
#
# This function takes a single Windows-style path as an argument and
# prints both the original Windows path and its equivalent Unix-style
# path for use in Git Bash.
#
# It uses `cygpath -u` internally to perform the conversion.
#
# USAGE:
#   path 'C:\Users\tonyh\Desktop\file.txt'
#   path 'D:\local\cursor\feedback_portal\scripts\compare_yml.txt'
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

path() {
  if [ -z "$1" ]; then
    echo "Usage: path 'C:\\path\\to\\file_or_directory'"
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
}


