# echo ">>> .bashrc loaded at $(date) <<<"
# Custom prompt
PS1='$(basename "$PWD")\$ '

# Aliases
alias ll='ls -la --color=auto'
alias gs='git status'
alias py='python'

# Environment variables
export PATH=$PATH:$HOME/bin

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
