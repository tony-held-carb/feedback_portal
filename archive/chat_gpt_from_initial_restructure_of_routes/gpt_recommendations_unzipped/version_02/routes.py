"""
Blueprint-based routes for the main application.

This file contains all route definitions originally in app.py,
migrated to a Flask Blueprint for modularity.

Routes are attached to the 'main' Blueprint.

Notes:
    * All prior documentation, TODOs, and inline comments are retained.
    * Requires that create_app() in app.py registers this blueprint.

"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import current_app  # to access app context
from werkzeug.exceptions import abort

# Add any additional imports needed from other local modules
# e.g. from .models import db, SomeModel

main = Blueprint("main", __name__)



@main.route('/')
def index():
  """
  Flask route to the root of web portal, currently lists incidences.
  """
  table_name = 'incidences'
  colum_name_pk = 'id_incidence'
  rows = get_rows_by_table_name(db, base, table_name, colum_name_pk, ascending=False)

@main.route('/incidence_update/<int:id_>/', methods=('GET', 'POST'))
def incidence_update(id_):
  """
  Flask route to update an existing incidence.
  """

@main.route('/og_incidence_create/', methods=('GET', 'POST'))
def og_incidence_create():
  """
  Flask route to create new Oil & Gas incidence via web interface.
  """
  logger.debug(f"og_incidence_create() - beginning.")
  table_name = 'incidences'
  col_name = 'misc_json'

@main.route('/landfill_incidence_create/', methods=('GET', 'POST'))
def landfill_incidence_create():
  """
  Flask route to create new Landfill incidence via web interface.
  """
  logger.debug(f"landfill_incidence_create called.")
  table_name = 'incidences'
  col_name = 'misc_json'

@main.route('/search/', methods=('GET', 'POST'))
def search():
  """
  Flask route to conduct a search from the nav bar.
  Currently, in development and will only echo the search string.
  """
  logger.debug(f"In search route:")
  logger.debug(f"{request.form=}")
  search_string = request.form.get('navbar_search')
  logger.debug(f"{search_string=}")

@main.route('/diagnostics')
def diagnostics():
  """
  Flask route to show diagnostic info for code in development.
  """
  logger.info(f"diagnostics() called")

@main.route('/show_dropdown_dict')
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

@main.route('/show_database_structure')
def show_database_structure():
  """
  Flask route to show database structure as a diagnostic
  """
  logger.info(f"Displaying database structure")
  result = obj_to_html(Globals.db_column_types)
  result = f"<p><strong>Postgres Database Structure=</strong></p> <p>{result}</p>"
  return render_template('diagnostics.html', html_content=result)

@main.route('/show_feedback_form_structure')
def show_feedback_form_structure():
  """
  Flask route to show wtforms structure as a diagnostic.
  """
  from arb.portal.wtf_forms import OGFeedback, LandfillFeedback
  logger.info(f"Displaying wtforms structure as a diagnostic")

@main.route('/show_log_file')
def show_log_file():
  """
  Flask route to show the log file as a diagnostic.
  """
  logger.info(f"Displaying the log file as a diagnostic")
  with open('logs/operator_portal.log', 'r') as file:
    file_content = file.read()

@main.route('/list_uploads')
def list_uploads():
  """
  Flask route to list files in the uploads folder.
  """
  logger.debug(f"in list_uploads")
  up_dir = Path("static/uploads")
  # print(f"{type(up_dir)=}: {up_dir=}")
  files = [x.name for x in up_dir.iterdir() if x.is_file()]
  logger.debug(f"{files=}")

@main.route('/upload/<message>', methods=['GET', 'POST'])
def upload_file(message=None):
  """
  Flask route to upload file from client to server.

@main.route('/background/', methods=('GET', 'POST'))
def background():
  """
  Flask route to experiment with differing background approaches.
  """
  logger.debug(f"In background route:")

@main.route('/sticky/', methods=('GET', 'POST'))
def sticky():
  """
  Flask route to experiment with differing formatting structures.
  """
  logger.debug(f"In sticky route:")

@main.route('/modify_json_content')
def modify_json_content():
  """
  Flask route to demonstrate how to update a json field in a postgres column.

@main.route('/run_sql_script')
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

@main.route('/add_form_dummy_data')
def add_form_dummy_data():
  """
  Flask route to add random dummy oil and gas data to the incidence table for diagnostics.
  """
  logger.info(f"Adding dummy data for feedback forms")
  arb.portal.db_hardcoded.add_og_dummy_data(db, base, 'incidences')

@main.route('/drag_and_drop', methods=['GET', 'POST'])
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