echo ">>> .bashrc loaded at $(date) <<<"

# Custom prompt
PS1='$(basename "$PWD")\$ '

# Environment variables common to all environments
export PATH=$PATH:$HOME/bin

# Use the machine name to customize different environments
# on windows/linux you can use
# export MACHINE_NAME="TONY_EC2"
# setx MACHINE_NAME "TONY_HOME"           (CMD or Git Bash)

# if you ssh you need to check the ip because export variables won't persist
# Set MACHINE_NAME if private IP is 10.93.112.44
LOCAL_IP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)
echo "Detected IP: $LOCAL_IP"
if [[ "$LOCAL_IP" == "10.93.112.44" ]]; then
  export MACHINE_NAME="TONY_EC2"
fi
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
    CONDA_HOME="/home/theld/miniconda3"
    export portal="/home/theld/code/git_repos/feedback_portal"
    export PLAYWRIGHT_NODEJS_PATH=~/miniconda3/envs/mini_conda_02/bin/node
    ;;
  *)
    echo "⚠️  Unknown MACHINE_NAME='$MACHINE_NAME'."
    ;;
esac

# Derived Environmental Variables
export prod="$portal/source/production"
export PATH="$PATH:$portal/scripts"
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$prod"

# Additional Settings
export TERM=xterm-256color

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

# Source custom functions
if [ -f ~/.functions.sh ]; then
  source ~/.functions.sh
fi
