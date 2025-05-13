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
  * git clone https://tony-held-carb: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@github.com/tony-held-carb/feedback_portal  --origin github
  * cd feedback_portal
  * git branch -a
  * git checkout ec2_deploy_03 <or your remote branch of interest> 
  * git pull
* Make shell scripts executable (linux only)
  * chmod +x /home/theld/code/git_repos/feedback_portal/shell_scripts/*.sh
* Run the flask app (Standard Recommended Approach)
  * cd feedback_portal\source\production\arb>
    * run on local host (for your laptop only) 
      * flask --app wsgi run -p 2113 --debug
    * ec2 on public host 
      * flask --app wsgi run --host=0.0.0.0 -p 2113 --debug
    * ec2 to run as a process that will not close after the ssh terminates
      * ./feedback_portal/shell_scripts/launch_with_screen.sh
      * ./feedback_portal/shell_scripts/stop_with_screen.sh
* Access the app
  * windows: http://127.0.0.1:5000/
  * linux: http://10.93.112.44:2113

### Notes:
* 'todo (consider)' is used in python comments to indicate optional todo items
* naming convention
  * model: an SQLAlchemy model instance
  * wtf_form: a wtform instance

### Archiving:
* portal had a major refactor and the previous project designs were archived.
* If the repo is to be archived (it becomes unstable for some reason), save it
  to: feedback_portal_old_vxx where xx is a 2 digit number for archive before
  recreating a new feedback_portal.  The next archive should be feedback_portal_old_v04.
