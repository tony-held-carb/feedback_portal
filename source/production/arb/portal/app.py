"""
The Feedback Portal Phase 3 is a flask app/website that allows for the ingestion and editing
of feedback data from facility operators.

Usage:
  * in the directory with app.py (this file) at command line type: flask run
  * optional arguments to flask run
      --no-reload: does not automatically reload flask when source code changes
      --host=0.0.0.0: allows access from non-local clients (e.g. from an ec2 instance)
      -p 5150: set the app port to a value other than 5000 to avoid conflicts
  * navigate to  http://127.0.0.1:5000 (default port) or http://10.93.112.44:5150 (example explicit port)

Notes:
  * The app.py file should only contain imports, initialization, routes, or functions
    that return 'render_template'
  * app specific functions should be in app_util.py
  * Best practices on the database variable db.
      - import db at the top of the app.py file to avoid having to include db in each parameter
      - pass db as an argument for any other usage to allow for generalized code.
  * Make sure to import the models you create in python in db_create of config.py for them to register properly
  * import order is important for flask/sqlalchemy.  Must import globals, extensions, then config
"""
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote
from zoneinfo import ZoneInfo

from flask import Flask, abort, redirect, render_template, request, url_for
from sqlalchemy.orm.attributes import flag_modified

import arb.__get_logger as get_logger
import arb.portal.db_hardcoded
import arb.utils.sql_alchemy
from arb.portal.app_util import dict_to_database, get_sector_info, upload_and_update_db
from arb.portal.config import Config, db_initialize_and_create, reflect_database
from arb.portal.extensions import db
from arb.portal.globals import Globals
from arb.utils.diagnostics import obj_to_html
from arb.utils.sql_alchemy import add_commit_and_log_model, find_auto_increment_value, get_class_from_table_name, get_rows_by_table_name, \
  sa_model_diagnostics, sa_model_to_dict
from arb.utils.wtf_forms_util import get_wtforms_fields, initialize_drop_downs, model_to_wtform, validate_no_csrf, wtf_count_errors, \
  wtform_to_model

__version__ = "1.0.0"
logger, pp_log = get_logger.get_logger(__name__, __file__)

#####################################################################
# Create and Configure Flask App
#####################################################################
app = Flask(__name__)
# print(f"{type(app)=}")
Config.configure_flask_app(app)

#####################################################################
# Associate db with the flask app & determines the schema of postgres database
# db_initialize_and_create calls db_create.  You must import all SQLAlchemy
# models defined in python in db_create for them to be properly initialized.
#####################################################################
db_initialize_and_create(app, db)
base = reflect_database(app, db)  # determines schema of postgres database

#####################################################################
# Save db schema to global variables, & load drop down selector information
# #####################################################################
Globals.load_type_mapping(app, db, base)
Globals.load_drop_downs(app, db)

#####################################################################
# Import wtf_forms models below (not at the top of the file)
# Placement below avoids initialization issues because class level objects require globals to be already loaded
# Alternatively, these imports could be imported at the function level only by funcs that use them.
#####################################################################
pass


#####################################################################
# User facing endpoints
#####################################################################

@app.route('/')
def index():
  """
  Flask route to the root of web portal, currently lists incidences.
  """
  table_name = 'incidences'
  colum_name_pk = 'id_incidence'
  rows = get_rows_by_table_name(db, base, table_name, colum_name_pk, ascending=False)

  return render_template('index.html', model_rows=rows)


@app.route('/incidence_update/<int:id_>/', methods=('GET', 'POST'))
def incidence_update(id_):
  """
  Flask route to update an existing incidence.
  """

  logger.debug(f"incidence_update called with id= {id_}.")
  table_name = 'incidences'
  table = get_class_from_table_name(base, table_name)

  # get_or_404 uses the tables primary key
  # model_row = db.session.query(table).get_or_404(id_)
  # todo turn this into a get and if it is null, then redirect? to the spreadsheet upload
  # todo consider turning into one_or_none and have error handling
  rows = db.session.query(table).filter_by(id_incidence=id_).all()
  if not rows:
    message = f"A request was made to edit a non-existent id_incidence ({id_}).  Consider uploading the incidence by importing a spreadsheet."
    return redirect(url_for('upload_file', message=message))
  if len(rows) > 1:
    abort(500, description=f"Multiple rows found for id={id_}")
  model_row = rows[0]

  sector, sector_type = get_sector_info(db, base, id_)

  logger.debug(f"calling incidence_prep()")
  return incidence_prep(model_row,
                        crud_type='update',
                        sector_type=sector_type,
                        default_dropdown=Globals.PLEASE_SELECT)


@app.route('/og_incidence_create/', methods=('GET', 'POST'))
def og_incidence_create():
  """
  Flask route to create new Oil & Gas incidence via web interface.
  """
  logger.debug(f"og_incidence_create() - beginning.")
  table_name = 'incidences'
  col_name = 'misc_json'

  data_dict = arb.portal.db_hardcoded.get_og_dummy_data()

  id_ = dict_to_database(db,
                         base,
                         data_dict,
                         table_name=table_name,
                         json_field=col_name,
                         )

  logger.debug(f"og_incidence_create() - leaving.")
  return redirect(url_for('incidence_update', id_=id_))


@app.route('/landfill_incidence_create/', methods=('GET', 'POST'))
def landfill_incidence_create():
  """
  Flask route to create new Landfill incidence via web interface.
  """
  logger.debug(f"landfill_incidence_create called.")
  table_name = 'incidences'
  col_name = 'misc_json'

  data_dict = arb.portal.db_hardcoded.get_landfill_dummy_data()

  id_ = dict_to_database(db,
                         base,
                         data_dict,
                         table_name=table_name,
                         json_field=col_name,
                         )

  logger.debug(f"landfill_incidence_create() - leaving.")
  return redirect(url_for('incidence_update', id_=id_))


@app.post('/incidence_delete/<int:id_>/')
def incidence_delete(id_):
  """
  Flask route to delete an incidence given its incidence_id.

  Notes:
    * This will allow one to delete an incidence from the database from the portal interface
      which may be something that requires a carb password to avoid accidental deletion.
  """
  logger.debug(f"Updating database with route incidence_delete for id= {id_}:")

  table_name = 'incidences'
  table = get_class_from_table_name(base, table_name)
  model_row = db.session.query(table).get_or_404(id_)
  arb.utils.sql_alchemy.delete_commit_and_log_model(db,
                                                    model_row,
                                                    comment=f'Deleting incidence row {id_}')

  return redirect(url_for('index'))


@app.route('/search/', methods=('GET', 'POST'))
def search():
  """
  Flask route to conduct a search from the nav bar.
  Currently, in development and will only echo the search string.
  """
  logger.debug(f"In search route:")
  logger.debug(f"{request.form=}")
  search_string = request.form.get('navbar_search')
  logger.debug(f"{search_string=}")

  return render_template('search.html',
                         search_string=search_string,
                         )


@app.route('/diagnostics')
def diagnostics():
  """
  Flask route to show diagnostic info for code in development.
  """
  logger.info(f"diagnostics() called")

  result = find_auto_increment_value(db, "incidences", "id_incidence")

  html_content = f"<p><strong>Diagnostic Results=</strong></p> <p>{result}</p>"
  return render_template('diagnostics.html', html_content=html_content)


@app.route('/show_dropdown_dict')
def show_dropdown_dict():
  """
  Flask route to show drop-down data structures as a diagnostic.
  """
  logger.info(f"Determining dropdown dict")
  # update drop down tables
  Globals.load_drop_downs(app, db)
  result1 = obj_to_html(Globals.drop_downs)
  result2 = obj_to_html(Globals.drop_downs_contingent)
  result = (f"<p><strong>Globals.drop_downs=</strong></p> <p>{result1}</p>"
            f"<p><strong>Globals.drop_downs_contingent=</strong></p> <p>{result2}</p>")
  return render_template('diagnostics.html', html_content=result)


@app.route('/show_database_structure')
def show_database_structure():
  """
  Flask route to show database structure as a diagnostic
  """
  logger.info(f"Displaying database structure")
  result = obj_to_html(Globals.db_column_types)
  result = f"<p><strong>Postgres Database Structure=</strong></p> <p>{result}</p>"
  return render_template('diagnostics.html', html_content=result)


@app.route('/show_feedback_form_structure')
def show_feedback_form_structure():
  """
  Flask route to show wtforms structure as a diagnostic.
  """
  from arb.portal.wtf_forms import OGFeedback, LandfillFeedback
  logger.info(f"Displaying wtforms structure as a diagnostic")

  form1 = OGFeedback()
  fields1 = get_wtforms_fields(form1)
  result1 = obj_to_html(fields1)

  form2 = LandfillFeedback()
  fields2 = get_wtforms_fields(form2)
  result2 = obj_to_html(fields2)

  result = (f"<p><strong>WTF OGFeedback Form Structure=</strong></p> <p>{result1}</p>"
            f"<p><strong>WTF LandfillFeedback Form Structure=</strong></p> <p>{result2}</p>")

  return render_template('diagnostics.html', html_content=result)


@app.route('/show_log_file')
def show_log_file():
  """
  Flask route to show the log file as a diagnostic.
  """
  logger.info(f"Displaying the log file as a diagnostic")
  with open('logs/operator_portal.log', 'r') as file:
    file_content = file.read()

  # result = obj_to_html(file_content)
  result = f"<p><strong>Logger file content=</strong></p> <p><pre>{file_content}</pre></p>"
  return render_template('diagnostics.html', html_content=result)


# Index route: list files in the uploads folder
@app.route('/list_uploads')
def list_uploads():
  """
  Flask route to list files in the uploads folder.
  """
  logger.debug(f"in list_uploads")
  up_dir = Path("static/uploads")
  # print(f"{type(up_dir)=}: {up_dir=}")
  files = [x.name for x in up_dir.iterdir() if x.is_file()]
  logger.debug(f"{files=}")

  return render_template('list_uploads.html', files=files)


@app.route('/upload', methods=['GET', 'POST'])
@app.route('/upload/<message>', methods=['GET', 'POST'])
def upload_file(message=None):
  """
  Flask route to upload file from client to server.

  Notes:
    * For example usage pattern of file upload see: https://flask.palletsprojects.com/en/3.0.x/patterns/fileuploads/
    * A file upload from a webpage occurs on a post and the desired file upload can be extracted from the request with:
        request_file = request.files['file']
  """
  if message:
    # Decode URL-encoded message (e.g., '+' to space, '%20' to space, etc.)
    message = unquote(message)
    logger.debug(f"upload_file called with {message=}")

  upload_dir = app.config['UPLOAD_FOLDER']
  logger.debug(f"Request to upload file to server with: \n\t{request.files=}\n\t{upload_dir=}")

  if request.method == 'POST':
    # Re request file upload if no file was in the post
    if 'file' not in request.files or request.files['file'].filename == "":
      return redirect(request.url)

    logger.debug(f"{request.files['file']=}")
    request_file = request.files['file']

    if request_file:
      # todo - update function names for clarity?
      file_name, id_, sector = upload_and_update_db(db, upload_dir, request_file, base)
      logger.debug(f"{sector=}")
      if id_:
        logger.debug(f"upload_file() {id_=}")
        return redirect(url_for('incidence_update', id_=id_))
      else:
        logger.debug(f"upload_file() Did not contain feedback format: {file_name=}")
        return render_template('upload.html', upload_message=f"Successfully uploaded file: {file_name.name}")

  return render_template('upload.html', upload_message=message)


#####################################################################
# Diagnostic and developer endpoints
#####################################################################

@app.route('/background/', methods=('GET', 'POST'))
def background():
  """
  Flask route to experiment with differing background approaches.
  """
  logger.debug(f"In background route:")

  return render_template('background.html')


@app.route('/sticky/', methods=('GET', 'POST'))
def sticky():
  """
  Flask route to experiment with differing formatting structures.
  """
  logger.debug(f"In sticky route:")

  return render_template('sticky.html')


@app.route('/modify_json_content')
def modify_json_content():
  """
  Flask route to demonstrate how to update a json field in a postgres column.

  Notes:
    - ORM can get confused if you modify the json leading to it not being persisted properly:
      https://bashelton.com/2014/03/updating-postgresql-json-fields-via-sqlalchemy/
  """
  id_incidence = 5  # hard coded incidence to modify

  # for i, map_name in enumerate(Base.classes):
  #   table_name = str(map_name.__table__.name)
  #   print(i, table_name)
  incidences = base.classes.incidences

  session = db.session
  model = session.query(incidences).get(id_incidence)
  logger.debug(f"{model=}")
  json_content = model.misc_json

  time_stamp = datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S")
  json_content['time_stamp'] = time_stamp

  model.misc_json = json_content
  flag_modified(model, "misc_json")
  # model.misc_json['temp'] = 123456
  db.session.add(model)
  db.session.commit()

  return json_content


@app.route('/run_sql_script')
def run_sql_script():
  """
 (Outdated) Flask route to run a sql_script which adds tables & data to the database from a
  sql text file and convert some tables into drop down structures suitable for select drop-downs.
  """
  return "This script is no longer in service - it was originally designed for sqlite"
  # logger.info(f"Running sql script")
  # database.add_static_table_content()
  # # update drop down tables
  # Globals.load_drop_downs(app)
  # return '<h1>SQL script run</h1>'


@app.route('/add_form_dummy_data')
def add_form_dummy_data():
  """
  Flask route to add random dummy oil and gas data to the incidence table for diagnostics.
  """
  logger.info(f"Adding dummy data for feedback forms")
  arb.portal.db_hardcoded.add_og_dummy_data(db, base, 'incidences')

  return '<h1>Dummy Feedback Form Data Created</h1>'


@app.route('/drag_and_drop', methods=['GET', 'POST'])
def drag_and_drop_01():
  """
  (Outdated) Flask route to output diagnostics to get drag and drop functionality working
  """
  if request.method == 'POST':
    if 'file' not in request.files:
      return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
      return redirect(request.url)
    if file:
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
      return redirect(url_for('drag_and_drop_01'))
  return render_template('drag_and_drop_01.html')


# ------------------------------------------------------------
# Functions that return render_template
# (all other helper functions should be considered moving to app_util.py)
# ------------------------------------------------------------


def incidence_prep(model_row,
                   crud_type,
                   sector_type,
                   default_dropdown="Please Select"):
  """
  Helper function used by many flask routes to render feedback forms for
  both creation and updating.

  Args:
    model_row (SQLAlchemy.Model): Single row from a SQLAlchemy model
    crud_type (str): 'update' or 'create'
    sector_type (str): 'Oil & Gas' or 'Landfill'
    default_dropdown (str): Defaults if no drop down is selected.

  Returns (str): html for dynamic page

  Notes:

  """
  from arb.portal.wtf_forms import OGFeedback, LandfillFeedback
  logger.debug(f"incidence_prep() called with {crud_type=}, {sector_type=}")
  sa_model_diagnostics(model_row)

  if sector_type == "Oil & Gas":
    logger.debug(f"({sector_type=}) will use an Oil & Gas Feedback Form")
    wtf_form = OGFeedback()
    template_file = 'og_feedback.html'
  elif sector_type == "Landfill":
    logger.debug(f"({sector_type=}) will use a Landfill Feedback Form")
    wtf_form = LandfillFeedback()
    template_file = 'landfill_feedback.html'
  else:
    raise ValueError(f"Unknown sector type: '{sector_type}'.")

  if request.method == 'GET':
    # Populate wtform from model data
    model_to_wtform(model_row, wtf_form)
    # todo - maybe put update contingencies here?


    # obj_diagnostics(wtf_form, message="wtf_form in incidence_prep() after model_to_wtform")

    # For GET requests for row creation, don't validate and error_count_dict will be all zeros
    # For GET requests for row update, validate (except for the csrf token that is only present for a POST)
    if crud_type == 'update':
      validate_no_csrf(wtf_form, extra_validators=None)

  # Set all select elements that are a default value (None) to "Please Select" value
  initialize_drop_downs(wtf_form, default=default_dropdown)
  # logger.debug(f"\n\t{wtf_form.data=}")

  if request.method == 'POST':
    # Validate and count errors
    wtf_form.validate()
    error_count_dict = wtf_count_errors(wtf_form, log_errors=True)

    # Diagnostics of model before updating with wtform values
    model_before = sa_model_to_dict(model_row)
    wtform_to_model(model_row, wtf_form)
    add_commit_and_log_model(db,
                             model_row,
                             comment='call to wtform_to_model(model_row, wtf_form)',
                             model_before=model_before)
    # todo - need to include logic here to retain the new id that is assigned from adding a new model?
    # looks like the id_incidence in the json is decoupled from the row id_incidence, which can lead to funny behavior
    # when an incidence is added it will get an auto generated id, which needs to propagate tot he wtform and model
    # need to check ahead of time if you are duplicating id so you don't get uniqueness issues
    # will likely break the spread sheet import process on initial refactor ...

    # Determine course of action for successful database update based on which button was submitted
    button = request.form.get('submit_button')

    if button == 'validate_and_submit':
      logger.debug(f"validate_and_submit was pressed")
      if wtf_form.validate():
        return redirect(url_for('index'))
    elif button == 'update_incidence_status':
      logger.debug(f"update_incidence_status was pressed")
      html_content = f"you clicked update_incidence_status"
      # todo - implement the status and notes section
      return render_template('diagnostics.html', html_content=html_content)
      # return render_template('og_carb_notes.html',
      #                        wtf_form=wtf_form,
      #                        crud_type=crud_type,
      #                        error_count_dict=error_count_dict)

  error_count_dict = wtf_count_errors(wtf_form, log_errors=True)

  logger.debug(f"incidence_prep() about to render get template")

  return render_template(template_file,
                         wtf_form=wtf_form,
                         crud_type=crud_type,
                         error_count_dict=error_count_dict,
                         )


if __name__ == '__main__':
  """
  How to run the operator portal app from the EC2

  1. generate token from github for access to tony-held-carb repos:
      - on 2025-04-28 I created the token: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
  2. git clone https://<your-username>:<your-token>@github.com/tony-held-carb/feedback_portal.git
      git clone https://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@github.com/tony-held-carb/feedback_portal.git 
  3. cd source/production/arb/portal
  4. conda deactivate
  5. conda activate mini_conda_01
  6. git pull (<- to update your local repo)
  7. flask run --host=0.0.0.0 -p 2112
  8. open browser to http://10.93.112.44:2112
  """

  # app.run(host="0.0.0.0", port=5150, debug=True)
  app.run()
  # app.run(debug=False, use_reloader=False) # allows pycharm debugger to catch errors
