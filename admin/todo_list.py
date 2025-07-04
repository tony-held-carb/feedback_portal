"""

# todo - Next Steps
----------------------------

* ---------   Logging Related ----------
* maybe refactor __get_logger.py
* may want to put it in its own package.
* looks like xl_create now logs to arb_portal.log, that was not the intent ...
* Ultimately, need to use the username in the log

* ---------   Datetime Related ----------
* make a data contract regarding datetime, casting and storage
* staging made it clear that the json files don't store in utc, which is against the
  data contract.

* Data in local time flagged with (todo - datetime - )
  * dummy data
    * todo - need to make sure hard coded values are utc aware
      * update datetime.datetime.now() statements
  * spreadsheets
    * should be read in as naive and immediately convert to utc aware
      * update extract_tabs for datetimes
  * html elements
    * for display - cast to ca local just before presentation
      * finding out where this is done ...
      * looks like incidence_prep has the get/setters
        * for get - model_to_wtform -> deserialize_dict called -> cast_model_value
          * cast_model_value is where the conversion to datetime is updated, update here ...
        * for post - wtform_to_model -> make_dict_serializeable
          * make_dict_serializeable is where the updates should be made
  * look for any references to convert_time_to_ca and remove any casting to avoid confusion
  * looks like cast_model_value and make_dict_serializeable have some overlapping logic
      they may want to be consolidated or somehow aligned with json serialize/deserialize hooks/logic

* ---------   JSON Incidence Row Gotchas ----------
* link to plume tracker now works off row id rather than misc_json contents.
  * it may be possible to get rid of id_incidence entirely from misc_json, but
    that will require wtforms to be changed and the filter logic.  keeping it in for now.
  * id_incidence was left in json so that the filters work.  there may be a better way (perhaps use row.id_incidence)
    alternatively, the code could likely be strengthened to never allow id_incidence to be changed within the json column.

* need to figure out what to do with delete incidences? (may not really happen often)


* ---------   UI/UX ideas ----------
* if a incidence passes validation, have it splash a success message before going to index
* consider new color for validate that stands out more
* if you click an old incidence that is no longer around in the portal updates, it will redirect you to the spreadsheet
upload, it needs to have a message saying that the id needs to be created or that it was deleted ...
* high priority code reorg so that primary keys work as expected and allow for staged changes
  * figure out when/if incidence primary key can be changed/enabled

* ---------   HTML & Forms ----------
* convert portal app from content_1 to standard content block pattern
  * update all templates in arb.portal to use {% block content %} instead of {% block content_1 %}
  * this will improve consistency with Flask conventions and reduce confusion when integrating with other packages
  * consider using descriptive block names like main_content, sidebar_content if multiple content areas are needed

* refactor forms as they are currently duplicative

* ---------   Create New Form Capacity for the new sectors ----------
* have parse_xl_file alias the Sectors and Schemas

* figure out how to handle the pseudo check boxes in the new dairy forms
* make sure to strip checkbox feedback forms
* have new forms upload to database and json, but don't try to show forms that don't exist yet


* ---------   Protocols and Recommendations ----------
* make updates from C:\Users\theld\OneDrive - California Air Resources Board\OneDriveLinks\Data Management Plan\Operator Portal\operator_portal_feature_requests_010.xlsm
  * Start with Portal UI/UX Requests
  *  Change 'not a citation' to 'not an enforcement action' - hmmm, I can't remember the context of this, so hunt around for these words

* check that the app/database is working using testing_protocol_and_notes.txt

* implement recs from gpt to make the site more robust
    Flask Data Integrity Review:  https://chatgpt.com/share/6823ec4c-bd20-800b-b83f-a85fb93ffcd8
      * Ensure Optional() validators are used in WTForms where nullable columns exist in SQLAlchemy.
          - not sure this really applies as we are updating the json field keys, not db column names.

* ---------   future initiatives----------

  * add user log-in
  * unit testing
  * move to s3 bucket
  * use carb ois github deployment (docker, etc)

"""
