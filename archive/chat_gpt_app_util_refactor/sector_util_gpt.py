"""Sector Util - Auto-split from app_util."""

# Imports

from datetime import datetime
from pathlib import Path

from flask import redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy.ext.automap import AutomapBase
from sqlalchemy.ext.declarative import DeclarativeMeta
from werkzeug.datastructures import FileStorage

from arb.__get_logger import get_logger
from arb.portal.constants import PLEASE_SELECT
from arb.portal.db_hardcoded import LANDFILL_SECTORS, OIL_AND_GAS_SECTORS
from arb.portal.extensions import db
from arb.utils.excel.xl_parse import get_json_file_name
from arb.utils.json import json_load_with_meta
from arb.utils.sql_alchemy import add_commit_and_log_model, get_class_from_table_name, get_foreign_value, get_table_row_and_column, \
  sa_model_diagnostics, sa_model_to_dict
from arb.utils.web_html import upload_single_file
from arb.utils.wtf_forms_util import (
  initialize_drop_downs, model_to_wtform,
  validate_no_csrf, wtf_count_errors, wtform_to_model
)

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')



def get_sector_info(db: SQLAlchemy,
                    base: AutomapBase,
                    id_: int) -> tuple[str, str]:
  """
  Resolve the sector and sector_type for a given incidence ID.

  Args:
    db (SQLAlchemy): SQLAlchemy database instance.
    base (AutomapBase): SQLAlchemy automapped declarative base.
    id_ (int): ID of the row in the `incidences` table.

  Returns:
    tuple[str, str]: (sector, sector_type)
  """
  logger.debug(f"get_sector_info() called to determine sector & sector type for {id_=}")
  primary_table_name = "incidences"
  json_column = "misc_json"
  sector = None
  sector_type = None

  # Find the sector from the foreign table if incidence was created by plume tracker.
  sector_by_foreign_key = get_foreign_value(
    db, base,
    primary_table_name=primary_table_name,
    foreign_table_name="sources",
    primary_table_fk_name="source_id",
    foreign_table_column_name="sector",
    primary_table_pk_value=id_,
  )

  # Get the row and misc_json field from the incidence table
  row, misc_json = get_table_row_and_column(
    db, base,
    table_name=primary_table_name,
    column_name=json_column,
    id_=id_,
  )

  if misc_json is None:
    misc_json = {}

  sector = resolve_sector(sector_by_foreign_key, row, misc_json)
  sector_type = get_sector_type(sector)

  logger.debug(f"get_sector_info() returning {sector=} {sector_type=}")
  return sector, sector_type



def resolve_sector(sector_by_foreign_key: str | None,
                   row: DeclarativeMeta,
                   misc_json: dict) -> str:
  """
  Determine the appropriate sector from FK and JSON sources.

  Args:
    sector_by_foreign_key (str | None): Sector from `sources` table.
    row (DeclarativeMeta): Row from `incidences` table (SQLAlchemy result).
    misc_json (dict): Parsed `misc_json` content.

  Returns:
    str: Sector string.

  Raises:
    ValueError: If values are missing or conflict.
  """
  logger.debug(f"resolve_sector() called with {sector_by_foreign_key=}, {row=}, {misc_json=}")
  sector = None
  sector_by_json = misc_json.get("sector")

  if sector_by_foreign_key is None:
    logger.warning("sector column value in sources table is None.")

  if sector_by_json is None:
    logger.warning("'sector' not in misc_json")

  if sector_by_foreign_key is None and sector_by_json is None:
    logger.error("Can't determine incidence sector")
    raise ValueError("Can't determine incidence sector")

  if sector_by_foreign_key is not None and sector_by_json is not None:
    if sector_by_foreign_key != sector_by_json:
      logger.error(f"Sector mismatch: {sector_by_foreign_key=}, {sector_by_json=}")
      raise ValueError("Can't determine incidence sector")

  sector = sector_by_foreign_key or sector_by_json

  logger.debug(f"resolve_sector() returning {sector=}")
  return sector



def get_sector_type(sector: str) -> str:
  """
  Map a sector name to its broad classification.

  Args:
    sector (str): Input sector label.

  Returns:
    str: One of "Oil & Gas" or "Landfill".

  Raises:
    ValueError: On unknown sector input.
  """

  if sector in OIL_AND_GAS_SECTORS:
    return "Oil & Gas"
  elif sector in LANDFILL_SECTORS:
    return "Landfill"
  else:
    raise ValueError(f"Unknown sector type: '{sector}'.")



def upload_and_update_db(db: SQLAlchemy,
                         upload_dir: str | Path,
                         request_file: FileStorage,
                         base: AutomapBase
                         ) -> tuple[str, int | None, str | None]:
  """
  Save uploaded file, parse contents, and insert or update DB rows.

  Args:
    db (SQLAlchemy): Database instance.
    upload_dir (str | Path): Directory where file will be saved.
    request_file (FileStorage): Flask `request.files[...]` object.
    base (AutomapBase): Automapped schema metadata.

  Returns:
    tuple[str, int | None, str | None]: Filename, id_incidence, sector.
  """
  logger.debug(f"upload_and_update_db() called with {request_file=}")
  id_ = None
  sector = None

  file_name = upload_single_file(upload_dir, request_file)
  add_file_to_upload_table(db, file_name, status="File Added", description=None)

  # if file is xl and can be converted to json,
  # save a json version of the file and return the filename
  json_file_name = get_json_file_name(file_name)
  if json_file_name:
    id_, sector = json_file_to_db(db, json_file_name, base)

  return file_name, id_, sector



def json_file_to_db(db: SQLAlchemy,
                    file_name: str | Path,
                    base: AutomapBase
                    ) -> tuple[int, str]:
  """
  Load a JSON file and insert its contents into the `incidences` table.

  Args:
    db (SQLAlchemy): SQLAlchemy session used to commit the new row.
    file_name (str | Path): Path to the JSON file on disk.
    base (AutomapBase): SQLAlchemy automapped metadata base.

  Returns:
    tuple[int, str]: The (id_incidence, sector) extracted from the inserted row.

  Raises:
    FileNotFoundError: If the specified file path does not exist.
    json.JSONDecodeError: If the file is not valid JSON.
  """

  json_as_dict, metadata = json_load_with_meta(file_name)
  return xl_dict_to_database(db, base, json_as_dict)



def xl_dict_to_database(db, base, xl_dict: dict, tab_name: str = "Feedback Form") -> tuple[int, str]:
  """
  Insert or update a row from an Excel-parsed JSON dictionary into the database.

  Args:
    db (SQLAlchemy): SQLAlchemy database instance.
    base (AutomapBase): Reflected SQLAlchemy base metadata.
    xl_dict (dict): Parsed Excel document with 'metadata' and 'tab_contents'.
    tab_name (str): Name of the worksheet tab to extract.

  Returns:
    tuple[int, str]: Tuple of (id_incidence, sector) after row insertion.
  """
  logger.debug(f"xl_dict_to_database() called with {xl_dict=}")
  metadata = xl_dict["metadata"]
  sector = metadata["sector"]
  tab_data = xl_dict["tab_contents"][tab_name]
  tab_data["sector"] = sector

  id_ = dict_to_database(db, base, tab_data)
  return id_, sector



def incidence_prep(model_row: DeclarativeMeta,
                   crud_type: str,
                   sector_type: str,
                   default_dropdown: str) -> str:
  """
  Generate the context and render the HTML template for a feedback record.

  Populates WTForms fields from the model and applies validation logic
  depending on the request method (GET/POST). Integrates conditional
  dropdown resets, CSRF-less validation, and feedback record persistence.

  Args:
    model_row (DeclarativeMeta): SQLAlchemy model row for the feedback entry.
    crud_type (str): 'create' or 'update'.
    sector_type (str): 'Oil & Gas' or 'Landfill'.
    default_dropdown (str): Value used to fill in blank selects.

  Returns:
    str: Rendered HTML from the appropriate feedback template.

  Raises:
    ValueError: If the sector type is invalid.
  """
  # imports below can't be moved to top of file because they require Globals to be initialized
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

  # todo - trying to make sure invalid drop-downs become "Please Select"
  #        may want to look into using validate_no_csrf or initialize_drop_downs (or combo)

  # Set all select elements that are a default value (None) to "Please Select" value
  initialize_drop_downs(wtf_form, default=default_dropdown)
  # logger.debug(f"\n\t{wtf_form.data=}")

  if request.method == 'POST':
    # Validate and count errors
    wtf_form.validate()
    error_count_dict = wtf_count_errors(wtf_form, log_errors=True)

    # Diagnostics of model before updating with wtform values
    # Likely can comment out model_before and add_commit_and_log_model
    # if you want less diagnostics and redundant commits
    model_before = sa_model_to_dict(model_row)
    wtform_to_model(model_row, wtf_form, ignore_fields=["id_incidence"])
    add_commit_and_log_model(db,
                             model_row,
                             comment='call to wtform_to_model()',
                             model_before=model_before)

    # Determine course of action for successful database update based on which button was submitted
    button = request.form.get('submit_button')

    # todo - change the button name to save?
    if button == 'validate_and_submit':
      logger.debug(f"validate_and_submit was pressed")
      if wtf_form.validate():
        return redirect(url_for('main.index'))

  error_count_dict = wtf_count_errors(wtf_form, log_errors=True)

  logger.debug(f"incidence_prep() about to render get template")

  return render_template(template_file,
                         wtf_form=wtf_form,
                         crud_type=crud_type,
                         error_count_dict=error_count_dict,
                         id_incidence=model_row.id_incidence,
                         )
