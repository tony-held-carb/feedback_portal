# Feedback Portal Project

* The pycharm project name and GitHub repo name for this project are both 'feedback_portal.'
  * https://github.com/tony-held-carb/feedback_portal

### Running the Portal Flask App
* Laptop (Windows): http://127.0.0.1:<port_number>
    * cd $prod
    * flask --app arb/wsgi run --debug --no-reload          -> http://127.0.0.1:5000/
    * flask --app arb/wsgi run --debug --no-reload -p 2113  -> http://127.0.0.1:2113/  
* EC2 Linux: http://10.93.112.44:2113
  * flask --app arb/wsgi run --debug --no-reload -p 2113 --host=0.0.0.0     -> http://10.93.112.44:2113/
  * Run the flask app as a process that will not close after the ssh terminates
    * stop any running portal flask apps
        * portal_screen_stop.sh
      * launch the flask app
        * portal_screen_launch.sh
  * Logging directories
    * $HOME/code/git_repos/feedback_portal/logs/
    * removing existing log files:
      * rm $HOME/code/git_repos/feedback_portal/logs/*.log

### Running testing.
  * cd $portal
  * if you don't want to run on http://127.0.0.1:5000
    * create TEST_BASE_URL environmental variable
  * pytest tests/arb -v  > pytest_home_all_21.txt 2>&1
  * pytest tests/e2e -v  > pytest_home_e2e_21.txt 2>&1
  * pytest tests/arb -v  > pytest_laptop_all_21.txt 2>&1
  * pytest tests/e2e -v  > pytest_laptop_e2e_21.txt 2>&1
  * pytest tests/arb -v  > pytest_EC2_all_21.txt 2>&1
  * pytest tests/e2e -v  > pytest_EC2_e2e_21.txt 2>&1
  * tail -f pytest_laptop_all_21.txt 2>&1
  * tail -f pytest_laptop_e2e_21.txt 2>&1
  * 
### Cloning Portal
* Navigate to the root path of repos
  * cd $portal/..
* Removing the old git repo (if necessary)
  * rm -rf feedback_portal
* Clone the latest portal repo
  * git clone https://tony-held-carb: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@github.com/tony-held-carb/feedback_portal  --origin github

### Creating & Pushing documentation site to GitHub
* making the docs
  * cd $prod
  * mkdocs build --clean > mkdocs_clean_build.txt 2>&1
* Pushing to GitHub docs
  * mkdocs gh-deploy --clean
* run local server
  * mkdocs serve

### Make shell scripts executable
  * chmod +x $portal/scripts/*.sh

### Environmental Variables
  * portal, prod
  * Usage: 
    * prepend variables with $.  
    * For example: cd $portal

### Common Git Commands
  * cd to project directory:
    * $portal
  * list all branches:
    * git branch -a
  * delete a local branch
    * git branch -d branch_name
  * git checkout <your_branch>
  * git pull
  * git push
  * git fetch --all --prune 
  * updates all branches and removes dead local branches
        git fetch   Downloads objects and refs from remote (no merge or rebase)
        --all       Fetches from all remotes (if you have more than origin)
        --prune     Removes stale remote-tracking branches that no longer exist on GitHub

### Updating home repo after PR on my work machine
old branch: refactor_old
new branch: refactor_new

update                            git checkout refactor_new
so that it is one greater than    git branch -d refactor_old

git status
git fetch --all --prune
git branch -a
git checkout refactor_new
git status
git branch -d refactor_old
git remote prune origin
git branch -a
git status

### Installing mini conda
  * [mini conda docs](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html)
  * linux installation:
    * mkdir -p ~/miniconda3
    * wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
    * bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
    * rm ~/miniconda3/miniconda.sh

### Creating mini_conda_02 virtual environment
  * For details see: [mini_conda_02.yml](admin/mini_conda_02.yml) 
* Activate mini_conda environment
  * conda deactivate
  * conda activate mini_conda_02
