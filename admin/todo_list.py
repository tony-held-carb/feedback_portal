"""

# todo - Next Steps
----------------------------

* todo - start here ...

  * so many todos are associated with Please Select.  May want to make sure that is all working and move on ...
    * I don't know that you need default payloads anymore ... seems like everything should automatically go to Please Select

  * merge in the new code for the ec2

  * if a incidence passes validation, have it splash a success message before going to index

  * don't let there be a decoupling between the incidence column and the json key:value
    * don't allow id_incidence to be changed after it has been created
    * maybe block the creation of new incidence from portal
    * seems like i have to strip out some logic and todo's since the templates now work off the row id rather than json field id


* consider new color for validate that stands out more
* consider diff blue for card headers

* if you click an old incidence that is no longer around in the portal updates, it will redirect you to the spreadsheet
upload, it needs to have a message saying that the id needs to be created or that it was deleted ...



* link to plume tracker now works off row id rather than misc_json contents.
  * it may be possible to get rid of id_incidence entirely from misc_json, but
    that will require wtforms to be changed and the filter logic.  keeping it in for now.
* id_incidence was left in json so that the filters work.  there may be a better way (perhaps use row.id_incidence)
  alternatively, the code could likely be strengthened to never allow id_incidence to be changed within the json column.


* 'Please Selects' should no longer persist to database, but
  may want to rethink how please selects are handled in general?

* check that change log is working properly, there may be trouble with empty strings or None's ...

* check that the app/database is working using testing_protocol_and_notes.txt
  * update release notes and wsgi for uniform guidance on flask runs

  * looks like xl_create now logs to arb_portal.log, that was not the intent ...


  * implement recs from gpt to make the site more robust
      Flask Data Integrity Review:  https://chatgpt.com/share/6823ec4c-bd20-800b-b83f-a85fb93ffcd8
        * Ensure Optional() validators are used in WTForms where nullable columns exist in SQLAlchemy.
            - not sure this really applies as we are updating the json field keys, not db column names.

* high priority code reorg so that primary keys work as expected and allow for staged changes
  * figure out when/if incidence primary key can be changed/enabled
  * figure out if we want data to initially only be cached and then updated afterwards
  * so you can revert back to old state when you propose a spreadsheet upload
  * add flask user authentication and add to logging routines

* future initiatives
  * use blueprint structure
    * Flask App Blueprinting Structure: https://chatgpt.com/share/6823ecba-5fb4-800b-b0b6-0128d6d649d9
  * add user log-in
  * update logging based on flask user
  * potentially come up with unit testing

* make updates from C:\Users\theld\OneDrive - California Air Resources Board\OneDriveLinks\Data Management Plan\Operator Portal\operator_portal_feature_requests_010.xlsm
  * Start with Portal UI/UX Requests
  *  Change 'not a citation' to 'not an enforcement action' - hmmm, I can't remember the context of this, so hunt around for these words

* code refactor to move file handling out of routes?
* Probably want to have a form passes validation modal after you validate.  Maybe stay on same page?


Forget me nots
----------------------------
1.  I asked chat gpt to make restructure the first time and did not accept them because their were mistakes
and i was confused, there was some pretty interesting request preprocessing that I would like to revisit
as I don't know how to do that and it seemed very powerful.  Try to revisit
2. changed drop down to drop-down in python, likely have to make those changes on the spreadsheets at some point.

"""
