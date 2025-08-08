# Exit early if not an interactive shell (e.g., SFTP, SCP)
case "$-" in
  *i*) ;;  # interactive, continue as normal
  *) return ;;  # non-interactive: exit early to prevent SFTP issues
esac

echo ">>> .bashrc loaded at $(date) <<<"

# Custom prompt
PS1='$(basename "$PWD")\$ '

echo "Broken by the nibbler"

# Environment variables common to all environments
export PATH=$PATH:$HOME/bin

# # Source custom functions
if [ -f ~/.functions.sh ]; then
  source ~/.functions.sh
fi

# detect machine name using .functions.sh
detect_os
detect_machine_location
export MACHINE_NAME="${MACHINE_LOCATION}_${OS_TYPE}"
echo "MACHINE_NAME=$MACHINE_NAME"


case "$MACHINE_NAME" in
  "TONY_HOME_WINDOWS")
    CONDA_HOME="/c/Users/tonyh/miniconda3"
    export portal="/d/local/cursor/feedback_portal"
    ;;
  "TONY_HOME_WSL")
    CONDA_HOME="/home/tonyh/miniconda3"
    export portal="/home/tonyh/git_repos/feedback_portal"
    export DATABASE_URI=postgresql+psycopg2://postgres:methane@192.168.1.66:5432/tony_home_tracker
    # export DATABASE_URI=postgresql+psycopg2://postgres:methane@host.docker.internal:5432/tony_home_tracker
    ;;
  "TONY_WORK_WINDOWS")
    CONDA_HOME="/c/Users/theld/AppData/Local/miniconda3"
    export portal="/c/tony_local/pycharm/feedback_portal"
    ;;
  "TONY_EC2_LINUX")
    CONDA_HOME="/home/theld/miniconda3"
    export portal="/home/theld/code/git_repos/feedback_portal"
#    export PLAYWRIGHT_NODEJS_PATH=~/miniconda3/envs/mini_conda_02/bin/node
    ;;
  *)
    echo "⚠️  Unknown MACHINE_NAME='$MACHINE_NAME'."
    ;;
esac

# Derived Environmental Variables
export prod="$portal/source/production"
export PATH="$PATH:$portal/scripts"
export PYTHONPATH="$prod"


# initialize conda and activate default environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
  # Windows (Git Bash)
  if [[ -n "$CONDA_HOME" && -f "$CONDA_HOME/Scripts/conda.exe" ]]; then
    # echo ">>> .bashrc found conda.exe at $(date) <<<"
    eval "$("$CONDA_HOME/Scripts/conda.exe" 'shell.bash' 'hook')"
    # echo ">>> .bashrc finished conda eval at $(date) <<<"
  else
    echo ">>> .bashrc did NOT find conda.exe at expected location: $CONDA_HOME/Scripts/conda.exe <<<"
  fi
else
  # Linux
  if [[ -n "$CONDA_HOME" && -f "$CONDA_HOME/bin/conda" ]]; then
    # echo ">>> .bashrc found conda at $(date) <<<"
    eval "$("$CONDA_HOME/bin/conda" 'shell.bash' 'hook')"
    # echo ">>> .bashrc finished conda eval at $(date) <<<"
  else
    echo ">>> .bashrc did NOT find conda at expected location: $CONDA_HOME/bin/conda <<<"
  fi
fi
conda activate mini_conda_02

# # Additional Settings
# export TERM=xterm-256color

# # Aliases
alias ll='ls -la --color=auto'
alias gs='git status'
alias py='python'
alias run="$portal/scripts/run"
alias run_all="$portal/scripts/run_all"

# start in the portal directory
cd $portal

# Tell Git to ignore permission differences locally
# This prevents Git from treating chmod +x changes as meaningful diffs.
git config --local core.fileMode false


# Diagnostics
echo "portal=$portal"
echo "prod=$prod"
echo "CONDA_HOME=$CONDA_HOME"
echo "PYTHONPATH=$PYTHONPATH"
echo ""
echo 'to run flask: cd $prod, flask --app arb/wsgi run --debug --no-reload -p 2113'
echo 'pytest tests/arb -v  > "pytest_${MACHINE_NAME}_all_00.txt" 2>&1'
echo 'pytest tests/e2e -v -s --durations=0 > "pytest_${MACHINE_NAME}_e2e_00.txt" 2>&1'
echo ""
