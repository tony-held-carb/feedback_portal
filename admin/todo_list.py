"""

# todo - Next Steps
----------------------------
* check that the app/database is working using testing_protocol_and_notes.txt

  * update placeholder for wtforms validation
  * resume tomorrow making the dropdowns more robust

  * if a incidence passes validation, have it spalsh a success message before going to index
  * don't let there be a decoupling between the incidence column and the json key:value
    * don't allow it to be changed after it has been created
    * maybe block the creation of new incidence from portal

  * implement recs from gpt to make the site more robust
      Flask Data Integrity Review:  https://chatgpt.com/share/6823ec4c-bd20-800b-b83f-a85fb93ffcd8
        * Ensure Optional() validators are used in WTForms where nullable columns exist in SQLAlchemy.
            - not sure this really applies as we are udating the json field keys, not db column names.


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

"""
