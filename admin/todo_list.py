"""

# todo - Next Steps
----------------------------
* next step is to clean up the wtforms as they are massive and duplicative
  and we will be creating energy and other forms shortly.


* future initiatives
  * add user log-in
  * unit testing
  * move to s3 bucket
  * use carb ois github deployment (docker, etc)

* UI/UX ideas
  * if a incidence passes validation, have it splash a success message before going to index
  * consider new color for validate that stands out more
  * consider diff blue for card headers
  * if you click an old incidence that is no longer around in the portal updates, it will redirect you to the spreadsheet
  upload, it needs to have a message saying that the id needs to be created or that it was deleted ...

* link to plume tracker now works off row id rather than misc_json contents.
  * it may be possible to get rid of id_incidence entirely from misc_json, but
    that will require wtforms to be changed and the filter logic.  keeping it in for now.
  * id_incidence was left in json so that the filters work.  there may be a better way (perhaps use row.id_incidence)
    alternatively, the code could likely be strengthened to never allow id_incidence to be changed within the json column.

* need to figure out what to do with delete incidences? (may not really happen often)

* check that the app/database is working using testing_protocol_and_notes.txt

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
