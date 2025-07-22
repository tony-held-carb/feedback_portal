"""

# todo - Next Steps
----------------------------
creating PR 27 is to continue e2e testing

7/22/25 planning to deploy the new version of the portal to ec2 and updating notes/testing for next steps

* merged in refactor_27, continuing on new branch 28

* the testing seems to be working, so going to check in the PR and create a new branch for doc/buttoning up

* compile all the next todo's into feature requests that will be done in the future, and that which has to be done for the new launch

* consider truing up the file structure on the ec2 along with .bashrc files for consistency
* may want to combine the shell and shell_scripts into a single directory
* update docs to show what testing was done, consider creating a primer for the rest of the group
* create a protocol/template for documenting source code consistent with testing approach
* create a launch new version protocol for automated and manual testing
* review testing_protocol_and_notes.txt
* deploy to ec2
* update notes and scripts to launch from app/wsgi
* come up with some CI/CD that addresses docstring, type safety, edge and corner case, how functions process "", None, or other values that could be error prone



-------------------------------------------------------
Future Initiatives & Feature Requests Below
-------------------------------------------------------


* ---------   HTML & Forms ----------
* consider new color for validate that stands out more.  It may be easier just to give a pop-up
  and stay on the current page
* consider having all the pages use the frozen buttons on the bottom approach across the site

* ---------   Protocols and Recommendations ----------
* make updates from C:\Users\theld\OneDrive - California Air Resources Board\OneDriveLinks\Data Management Plan\Operator Portal\operator_portal_feature_requests_010.xlsm
  * Start with Portal UI/UX Requests
  *  Change 'not a citation' to 'not an enforcement action' - hmmm, I can't remember the context of this, so hunt around for these words


* ---------   Create New Form Capacity for the new sectors ----------
* refactor forms as they are currently duplicative
* have parse_xl_file alias the Sectors and Schemas
* figure out how to handle the pseudo check boxes in the new dairy forms
* make sure to strip checkbox feedback forms
* have new forms upload to database and json, but don't try to show forms that don't exist yet

* ---------   Key persistence refactor ----------
* how data are loaded/stored converted is still a bit confusing
* did an initial review of key functions and put it in documentation for future consideration
* link to plume tracker now works off row id rather than misc_json contents.
  * it may be possible to get rid of id_incidence entirely from misc_json, but
    that will require wtforms to be changed and the filter logic.  keeping it in for now.
  * id_incidence was left in json so that the filters work.  there may be a better way (perhaps use row.id_incidence)
    alternatively, the code could likely be strengthened to never allow id_incidence to be changed within the json column.
  * need to figure out what to do with delete incidences? (may not really happen often)
* high priority code reorg so that primary keys work as expected and allow for staged changes
  * figure out when/if incidence primary key can be changed/enabled

* ---------   future initiatives----------
  * add user log-in
    * Ultimately, need to use the username in the log
  * move to s3 bucket
  * use carb ois github deployment (docker, etc)

* ---------   Error Handling and Debugging Improvements ----------
* TODO: Add a fail-fast check after app initialization (in create_app) to raise a clear error if app.base is missing. This will ensure that database reflection failures (e.g., due to DB downtime) are immediately obvious, rather than causing obscure errors later in the app.

"""
