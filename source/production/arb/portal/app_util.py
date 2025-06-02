"""
app_util.py has utility functions specific to the feedback_portal app.

Notes:
    * General-purpose utility functions not tightly coupled with feedback_portal
      should be placed in arb.util so they can be reused in other projects.
"""

from datetime import datetime
from pathlib import Path

from flask import redirect, render_template, request, url_for
from sqlalchemy import or_
from sqlalchemy.orm.attributes import flag_modified

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


def get_sector_info(db, base, id_):
  """
  Given an incidence primary key, return the sector and sector type.

  The sector and sector type can be in the foreign table sources, in its sector column
  and/or can be in the misc_json field.

  Args:
    db (SQLAlchemy session): Database connection.
    base (SQLAlchemy base): Declarative base object for model reflection.
    id_ (int): Primary key of the 'incidences' table.

  Returns:
    tuple[str, str]: (sector, sector_type)
      sector: Name of the sector (e.g., "Oil & Gas").
      sector_type: Grouping of the sector (e.g., "Oil & Gas", "Landfill").

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


def resolve_sector(sector_by_foreign_key, row, misc_json):
  """
  Attempt to reconcile sector mismatches between JSON and FK values.

  Args:
      sector_by_foreign_key (str | None): Sector from foreign key relationship.
      row (SQLAlchemy model): Row model to update if needed.
      misc_json (dict): Dictionary for misc_json column.

  Returns:
      str: Final sector value.
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


def get_sector_type(sector):
  """
  Determine sector_type grouping from specific sector name.

  Args:
      sector (str): Name of the sector.

  Returns:
      str: Sector type ("Oil & Gas" or "Landfill").

  Raises:
      ValueError: If sector is unknown.
  """

  if sector in OIL_AND_GAS_SECTORS:
    return "Oil & Gas"
  elif sector in LANDFILL_SECTORS:
    return "Landfill"
  else:
    raise ValueError(f"Unknown sector type: '{sector}'.")


def upload_and_update_db(db, upload_dir, request_file, base):
  """
  Upload a file from a web form, parse it, and update the database.

  Args:
      db (SQLAlchemy session): Database connection.
      upload_dir (str | Path): Directory to store uploaded file.
      request_file (FileStorage): Uploaded file from request.files.
      base (SQLAlchemy base): Declarative base.

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


def json_file_to_db(db, file_name, base):
  """
  Load JSON from file and update the database.

  Args:
      db (SQLAlchemy session): Database connection.
      file_name (str | Path): Path to JSON file.
      base (SQLAlchemy base): Declarative base.

  Returns:
      tuple[int, str]: ID and sector from inserted record.
  """
  json_as_dict, metadata = json_load_with_meta(file_name)
  return xl_dict_to_database(db, base, json_as_dict)


def xl_dict_to_database(db, base, xl_dict, tab_name="Feedback Form"):
  """
  Convert Excel-derived dict structure to DB row.

  Args:
      db (SQLAlchemy session): Database connection.
      base (SQLAlchemy base): Declarative base.
      xl_dict (dict): Parsed Excel JSON content.
      tab_name (str): Worksheet/tab name to extract data from.

  Returns:
      tuple[int, str]: id_incidence and sector.
  """
  logger.debug(f"xl_dict_to_database() called with {xl_dict=}")
  metadata = xl_dict["metadata"]
  sector = metadata["sector"]
  tab_data = xl_dict["tab_contents"][tab_name]
  tab_data["sector"] = sector

  id_ = dict_to_database(db, base, tab_data)
  return id_, sector


def get_ensured_row(db,
                    base,
                    table_name: str = "incidences",
                    primary_key_name: str = "id_incidence",
                    id_: int = None):
  """
  Ensure a row exists in the specified table with the given primary key.

  If `id_` is provided, attempts to retrieve the row from the database.
  If it does not exist, creates a new row with that ID.
  If `id_` is not provided, creates a new row with an auto-incremented primary key.

  Args:
      db: SQLAlchemy database object with a `.session`.
      base: Declarative base used for table introspection.
      table_name (str): Name of the target table (default: "incidences").
      primary_key_name (str): Name of the primary key column (default: "id_incidence").
      id_ (int): Optional. Value of the primary key to fetch or create.

  Returns:
      tuple: A tuple of (model instance, primary key value).

  Raises:
      AttributeError: If the specified primary key column does not exist on the model.
  """
  session = db.session
  table = get_class_from_table_name(base, table_name)

  if id_ is not None:
    logger.debug(f"Retrieving {table_name} row with {primary_key_name}={id_}")
    model = session.get(table, id_)
    if model is None:
      logger.debug(f"No existing row found; creating new {table_name} row with {primary_key_name}={id_}")
      model = table(**{primary_key_name: id_})
  else:
    logger.debug(f"Creating new {table_name} row with auto-generated {primary_key_name}")
    model = table(**{primary_key_name: None})
    session.add(model)
    session.commit()
    id_ = getattr(model, primary_key_name)
    logger.debug(f"{table_name} row created with {primary_key_name}={id_}")

  return model, id_


def dict_to_database(db,
                     base,
                     data_dict: dict,
                     table_name: str = "incidences",
                     primary_key: str = "id_incidence",
                     json_field: str = "misc_json") -> int:
  """
  Insert or update a JSON payload into a SQLAlchemy model.

  Args:
      db: SQLAlchemy database object with a `.session`.
      base: Declarative base for schema introspection.
      data_dict (dict): Form or JSON payload data.
      table_name (str): Name of the target table (default: "incidences").
      primary_key (str): Name of the primary key column (default: "id_incidence").
      json_field (str): Name of the column that stores the JSON payload (default: "misc_json").

  Returns:
      int: The primary key value of the updated or inserted row.

  Raises:
      ValueError: If `data_dict` is empty.
  """
  from arb.utils.wtf_forms_util import update_model_with_payload

  if not data_dict:
    msg = "Attempt to add empty entry to database"
    logger.warning(msg)
    raise ValueError(msg)

  id_ = data_dict.get(primary_key)
  new_row = id_ is None

  model, id_ = get_ensured_row(
    db=db,
    base=base,
    table_name=table_name,
    primary_key_name=primary_key,
    id_=id_
  )

  # Backfill generated primary key into payload if it was not supplied
  if new_row:
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


def add_file_to_upload_table(db, file_name, status=None, description=None):
  """
  Add metadata entry to the uploaded_files table.

  Args:
      db (SQLAlchemy session): Database connection.
      file_name (str | Path): Full path to uploaded file.
      status (str | None): Optional status label.
      description (str | None): Optional textual description.
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


def apply_portal_update_filters(query, PortalUpdate, args):
  """
  Applies filters to a SQLAlchemy query for PortalUpdate entries.

  This function supports filtering by:
  - Field key (partial match)
  - User (partial match)
  - Comments (partial match)
  - Timestamp range (start_date, end_date in YYYY-MM-DD format)
  - ID incidence (exact matches, bounded ranges, unbounded ranges)

  Supported ID formats (via filter_id_incidence):
  ------------------------------------------------
  - "123"                  → Matches ID 123 exactly
  - "100-200"              → Matches IDs from 100 to 200 inclusive
  - "-250"                 → Matches all IDs ≤ 250
  - "300-"                 → Matches all IDs ≥ 300
  - "123,150-200,250-"     → Mixed exacts and ranges
  - "abc, 100-xyz, 222"    → Invalid parts are ignored

  Args:
      query (Query): SQLAlchemy query object.
      PortalUpdate (Base): PortalUpdate SQLAlchemy model class.
      args (dict): Dictionary of GET parameters (e.g., request.args).

  Returns:
      Query: Filtered SQLAlchemy query.
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


def incidence_prep(model_row,
                   crud_type,
                   sector_type,
                   default_dropdown=None):
  """
  Helper function used by many flask routes to render feedback forms for
  both creation and updating.

  Args:
    model_row (SQLAlchemy.Model): Single row from a SQLAlchemy model
    crud_type (str): 'update' or 'create'
    sector_type (str): 'Oil & Gas' or 'Landfill'
    default_dropdown (str): Defaults if no drop-down is selected.

  Returns (str): html for dynamic page

  Notes:

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
    model_before = sa_model_to_dict(model_row)
    wtform_to_model(model_row, wtf_form, ignore_fields=["id_incidence"])
    add_commit_and_log_model(db,
                             model_row,
                             comment='call to wtform_to_model()',
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
        return redirect(url_for('main.index'))

  error_count_dict = wtf_count_errors(wtf_form, log_errors=True)

  logger.debug(f"incidence_prep() about to render get template")

  return render_template(template_file,
                         wtf_form=wtf_form,
                         crud_type=crud_type,
                         error_count_dict=error_count_dict,
                         id_incidence=model_row.id_incidence,
                         )
