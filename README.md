### Feedback Portal Project Overview

* The pycharm project name and github repo for this project are both named 'feedback_portal'.
  * https://github.com/tony-held-carb/feedback_portal
  * C:\one_drive\code\pycharm\feedback_portal

### Usage:
* Install mini conda (if not already installed)
  * [mini conda docs](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html)
  * linux installation:
    * mkdir -p ~/miniconda3
    * wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
    * bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
    * rm ~/miniconda3/miniconda.sh
* Create mini_conda_01 virtual environment (if not already installed)
  * See [mini_conda_01.yml](admin/mini_conda_01.yml) for details
* Activate mini_conda environment
  * conda deactivate
  * conda activate mini_conda_01
* Navigate to root path of repos
  * windows: "C:\one_drive\code\pycharm\"
  * ec2: cd "/home/theld/code/git_repos"
* Removing the old git repo (if necessary)
  * rm -rf feedback_portal
* Clone the latest portal repo (if necessary)
  * ssh to ec2: user theld
  * cd code/git_repos/
  * git clone https://tony-held-carb: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@github.com/tony-held-carb/feedback_portal  --origin github
  * cd feedback_portal
  * git fetch --all --prune 
    * updates all branches and removes dead local branches
        git fetch   Downloads objects and refs from remote (no merge or rebase)
        --all       Fetches from all remotes (if you have more than origin)
        --prune     Removes stale remote-tracking branches that no longer exist on GitHub
  * git branch -a
    * lists all branches
  * git checkout your_branch
  * git pull
  * git push
* Make shell scripts executable (linux only)
  * chmod +x /home/theld/code/git_repos/feedback_portal/shell_scripts/*.sh
  * remove the old scripts if you are having git pull issues
    * rm /home/theld/code/git_repos/feedback_portal/shell_scripts/*.sh
* Run the flask app
    * ec2 to run as a process that will not close after the ssh terminates
      * cd "/home/theld/code/git_repos/feedback_portal/shell_scripts"
        * ./launch_with_screen.sh
        * ./stop_with_screen.sh
        * logs will go to directory:  /home/theld/code/git_repos/feedback_portal/logs/
          * rm /home/theld/code/git_repos/feedback_portal/logs/*.log
        * cat /home/theld/code/git_repos/feedback_portal/logs/screen_flask_2025_05_14_18_59_38.log
    * ec2 on public host 
      * cd /home/theld/code/git_repos/feedback_portal/source/production/arb
      * flask --app wsgi run --host=0.0.0.0 -p 2113 --debug
    * run on local host (for your laptop only) 
      * cd "C:\one_drive\code\pycharm\feedback_portal\source\production\arb"
      * flask --app wsgi run --debug --no-reload -p 2113
* Access the app
  * windows: http://127.0.0.1:5000/
  * linux: http://10.93.112.44:2113

### Archiving:
* portal had a major refactor and the previous project designs were archived.
* If the repo is to be archived (it becomes unstable for some reason), save it
  to: feedback_portal_old_vxx where xx is a 2 digit number for archive before
  recreating a new feedback_portal.  The next archive should be feedback_portal_old_v04.
