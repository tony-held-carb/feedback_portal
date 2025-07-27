echo ">>> .bash_profile loaded at $(date) <<<"
if [ -f ~/.bashrc ]; then
  echo ">>> .bash_profile found .bashrc at $(date) <<<"
  echo ">>> .bash_profile is about to source .bashrc at $(date) <<<"
  . ~/.bashrc
  echo ">>> .bash_profile finished sourcing .bashrc at $(date) <<<"
else
  echo ">>> .bash_profile did NOT find .bashrc at $(date) <<<"
fi

