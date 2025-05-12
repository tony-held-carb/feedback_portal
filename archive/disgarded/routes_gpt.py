"""
Blueprint-based routes for the main application.

This file contains all route definitions originally in app.py,
migrated to a Flask Blueprint for modularity.

Routes are attached to the 'main' Blueprint.

Notes:
    * All prior documentation, TODOs, and inline comments are retained.
    * Requires that create_app() in app.py registers this blueprint.
"""

import os
from datetime import datetime
from urllib.parse import unquote
from zoneinfo import ZoneInfo

from flask import (Blueprint, abort, current_app, redirect, render_template, request, send_from_directory, url_for)
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.attributes import flag_modified

import arb.__get_logger as get_logger
import arb.portal.db_hardcoded
import arb.utils.sql_alchemy
from arb.portal.app_util import (
  dict_to_database,
  get_sector_info,
  upload_and_update_db,
)
from arb.portal.constants import PLEASE_SELECT
from arb.portal.extensions import db
from arb.portal.globals import Globals
from arb.utils.diagnostics import obj_to_html
from arb.utils.sql_alchemy import (
  add_commit_and_log_model,
  find_auto_increment_value,
  get_class_from_table_name,
  get_rows_by_table_name,
  sa_model_diagnostics,
  sa_model_to_dict,
)
from arb.utils.wtf_forms_util import (
  get_wtforms_fields,
  initialize_drop_downs,
  model_to_wtform,
  validate_no_csrf,
  wtf_count_errors,
  wtform_to_model,
)

__version__ = "1.0.0"
logger, pp_log = get_logger.get_logger(__name__, __file__)

main = Blueprint("main", __name__)


@main.route("/")
def index():
  """
  Render the home page that lists all incidence records.

  Returns:
      str: Rendered HTML template with incidence records.
  """
  base: DeclarativeMeta = current_app.base  # type: ignore[attr-defined]
  table_name = "incidences"
  column_name_pk = "id_incidence"

  rows = get_rows_by_table_name(
    db,
    base,
    table_name,
    column_name_pk,
    ascending=False,
  )
  return render_template("index.html", model_rows=rows)


@main.route("/incidence_update/<int:id_>/", methods=("GET", "POST"))
def incidence_update(id_: int):
  """
  Update an existing incidence by rendering its feedback form.

  Args:
      id_ (int): Primary key of the incidence.

  Returns:
      str: Rendered HTML feedback form, or redirects if not found.
  """
  logger.debug(f"incidence_update called with id= {id_}.")
  base: DeclarativeMeta = current_app.base  # type: ignore[attr-defined]
  table_name = "incidences"
  table = get_class_from_table_name(base, table_name)

  rows = db.session.query(table).filter_by(id_incidence=id_).all()

  if not rows:
    message = (
      f"A request was made to edit a non-existent id_incidence ({id_}). "
      "Consider uploading the incidence by importing a spreadsheet."
    )
    return redirect(url_for("main.upload_file", message=message))

  if len(rows) > 1:
    abort(500, description=f"Multiple rows found for id={id_}")

  model_row = rows[0]
  sector, sector_type = get_sector_info(db, base, id_)

  logger.debug("calling incidence_prep()")
  return incidence_prep(
    model_row,
    crud_type="update",
    sector_type=sector_type,
    default_dropdown=PLEASE_SELECT,
  )


@main.route("/og_incidence_create/", methods=("GET", "POST"))
def og_incidence_create():
  """
  Create a new Oil & Gas incidence entry using dummy data.

  Returns:
      werkzeug.wrappers.Response: Redirect to the update page for new incidence.
  """
  logger.debug("og_incidence_create() - beginning.")
  base: DeclarativeMeta = current_app.base  # type: ignore[attr-defined]
  table_name = "incidences"
  col_name = "misc_json"

  data_dict = arb.portal.db_hardcoded.get_og_dummy_data()

  id_ = dict_to_database(
    db,
    base,
    data_dict,
    table_name=table_name,
    json_field=col_name,
  )

  logger.debug("og_incidence_create() - leaving.")
  return redirect(url_for("main.incidence_update", id_=id_))


@main.route("/landfill_incidence_create/", methods=("GET", "POST"))
def landfill_incidence_create():
  """
  Create a new Landfill incidence entry using dummy data.

  Returns:
      werkzeug.wrappers.Response: Redirect to the update page for new incidence.
  """
  logger.debug("landfill_incidence_create() called.")
  base: DeclarativeMeta = current_app.base  # type: ignore[attr-defined]
  table_name = "incidences"
  col_name = "misc_json"

  data_dict = arb.portal.db_hardcoded.get_landfill_dummy_data()

  id_ = dict_to_database(
    db,
    base,
    data_dict,
    table_name=table_name,
    json_field=col_name,
  )

  logger.debug("landfill_incidence_create() - leaving.")
  return redirect(url_for("main.incidence_update", id_=id_))


@main.post("/incidence_delete/<int:id_>/")
def incidence_delete(id_: int):
  """
  Delete an incidence from the database by its ID.

  Notes:
      * This endpoint deletes rows from the database.
        In production, it may require authentication to prevent accidental deletion.

  Args:
      id_ (int): Primary key of the incidence.

  Returns:
      werkzeug.wrappers.Response: Redirect to index page.
  """
  logger.debug(f"incidence_delete() called for id= {id_}")
  base: DeclarativeMeta = current_app.base  # type: ignore[attr-defined]
  table_name = "incidences"
  table = get_class_from_table_name(base, table_name)

  model_row = db.session.query(table).get_or_404(id_)

  arb.utils.sql_alchemy.delete_commit_and_log_model(
    db,
    model_row,
    comment=f"Deleting incidence row {id_}",
  )

  return redirect(url_for("main.index"))


@main.route("/search/", methods=("GET", "POST"))
def search():
  """
  Perform a basic search using the navbar.

  Returns:
      str: Rendered HTML showing search input (for future implementation).
  """
  logger.debug("In search route:")
  logger.debug(f"{request.form=}")
  search_string = request.form.get("navbar_search")
  logger.debug(f"{search_string=}")

  return render_template("search.html", search_string=search_string)


@main.route("/diagnostics")
def diagnostics():
  """
  Show internal auto-increment diagnostic for the 'incidences' table.

  Returns:
      str: Rendered HTML showing diagnostic output.
  """
  logger.info("diagnostics() called")
  result = find_auto_increment_value(db, "incidences", "id_incidence")
  html_content = f"<p><strong>Diagnostic Results=</strong></p> <p>{result}</p>"
  return render_template("diagnostics.html", html_content=html_content)


@main.route("/show_dropdown_dict")
def show_dropdown_dict():
  """
  Show HTML rendering of drop-down structures loaded into Globals.

  Returns:
      str: Rendered HTML with drop-downs and contingent values.
  """
  logger.info("Determining dropdown dict")
  Globals.load_drop_downs(current_app, db)

  result1 = obj_to_html(Globals.drop_downs)
  result2 = obj_to_html(Globals.drop_downs_contingent)

  result = (
    f"<p><strong>Globals.drop_downs=</strong></p> <p>{result1}</p>"
    f"<p><strong>Globals.drop_downs_contingent=</strong></p> <p>{result2}</p>"
  )
  return render_template("diagnostics.html", html_content=result)


@main.route("/show_database_structure")
def show_database_structure():
  """
  Display HTML rendering of the application's database schema.

  Returns:
      str: Rendered HTML with table and column information.
  """
  logger.info("Displaying database structure")
  result = obj_to_html(Globals.db_column_types)
  result = f"<p><strong>Postgres Database Structure=</strong></p> <p>{result}</p>"
  return render_template("diagnostics.html", html_content=result)


@main.route("/show_feedback_form_structure")
def show_feedback_form_structure():
  """
  Show form field structures for both feedback form types.

  Returns:
      str: Rendered HTML comparing WTForms structures.
  """
  from arb.portal.wtf_forms import OGFeedback, LandfillFeedback

  logger.info("Displaying wtforms structure as a diagnostic")

  form1 = OGFeedback()
  fields1 = get_wtforms_fields(form1)
  result1 = obj_to_html(fields1)

  form2 = LandfillFeedback()
  fields2 = get_wtforms_fields(form2)
  result2 = obj_to_html(fields2)

  result = (
    f"<p><strong>WTF OGFeedback Form Structure=</strong></p> <p>{result1}</p>"
    f"<p><strong>WTF LandfillFeedback Form Structure=</strong></p> <p>{result2}</p>"
  )
  return render_template("diagnostics.html", html_content=result)


@main.route("/show_log_file")
def show_log_file():
  """
  Display contents of the log file for diagnostics.

  Returns:
      str: Rendered HTML showing contents of the log file.
  """
  logger.info("Displaying the log file as a diagnostic")

  with open("logs/flask.log", "r") as file:
    file_content = file.read()

  result = f"<p><strong>Logger file content=</strong></p> <p><pre>{file_content}</pre></p>"
  return render_template("diagnostics.html", html_content=result)


@main.route("/list_uploads")
def list_uploads():
  """
  List all files currently in the configured UPLOAD_FOLDER.

  Returns:
      str: Rendered HTML listing file names.
  """
  logger.debug("in list_uploads")
  upload_folder = current_app.config["UPLOAD_FOLDER"]
  files = [x.name for x in upload_folder.iterdir() if x.is_file()]
  logger.debug(f"{files=}")

  return render_template("list_uploads.html", files=files)


@main.route("/uploads/<path:filename>")
def uploaded_file(filename: str):
  """
  Serve uploaded file directly from the server's upload directory.

  Args:
      filename (str): File name relative to the uploads folder.

  Returns:
      werkzeug.wrappers.Response: Flask file response or 404 if not found.
  """
  upload_folder = current_app.config["UPLOAD_FOLDER"]
  file_path = os.path.join(upload_folder, filename)

  if not os.path.exists(file_path):
    abort(404)

  return send_from_directory(upload_folder, filename)


@main.route("/upload", methods=["GET", "POST"])
@main.route("/upload/<message>", methods=["GET", "POST"])
def upload_file(message: str | None = None):
  """
  Upload a file from the client and attempt to parse and commit it to the database.

  Args:
      message: Optional URL-encoded string passed as a message.

  Returns:
      str: Rendered template or redirect after upload.
  """
  base: DeclarativeMeta = current_app.base  # type: ignore[attr-defined]

  if message:
    message = unquote(message)
    logger.debug(f"upload_file() called with message: {message}")

  upload_dir = current_app.config["UPLOAD_FOLDER"]
  logger.debug(
    f"Request to upload file to server:\n\t{request.files=}\n\t{upload_dir=}"
  )

  if request.method == "POST":
    if "file" not in request.files or request.files["file"].filename == "":
      return redirect(request.url)

    request_file = request.files["file"]
    logger.debug(f"{request_file=}")

    if request_file:
      file_name, id_, sector = upload_and_update_db(
        db, upload_dir, request_file, base
      )
      logger.debug(f"{sector=}")

      if id_:
        logger.debug(f"upload_file(): redirecting to update {id_=}")
        return redirect(url_for("main.incidence_update", id_=id_))
      else:
        logger.debug(f"upload_file(): Not feedback format. {file_name=}")
        return render_template(
          "upload.html",
          upload_message=f"Successfully uploaded file: {file_name.name}",
        )

  return render_template("upload.html", upload_message=message)


def incidence_prep(
    model_row,
    crud_type: str,
    sector_type: str,
    default_dropdown: str = "Please Select",
):
  """
  Helper function to render feedback form pages based on incidence model and sector.

  Args:
      model_row: SQLAlchemy model row for incidence.
      crud_type: 'create' or 'update'.
      sector_type: 'Oil & Gas' or 'Landfill'.
      default_dropdown: Default text for unset select fields.

  Returns:
      str: Rendered feedback HTML page.
  """
  from arb.portal.wtf_forms import OGFeedback, LandfillFeedback

  logger.debug(f"incidence_prep() called with {crud_type=}, {sector_type=}")
  sa_model_diagnostics(model_row)

  if sector_type == "Oil & Gas":
    logger.debug("Using Oil & Gas Feedback Form")
    wtf_form = OGFeedback()
    template_file = "og_feedback.html"
  elif sector_type == "Landfill":
    logger.debug("Using Landfill Feedback Form")
    wtf_form = LandfillFeedback()
    template_file = "landfill_feedback.html"
  else:
    raise ValueError(f"Unknown sector type: '{sector_type}'.")

  if request.method == "GET":
    model_to_wtform(model_row, wtf_form)

    if crud_type == "update":
      validate_no_csrf(wtf_form)

  initialize_drop_downs(wtf_form, default=default_dropdown)

  if request.method == "POST":
    wtf_form.validate()
    error_count_dict = wtf_count_errors(wtf_form, log_errors=True)

    model_before = sa_model_to_dict(model_row)
    wtform_to_model(model_row, wtf_form)

    add_commit_and_log_model(
      db,
      model_row,
      comment="call to wtform_to_model(model_row, wtf_form)",
      model_before=model_before,
    )

    button = request.form.get("submit_button")

    if button == "validate_and_submit":
      logger.debug("validate_and_submit was pressed")
      if wtf_form.validate():
        return redirect(url_for("main.index"))

    elif button == "update_incidence_status":
      logger.debug("update_incidence_status was pressed")
      html_content = "you clicked update_incidence_status"
      return render_template("diagnostics.html", html_content=html_content)

  error_count_dict = wtf_count_errors(wtf_form, log_errors=True)

  logger.debug("Rendering feedback form template")
  return render_template(
    template_file,
    wtf_form=wtf_form,
    crud_type=crud_type,
    error_count_dict=error_count_dict,
  )


@main.route("/modify_json_content")
def modify_json_content():
  """
  Demonstrates how to update a JSON field in a Postgres JSONB column.

  Notes:
      - SQLAlchemy requires `flag_modified` to persist changes to JSON columns.
      - This example modifies a hardcoded row with id_incidence=5.

  Returns:
      dict: Modified JSON content from the model.
  """
  base: DeclarativeMeta = current_app.base  # type: ignore[attr-defined]
  id_incidence = 5  # hardcoded test case

  incidences = base.classes.incidences
  session = db.session

  model = session.query(incidences).get(id_incidence)
  logger.debug(f"{model=}")

  json_content = model.misc_json
  time_stamp = datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d %H:%M:%S")
  json_content["time_stamp"] = time_stamp

  model.misc_json = json_content
  flag_modified(model, "misc_json")
  db.session.add(model)
  db.session.commit()

  return json_content


@main.route("/add_form_dummy_data")
def add_form_dummy_data():
  """
  Insert hardcoded dummy data into the incidence table.

  Returns:
      str: Confirmation message.
  """
  logger.info("Adding dummy data for feedback forms")
  base: DeclarativeMeta = current_app.base  # type: ignore[attr-defined]

  arb.portal.db_hardcoded.add_og_dummy_data(db, base, "incidences")
  return "<h1>Dummy Feedback Form Data Created</h1>"


@main.route("/drag_and_drop", methods=["GET", "POST"])
def drag_and_drop_01():
  """
  Basic drag-and-drop file upload interface (demo only).

  Returns:
      str: Rendered drag-and-drop upload form.
  """
  if request.method == "POST":
    if "file" not in request.files:
      return redirect(request.url)

    file = request.files["file"]
    if file.filename == "":
      return redirect(request.url)

    if file:
      file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], file.filename))
      return redirect(url_for("main.drag_and_drop_01"))

  return render_template("drag_and_drop_01.html")


@main.route("/run_sql_script")
def run_sql_script():
  """
  (Deprecated) Execute a SQL script to seed the database.

  Returns:
      str: Notice that this route is deprecated.
  """
  return "This script is no longer in service - it was originally designed for sqlite"


@main.route("/background/", methods=["GET", "POST"])
def background():
  """
  Experimental route for testing background color formatting.

  Returns:
      str: Rendered HTML page with background experiments.
  """
  logger.debug("In background route")
  return render_template("background.html")


@main.route("/sticky/", methods=["GET", "POST"])
def sticky():
  """
  Experimental route for testing sticky layout behavior.

  Returns:
      str: Rendered HTML page for sticky layout demo.
  """
  logger.debug("In sticky route")
  return render_template("sticky.html")


def run_diagnostics():
  """
  Run offline diagnostics for key route logic and helper functions.

  This diagnostic is intended for local development. It performs static,
  non-Flask-context logic checks and prints results to stdout.

  Example:
      >>> if __name__ == "__main__":
      >>>     run_diagnostics()
  """

  print("\n[RUNNING ROUTE MODULE DIAGNOSTICS]")

  # Test: simulate drop-down loading
  try:
    print("\n[TEST] Simulate dropdown structure generation...")
    from arb.portal.globals import Globals
    Globals.drop_downs = {"example_key": ["A", "B"]}
    Globals.drop_downs_contingent = {"key_contingent_on_base": {"A": ["X", "Y"]}}

    assert "example_key" in Globals.drop_downs
    assert isinstance(Globals.drop_downs["example_key"], list)
    print("✔ drop_down structures loaded correctly")
  except Exception as e:
    print(f"✖ drop_down structure test failed: {e}")

  # Test: simulate WTForms field extraction
  try:
    print("\n[TEST] Simulate WTForms field extraction...")
    from arb.portal.wtf_forms import OGFeedback
    form = OGFeedback()
    fields = get_wtforms_fields(form)
    assert isinstance(fields, list)
    print(f"✔ Extracted {len(fields)} WTForm fields from OGFeedback")
  except Exception as e:
    print(f"✖ WTForms field test failed: {e}")

  # Test: simulate object HTML rendering
  try:
    print("\n[TEST] Simulate HTML rendering via obj_to_html...")
    test_obj = {"a": 1, "b": [2, 3]}
    html = obj_to_html(test_obj)
    assert isinstance(html, str) and "<" in html
    print("✔ obj_to_html returned HTML string")
  except Exception as e:
    print(f"✖ obj_to_html test failed: {e}")

  # Test: mock feedback form prep
  try:
    print("\n[TEST] Simulate form prep with dummy data...")

    class DummyRow:
      misc_json = {"sector": "Oil & Gas"}

      def __repr__(self): return "DummyRow()"

    dummy_row = DummyRow()
    output = sa_model_to_dict(dummy_row)
    assert isinstance(output, dict)
    print("✔ sa_model_to_dict mock works with dummy row")
  except Exception as e:
    print(f"✖ Form prep simulation failed: {e}")

  print("\n[DIAGNOSTICS COMPLETE]\n")


if __name__ == "__main__":
  run_diagnostics()
