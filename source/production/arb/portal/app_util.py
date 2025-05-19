"""
app_util.py has utility functions specific to the feedback_portal app.

Notes:
    * General-purpose utility functions not tightly coupled with feedback_portal
      should be placed in arb.util so they can be reused in other projects.
"""

from pathlib import Path

from sqlalchemy.orm.attributes import flag_modified

from arb.__get_logger import get_logger
from arb.portal.db_hardcoded import LANDFILL_SECTORS, OIL_AND_GAS_SECTORS
from arb.utils.excel.xl_parse import get_json_file_name
from arb.utils.json import json_load_with_meta
from arb.utils.sql_alchemy import (
  add_commit_and_log_model,
  get_class_from_table_name,
  get_foreign_value,
  get_table_row_and_column,
  sa_model_to_dict,
)
from arb.utils.web_html import upload_single_file

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def get_sector_info(db, base, id_):
  """
  Given an incidence primary key, return the sector and sector type.

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

  sector_by_foreign_key = get_foreign_value(
    db, base,
    primary_table_name=primary_table_name,
    foreign_table_name="sources",
    primary_table_fk_name="source_id",
    foreign_table_column_name="sector",
    primary_table_pk_value=id_,
  )

  row, misc_json = get_table_row_and_column(
    db, base,
    table_name=primary_table_name,
    column_name=json_column,
    id_=id_,
  )

  if misc_json is None:
    misc_json = {}

  row_before = sa_model_to_dict(row)
  _ = resolve_sector(sector_by_foreign_key, row, misc_json)
  sector, sector_type = resolve_sector_type(row, misc_json)

  add_commit_and_log_model(
    db, row,
    comment="resolving sector and sector_type",
    model_before=row_before,
  )

  logger.debug(f"get_sector_info() returning {sector=} {sector_type=}")
  return sector, sector_type


def resolve_sector_type(row, misc_json):
  """
  Resolve the sector_type value based on the sector in misc_json.

  Args:
      row (SQLAlchemy model): Database model instance for the row.
      misc_json (dict): Dictionary from the misc_json column.

  Returns:
      tuple[str, str]: (sector, sector_type)
  """
  logger.debug(f"resolve_sector_type() called with {row=}, {misc_json=}")
  sector = misc_json["sector"]
  sector_type = get_sector_type(sector)

  if "sector_type" not in misc_json:
    misc_json["sector_type"] = sector_type
    flag_modified(row, "misc_json")
    logger.debug(f"sector_type initialized to: {sector_type}")
  elif misc_json["sector_type"] != sector_type:
    logger.warning(
      f"Sector Type mismatch; JSON will not be adjusted from {misc_json['sector_type']} to {sector_type=}"
    )

  logger.debug(f"resolve_sector_type() returning with {sector=}, {sector_type=}")
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
  default_sector = "Oil & Gas"

  if sector_by_foreign_key is None:
    logger.warning("sector column value in sources table is None.")
  elif "sector" not in misc_json:
    logger.warning(f"Sector undefined in JSON. Setting to {sector_by_foreign_key=}")
    misc_json["sector"] = sector_by_foreign_key
    flag_modified(row, "misc_json")
  elif sector_by_foreign_key != misc_json["sector"]:
    logger.warning(
      f"Sector mismatch, JSON data not adjusted. {sector_by_foreign_key=}, {misc_json['sector']=}"
    )

  # Ensure json entry for sector
  if "sector" not in misc_json:
    misc_json["sector"] = default_sector
    flag_modified(row, "misc_json")

  logger.debug(f"resolve_sector() returning {misc_json['sector']=}")
  return misc_json["sector"]


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
  # todo - add ValueError: Unknown sector type: 'Recycling & Waste: Landfills'.

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

  # todo (consider) - filter out "Please Select"

  # todo (update) - use the payload routine apply_json_patch_and_log
  #               - may have synch issues with json id and row id

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
