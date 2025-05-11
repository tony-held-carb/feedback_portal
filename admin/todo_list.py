# most to do items were moved to a spreadsheet feature tracker located at:
# C:\Users\theld\OneDrive - California Air Resources Board\OneDriveLinks\Data Management Plan\Operator Portal\operator_portal_feature_requests_002.xlsm


"""
chatgpt request template
----------------------------
I would like ***

1) app.py current has all the routes, please create a file named routes.py that has all routes associated with this project
2) in the routes file, use a blueprinting system where all the routes will use a newly created 'main' route
3) app.py should create a code factory app that is called in a separate wsgi file to make the app more portable.

Please refactor the following python code using the following style preferences:
1) use google formatting docstrings
2) use modern type hinting in the docstrings (not in the function definition).
3) docstring type hinting should be in the format:  variable_name (type_hint): variable description.
4) Include extensive documentation and examples.
5) Review all of the code and provide all suggestions in one response, not incrementally prompting me for additional information.
6) Include the full text for any file you create or propose to change.
7) Retain, all previous documentation, notes, and todos where possible
8) do not import typing, rather use modern type hinting such as the | symbol
9) do not omit any code for brevity, i'm going to copy paste your code into a new file.

Please create a new function named run_diagnostics that includes testing of key features of this file.

# todo - next steps
Next steps
----------------------------
* essential steps to get the app running on the ec2
  * learn how tags work and how to go to a specific tag
  * tag/ensure tag for main branch
  * merge latest changes to main branch
  * tag the gpt refactored code
  * learn how to set the port with the wsgi run
  * learn how to run without the terminal being on
  * learn how to stop the run in no-hup or background
  * connect to dan's database
  * check that the database is working
  * put password protect for deleting records or disable this ability
  * update logging to include user, default to anonymous in the mean time so all logging
    uses same format

* high priority code reorg so that primary keys work as expected and allow for staged changes
  * figure out when/if incidence primary key can be changed/enabled
  * figure out if we want data to initially only be cached and then updated afterwards
  * so you can revert back to old state when you propose a spreadsheet upload


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
