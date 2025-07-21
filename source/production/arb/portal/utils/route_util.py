"""
  Utilities for preparing rendering context and template output for feedback form pages.

  This module supports both 'create' and 'update' operations for feedback forms,
  integrating SQLAlchemy model rows with WTForms-based forms, enforcing dropdown resets,
  and applying conditional rendering logic based on sector type and CRUD mode.

  Args:
    None

  Returns:
    None

  Attributes:
    incidence_prep (function): Prepares and renders feedback form pages.
    render_readonly_sector_view (function): Renders read-only sector views.
    generate_upload_diagnostics (function): Generates diagnostics for upload failures.
    generate_staging_diagnostics (function): Generates diagnostics for staging failures.
    format_diagnostic_message (function): Formats diagnostic messages for display.
    logger (logging.Logger): Logger instance for this module.

  Examples:
    from arb.portal.utils.route_util import incidence_prep
    html = incidence_prep(model_row, 'create', 'Oil & Gas', 'Please Select')

  Notes:
    - Used by feedback portal routes for form rendering and diagnostics.
    - Integrates with WTForms and SQLAlchemy models.
"""

import logging
from pathlib import Path
from typing import List, Optional

from flask import Response, flash, render_template, request
from sqlalchemy.ext.automap import AutomapBase

from arb.portal.constants import PLEASE_SELECT
from arb.portal.extensions import db
from arb.utils.sql_alchemy import add_commit_and_log_model, sa_model_diagnostics, sa_model_to_dict
from arb.utils.wtf_forms_util import initialize_drop_downs, model_to_wtform, validate_no_csrf, wtf_count_errors, wtform_to_model

logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def incidence_prep(model_row: AutomapBase,
                   crud_type: str,
                   sector_type: str,
                   default_dropdown: str) -> str | Response:
  """
  Generate the context and render the HTML template for a feedback record.

  Populates WTForms fields from the model and applies validation logic
  depending on the request method (GET/POST). Integrates conditional
  dropdown resets, CSRF-less validation, and feedback record persistence.

  Args:
    model_row (AutomapBase): SQLAlchemy AutomapBase.
    crud_type (str): 'create' or 'update'.
    sector_type (str): 'Oil & Gas' or 'Landfill'.
    default_dropdown (str): Value used to fill in blank selects.

  Returns:
    str | Response: Rendered HTML from the appropriate feedback template or a Flask Response.

  Raises:
    ValueError: If the sector type is invalid.

  Examples:
    html = incidence_prep(model_row, 'update', 'Oil & Gas', 'Please Select')
    # Renders the Oil & Gas feedback form for updating a record

  Notes:
    - Handles both GET and POST requests for feedback forms.
    - Integrates with WTForms and SQLAlchemy models.
    - Shows a success popup if validation passes on submit.
  """
  # The imports below can't be moved to the top of the file because they require Globals to be initialized
  # prior to first use (Globals.load_drop_downs(app, db)).
  from arb.portal.wtf_landfill import LandfillFeedback
  from arb.portal.wtf_oil_and_gas import OGFeedback

  logger.debug(f"incidence_prep() called with {crud_type=}, {sector_type=}")
  sa_model_diagnostics(model_row)

  if default_dropdown is None:
    default_dropdown = PLEASE_SELECT

  if sector_type == "Oil & Gas":
    logger.debug(f"({sector_type=}) will use an Oil & Gas Feedback Form")
    wtf_form = OGFeedback()
    template_file = 'feedback_oil_and_gas.html'
  elif sector_type == "Landfill":
    logger.debug(f"({sector_type=}) will use a Landfill Feedback Form")
    wtf_form = LandfillFeedback()
    template_file = 'feedback_landfill.html'
  else:
    # Handle unsupported sectors with a read-only view
    logger.info(f"({sector_type=}) is not supported for interactive editing - showing read-only view")
    return render_readonly_sector_view(model_row, sector_type, crud_type)

  if request.method == 'GET':
    # Populate wtform from model data
    model_to_wtform(model_row, wtf_form)
    # todo - maybe put update contingencies here?
    # obj_diagnostics(wtf_form, message="wtf_form in incidence_prep() after model_to_wtform")

    # For GET requests for row creation, don't validate and error_count_dict will be all zeros
    # For GET requests for row update, validate (except for the csrf token that is only present for a POST)
    if crud_type == 'update':
      validate_no_csrf(wtf_form, extra_validators=None)

  # todo - trying to make sure invalid drop-downs become "Please Select"
  #        may want to look into using validate_no_csrf or initialize_drop_downs (or combo)

  # Set all select elements that are a default value (None) to "Please Select" value
  initialize_drop_downs(wtf_form, default=default_dropdown)
  # logger.debug(f"\n\t{wtf_form.data=}")

  if request.method == 'POST':
    # Validate and count errors
    wtf_form.validate()
    _ = wtf_count_errors(wtf_form, log_errors=True)

    # Diagnostics of the model before updating with wtform values
    # Likely can comment out model_before and add_commit_and_log_model
    # if you want less diagnostics and redundant commits
    model_before = sa_model_to_dict(model_row)
    wtform_to_model(model_row, wtf_form, ignore_fields=["id_incidence"])
    add_commit_and_log_model(db,
                             model_row,
                             comment='call to wtform_to_model()',
                             model_before=model_before)

    # Determine the course of action for successful database update based on which button was submitted
    button = request.form.get('submit_button')

    # todo - change the button name to save?
    if button == 'validate_and_submit':
      logger.debug(f"validate_and_submit was pressed")
      # Check if there are any validation errors
      error_count_dict = wtf_count_errors(wtf_form, log_errors=True)
      total_errors = sum(error_count_dict.values())
      logger.debug(f"Error count dict: {error_count_dict}, total_errors: {total_errors}")

      if total_errors == 0:
        # No validation errors - show success popup
        logger.debug("No validation errors found - showing success popup")
        flash("✅ All changes have been saved successfully! No validation warnings or errors found.", "success")
        return render_template(template_file,
                               wtf_form=wtf_form,
                               crud_type=crud_type,
                               error_count_dict=error_count_dict,
                               id_incidence=getattr(model_row, "id_incidence", None),
                               show_success_popup=True)
      else:
        logger.debug(f"Validation errors found: {total_errors} - not showing success popup")

  error_count_dict = wtf_count_errors(wtf_form, log_errors=True)

  logger.debug(f"incidence_prep() about to render get template")

  return render_template(template_file,
                         wtf_form=wtf_form,
                         crud_type=crud_type,
                         error_count_dict=error_count_dict,
                         id_incidence=getattr(model_row, "id_incidence", None),
                         show_success_popup=False,  # Default to False for regular form display
                         )


def render_readonly_sector_view(model_row: AutomapBase, sector_type: str, crud_type: str) -> str:
  """
  Render a read-only view for sectors that don't have interactive forms.

  Args:
    model_row (AutomapBase): Database model row containing incidence data.
    sector_type (str): The unsupported sector type.
    crud_type (str): Type of CRUD operation ('create', 'update', 'delete').

  Returns:
    str: Rendered HTML with formatted read-only data.

  Examples:
    html = render_readonly_sector_view(model_row, 'Unknown', 'update')
    # Renders a read-only view for an unsupported sector

  Notes:
    - Used for sectors that do not have interactive feedback forms.
    - Displays all misc_json fields in alphabetical order.
  """
  logger.debug(f"render_readonly_sector_view() called for sector_type={sector_type}")

  # Extract data from the model
  id_incidence = getattr(model_row, "id_incidence", None)
  misc_json = getattr(model_row, "misc_json", {}) or {}

  # Create alphabetically sorted list of all fields
  all_fields = []

  # Add all misc_json fields, sorted alphabetically
  if misc_json:
    for key, value in sorted(misc_json.items()):
      all_fields.append((key, value))

  return render_template('readonly_sector_view.html',
                         sector_type=sector_type,
                         id_incidence=id_incidence,
                         crud_type=crud_type,
                         all_fields=all_fields,
                         misc_json=misc_json)


def generate_upload_diagnostics(request_file, file_path: Optional[Path] = None,
                                include_id_extraction: bool = False) -> List[str]:
  """
  Generate diagnostic information for upload failures.

  This function analyzes what succeeded and what failed in the upload process,
  providing detailed information to help users understand and fix issues.

  Args:
    request_file: The uploaded file object from Flask request.
    file_path (Optional[Path]): Optional path to the saved file.
    include_id_extraction (bool): Whether to include ID extraction diagnostics (for staged uploads).

  Returns:
    List[str]: List of diagnostic messages with ✅/❌ indicators.

  Examples:
    diagnostics = generate_upload_diagnostics(request_file, file_path)
    # Returns a list of diagnostic messages for the upload process

  Notes:
    - Checks file upload, disk save, JSON conversion, and optional ID extraction.
    - Returns early if any step fails.
  """
  error_details = []

  # Check if file was uploaded successfully
  if request_file and request_file.filename:
    error_details.append("✅ File uploaded successfully")
  else:
    error_details.append("❌ No file selected or file upload failed")
    return error_details

  # Check if file was saved to disk
  if file_path and file_path.exists():
    error_details.append(f"✅ File saved to disk: {file_path.name}")
  else:
    error_details.append("❌ File could not be saved to disk")
    return error_details

  # Check if file can be converted to JSON
  try:
    from arb.portal.utils.db_ingest_util import convert_excel_to_json_if_valid
    json_path, sector = convert_excel_to_json_if_valid(file_path)
    if json_path:
      error_details.append(f"✅ File converted to JSON successfully")
      error_details.append(f"✅ Sector detected: {sector}")

      # Check ID extraction if requested
      if include_id_extraction:
        try:
          from arb.portal.utils.db_ingest_util import extract_id_from_json
          from arb.utils.json import json_load_with_meta
          json_data, _ = json_load_with_meta(json_path)
          id_ = extract_id_from_json(json_data)
          if id_:
            error_details.append(f"✅ ID extracted successfully: {id_}")
          else:
            error_details.append("❌ Could not extract ID from JSON data")
        except Exception as e:
          error_details.append(f"❌ ID extraction failed: {str(e)}")
    else:
      error_details.append("❌ File format not recognized - could not convert to JSON")
  except Exception as e:
    error_details.append(f"❌ JSON conversion failed: {str(e)}")

  return error_details


def generate_staging_diagnostics(request_file, file_path: Optional[Path] = None,
                                 staged_filename: Optional[str] = None,
                                 id_: Optional[int] = None,
                                 sector: Optional[str] = None) -> List[str]:
  """
  Generate diagnostic information specifically for staging failures.

  This function provides detailed diagnostics for the staging workflow,
  including staging file creation and metadata capture.

  Args:
    request_file: The uploaded file object from Flask request.
    file_path (Optional[Path]): Optional path to the saved file.
    staged_filename (Optional[str]): Optional name of the staged file.
    id_ (Optional[int]): Optional extracted ID.
    sector (Optional[str]): Optional detected sector.

  Returns:
    List[str]: List of diagnostic messages with ✅/❌ indicators.

  Examples:
    diagnostics = generate_staging_diagnostics(request_file, file_path, staged_filename, id_, sector)
    # Returns a list of diagnostic messages for the staging process

  Notes:
    - Builds on upload diagnostics and adds staging-specific checks.
    - Verifies staging file creation and metadata capture.
  """
  error_details = []

  # Start with basic upload diagnostics
  basic_diagnostics = generate_upload_diagnostics(request_file, file_path, include_id_extraction=True)
  error_details.extend(basic_diagnostics)

  # Add staging-specific checks
  if staged_filename:
    error_details.append(f"✅ Staging file created: {staged_filename}")

    # Check if staging file exists on disk
    try:
      from arb.portal.config.accessors import get_upload_folder
      staging_dir = Path(get_upload_folder()) / "staging"
      staged_path = staging_dir / staged_filename
      if staged_path.exists():
        error_details.append("✅ Staging file saved to disk successfully")
      else:
        error_details.append("❌ Staging file not found on disk")
    except Exception as e:
      error_details.append(f"❌ Could not verify staging file: {str(e)}")
  else:
    error_details.append("❌ Staging file creation failed")

  # Check metadata capture
  if id_ and sector:
    error_details.append(f"✅ Metadata captured: ID={id_}, Sector={sector}")
  else:
    error_details.append("❌ Metadata capture incomplete")

  return error_details


def format_diagnostic_message(error_details: List[str],
                              custom_message: str = "Upload processing failed.") -> str:
  """
  Format diagnostic information into a user-friendly message.

  Args:
    error_details (List[str]): List of diagnostic messages from generate_upload_diagnostics.
    custom_message (str): Custom message to prepend to diagnostics.

  Returns:
    str: Formatted diagnostic message for display.

  Examples:
    msg = format_diagnostic_message(["✅ File uploaded", "❌ Save failed"])
    # Returns a formatted string for display to the user

  Notes:
    - Summarizes successes and failures in the upload/staging process.
    - Returns the custom message if no details are provided.
  """
  if not error_details:
    return custom_message

  # Find the last success and first failure
  successes = [msg for msg in error_details if msg.startswith("✅")]
  failures = [msg for msg in error_details if msg.startswith("❌")]

  if not failures:
    return f"{custom_message} All steps completed successfully."

  # Build the message
  message_parts = [custom_message]
  message_parts.append("")
  message_parts.append("Diagnostic Information:")

  # Show all diagnostic steps
  for detail in error_details:
    message_parts.append(f"  {detail}")

  # Add summary
  if successes:
    message_parts.append("")
    message_parts.append(f"✅ {len(successes)} step(s) completed successfully")
  message_parts.append(f"❌ Failed at: {failures[0].replace('❌ ', '')}")

  return "\n".join(message_parts)
