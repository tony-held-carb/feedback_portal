"""
Blueprint-based route definitions for the ARB Feedback Portal.

This module defines all Flask routes originally found in `app.py`,
now organized under the `main` Blueprint for modularity.

Args:
  None

Returns:
  None

Attributes:
  main (Blueprint): Flask Blueprint for all portal routes.
  logger (logging.Logger): Logger instance for this module.

Examples:
  from arb.portal.routes import main
  app.register_blueprint(main)

Notes:
  - All routes assume that `create_app()` registers the `main` Blueprint.
  - Developer diagnostics are inlined near the end of the module.
"""

import csv
import datetime
import os
import logging
from io import StringIO
from pathlib import Path
from typing import Any, Union
from urllib.parse import unquote

from flask import Blueprint, Response, abort, current_app, flash, redirect, render_template, request, send_from_directory, \
  url_for  # to access app context
from flask.typing import ResponseReturnValue
from sqlalchemy.ext.automap import AutomapBase
from werkzeug.exceptions import abort

import arb.portal.db_hardcoded
import arb.utils.sql_alchemy
from arb.portal.config.accessors import get_upload_folder
from arb.portal.constants import PLEASE_SELECT
from arb.portal.extensions import db
from arb.portal.globals import Globals
from arb.portal.json_update_util import apply_json_patch_and_log
from arb.portal.sqla_models import PortalUpdate
from arb.portal.startup.runtime_info import LOG_FILE
from arb.portal.utils.db_ingest_util import dict_to_database, extract_tab_and_sector, upload_and_stage_only, upload_and_update_db, \
  xl_dict_to_database
from arb.portal.utils.db_introspection_util import get_ensured_row
from arb.portal.utils.form_mapper import apply_portal_update_filters
from arb.portal.utils.route_util import incidence_prep
from arb.portal.utils.sector_util import get_sector_info
from arb.portal.wtf_landfill import LandfillFeedback
from arb.portal.wtf_oil_and_gas import OGFeedback
from arb.portal.wtf_upload import UploadForm
from arb.utils.diagnostics import obj_to_html
from arb.utils.file_io import read_file_reverse
from arb.utils.json import compute_field_differences, json_load_with_meta
from arb.utils.sql_alchemy import find_auto_increment_value, get_class_from_table_name, get_rows_by_table_name
from arb.utils.wtf_forms_util import get_wtforms_fields, prep_payload_for_json
from arb.portal.utils.route_util import generate_upload_diagnostics, format_diagnostic_message, generate_staging_diagnostics

__version__ = "1.0.0"
logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')

main = Blueprint("main", __name__)


@main.route('/')
def index() -> str:
  """
  Display the homepage with a list of all existing incidence records.

  Args:
    None

  Returns:
    str: Rendered HTML for the homepage with incidence records.

  Examples:
    # In browser: GET /
    # Returns: HTML page with table of incidences
  """

  base: AutomapBase = current_app.base  # type: ignore[attr-defined]
  table_name = 'incidences'
  colum_name_pk = 'id_incidence'
  rows = get_rows_by_table_name(db, base, table_name, colum_name_pk, ascending=False)

  return render_template('index.html', model_rows=rows)


@main.route('/incidence_update/<int:id_>/', methods=('GET', 'POST'))
def incidence_update(id_: int) -> Union[str, Response]:
  """
  Display and edit a specific incidence record by ID.

  Args:
    id_ (int): Primary key of the incidence to edit.

  Returns:
    str|Response: Rendered HTML of the feedback form for the selected incidence,
         or a redirect to the upload page if the ID is missing.

  Raises:
    500 Internal Server Error: If multiple records are found for the same ID.

  Examples:
    # In browser: GET /incidence_update/123/
    # Returns: HTML form for editing incidence 123

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
  if table is None:
    abort(500, description="Could not get table class for incidences")

  # Type cast to help with SQLAlchemy typing
  table_class = table  # type: Any
  rows = db.session.query(table_class).filter_by(id_incidence=id_).all()
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

  Args:
    None

  Returns:
    Response: Redirect to the `incidence_update` page for the newly created ID.

  Examples:
    # In browser: POST /og_incidence_create/
    # Redirects to: /incidence_update/<new_id>/

  Notes:
    - Dummy data is loaded from `db_hardcoded.get_og_dummy_form_data()`.
  """
  logger.debug(f"og_incidence_create() - beginning.")
  base: AutomapBase = current_app.base  # type: ignore[attr-defined]
  table_name = 'incidences'
  col_name = 'misc_json'

  data_dict = arb.portal.db_hardcoded.get_og_dummy_form_data()

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

  Args:
    None

  Returns:
    Response: Redirect to the `incidence_update` page for the newly created ID.

  Examples:
    # In browser: POST /landfill_incidence_create/
    # Redirects to: /incidence_update/<new_id>/

  Notes:
    - Dummy data is loaded from `db_hardcoded.get_landfill_dummy_form_data()`.
  """

  logger.debug(f"landfill_incidence_create called.")
  base: AutomapBase = current_app.base  # type: ignore[attr-defined]
  table_name = 'incidences'
  col_name = 'misc_json'

  data_dict = arb.portal.db_hardcoded.get_landfill_dummy_form_data()

  id_ = dict_to_database(db,
                         base,
                         data_dict,
                         table_name=table_name,
                         json_field=col_name,
                         )

  logger.debug(f"landfill_incidence_create() - leaving.")
  return redirect(url_for('main.incidence_update', id_=id_))


@main.post('/incidence_delete/<int:id_>/')
def incidence_delete(id_: int) -> ResponseReturnValue:
  """
  Delete a specified incidence from the database.

  Args:
    id_ (int): Primary key of the incidence to delete.

  Returns:
    Response: Redirect to the homepage after deletion.

  Examples:
    # In browser: POST /incidence_delete/123/
    # Redirects to: /

  Notes:
    - Future: consider adding authorization (e.g., CARB password) to restrict access.
  """

  logger.debug(f"Updating database with route incidence_delete for id= {id_}:")
  base: AutomapBase = current_app.base  # type: ignore[attr-defined]

  table_name = 'incidences'
  table = get_class_from_table_name(base, table_name)
  if table is None:
    abort(500, description="Could not get table class for incidences")

  # Type cast to help with SQLAlchemy typing
  table_class = table  # type: Any
  model_row = db.session.query(table_class).get_or_404(id_)

  # todo - ensure portal changes are properly updated
  arb.utils.sql_alchemy.delete_commit_and_log_model(db,
                                                    model_row,
                                                    comment=f'Deleting incidence row {id_}')
  return redirect(url_for('main.index'))


@main.route('/list_uploads')
def list_uploads() -> str:
  """
  List all files in the upload directory.

  Args:
    None

  Returns:
    str: Rendered HTML showing all uploaded Excel files available on disk.

  Examples:
    # In browser: GET /list_uploads
    # Returns: HTML page listing uploaded files
  """

  logger.debug(f"in list_uploads")
  upload_folder = get_upload_folder()
  # up_dir = Path("portal/static/uploads")
  # print(f"{type(up_dir)=}: {up_dir=}")
  files = [x.name for x in upload_folder.iterdir() if x.is_file()]
  logger.debug(f"{files=}")

  return render_template('uploads_list.html', files=files)


@main.route('/list_staged')
def list_staged() -> str:
  """
  List all staged files available for review or processing.

  Args:
    None

  Returns:
    str: Rendered HTML showing all staged files.

  Examples:
    # In browser: GET /list_staged
    # Returns: HTML page listing staged files
  """
  logger.debug("list_staged route called")

  staging_dir = Path(get_upload_folder()) / "staging"
  staged_files = []

  if staging_dir.exists():
    for file_path in staging_dir.glob("*.json"):
      try:
        # Extract ID from filename (format: id_XXXX_ts_YYYYMMDD_HHMMSS.json)
        filename = file_path.name
        if filename.startswith("id_") and "_ts_" in filename:
          id_part = filename.split("_ts_")[0]
          id_incidence = int(id_part.replace("id_", ""))

          # Load metadata to get more info
          try:
            _, metadata = json_load_with_meta(file_path)
            base_misc_json = metadata.get("base_misc_json", {})
            sector = base_misc_json.get("sector", "Unknown")
          except Exception:
            sector = "Unknown"

          staged_files.append({
            'filename': filename,
            'id_incidence': id_incidence,
            'sector': sector,
            'file_size': file_path.stat().st_size,
            'modified_time': datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
          })
      except Exception as e:
        logger.warning(f"Could not process staged file {file_path}: {e}")

  # Sort by modification time (newest first)
  staged_files.sort(key=lambda x: x['modified_time'], reverse=True)

  return render_template('staged_list.html', staged_files=staged_files)


@main.route('/upload', methods=['GET', 'POST'])
@main.route('/upload/<message>', methods=['GET', 'POST'])
def upload_file(message: str | None = None) -> Union[str, Response]:
  """
  Handle file upload form and process uploaded Excel files.

  Args:
    message (str | None): Optional message to display on the upload page.

  Returns:
    str|Response: Rendered HTML for the upload form, or redirect after upload.

  Examples:
    # In browser: GET /upload
    # Returns: HTML upload form
    # In browser: POST /upload
    # Redirects to: /list_uploads or error page
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

      # Step 1: Save file and attempt DB ingest
      file_path, id_, sector = upload_and_update_db(db, upload_folder, request_file, base)

      if id_:
        logger.debug(f"Upload successful: id={id_}, sector={sector}. Redirecting to update page.")
        return redirect(url_for('main.incidence_update', id_=id_))

      # Step 2: Handle schema recognition failure with enhanced diagnostics
      logger.warning(f"Upload failed schema recognition: {file_path=}")
      error_details = generate_upload_diagnostics(request_file, file_path)
      detailed_message = format_diagnostic_message(error_details, 
                                                  "Uploaded file format not recognized.")
      return render_template(
        'upload.html',
        form=form,
        upload_message=detailed_message
      )

    except Exception as e:
      logger.exception("Exception occurred during upload or parsing.")
      
      # Enhanced error handling with diagnostic information
      error_details = generate_upload_diagnostics(request_file, 
                                                 file_path if 'file_path' in locals() else None)
      detailed_message = format_diagnostic_message(error_details)
      
      return render_template(
        'upload.html',
        form=form,
        upload_message=detailed_message
      )

  # GET request: display form
  return render_template('upload.html', form=form, upload_message=message)


@main.route('/upload_staged', methods=['GET', 'POST'])
@main.route('/upload_staged/<message>', methods=['GET', 'POST'])
def upload_file_staged(message: str | None = None) -> Union[str, Response]:
  """
  Handle staged file upload form and process staged Excel files.

  Args:
    message (str | None): Optional message to display on the staged upload page.

  Returns:
    str|Response: Rendered HTML for the staged upload form, or redirect after upload.

  Examples:
    # In browser: GET /upload_staged
    # Returns: HTML staged upload form
    # In browser: POST /upload_staged
    # Redirects to: /list_staged or error page
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
      
      # Enhanced success feedback with staging details
      success_message = (
        f"✅ File '{request_file.filename}' staged successfully!\n"
        f"📋 ID: {id_}\n"
        f"🏭 Sector: {sector}\n"
        f"📁 Staged as: {staged_filename}\n"
        f"🔍 Ready for review and confirmation."
      )
      flash(success_message, "success")
      return redirect(url_for('main.review_staged', id_=id_, filename=staged_filename))

    except Exception as e:
      logger.exception("Exception occurred during staged upload.")
      
      # Enhanced error handling with staging-specific diagnostic information
      error_details = generate_staging_diagnostics(
        request_file, 
        file_path if 'file_path' in locals() else None,
        staged_filename if 'staged_filename' in locals() else None,
        id_ if 'id_' in locals() else None,
        sector if 'sector' in locals() else None
      )
      detailed_message = format_diagnostic_message(error_details, 
                                                  "Staged upload processing failed.")
      
      return render_template(
        'upload_staged.html',
        form=form,
        upload_message=detailed_message
      )

  # GET request: display form
  return render_template('upload_staged.html', form=form, upload_message=message)


@main.route("/review_staged/<int:id_>/<filename>", methods=["GET"])
def review_staged(id_: int, filename: str) -> str | Response:
  """
  Review the contents of a staged file for a specific incidence ID.

  Args:
    id_ (int): Incidence ID associated with the staged file.
    filename (str): Name of the staged file to review.

  Returns:
    str|Response: Rendered HTML for file review, or redirect if not found.

  Examples:
    # In browser: GET /review_staged/123/myfile.xlsx
    # Returns: HTML review page for the file
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
    staged_payload = extract_tab_and_sector(staged_data, tab_name="Feedback Form")
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
  Confirm and apply a staged update for a specific incidence ID and file.

  Args:
    id_ (int): Incidence ID to update.
    filename (str): Name of the staged file to confirm.

  Returns:
    Response: Redirect to the incidence update page after applying the update.

  Examples:
    # In browser: POST /confirm_staged/123/myfile.xlsx
    # Redirects to: /incidence_update/123/
  """
  import shutil

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

  # Extract form data from the staged JSON structure
  # staged_data contains: {'metadata': {...}, 'schemas': {...}, 'tab_contents': {'Feedback Form': {...}}}
  # We need to extract just the form data from tab_contents and include sector from metadata
  form_data = extract_tab_and_sector(staged_data, tab_name="Feedback Form")
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
    id_=id_,
    add_to_session=True
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
    flash(
      "⚠️ The database was changed by another user before your updates were confirmed. Please review the new database state and reconfirm which fields you wish to update.",
      "warning")
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

    flash(f"✅ Successfully updated record {id_}. {len(patch)} fields changed. Staged file moved to processed directory.", "success")

  except Exception as e:
    # Rollback on error to prevent partial commits
    logger.error(f"[confirm_staged] ❌ Error during database update: {e}")
    logger.exception(f"[confirm_staged] Full exception details:")
    db.session.rollback()
    flash(f"❌ Error applying updates for ID {id_}: {e}", "danger")
    return redirect(url_for("main.upload_file_staged"))

  return redirect(url_for("main.upload_file_staged"))


@main.route("/discard_staged_update/<int:id_>", methods=["POST"])
def discard_staged_update(id_: int) -> Response:
  """
  Discard a staged update for a specific incidence ID.

  Args:
    id_ (int): Incidence ID for which to discard the staged update.

  Returns:
    Response: Redirect to the staged uploads list after discarding the update.

  Examples:
    # In browser: POST /discard_staged_update/123
    # Redirects to: /list_staged
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
  Apply a staged update to the database for a specific incidence ID.

  Args:
    id_ (int): Incidence ID to apply the staged update to.

  Returns:
    Response: Redirect to the incidence update page after applying the update.

  Examples:
    # In browser: POST /apply_staged_update/123
    # Redirects to: /incidence_update/123/
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
  Serve a file from the uploads directory.

  Args:
    filename (str): Name of the file to serve.

  Returns:
    Response: File response for download or viewing in browser.

  Examples:
    # In browser: GET /serve_file/myfile.xlsx
    # Returns: File download or inline view
  """

  upload_folder = get_upload_folder()
  file_path = os.path.join(upload_folder, filename)

  if not os.path.exists(file_path):
    abort(404)

  return send_from_directory(upload_folder, filename)


@main.route("/portal_updates")
def view_portal_updates() -> str:
  """
  Display a table of all portal update log entries.

  Args:
    None

  Returns:
    str: Rendered HTML table of portal update logs.

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
  Export all portal update log entries as a CSV file.

  Args:
    None

  Returns:
    Response: CSV file download of portal update logs.

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
  Search for incidences or updates in the portal database.

  Args:
    None

  Returns:
    str: Rendered HTML search results page.

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
  Display developer diagnostics and runtime information.

  Args:
    None

  Returns:
    str: Rendered HTML diagnostics page.

  Examples:
    # In browser: GET /diagnostics
    # Returns: HTML diagnostics info
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
  Show the current dropdown dictionary used in forms.

  Args:
    None

  Returns:
    str: Rendered HTML of dropdown dictionary.

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
  Show the structure of the portal database (tables, columns, types).

  Args:
    None

  Returns:
    str: Rendered HTML of database structure.

  Examples:
    # In browser: GET /show_database_structure
    # Returns: HTML with database structure
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
  Show the structure of the feedback form (fields, types, validators).

  Args:
    None

  Returns:
    str: Rendered HTML of feedback form structure.

  Examples:
    # In browser: GET /show_feedback_form_structure
    # Returns: HTML with feedback form structure
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


# @main.route('/show_log_file')
# def show_log_file() -> str:
#   """
#   Display the contents of the server's current log file.
#
#   Returns:
#     str: Rendered HTML with the full log file shown inside a <pre> block.
#
#   Notes:
#     - Useful for debugging in development or staging.
#   """
#
#   logger.info(f"Displaying the log file as a diagnostic")
#   lines = read_file_reverse(LOG_FILE, n=1000)
#   file_content = ''.join(lines)
#
#   # result = obj_to_html(file_content)
#   result = f"<p><strong>Logger file content=</strong></p> <p><pre>{file_content}</pre></p>"
#   return render_template('diagnostics.html',
#                          header="Log File Contents",
#                          # subheader="Full log output from the running server instance.",
#                          html_content=result,
#                          )


@main.route('/show_log_file')
def show_log_file() -> str:
  """
  Display the last N lines of the portal log file.

  Query Parameters:
    lines (int, optional): Number of lines to show from the end of the log file.
                           Defaults to 1000 if not provided or invalid.
  Args:
    None

  Returns:
    str: Rendered HTML with the log file content shown inside a <pre> block.

  Example Usage:
    /show_log_file?lines=500

  Notes:
    - Useful for debugging in development or staging.
    - Efficient for large files using read_file_reverse().
  """
  default_lines = 1000
  try:
    num_lines = int(request.args.get('lines', default_lines))
    if num_lines < 1:
      raise ValueError
  except ValueError:
    num_lines = default_lines

  logger.info(f"Displaying the last {num_lines} lines of the log file as a diagnostic")

  lines = read_file_reverse(LOG_FILE, n=num_lines)
  file_content = '\n'.join(lines)

  result = f"<p><strong>Last {num_lines} lines of logger file:</strong></p><p><pre>{file_content}</pre></p>"
  return render_template(
    'diagnostics.html',
    header="Log File Contents",
    html_content=result,
  )
