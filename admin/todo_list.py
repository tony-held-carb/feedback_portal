"""

# todo - Next Steps
----------------------------
* creating new refactor 23 branch - initial thought it to add testing where convenient

* check if this was done:
  * if you upload a spreadsheet via upload_file or upload_file_staged, you will want it to
    1) upload the file always if save/possible
    2) convert the files to json if possible and save that too
    3) update the database with json contents if possible
    4) display the appropriate feedback form if it is an implemented sector (currenlty only Oil & Gas and Landfill)
    5) provide diagnostic information as to whether the initial file was uploaded, if it was converted to json, if the database was updated, if show the feedback form if the sector is implemented, otherwise indicate that it is not

* check if this was done:
  * Currently, if you click save and the incidence update has no errors you are redirected to the index page
    I would prefer that you stay on the incidence page and get a modal saying that your changes were saved
    and that there are no known validation errors associated with the incidence


* ---------   HTML & Forms ----------
* consider new color for validate that stands out more.  It may be easier just to give a pop-up
  and stay on the current page
* consider having all the pages use the frozen buttons on the bottom approach across the site

* ---------   Protocols and Recommendations ----------
* make updates from C:\Users\theld\OneDrive - California Air Resources Board\OneDriveLinks\Data Management Plan\Operator Portal\operator_portal_feature_requests_010.xlsm
  * Start with Portal UI/UX Requests
  *  Change 'not a citation' to 'not an enforcement action' - hmmm, I can't remember the context of this, so hunt around for these words

* check that the app/database is working using testing_protocol_and_notes.txt


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
  * unit testing
  * move to s3 bucket
  * use carb ois github deployment (docker, etc)

"""
