"""
Application-specific utility functions for the ARB Feedback Portal.

This module provides helpers for resolving sector data, handling file uploads,
preparing database rows, and integrating WTForms with SQLAlchemy models.

Key Capabilities:
-----------------
- Resolve sector and sector_type for an incidence
- Insert or update rows from Excel/JSON payloads
- Reflect and verify database schema and rows
- Track uploaded files via the UploadedFile table
- Apply filter logic to the portal_updates log view
- Generate context and form logic for feedback pages

Typical Usage:
--------------
- File ingestion and incidence row creation
- Dynamic form loading from model rows
- Sector/type resolution from related tables
- Upload tracking and file diagnostics
"""
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


def xl_dict_to_database(db,
                        base,
                        xl_dict: dict,
                        tab_name: str = "Feedback Form") -> tuple[int, str]:
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


def get_ensured_row(db, base, table_name="incidences", primary_key_name="id_incidence", id_=None) -> tuple:
  """
  Retrieve or create a row in the specified table using a primary key.

  If the row exists, it is returned. Otherwise, a new row is created and committed.

  Args:
    db (SQLAlchemy): SQLAlchemy database instance.
    base (AutomapBase): Reflected SQLAlchemy base metadata.
    table_name (str): Table name to operate on. Defaults to 'incidences'.
    primary_key_name (str): Name of the primary key column. Defaults to 'id_incidence'.
    id_ (int | None): Primary key value. If None, a new row is created.

  Returns:
    tuple: (model, id_, is_new_row)
      - model: SQLAlchemy ORM instance
      - id_: Primary key value
      - is_new_row: Whether a new row was created (True/False)

  Raises:
    AttributeError: If the model class lacks the specified primary key.
  """

  is_new_row = False

  session = db.session
  table = get_class_from_table_name(base, table_name)

  if id_ is not None:
    logger.debug(f"Retrieving {table_name} row with {primary_key_name}={id_}")
    model = session.get(table, id_)
    if model is None:
      is_new_row = True
      logger.debug(f"No existing row found; creating new {table_name} row with {primary_key_name}={id_}")
      model = table(**{primary_key_name: id_})
  else:
    is_new_row = True
    logger.debug(f"Creating new {table_name} row with auto-generated {primary_key_name}")
    model = table(**{primary_key_name: None})
    session.add(model)
    session.commit()
    id_ = getattr(model, primary_key_name)
    logger.debug(f"{table_name} row created with {primary_key_name}={id_}")

  return model, id_, is_new_row


def dict_to_database(db,
                     base,
                     data_dict: dict,
                     table_name="incidences",
                     primary_key="id_incidence",
                     json_field="misc_json") -> int:
  """
  Insert or update a row in the specified table using a dictionary payload.

  The payload is merged into a model instance and committed to the database.

  Args:
    db (SQLAlchemy): SQLAlchemy database instance.
    base (AutomapBase): Reflected SQLAlchemy base metadata.
    data_dict (dict): Dictionary containing payload data.
    table_name (str): Table name to modify. Defaults to 'incidences'.
    primary_key (str): Name of the primary key field. Defaults to 'id_incidence'.
    json_field (str): Name of the JSON field to update. Defaults to 'misc_json'.

  Returns:
    int: Final value of the primary key for the affected row.

  Raises:
    ValueError: If data_dict is empty.
    AttributeError: If the resulting model does not expose the primary key.
  """

  from arb.utils.wtf_forms_util import update_model_with_payload

  if not data_dict:
    msg = "Attempt to add empty entry to database"
    logger.warning(msg)
    raise ValueError(msg)

  id_ = data_dict.get(primary_key)

  model, id_, is_new_row = get_ensured_row(
    db=db,
    base=base,
    table_name=table_name,
    primary_key_name=primary_key,
    id_=id_
  )

  # Backfill generated primary key into payload if it was not supplied
  if is_new_row:
    logger.debug(f"Backfilling {primary_key} = {id_} into payload")
    data_dict[primary_key] = id_

  update_model_with_payload(model, data_dict, json_field=json_field)

  session = db.session
  session.add(model)
  session.commit()

  # Final safety: extract final PK from model
  try:
    return getattr(model, primary_key)
  except AttributeError as e:
    logger.error(f"Model has no attribute '{primary_key}': {e}")
    raise


def add_file_to_upload_table(db, file_name: str | Path,
                             status=None,
                             description=None) -> None:
  """
  Insert a record into the `UploadedFile` table for audit and diagnostics.

  Args:
    db (SQLAlchemy): SQLAlchemy database instance.
    file_name (str | Path): File path or name to be recorded.
    status (str | None): Optional upload status label.
    description (str | None): Optional notes for the upload event.

  Returns:
    None
  """

  # todo (consider) to wrap commit in log?
  from arb.portal.sqla_models import UploadedFile

  logger.debug(f"Adding uploaded file to upload table: {file_name=}")
  model_uploaded_file = UploadedFile(
    path=str(file_name),
    status=status,
    description=description,
  )
  db.session.add(model_uploaded_file)
  db.session.commit()
  logger.debug(f"{model_uploaded_file=}")


def apply_portal_update_filters(query, PortalUpdate, args: dict):
  """
  Apply user-defined filters to a `PortalUpdate` SQLAlchemy query.

  Args:
    query (SQLAlchemy Query): Query to be filtered.
    PortalUpdate (Base): ORM model class for the portal_updates table.
    args (dict): Typically from `request.args`, containing filter values.

  Supported filters:
    - Substring matches on key, user, comments
    - ID exact match or range parsing (e.g. "100-200, 250")
    - Date range filtering via `start_date` and `end_date`

  Supported ID formats (via filter_id_incidence):
  ------------------------------------------------
  - "123"                  → Matches ID 123 exactly
  - "100-200"              → Matches IDs from 100 to 200 inclusive
  - "-250"                 → Matches all IDs ≤ 250
  - "300-"                 → Matches all IDs ≥ 300
  - "123,150-200,250-"     → Mixed exacts and ranges
  - "abc, 100-xyz, 222"    → Invalid parts are ignored

  Returns (SQLAlchemy Query):
    SQLAlchemy query: Modified query with filters applied.
  """
  filter_key = args.get("filter_key", "").strip()
  filter_user = args.get("filter_user", "").strip()
  filter_comments = args.get("filter_comments", "").strip()
  filter_id_incidence = args.get("filter_id_incidence", "").strip()
  start_date_str = args.get("start_date", "").strip()
  end_date_str = args.get("end_date", "").strip()

  if filter_key:
    query = query.filter(PortalUpdate.key.ilike(f"%{filter_key}%"))
  if filter_user:
    query = query.filter(PortalUpdate.user.ilike(f"%{filter_user}%"))
  if filter_comments:
    query = query.filter(PortalUpdate.comments.ilike(f"%{filter_comments}%"))

  if filter_id_incidence:
    id_exact = set()
    id_range_clauses = []

    for part in filter_id_incidence.split(","):
      part = part.strip()
      if not part:
        continue
      if "-" in part:
        try:
          start, end = part.split("-")
          start = start.strip()
          end = end.strip()
          if start and end:
            start_val = int(start)
            end_val = int(end)
            if start_val <= end_val:
              id_range_clauses.append(PortalUpdate.id_incidence.between(start_val, end_val))
          elif start:
            start_val = int(start)
            id_range_clauses.append(PortalUpdate.id_incidence >= start_val)
          elif end:
            end_val = int(end)
            id_range_clauses.append(PortalUpdate.id_incidence <= end_val)
        except ValueError:
          continue  # Ignore malformed part
      elif part.isdigit():
        id_exact.add(int(part))

    clause_list = []
    if id_exact:
      clause_list.append(PortalUpdate.id_incidence.in_(sorted(id_exact)))
    clause_list.extend(id_range_clauses)

    if clause_list:
      query = query.filter(or_(*clause_list))

  try:
    if start_date_str:
      start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
      query = query.filter(PortalUpdate.timestamp >= start_dt)
    if end_date_str:
      end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
      end_dt = end_dt.replace(hour=23, minute=59, second=59)
      query = query.filter(PortalUpdate.timestamp <= end_dt)
  except ValueError:
    pass  # Silently ignore invalid date inputs

  return query


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
