"""
database_ingest_util.py

This module provides database ingestion helpers for inserting or updating rows
based on structured dictionaries, particularly those derived from Excel templates.

It includes:
- Generic row ingestion from any dict using SQLAlchemy reflection
- Excel-specific wrapper for sector-based data (xl_dict_to_database)
"""

from pathlib import Path

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import AutomapBase
from werkzeug.datastructures import FileStorage

from arb.__get_logger import get_logger
from arb.portal.utils.db_introspection_util import get_ensured_row
from arb.portal.utils.file_upload_util import add_file_to_upload_table
from arb.utils.excel.xl_parse import get_json_file_name  # ✅ confirmed working version
from arb.utils.json import json_load_with_meta  # ✅ confirmed working version
from arb.utils.web_html import upload_single_file

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def xl_dict_to_database(db: SQLAlchemy,
                        base: AutomapBase,
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


def dict_to_database(db: SQLAlchemy,
                     base: AutomapBase,
                     data_dict: dict,
                     table_name: str = "incidences",
                     primary_key: str = "id_incidence",
                     json_field: str = "misc_json") -> int:
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

  # Final safety: extract final PK from the model
  try:
    return getattr(model, primary_key)
  except AttributeError as e:
    logger.error(f"Model has no attribute '{primary_key}': {e}")
    raise


def json_file_to_db(db: SQLAlchemy,
                    file_name: str | Path,
                    base: AutomapBase
                    ) -> tuple[int, str]:
  """
  Parse a previously uploaded JSON file and write it to the DB.

  Args:
    db (SQLAlchemy): SQLAlchemy DB instance.
    file_name (str | Path): Path to a .json file matching Excel schema.
    base (AutomapBase): Reflected schema metadata.

  Returns:
    tuple[int, str]: The (id_incidence, sector) extracted from the inserted row.

  Raises:
    FileNotFoundError: If the specified file path does not exist.
    json.JSONDecodeError: If the file is not valid JSON.
  """

  json_as_dict, metadata = json_load_with_meta(file_name)
  return xl_dict_to_database(db, base, json_as_dict)


def upload_and_update_db_old(db: SQLAlchemy,
                             upload_dir: str | Path,
                             request_file: FileStorage,
                             base: AutomapBase
                             ) -> tuple[Path, int | None, str | None]:
  """
  Deprecated: used prior to staged update refactor (2025-06-11)

  Save uploaded file, parse contents, and insert or update DB rows.

  Args:
    db (SQLAlchemy): Database instance.
    upload_dir (str | Path): Directory where file will be saved.
    request_file (FileStorage): Flask `request.files[...]` object.
    base (AutomapBase): Automapped schema metadata.

  Returns:
    tuple[Path, int | None, str | None]: Filename, id_incidence, sector.
  """
  logger.debug(f"upload_and_update_db() called with {request_file=}")
  id_ = None
  sector = None

  file_name = upload_single_file(upload_dir, request_file)
  add_file_to_upload_table(db, file_name, status="File Added", description=None)

  # if the file is xl and can be converted to JSON,
  # save a JSON version of the file and return the filename
  json_file_name = get_json_file_name(file_name)
  if json_file_name:
    id_, sector = json_file_to_db(db, json_file_name, base)

  return file_name, id_, sector


def upload_and_update_db(db: SQLAlchemy,
                         upload_dir: str | Path,
                         request_file: FileStorage,
                         base: AutomapBase
                         ) -> tuple[Path, int | None, str | None]:
  """
  Legacy wrapper function: Save uploaded file, attempt Excel → JSON → DB ingest.

  Args:
    db (SQLAlchemy): Database instance.
    upload_dir (str | Path): Upload destination path.
    request_file (FileStorage): Incoming file from Flask.
    base (AutomapBase): Reflected metadata base.

  Returns:
    tuple[Path, int | None, str | None]: Saved file path, id, and sector.
  """
  logger.debug(f"upload_and_update_db() called with {request_file=}")
  id_ = None
  sector = None

  file_path = upload_single_file(upload_dir, request_file)
  add_file_to_upload_table(db, file_path, status="File Added", description=None)

  json_path = convert_file_to_json(file_path)
  if json_path:
    id_, sector = prepare_staged_update(json_path, db, base)

  return file_path, id_, sector


def convert_file_to_json(file_path: Path) -> Path | None:
  """
  Convert an uploaded Excel file to a JSON file, if possible.

  Args:
    file_path (Path): Path to the saved Excel file.

  Returns:
    Path | None: Path to the generated JSON file, or None if conversion failed.
  """
  json_file_path = get_json_file_name(file_path)
  if not json_file_path:
    logger.warning(f"File {file_path} could not be converted to JSON.")
    return None
  logger.debug(f"Converted Excel to JSON: {json_file_path}")
  return json_file_path


def prepare_staged_update(json_path: Path,
                          db: SQLAlchemy,
                          base: AutomapBase
                          ) -> tuple[int | None, str | None]:
  """
  Prepare staging logic for a JSON file by attempting to extract id and sector.
  Does not apply updates yet.

  Args:
    json_path (Path): Path to the parsed JSON file.
    db (SQLAlchemy): Active database connection.
    base (AutomapBase): SQLAlchemy reflection base.

  Returns:
    tuple[int | None, str | None]: id_incidence and sector name, if available.
  """
  return json_file_to_db(db, json_path, base)
