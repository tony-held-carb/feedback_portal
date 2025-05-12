### Plume operator portal repo
### Refactored for Group Dry Run Exercise for the week of 11/18/24

### Versioning:

* [portal_01](archive/portal_01) - initial design of portal with user authentication
* [portal_02](archive/portal_02) - June 2024 revised design focusing on incident input
* [portal_03](archive/portal_03) - November 2024 revised design using the plume tracker database
* [portal_04](source/production/arb/portal) - November 30, 2024 port to new repository
* [portal](source/production/arb/portal) - Dec 28, 2024 re-org of source code, 
  * portal version are named in the __init__ file not as a suffix
* feedback_portal - reorg on 2025-04-03 because presentation made repo too bulky
  * archived old portal C:\one_drive\code\pycharm\archive\feedback_portal_backup_2025_04_03
  * the portal_01, 02, 03 archives are no longer part of this repo, go to feedback_portal_backup_2025_04_03 if they are needed
  * pycharm uses the mini_conda_01 environment
* 
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
* Removing the old git repo (if necessary)
  * rm -rf feedback_portal
* Clone the latest portal repo (if necessary)
    * git clone https://tony-held-carb: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@github.com/tony-held-carb/feedback_portal  --origin github    
    * git branch -a
    * git checkout ec2_deploy_03 <or your remote branch of interest> 
    * git pull
* Change to the working directory of the operator portal
  * cd versions/portal_04/
* Run the flask app
  * Turn on debugger --debug
  * Normal usage
    * flask run -p 2113 --debug
    * flask run --host=0.0.0.0 -p 2112
    * flask run --host=0.0.0.0 -p 2113 --debug
  * Run app in the background
    * flask run --host=0.0.0.0 -p 2112 &
    * flask run --host=0.0.0.0 -p 2113 &
  * Run app in the background that does not end when you log out
    * nohup flask run --host=0.0.0.0 -p 2112 &
    * nohup flask run --host=0.0.0.0 -p 2113 &
* Access the app
  * point browser to http://10.93.112.44:2112
  * point browser to http://10.93.112.44:2113

### Notes:
* 'todo (consider)' is used in python comments to indicate optional todo items
* naming convention
  * model: an SQLAlchemy model instance
  * wtf_form: a wtform instance

Possible starting point for best practices for archiving/versioning:

1. Include a RELEASE_NOTES.md file at the root of your file structure.  Example content of this file:

```
## v1.0.0 - 2025-04-28
- Feedback portal first stable release using ISD/ED approached spreadsheet feedback forms
- Current versions of feedback forms
  - energy_operator_feedback_v002.xlsx (Schema: energy_v00_01.json)
  - landfill_operator_feedback_v070.xlsx (Schema: landfill_v01_00.json)
  - oil_and_gas_operator_feedback_v070.xlsx (Schema: oil_and_gas_v01_00.json)
```

2. There are two options for including a version file at the root of your code, one is to have an __init__.py file with the line:
__version__ = "1.0.0".
The other option is to create a file named VERSION that is a plain text file with only one line of non-comments that includes the version number of your code.  For example "1.0.0"

3. Version Tagging in Git
Example git tag -a v1.0.0 -m "Stable release v1.0.0 - ready for archive"
- Benefits include:
  - Built-in to Git
  - Easy to find later
  - Common practice (PyPI, GitHub, etc.)

4. Create an archive (.zip or .tar.gz)

- After tagging, you can create a snapshot from the command line.  For example:
  - git archive --format=zip --output=feedback_portal_v1.0.0.zip v1.0.0
- Benefits include:
  - Can store it offline, S3, external drive, etc.