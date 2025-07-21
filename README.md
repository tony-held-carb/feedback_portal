# Feedback Portal Project

* The pycharm project name and GitHub repo name for this project are both 'feedback_portal.'
  * https://github.com/tony-held-carb/feedback_portal

### Running the Portal Flask App
* EC2 Linux: http://10.93.112.44:2113
  * Run the flask app as a process that will not close after the ssh terminates
    * cd $portal/shell_scripts
      * stop any running portal flask apps
        * ./stop_with_screen.sh
      * launch the flask appcd
        * ./launch_with_screen.sh
  * Logging directories
    * /home/theld/code/git_repos/feedback_portal/logs/
    * removing existing log files:
      * rm /home/theld/code/git_repos/feedback_portal/logs/*.log
    * show contents of the log file:
* Laptop (Windows): http://127.0.0.1:2113/
    * cd %portal%\source\production\arb
      * flask --app wsgi run --debug --no-reload -p 2113
  * cursor says if you run from arb, Python treats arb as the current directory, not as a package, which can break relative imports and Flask’s app discovery. it recommends:
    * cd %portal%\source\production
    * cd /d D:\local\cursor\feedback_portal\source\production
      * flask --app arb/wsgi run --debug --no-reload -p 2113

### Common Git Commands
  * cd to project directory:
    * (linux): cd $portal
    * (windows): cd %portal%
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

### Playwright Upload Page Diagnostics (tests/e2e/test_single_page.py)
This script helps both beginners and advanced users inspect and debug the HTML structure of the upload page using Playwright (Python).

**Purpose:**
- Identify selectors for form elements (buttons, inputs, file uploads, drop zones, etc.)
- Print detailed information about each element for easy inspection
- Save a screenshot and output a snippet of the page source

**When to use:**
- Writing or debugging Playwright end-to-end tests
- When the upload page changes and you want to see the new structure
- Onboarding new developers or QA engineers to the project

**Prerequisites:**
- Python 3.8+
- Playwright Python package (`pip install playwright`)
- Playwright browsers installed (`playwright install`)

**Usage:**
1. Ensure the web app is running (default: http://127.0.0.1:5000/upload)
2. Run the script:

   ```bash
   python tests/e2e/test_single_page.py
   ```
   (Optionally, edit the `page_url` variable in the script to target a different page.)

3. The script will launch a Chromium browser, print diagnostics to the console, and save a screenshot as `debug_upload_page.png`.

**Output:**
- Console output listing all buttons, inputs, forms, file inputs, and drop zones with their attributes and visibility
- The first 2000 characters of the page's HTML source
- A screenshot of the page for visual debugging

### Data Contracts:
  * misc_json only contains "Please Select" when it replaces a previously valid value.

### Cloning Portal
* Navigate to the root path of repos
  * windows: "C:\one_drive\code\pycharm\"
  * ec2: cd "/home/theld/code/git_repos"
* Removing the old git repo (if necessary)
  * rm -rf feedback_portal
* Clone the latest portal repo
  * ssh to ec2: user theld
  * cd code/git_repos/
  * git clone https://tony-held-carb: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@github.com/tony-held-carb/feedback_portal  --origin github

### Environmental Variables
* Linux
  * portal = "/home/theld/code/git_repos/feedback_portal"
  * Usage: 
    * prepend variables with $.  
    * For example: cd $portal
  * Creation:
    * add to .bashrc
      * export <variable_name>="<variable_value>"
      * export portal="/home/theld/code/git_repos/feedback_portal"

* Windows
  * portal = "C:\one_drive\code\pycharm\feedback_portal"
  * Usage: 
    * enclose with % 
    * For example: cd %portal%
  * Creation:
    * Open PowerShell (not Command Prompt):
      Press Win + S, type "PowerShell", and open it.
      [System.Environment]::SetEnvironmentVariable("<variable_name>", "<variable_value>", "User")
      [System.Environment]::SetEnvironmentVariable("portal", "C:\one_drive\code\pycharm\feedback_portal", "User")

### Make shell scripts executable (linux only)
  * chmod +x /home/theld/code/git_repos/feedback_portal/shell_scripts/*.sh
  * remove the old scripts if you are having git pull issues
    * rm /home/theld/code/git_repos/feedback_portal/shell_scripts/*.sh

### Installing mini conda
  * [mini conda docs](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html)
  * linux installation:
    * mkdir -p ~/miniconda3
    * wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
    * bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
    * rm ~/miniconda3/miniconda.sh

### Creating mini_conda_01 virtual environment
  * For details see: [mini_conda_01.yml](admin/mini_conda_01.yml) 
* Activate mini_conda environment
  * conda deactivate
  * conda activate mini_conda_01

### Pushing documentation site to GitHub
* Pushing to GitHub docs
  * mkdocs build
  * mkdocs gh-deploy --clean
* run local server
  * mkdocs serve

### Updating home repo after PR on my work machine
update                            git checkout refactor_27
so that it is one greater than    git branch -d refactor_26

git status
git fetch --all --prune
git branch -a
git checkout refactor_27
git status
git branch -d refactor_26
git remote prune origin