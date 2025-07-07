"""
route_util.py

This module prepares the rendering context and template output for individual
feedback form pages, supporting both 'create' and 'update' operations.

It integrates SQLAlchemy model rows with WTForms-based feedback forms,
enforces dropdown resets, and applies conditional rendering logic
based on sector type and CRUD mode.
"""

import logging
from pathlib import Path
from typing import List, Optional

from flask import Response, flash, redirect, render_template, request, url_for
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
    str: Rendered HTML from the appropriate feedback template.

  Raises:
    ValueError: If the sector type is invalid.
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
      if wtf_form.validate():
        # Instead of redirecting, return success flag for popup
        flash("✅ All changes have been saved successfully! No validation warnings or errors found.", "success")
        return render_template(template_file,
                               wtf_form=wtf_form,
                               crud_type=crud_type,
                               error_count_dict=wtf_count_errors(wtf_form, log_errors=True),
                               id_incidence=getattr(model_row, "id_incidence", None),
                               show_success_popup=True)

  error_count_dict = wtf_count_errors(wtf_form, log_errors=True)

  logger.debug(f"incidence_prep() about to render get template")

  return render_template(template_file,
                         wtf_form=wtf_form,
                         crud_type=crud_type,
                         error_count_dict=error_count_dict,
                         id_incidence=getattr(model_row, "id_incidence", None),
                         )


def render_readonly_sector_view(model_row: AutomapBase, sector_type: str, crud_type: str) -> str:
  """
  Render a read-only view for sectors that don't have interactive forms.
  
  Args:
    model_row: Database model row containing incidence data.
    sector_type: The unsupported sector type.
    crud_type: Type of CRUD operation ('create', 'update', 'delete').
    
  Returns:
    str: Rendered HTML with formatted read-only data.
  """
  logger.debug(f"render_readonly_sector_view() called for sector_type={sector_type}")
  
  # Extract data from the model
  id_incidence = getattr(model_row, "id_incidence", None)
  misc_json = getattr(model_row, "misc_json", {}) or {}
  
  # Format the data for display
  formatted_data = []
  
  # Add basic record info
  formatted_data.append({
    'section': 'Record Information',
    'fields': [
      ('Incidence/Emission ID', id_incidence),
      ('Sector', sector_type),
      ('Record Type', crud_type.title()),
    ]
  })
  
  # Add all misc_json fields, grouped by common patterns
  if misc_json:
    # Group fields by common prefixes or types
    location_fields = {}
    monitoring_fields = {}
    description_fields = {}
    other_fields = {}
    
    for key, value in misc_json.items():
      key_lower = key.lower()
      if any(prefix in key_lower for prefix in ['location', 'address', 'site', 'facility']):
        location_fields[key] = value
      elif any(prefix in key_lower for prefix in ['monitor', 'detect', 'measure', 'sensor']):
        monitoring_fields[key] = value
      elif any(prefix in key_lower for prefix in ['description', 'comment', 'note', 'detail']):
        description_fields[key] = value
      else:
        other_fields[key] = value
    
    # Add sections if they have data
    if location_fields:
      formatted_data.append({
        'section': 'Location Information',
        'fields': [(k, v) for k, v in location_fields.items()]
      })
    
    if monitoring_fields:
      formatted_data.append({
        'section': 'Monitoring Information',
        'fields': [(k, v) for k, v in monitoring_fields.items()]
      })
    
    if description_fields:
      formatted_data.append({
        'section': 'Descriptions & Comments',
        'fields': [(k, v) for k, v in description_fields.items()]
      })
    
    if other_fields:
      formatted_data.append({
        'section': 'Other Information',
        'fields': [(k, v) for k, v in other_fields.items()]
      })
  
  return render_template('readonly_sector_view.html',
                         sector_type=sector_type,
                         id_incidence=id_incidence,
                         crud_type=crud_type,
                         formatted_data=formatted_data,
                         misc_json=misc_json)


def generate_upload_diagnostics(request_file, file_path: Optional[Path] = None, 
                               include_id_extraction: bool = False) -> List[str]:
  """
  Generate diagnostic information for upload failures.
  
  This function analyzes what succeeded and what failed in the upload process,
  providing detailed information to help users understand and fix issues.
  
  Args:
    request_file: The uploaded file object from Flask request
    file_path: Optional path to the saved file
    include_id_extraction: Whether to include ID extraction diagnostics (for staged uploads)
    
  Returns:
    List[str]: List of diagnostic messages with ✅/❌ indicators
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
    request_file: The uploaded file object from Flask request
    file_path: Optional path to the saved file
    staged_filename: Optional name of the staged file
    id_: Optional extracted ID
    sector: Optional detected sector
    
  Returns:
    List[str]: List of diagnostic messages with ✅/❌ indicators
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
    error_details: List of diagnostic messages from generate_upload_diagnostics
    custom_message: Custom message to prepend to diagnostics
    
  Returns:
    str: Formatted diagnostic message for display
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
