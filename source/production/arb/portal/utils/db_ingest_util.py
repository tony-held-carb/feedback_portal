"""
database_ingest_util.py

This module provides database ingestion helpers for inserting or updating rows
based on structured dictionaries, particularly those derived from Excel templates.

It includes:
- Generic row ingestion from any dict using SQLAlchemy reflection
- Excel-specific wrapper for sector-based data (xl_dict_to_database)
"""
import shutil
from pathlib import Path

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import AutomapBase
from werkzeug.datastructures import FileStorage

from arb.__get_logger import get_logger
from arb.portal.config.accessors import get_upload_folder
from arb.portal.utils.db_introspection_util import get_ensured_row
from arb.portal.utils.file_upload_util import add_file_to_upload_table
from arb.utils.excel.xl_parse import convert_upload_to_json, get_json_file_name_old
from arb.utils.json import extract_id_from_json, json_load_with_meta
from arb.utils.web_html import upload_single_file

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def xl_dict_to_database(db: SQLAlchemy,
                        base: AutomapBase,
                        xl_dict: dict,
                        tab_name: str = "Feedback Form",
                        dry_run: bool = False) -> tuple[int, str]:
  """
  Convert parsed Excel payload to DB insert/update or staging.

  Args:
    db (SQLAlchemy): DB instance.
    base (AutomapBase): Reflected schema base.
    xl_dict (dict): JSON payload from Excel parser.
    tab_name (str): Sheet name to extract.
    dry_run (bool): If True, simulate insert only.

  Returns:
    tuple[int, str]: (id_incidence, sector)
  """
  logger.debug(f"xl_dict_to_database() called with {xl_dict=}")
  metadata = xl_dict["metadata"]
  sector = metadata["sector"]
  tab_data = xl_dict["tab_contents"][tab_name]
  tab_data["sector"] = sector

  id_ = dict_to_database(db, base, tab_data, dry_run=dry_run)
  return id_, sector


def dict_to_database(db: SQLAlchemy,
                     base: AutomapBase,
                     data_dict: dict,
                     table_name: str = "incidences",
                     primary_key: str = "id_incidence",
                     json_field: str = "misc_json",
                     dry_run: bool = False) -> int:
  """
  Insert or update a row in the specified table using a dictionary payload.

  If `dry_run` is True, no database write will occur. This is useful for staging uploads.

  Args:
    db (SQLAlchemy): SQLAlchemy DB instance.
    base (AutomapBase): Reflected model metadata.
    data_dict (dict): Dictionary payload to insert/update.
    table_name (str): Table name to target.
    primary_key (str): Primary key column.
    json_field (str): Name of JSON field for form payload.
    dry_run (bool): If True, simulate logic without writing to DB.

  Returns:
    int: The id_incidence (or equivalent PK) inferred from payload or model.

  Raises:
    ValueError: If data_dict is empty.
    AttributeError: If PK cannot be resolved.
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

  if is_new_row:
    logger.debug(f"Backfilling {primary_key} = {id_} into payload")
    data_dict[primary_key] = id_

  update_model_with_payload(model, data_dict, json_field=json_field)

  if not dry_run:
    db.session.add(model)
    db.session.commit()

  # Final safety: extract final PK from the model
  try:
    return getattr(model, primary_key)
  except AttributeError as e:
    logger.error(f"Model has no attribute '{primary_key}': {e}")
    raise


def json_file_to_db(db: SQLAlchemy,
                    file_name: str | Path,
                    base: AutomapBase,
                    dry_run: bool = False) -> tuple[int, str]:
  """
  Parse and optionally insert a structured JSON file into DB.

  Args:
    db (SQLAlchemy): DB engine.
    file_name (Path): Path to .json file.
    base (AutomapBase): Reflected schema.
    dry_run (bool): If True, simulate insert only.

  Returns:
    tuple[int, str]: (id_incidence, sector)
  """
  # todo - datetime - looks like this is where the json file gets loaded
  json_as_dict, metadata = json_load_with_meta(file_name)
  return xl_dict_to_database(db, base, json_as_dict, dry_run=dry_run)


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
  json_file_name = get_json_file_name_old(file_name)
  if json_file_name:
    id_, sector = json_file_to_db(db, json_file_name, base)

  return file_name, id_, sector


def upload_and_update_db(db: SQLAlchemy,
                         upload_dir: str | Path,
                         request_file: FileStorage,
                         base: AutomapBase
                         ) -> tuple[Path, int | None, str | None]:
  """
  Save uploaded Excel file, convert to JSON, and write parsed contents to the database.

  Args:
    db (SQLAlchemy): SQLAlchemy database instance.
    upload_dir (str | Path): Directory where the uploaded file should be saved.
    request_file (FileStorage): File uploaded via the Flask request.
    base (AutomapBase): SQLAlchemy base object from automap reflection.

  Returns:
    tuple[Path, int | None, str | None]: Tuple of:
      - file path of saved Excel file,
      - id_incidence of inserted row (if any),
      - sector extracted from the JSON file.

  Notes:
    - This function performs a full ingest. It logs the file,
      parses Excel → JSON, and inserts the data into the database.
    - If the file cannot be parsed or inserted, None values are returned.
  """
  logger.debug(f"upload_and_update_db() called with {request_file=}")
  id_ = None
  sector = None

  file_path = upload_single_file(upload_dir, request_file)
  add_file_to_upload_table(db, file_path, status="File Added", description=None)

  json_path, sector = convert_excel_to_json_if_valid(file_path)
  if json_path:
    id_, _ = json_file_to_db(db, json_path, base)  # ✅ Perform full ingest

  return file_path, id_, sector


def convert_file_to_json_old(file_path: Path) -> Path | None:
  """
  Depreciated. use convert_excel_to_json_if_valid instead.

  Convert an uploaded Excel file to a JSON file, if possible.

  Args:
    file_path (Path): Path to the saved Excel file.

  Returns:
    Path | None: Path to the generated JSON file, or None if conversion failed.
  """
  json_file_path = get_json_file_name_old(file_path)
  if not json_file_path:
    logger.warning(f"File {file_path} could not be converted to JSON.")
    return None
  logger.debug(f"Converted Excel to JSON: {json_file_path}")
  return json_file_path


def extract_sector_from_json(json_path: Path) -> str | None:
  """
  Extract the sector name from a JSON file generated from Excel.

  Args:
    json_path (Path): Path to the JSON file.

  Returns:
    str | None: The sector name if found; otherwise, None.
  """
  try:
    json_data, _ = json_load_with_meta(json_path)
    return json_data.get("metadata", {}).get("sector")
  except Exception as e:
    logger.warning(f"Could not extract sector from {json_path}: {e}")
    return None


def convert_excel_to_json_if_valid(file_path: Path) -> tuple[Path | None, str | None]:
  """
  Convert an uploaded Excel or JSON file into a standardized JSON format,
  and return the output path and detected sector.

  Args:
    file_path (Path): Path to the uploaded file (Excel or JSON).

  Returns:
    tuple[Path | None, str | None]:
      - JSON file path (parsed or original),
      - sector string (if detected).
  """
  json_path = convert_upload_to_json(file_path)
  if json_path:
    logger.debug(f"File converted or passed through to JSON: {json_path}")
    sector = extract_sector_from_json(json_path)
    return json_path, sector
  else:
    logger.warning(f"Unable to convert uploaded file to JSON: {file_path}")
    return None, None


def store_staged_payload(id_: int, sector: str, json_data: dict) -> Path:
  """
  Save a parsed but uncommitted JSON payload to a staging directory.

  Args:
    id_ (int): Incidence ID.
    sector (str): Sector name (used for file naming).
    json_data (dict): Parsed JSON dictionary to save.

  Returns:
    Path: Path to the saved staging file.
  """
  from arb.utils.io_wrappers import save_json_safely

  staging_dir = Path(get_upload_folder()) / "staging"
  staging_dir.mkdir(parents=True, exist_ok=True)

  file_name = f"id_{id_}_{sector.lower()}.json"
  path = staging_dir / file_name
  save_json_safely(json_data, path)
  return path


def upload_and_stage_only(db: SQLAlchemy,
                          upload_dir: str | Path,
                          request_file: FileStorage,
                          base: AutomapBase
                          ) -> tuple[Path, int | None, str | None, dict]:
  """
  Save an uploaded Excel or JSON file, convert to JSON, and stage it for review.

  This function mimics upload_and_update_db() to ensure parity, but differs in that:
    - It does NOT update the database.
    - It returns the parsed JSON dict for review purposes.

  Args:
    db (SQLAlchemy): Active SQLAlchemy database instance.
    upload_dir (str | Path): Target upload folder path.
    request_file (FileStorage): Uploaded file from Flask request.
    base (AutomapBase): Reflected metadata (currently unused but passed for consistency).

  Returns:
    tuple[Path, int | None, str | None, dict]: Saved file path, extracted id_incidence,
    sector name, and parsed JSON contents.
  """
  logger.debug(f"upload_and_stage_only() called with {request_file=}")
  id_ = None
  sector = None
  json_data = {}

  file_path = upload_single_file(upload_dir, request_file)
  add_file_to_upload_table(db, file_path, status="File Added", description="Staged only (no DB write)")

  json_path, sector = convert_excel_to_json_if_valid(file_path)
  if json_path:
    json_data, _ = json_load_with_meta(json_path)
    id_ = extract_id_from_json(json_data)

  return file_path, id_, sector, json_data
