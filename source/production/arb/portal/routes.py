"""
Blueprint-based route definitions for the ARB Feedback Portal.

This module defines all Flask routes originally found in `app.py`,
now organized under the `main` Blueprint for modularity.

Routes cover:
  - Incidence form creation, editing, and deletion
  - File upload and viewing
  - Portal update log display and export
  - Diagnostics and developer views

Notes:
  - All routes assume that `create_app()` registers the `main` Blueprint.
  - Developer diagnostics are inlined near the end of the module.
"""

import csv
import datetime
import os
from io import StringIO
from pathlib import Path
from urllib.parse import unquote

from flask import Blueprint, Response, abort, current_app, flash, redirect, render_template, request, send_from_directory, \
  url_for  # to access app context
from flask.typing import ResponseReturnValue
from sqlalchemy.ext.automap import AutomapBase
from werkzeug.exceptions import abort

import arb.portal.db_hardcoded
import arb.utils.sql_alchemy
from arb.__get_logger import get_logger
from arb.portal.config.accessors import get_upload_folder
from arb.portal.constants import PLEASE_SELECT
from arb.portal.extensions import db
from arb.portal.globals import Globals
from arb.portal.json_update_util import apply_json_patch_and_log
from arb.portal.sqla_models import PortalUpdate
from arb.portal.startup.runtime_info import LOG_FILE
from arb.portal.utils.db_ingest_util import dict_to_database, upload_and_stage_only, upload_and_update_db, xl_dict_to_database
from arb.portal.utils.db_introspection_util import get_ensured_row
from arb.portal.utils.form_mapper import apply_portal_update_filters
from arb.portal.utils.route_util import incidence_prep
from arb.portal.utils.sector_util import get_sector_info
from arb.portal.wtf_landfill import LandfillFeedback
from arb.portal.wtf_oil_and_gas import OGFeedback
from arb.portal.wtf_upload import UploadForm
from arb.utils.diagnostics import obj_to_html
from arb.utils.json import compute_field_differences, extract_tab_payload, json_load_with_meta, json_save_with_meta
from arb.utils.sql_alchemy import find_auto_increment_value, get_class_from_table_name, get_rows_by_table_name
from arb.utils.wtf_forms_util import get_wtforms_fields, prep_payload_for_json

__version__ = "1.0.0"
logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')

main = Blueprint("main", __name__)


@main.route('/')
def index() -> str:
  """
  Display the homepage with a list of all existing incidence records.

  Queries the 'incidences' table in descending order of ID and renders
  the results in a summary table on the landing page.

  Returns:
    str: Rendered HTML for the homepage with incidence records.
  """

  base: AutomapBase = current_app.base  # type: ignore[attr-defined]
  table_name = 'incidences'
  colum_name_pk = 'id_incidence'
  rows = get_rows_by_table_name(db, base, table_name, colum_name_pk, ascending=False)

  return render_template('index.html', model_rows=rows)


@main.route('/incidence_update/<int:id_>/', methods=('GET', 'POST'))
def incidence_update(id_) -> str | Response:
  """
  Display and edit a specific incidence record by ID.

  Args:
    id_ (int): Primary key of the incidence to edit.

  Returns:
    str|Response: Rendered HTML of the feedback form for the selected incidence,
         or a redirect to the upload page if the ID is missing.

  Raises:
    500 Internal Server Error: If multiple records are found for the same ID.

  Notes:
    - Redirects if the ID is not found in the database.
    - Assumes each incidence ID is unique.
  """

  logger.debug(f"incidence_update called with id= {id_}.")
  base: AutomapBase = current_app.base  # type: ignore[attr-defined]
  table_name = 'incidences'
  table = get_class_from_table_name(base, table_name)

  # get_or_404 uses the tables primary key
  # model_row = db.session.query(table).get_or_404(id_)
  # todo turn this into a get and if it is null, then redirect? to the spreadsheet upload
  # todo consider turning into one_or_none and have error handling
  rows = db.session.query(table).filter_by(id_incidence=id_).all()
  if not rows:
    message = f"A request was made to edit a non-existent id_incidence ({id_}).  Consider uploading the incidence by importing a spreadsheet."
    return redirect(url_for('main.upload_file', message=message))
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
def og_incidence_create() -> Response:
  """
  Create a new dummy Oil & Gas incidence and redirect to its edit form.

  Returns:
    Response: Redirect to the `incidence_update` page for the newly created ID.

  Notes:
    - Dummy data is loaded from `db_hardcoded.get_og_dummy_data()`.
  """
  logger.debug(f"og_incidence_create() - beginning.")
  base: AutomapBase = current_app.base  # type: ignore[attr-defined]
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
  return redirect(url_for('main.incidence_update', id_=id_))


@main.route('/landfill_incidence_create/', methods=('GET', 'POST'))
def landfill_incidence_create() -> Response:
  """
  Create a new dummy Landfill incidence and redirect to its edit form.

  Returns:
    Response: Redirect to the `incidence_update` page for the newly created ID.

  Notes:
    - Dummy data is loaded from `db_hardcoded.get_landfill_dummy_data()`.
  """

  logger.debug(f"landfill_incidence_create called.")
  base: AutomapBase = current_app.base  # type: ignore[attr-defined]
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
  return redirect(url_for('main.incidence_update', id_=id_))


@main.post('/incidence_delete/<int:id_>/')
def incidence_delete(id_) -> Response:
  """
  Delete a specified incidence from the database.

  Args:
    id_ (int): Primary key of the incidence to delete.

  Returns:
    Response: Redirect to the homepage after deletion.

  Notes:
    - Future: consider adding authorization (e.g., CARB password) to restrict access.
  """

  logger.debug(f"Updating database with route incidence_delete for id= {id_}:")
  base: AutomapBase = current_app.base  # type: ignore[attr-defined]

  table_name = 'incidences'
  table = get_class_from_table_name(base, table_name)
  model_row = db.session.query(table).get_or_404(id_)

  # todo - ensure portal changes are properly updated
  arb.utils.sql_alchemy.delete_commit_and_log_model(db,
                                                    model_row,
                                                    comment=f'Deleting incidence row {id_}')
  return redirect(url_for('main.index'))


@main.route('/list_uploads')
def list_uploads() -> str:
  """
  List all files in the upload directory.

  Returns:
    str: Rendered HTML showing all uploaded Excel files available on disk.
  """

  logger.debug(f"in list_uploads")
  upload_folder = get_upload_folder()
  # up_dir = Path("portal/static/uploads")
  # print(f"{type(up_dir)=}: {up_dir=}")
  files = [x.name for x in upload_folder.iterdir() if x.is_file()]
  logger.debug(f"{files=}")

  return render_template('uploads_list.html', files=files)


@main.route('/upload', methods=['GET', 'POST'])
@main.route('/upload/<message>', methods=['GET', 'POST'])
def upload_file(message: str | None = None) -> str | Response:
  """
  Upload a spreadsheet or JSON file and immediately apply it to the database.

  This route handles file uploads (Excel or JSON), converts them into a
  structured format, and applies the contents directly to the database.
  If the upload and update succeed, the user is redirected to the update form.

  Args:
    message (str | None): Optional redirect message to show in the template.

  Returns:
    str | Response: Redirect to incidence update page on success, otherwise
    renders the upload form with error or status messages.
  """
  logger.debug("upload_file route called.")
  base: AutomapBase = current_app.base  # type: ignore[attr-defined]
  form = UploadForm()

  # Decode redirect message, if present
  if message:
    message = unquote(message)
    logger.debug(f"Received redirect message: {message}")

  upload_folder = get_upload_folder()
  logger.debug(f"Files received: {list(request.files.keys())}, upload_folder={upload_folder}")

  if request.method == 'POST':
    try:
      request_file = request.files.get('file')

      if not request_file or not request_file.filename:
        logger.warning("POST received with no file selected.")
        return render_template(
          'upload.html',
          form=form,
          upload_message="No file selected. Please choose a file."
        )

      logger.debug(f"Received uploaded file: {request_file.filename}")

      # Save file and attempt DB ingest
      file_path, id_, sector = upload_and_update_db(db, upload_folder, request_file, base)

      if id_:
        logger.debug(f"Upload successful: id={id_}, sector={sector}. Redirecting to update page.")
        return redirect(url_for('main.incidence_update', id_=id_))

      logger.warning(f"Upload failed schema recognition: {file_path=}")
      return render_template(
        'upload.html',
        form=form,
        upload_message=f"Uploaded file: {file_path.name} — format not recognized."
      )

    except Exception as e:
      logger.exception("Exception occurred during upload or parsing.")
      return render_template(
        'upload.html',
        form=form,
        upload_message="Error: Could not process the uploaded file. Make sure it is closed and try again."
      )

  # GET request: display form
  return render_template('upload.html', form=form, upload_message=message)


@main.route('/upload_staged', methods=['GET', 'POST'])
@main.route('/upload_staged/<message>', methods=['GET', 'POST'])
def upload_file_staged(message: str | None = None) -> str | Response:
  """
  Upload an Excel or JSON file, convert it to JSON, and stage it for review.

  This route handles both GET (form rendering) and POST (file upload) requests.
  Uploaded files are parsed and saved to a staging location, but are NOT applied
  to the database.

  Args:
    message (str | None): Optional message to display on page (from redirect).

  Returns:
    str | Response: HTML response or redirect based on staging outcome.
  """
  logger.debug("upload_file_staged route called.")
  base: AutomapBase = current_app.base  # type: ignore[attr-defined]
  form = UploadForm()

  # Decode optional redirect message
  if message:
    message = unquote(message)
    logger.debug(f"Received redirect message: {message}")

  upload_folder = get_upload_folder()
  logger.debug(f"Request received with files: {list(request.files.keys())}, upload_folder={upload_folder}")

  if request.method == 'POST':
    try:
      request_file = request.files.get('file')

      if not request_file or not request_file.filename:
        logger.warning("POST received with no file selected.")
        return render_template('upload_staged.html', form=form, upload_message="No file selected. Please choose a file.")

      logger.debug(f"Received uploaded file: {request_file.filename}")

      # Save and stage (no DB commit)
      file_path, id_, sector, json_data, staged_filename = upload_and_stage_only(db, upload_folder, request_file, base)

      if id_ is None or not staged_filename:
        logger.warning(f"Staging failed: missing or invalid id_incidence in {file_path.name}")
        return render_template(
          'upload_staged.html',
          form=form,
          upload_message="This file is missing a valid 'Incidence/Emission ID' (id_incidence). "
                         "Please verify the spreadsheet includes that field and try again."
        )

      logger.debug(f"Staged upload successful: id={id_}, sector={sector}, filename={staged_filename}. Redirecting to review page.")
      return redirect(url_for('main.review_staged', id_=id_, filename=staged_filename))

    except Exception as e:
      logger.exception("Exception occurred during staged upload.")
      return render_template(
        'upload_staged.html',
        form=form,
        upload_message="Error: Could not process the uploaded file. Make sure it is closed and try again."
      )

  # GET request: display form
  return render_template('upload_staged.html', form=form, upload_message=message)


@main.route("/review_staged/<int:id_>/<filename>", methods=["GET"])
def review_staged(id_: int, filename: str) -> str | Response:
  """
  Show a diff between a staged upload and the current database row.

  This view compares all keys in the staged JSON payload and marks
  which fields changed. It also passes metadata and supports display
  of unchanged fields for full audit.

  Args:
    id_ (int): ID of the row that was staged for update.
    filename (str): The staged file name to review.

  Returns:
    str: Rendered HTML with row-level differences and actions.
  """
  logger.debug(f"Reviewing staged upload for id={id_}, filename={filename}")

  base: AutomapBase = current_app.base  # type: ignore[attr-defined]
  staging_dir = Path(get_upload_folder()) / "staging"
  staged_json_path = staging_dir / filename

  if not staged_json_path.exists():
    logger.warning(f"Staged JSON file not found: {staged_json_path}")
    return render_template("review_staged.html", error=f"No staged data found for ID {id_}.")

  try:
    staged_data, metadata = json_load_with_meta(staged_json_path)
    staged_payload = extract_tab_payload(staged_data, tab_name="Feedback Form")
  except Exception:
    logger.exception("Error loading staged JSON")
    return render_template("review_staged.html", error="Could not load staged data.")

  model, _, is_new_row = get_ensured_row(
    db=db,
    base=base,
    table_name="incidences",
    primary_key_name="id_incidence",
    id_=id_
  )

  db_json = getattr(model, "misc_json", {}) or {}
  staged_fields = compute_field_differences(new_data=staged_payload, existing_data=db_json)

  if is_new_row:
    logger.info(f"⚠️ Staged ID {id_} did not exist in DB. A blank row was created for review.")

  logger.debug(f"Computed {sum(f['changed'] for f in staged_fields)} changes across {len(staged_fields)} fields")

  return render_template(
    "review_staged.html",
    id_incidence=id_,
    staged_fields=staged_fields,
    is_new_row=is_new_row,
    metadata=metadata,
    error=None,
    filename=filename,
  )


@main.route("/confirm_staged/<int:id_>/<filename>", methods=["POST"])
def confirm_staged(id_: int, filename: str) -> ResponseReturnValue:
  """
  Final confirmation of staged data. This route applies the staged changes to the
  database model and moves the staged JSON to the committed directory.

  The user must explicitly approve field-level overwrites via checkboxes. Only
  approved fields are updated; all others are left unchanged.

  Args:
    id_ (int): The incidence/emission ID being confirmed.
    filename (str): The staged file name being confirmed.

  Returns:
    ResponseReturnValue: Redirect to confirmation or error page.
  """
  import shutil
  from arb.utils.json import extract_tab_payload
  
  # Resolve paths
  root = get_upload_folder()
  staged_path = os.path.join(root, "staging", filename)
  processed_dir = os.path.join(root, "processed")
  os.makedirs(processed_dir, exist_ok=True)
  processed_path = os.path.join(processed_dir, filename)

  # Load staged payload and metadata
  try:
    staged_data, staged_meta = json_load_with_meta(Path(staged_path))
    base_misc_json = staged_meta.get("base_misc_json", {})
  except Exception as e:
    flash(f"Failed to load staged file for ID {id_}: {e}", "danger")
    return redirect(url_for("main.upload_file_staged"))

  # ✅ Extract the actual form data from the staged JSON structure
  # staged_data contains: {'metadata': {...}, 'schemas': {...}, 'tab_contents': {'Feedback Form': {...}}}
  # We need to extract just the form data from tab_contents
  form_data = extract_tab_payload(staged_data, tab_name="Feedback Form")
  if not form_data:
    flash(f"Failed to extract form data from staged file for ID {id_}", "danger")
    return redirect(url_for("main.upload_file_staged"))

  # Get the database model
  base: AutomapBase = current_app.base  # type: ignore[attr-defined]
  table_name = 'incidences'
  table = get_class_from_table_name(base, table_name)
  
  # Get or create the model row
  logger.info(f"[confirm_staged] Getting/creating model row for id_incidence={id_}")
  model_row, _, is_new_row = get_ensured_row(
    db=db,
    base=base,
    table_name=table_name,
    primary_key_name="id_incidence",
    id_=id_
  )
  logger.info(f"[confirm_staged] Model row result: type={type(model_row)}, "
              f"id_incidence={getattr(model_row, 'id_incidence', 'N/A')}, "
              f"is_new_row={is_new_row}")

  # Check for concurrent DB changes
  current_misc_json = getattr(model_row, "misc_json", {}) or {}
  logger.info(f"[confirm_staged] Current misc_json: {current_misc_json}")
  logger.info(f"[confirm_staged] Base misc_json from staging: {base_misc_json}")
  
  if current_misc_json != base_misc_json:
    logger.warning(f"[confirm_staged] Concurrent DB changes detected! "
                   f"current_misc_json != base_misc_json")
    flash("The database was changed by another user before your updates were confirmed. Please review the new database state and reconfirm which fields you wish to update.", "warning")
    return redirect(url_for("main.review_staged", id_=id_, filename=filename))

  # Build update patch only for fields user confirmed
  patch: dict = {}
  logger.info(f"[confirm_staged] Building patch from {len(form_data)} form fields")
  
  for key in form_data:
    checkbox_name = f"confirm_overwrite_{key}"
    confirmed = checkbox_name in request.form

    new_val = form_data[key]
    # Ensure we have a dictionary to work with, even if misc_json is None
    misc_json = getattr(model_row, "misc_json", {}) or {}
    old_val = misc_json.get(key)

    if confirmed or old_val in (None, "", [], {}):
      patch[key] = new_val
      logger.debug(f"[confirm_staged] Added to patch: {key}={new_val} (confirmed={confirmed})")

  logger.info(f"[confirm_staged] Final patch contains {len(patch)} fields: {list(patch.keys())}")

  if not patch:
    logger.warning(f"[confirm_staged] No fields in patch - no changes to save")
    flash("No fields were confirmed for update. No changes saved.", "warning")
    return redirect(url_for("main.upload_file_staged"))

  # 🆕 Prepare patch for JSON serialization (type coercion, datetime conversion, etc.)
  patch = prep_payload_for_json(patch)
  logger.info(f"[confirm_staged] Prepared patch for JSON: {patch}")

  # Apply patch to the database model
  try:
    logger.info(f"[confirm_staged] About to call apply_json_patch_and_log with {len(patch)} fields")
    apply_json_patch_and_log(
      model=model_row,
      updates=patch,
      json_field="misc_json",
      user="anonymous",
      comments=f"Staged update confirmed for ID {id_}"
    )
    logger.info(f"[confirm_staged] ✅ apply_json_patch_and_log completed successfully")
    
    # 🆕 Commit the database transaction to persist changes
    logger.info(f"[confirm_staged] About to commit database session")
    db.session.commit()
    logger.info(f"[confirm_staged] ✅ Database session committed successfully")
    
    # Move the staged JSON file to the processed directory
    shutil.move(staged_path, processed_path)
    logger.info(f"[confirm_staged] ✅ Moved staged file to processed: {processed_path}")
    
    flash(f"Successfully updated record {id_}. {len(patch)} fields changed.", "success")
    
  except Exception as e:
    # Rollback on error to prevent partial commits
    logger.error(f"[confirm_staged] ❌ Error during database update: {e}")
    logger.exception(f"[confirm_staged] Full exception details:")
    db.session.rollback()
    flash(f"Error applying updates for ID {id_}: {e}", "danger")
    return redirect(url_for("main.upload_file_staged"))

  return redirect(url_for("main.upload_file_staged"))


@main.route("/discard_staged_update/<int:id_>", methods=["POST"])
def discard_staged_update(id_: int) -> Response:
  """
  Discard a staged upload file without applying it to the database.

  Args:
    id_ (int): ID of the staged incidence file to discard.

  Returns:
    Response: Redirect to the staged upload page with status message.
  """
  staging_dir = Path(get_upload_folder()) / "staging"
  staged_file = staging_dir / f"{id_}.json"

  try:
    if staged_file.exists():
      staged_file.unlink()
      logger.info(f"✅ Discarded staged upload file: {staged_file}")
      flash(f"Discarded staged file for ID {id_}.", "info")
    else:
      logger.warning(f"⚠️ Tried to discard non-existent staged file: {staged_file}")
      flash(f"No staged file found for ID {id_}.", "warning")

  except Exception as e:
    logger.exception("Error discarding staged file")
    flash(f"Error discarding file: {e}", "danger")

  return redirect(url_for("main.upload_file_staged"))


@main.route('/apply_staged_update/<int:id_>', methods=['POST'])
def apply_staged_update(id_: int):
  """
  Apply a previously staged update to the database.

  Args:
    id_ (int): ID of the incidence row to update.

  Returns:
    Response: Redirect to the incidence update page with status message.

  Notes:
    - Loads the staged JSON file from the staging folder.
    - Applies the JSON to the database using xl_dict_to_database.
    - Deletes the staged file if applied successfully.
  """
  try:
    # staging_dir = Path(current_app.config["UPLOAD_STAGING_FOLDER"])
    staging_dir = Path(get_upload_folder()) / "staging"

    staged_file = staging_dir / f"{id_}.json"

    if not staged_file.exists():
      logger.error(f"Staged file does not exist: {staged_file}")
      flash("Staged file not found.", "danger")
      return redirect(url_for("main.upload_file_staged"))

    xl_dict, _ = json_load_with_meta(staged_file)
    base = current_app.base  # type: ignore[attr-defined]
    final_id, sector = xl_dict_to_database(db, base, xl_dict)

    logger.info(f"Applied staged update for id={final_id}, sector={sector}")

    try:
      staged_file.unlink()
      logger.debug(f"Deleted staged file: {staged_file}")
    except Exception as delete_error:
      logger.warning(f"Could not delete staged file: {delete_error}")

    return redirect(url_for("main.incidence_update", id_=final_id))

  except Exception as e:
    logger.exception("Failed to apply staged update.")
    flash("Error applying update. Please try again.", "danger")
    return redirect(url_for("main.upload_file_staged"))


@main.route("/serve_file/<path:filename>")
def serve_file(filename) -> Response:
  """
  Serve a file from the server's upload directory.

  Args:
    filename (str): Name of the file to serve.

  Returns:
    Response: Sends file content to the browser or triggers download.

  Raises:
    404 Not Found: If the file does not exist on disk.
  """

  upload_folder = get_upload_folder()
  file_path = os.path.join(upload_folder, filename)

  if not os.path.exists(file_path):
    abort(404)

  return send_from_directory(upload_folder, filename)


@main.route("/portal_updates")
def view_portal_updates() -> str:
  """
  Display a table of all updates recorded in `portal_updates`.

  Returns:
    str: Rendered HTML with sortable and filterable update logs.

  Notes:
    - Supports pagination, filtering, and sorting via query parameters.
    - Default sort is descending by timestamp.
  """
  sort_by = request.args.get("sort_by", "timestamp")
  direction = request.args.get("direction", "desc")
  page = int(request.args.get("page", 1))
  per_page = int(request.args.get("per_page", 100))

  query = db.session.query(PortalUpdate)
  query = apply_portal_update_filters(query, PortalUpdate, request.args)

  updates = query.order_by(PortalUpdate.timestamp.desc()).all()

  return render_template(
    "portal_updates.html",
    updates=updates,
    sort_by=sort_by,
    direction=direction,
    page=page,
    per_page=per_page,
    total_pages=1,
    filter_key=request.args.get("filter_key", "").strip(),
    filter_user=request.args.get("filter_user", "").strip(),
    filter_comments=request.args.get("filter_comments", "").strip(),
    filter_id_incidence=request.args.get("filter_id_incidence", "").strip(),
    start_date=request.args.get("start_date", "").strip(),
    end_date=request.args.get("end_date", "").strip(),
  )


@main.route("/portal_updates/export")
def export_portal_updates() -> Response:
  """
  Export filtered portal update logs as a downloadable CSV file.

  Returns:
    Response: CSV content as an attachment.

  Notes:
    - Respects filters set in the `/portal_updates` page.
    - Uses standard CSV headers and UTF-8 encoding.
  """
  query = db.session.query(PortalUpdate)
  query = apply_portal_update_filters(query, PortalUpdate, request.args)

  updates = query.order_by(PortalUpdate.timestamp.desc()).all()

  si = StringIO()
  writer = csv.writer(si)
  writer.writerow(["timestamp", "key", "old_value", "new_value", "user", "comments", "id_incidence"])

  for u in updates:
    writer.writerow([
      u.timestamp,
      u.key,
      u.old_value,
      u.new_value,
      u.user,
      u.comments,
      u.id_incidence or ""
    ])

  return Response(
    si.getvalue(),
    mimetype="text/csv",
    headers={"Content-Disposition": "attachment; filename=portal_updates_export.csv"}
  )


@main.route('/search/', methods=('GET', 'POST'))
def search() -> str:
  """
  Search route triggered by the navigation bar (stub for future use).

  Returns:
    str: Renders a search results page showing the query string.

  Notes:
    - Currently echoes the user-submitted query string.
  """
  logger.debug(f"In search route:")
  logger.debug(f"{request.form=}")
  search_string = request.form.get('navbar_search')
  logger.debug(f"{search_string=}")

  return render_template('search.html',
                         search_string=search_string,
                         )


#####################################################################
# Diagnostic and developer endpoints
#####################################################################

@main.route('/diagnostics')
def diagnostics() -> str:
  """
  Run diagnostics on the 'incidences' table and show the next ID.

  Returns:
    str: Rendered HTML showing auto-increment ID diagnostic.
  """

  logger.info(f"diagnostics() called")

  result = find_auto_increment_value(db, "incidences", "id_incidence")

  html_content = f"<p><strong>Diagnostic Results=</strong></p> <p>{result}</p>"
  return render_template('diagnostics.html',
                         header="Auto-Increment Check",
                         subheader="Next available ID value in the 'incidences' table.",
                         html_content=html_content,
                         modal_title="Success",
                         modal_message="Diagnostics completed successfully.",
                         )


@main.route('/show_dropdown_dict')
def show_dropdown_dict() -> str:
  """
  Display current dropdown and contingent dropdown values.

  Returns:
    str: Rendered HTML table of dropdown structures.

  Notes:
    - Useful for verifying dropdown contents used in WTForms.
  """

  logger.info(f"Determining dropdown dict")
  # update drop-down tables
  Globals.load_drop_downs(current_app, db)
  result1 = obj_to_html(Globals.drop_downs)
  result2 = obj_to_html(Globals.drop_downs_contingent)
  result = (f"<p><strong>Globals.drop_downs=</strong></p> <p>{result1}</p>"
            f"<p><strong>Globals.drop_downs_contingent=</strong></p> <p>{result2}</p>")
  return render_template('diagnostics.html',
                         header="Dropdown Dictionaries",
                         subheader="Loaded dropdown values and contingent mappings.",
                         html_content=result,
                         )


@main.route('/show_database_structure')
def show_database_structure() -> str:
  """
  Show structure of all reflected database columns.

  Returns:
    str: Rendered HTML with column type information for all tables.
  """

  logger.info(f"Displaying database structure")
  result = obj_to_html(Globals.db_column_types)
  result = f"<p><strong>Postgres Database Structure=</strong></p> <p>{result}</p>"
  return render_template('diagnostics.html',
                         header="Database Structure Overview",
                         subheader="Reflecting SQLAlchemy model metadata.",
                         html_content=result,
                         )


@main.route('/show_feedback_form_structure')
def show_feedback_form_structure() -> str:
  """
  Inspect and display WTForms structure for feedback forms.

  Returns:
    str: Rendered HTML showing field names/types for OG and Landfill forms.

  Notes:
    - Uses `get_wtforms_fields()` utility to introspect each form.
  """
  logger.info(f"Displaying wtforms structure as a diagnostic")

  form1 = OGFeedback()
  fields1 = get_wtforms_fields(form1)
  result1 = obj_to_html(fields1)

  form2 = LandfillFeedback()
  fields2 = get_wtforms_fields(form2)
  result2 = obj_to_html(fields2)

  result = (f"<p><strong>WTF OGFeedback Form Structure=</strong></p> <p>{result1}</p>"
            f"<p><strong>WTF LandfillFeedback Form Structure=</strong></p> <p>{result2}</p>")

  return render_template('diagnostics.html',
                         header="WTForms Feedback Form Structure",
                         subheader="Inspecting field mappings in Oil & Gas and Landfill feedback forms.",
                         html_content=result,
                         )


@main.route('/show_log_file')
def show_log_file() -> str:
  """
  Display the contents of the server's current log file.

  Returns:
    str: Rendered HTML with the full log file shown inside a <pre> block.

  Notes:
    - Useful for debugging in development or staging.
  """

  logger.info(f"Displaying the log file as a diagnostic")
  with open(LOG_FILE, 'r') as file:
    file_content = file.read()

  # result = obj_to_html(file_content)
  result = f"<p><strong>Logger file content=</strong></p> <p><pre>{file_content}</pre></p>"
  return render_template('diagnostics.html',
                         header="Log File Contents",
                         # subheader="Full log output from the running server instance.",
                         html_content=result,
                         )
