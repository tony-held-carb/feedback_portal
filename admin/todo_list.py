# most to do items were moved to a spreadsheet feature tracker located at:
# C:\Users\theld\OneDrive - California Air Resources Board\OneDriveLinks\Data Management Plan\Operator Portal\operator_portal_feature_requests_002.xlsm


"""

# todo - next steps
Next steps
----------------------------
  * come up with utility functions to help chmod/launch, etc
  * figure out where feedback forms and the backups are and archive them

  * create a list of must check/functionality for the portal, check it against spreadsheets, etc
  * potentially come up with unit testing

* check that the app/database is working
  * connect to dan's database
  * need to test a variety of usage cases to make sure input/output/logging is working as expected.
  * don't want the site to crash on its initial week ...

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

* future initiatives
  * use blueprint structure
  * add user log-in
  * update logging based on flask user


Forget me nots
----------------------------
1.  I asked chat gpt to make restructure the first time and did not accept them because their were mistakes
and i was confused, there was some pretty interesting request preprocessing that I would like to revisit
as I don't know how to do that and it seemed very powerful.  Try to revisit


"""
