# most to do items were moved to a spreadsheet feature tracker located at:
# C:\Users\theld\OneDrive - California Air Resources Board\OneDriveLinks\Data Management Plan\Operator Portal\operator_portal_feature_requests_002.xlsm


# todo - next steps
"""
* make updates from C:\Users\theld\OneDrive - California Air Resources Board\OneDriveLinks\Data Management Plan\Operator Portal\operator_portal_feature_requests_010.xlsm
  * Start with Portal UI/UX Requests
* 	Change 'not a citation' to 'not an enforcement action' - hmmm, I can't remember the context of this, so hunt around for these words

# code refactor to move file handling out of app.py

creating gpt_recommendations_02 because I may have put some bugs into gpt_recommendations_01.
I abandoned v01, I worked on v02, but I think it would be safe to get the stable portal on the ec2
before doing any major code re-works.

feedback portal now a clean repo, need to test that it still works on laptop,
then make it generalizable to the ec2

* probably want to disable the ability to delete an incidence
* ask dan for access to new db instance.

* Probably want to have a form passes validation modal after you validate.  Maybe stay on same page?

* preparing to use ChatGPT to restructure code
Forget me nots
----------------------------

chatgpt request

attached is the code base to be modified.  please propose the following changes:

1) app.py current has all the routes, please create a file named routes.py that has all routes associated with this project
2) in the routes file, use a blueprinting system where all the routes will use a newly created 'main' route
3) app.py should create a code factory app that is called in a separate wsgi file to make the app more portable.
4) use google docstrings with modern type hinting in the docstrings.
5) Include extensive documentation and examples.
6) Include the full text for any file you create or propose to change.
7) Retain, all previous documentation, notes, and todos

not sure if I liked the response, could be changing too much at one time.  Going to try a more incremental approach.
3. consider combining app_util to app
4. move routes to separate file and make sure it has a ref to the flask app (I think you monkey attach)

chat gpt structure - archive app.py so it can be called up again.
add the new app.py and route.py checking that all imports work

"""
