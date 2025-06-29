# Feedback Portal Release Notes:

Below are the tag names, dates, and overview of the Portal versions

## [Unreleased]
- Refactored staged upload system:
  - Staged files now use timestamped filenames (id_XXX_ts_YYYYMMDD_HHMMSS.json)
  - Processed staged files are moved to a 'processed' directory
  - Added concurrency/data loss protection: users are warned if the DB changes after staging
  - All routes and templates updated to use new filename-based system

### v1.7.0 - 2025-06-12
- running on ec2 since 6/12/25
- very stable and was used in a recent dry run
- it is far behind refactor_20 and was just tagged as v1.7.0 on 6/28/25 
  so we could return to it if the new changes are unstable
  
### v1.6.0 - 2025-06-11
- Debug version 1.6.0.  Stable, needs to be externally tested.
- Patch to warn rather than fail when sector types disagree between 
  the feedback form and foreign key table.

### v1.5.0 - 2025-06-10
- Debug version 1.5.0.  Stable, needs to be externally tested.
- Refactored to break up large files and facilitate unit testing.

### v1.4.0 - 2025-06-08
- Debug version 1.4.0.  Stable, needs to be externally tested.
- Documentation site created and new Help menu created.
 
### v1.3.0 - 2025-05-11
- Debug version 1.3.0.  Stable, needs to be externally tested.
- New page to view portal changes.
- JSON persisting updated to make storage more robust
- Uniform treatment of drop-downs.

### v1.2.0 - 2025-05-11
- Debug version 1.2.0. Can run on EC2 without interruption. 
- EC2 now able to run in detached mode without ssh staying open
- Readme documentation updated for remote usage

### v1.1.0 - 2025-05-11
- Debug version 1.1.0. Stable after GPT refactor
- Uses the same spreadsheet schemas as v1.0.0
- Can be run off EC2

### v1.0.0 - 2025-04-28
- Feedback portal first stable release using ISD/ED approached spreadsheet feedback forms
- Current versions of feedback forms
  - energy_operator_feedback_v002.xlsx (Schema: energy_v00_01.json)
  - landfill_operator_feedback_v070.xlsx (Schema: landfill_v01_00.json)
  - oil_and_gas_operator_feedback_v070.xlsx (Schema: oil_and_gas_v01_00.json)
- originally committed on 2025-04-28 and then rewritten 2025-05-11

## Tagged Versions: Benefits & Usage
- Benefits of this tagging approach include:
  - Built-in to Git
  - Easy to find later
  - Common practice (PyPI, GitHub, etc.)
- Creating a tag
  - git tag -a v1.0.0 -m "Stable release v1.0.0 - ready for archive"
  - git tag -a v1.3.0 -m "Version 1.3.0. New portal changes page, more robust json storage." 
- View tags
  - git tag
  - git show v1.0.0
- Checkout a tag
  - git checkout v1.0.0 # this puts you in a detached HEAD state
  - if you want to base a new branch off a tag
    - git checkout -b bugfix-from-v1.0.0 v1.0.0
  - delete a tag
    - git tag -d v1.0.0

## Archiving
- Archiving after tagging in git
  - After tagging, you can create a snapshot from the command line.  For example:
    - git archive --format=zip --output=feedback_portal_v1.0.0.zip v1.0.0
    - git archive --format=zip --output=feedback_portal_v1.2.0.zip v1.2.0
  - Benefits include:
    - Can store it offline, S3, external drive, etc.
- Archive locations and naming system
  - The project should always be called feedback_portal
  - If the repo is to be archived (it becomes unstable for some reason), save it to:
    - C:\one_drive\code\archived\feedback_portal as
    - feedback_portal_old_vxx
      - where xx is a 2 digit number
      - The next archive should be feedback_portal_old_v04
    - Create a new project with name feedback_portal and start with a clean code base.

## Versioning Systems
- There are two options for including a version file at the root of your code.
  - one is to have an __init__.py file with the line:
    - __version__ = "1.0.0".
  - The other option is to create a file named VERSION that is a plain text file with only one line of non-comments that includes the version number of your code.  For example "1.0.0"
