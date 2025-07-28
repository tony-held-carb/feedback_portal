# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# Tony Variables
# Usage example: cd $portal
export portal="/home/theld/code/git_repos/feedback_portal"

alias ec2_prep='source ~/code/git_repos/feedback_portal/shell_scripts/ec2_prep.sh'
alias ec2_run='source ~/code/git_repos/feedback_portal/shell_scripts/ec2_run.sh'

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/theld/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/theld/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/theld/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/theld/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

# Tony mods
# Simplified prompt: shows conda env and current folder
export PS1='${CONDA_DEFAULT_ENV:+($CONDA_DEFAULT_ENV) }[\W]\$ '

