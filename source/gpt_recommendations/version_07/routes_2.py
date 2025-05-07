"""
Blueprint-based routes for the main application.

This file contains all route definitions originally in app.py,
migrated to a Flask Blueprint for modularity.

Routes are attached to the 'main' Blueprint.

Notes:
    * All prior documentation, TODOs, and inline comments are retained.
    * Requires that create_app() in app.py registers this blueprint.

"""

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for  # to access app context
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

  return render_template('index.html', model_rows=rows)


@main.route('/incidence_update/<int:id_>/', methods=('GET', 'POST'))
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
                        default_dropdown=PLEASE_SELECT)


@main.route('/og_incidence_create/', methods=('GET', 'POST'))
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


@main.route('/landfill_incidence_create/', methods=('GET', 'POST'))
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


@main.post('/incidence_delete/<int:id_>/')
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

  return render_template('search.html',
                         search_string=search_string,
                         )


@main.route('/diagnostics')
def diagnostics():
  """
  Flask route to show diagnostic info for code in development.
  """
  logger.info(f"diagnostics() called")

  result = find_auto_increment_value(db, "incidences", "id_incidence")

  html_content = f"<p><strong>Diagnostic Results=</strong></p> <p>{result}</p>"
  return render_template('diagnostics.html', html_content=html_content)


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

  form1 = OGFeedback()
  fields1 = get_wtforms_fields(form1)
  result1 = obj_to_html(fields1)

  form2 = LandfillFeedback()
  fields2 = get_wtforms_fields(form2)
  result2 = obj_to_html(fields2)

  result = (f"<p><strong>WTF OGFeedback Form Structure=</strong></p> <p>{result1}</p>"
            f"<p><strong>WTF LandfillFeedback Form Structure=</strong></p> <p>{result2}</p>")

  return render_template('diagnostics.html', html_content=result)


@main.route('/show_log_file')
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

  return render_template('list_uploads.html', files=files)


@main.route('/upload', methods=['GET', 'POST'])
@main.route('/upload/<message>', methods=['GET', 'POST'])
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


@main.route('/background/', methods=('GET', 'POST'))
def background():
  """
  Flask route to experiment with differing background approaches.
  """
  logger.debug(f"In background route:")

  return render_template('background.html')


@main.route('/sticky/', methods=('GET', 'POST'))
def sticky():
  """
  Flask route to experiment with differing formatting structures.
  """
  logger.debug(f"In sticky route:")

  return render_template('sticky.html')


@main.route('/modify_json_content')
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

  return '<h1>Dummy Feedback Form Data Created</h1>'


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

# ------------------------------------------------------------
# Functions that return render_template
# (all other helper functions should be considered moving to app_util.py)
# ------------------------------------------------------------
