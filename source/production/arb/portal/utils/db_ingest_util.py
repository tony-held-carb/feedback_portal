"""
  Database ingestion helpers for inserting or updating rows based on structured dictionaries,
  particularly those derived from Excel templates.

  This module provides:
    - Generic row ingestion from any dict using SQLAlchemy reflection
    - Excel-specific wrapper for sector-based data (xl_dict_to_database)

  Attributes:
    logger (logging.Logger): Logger instance for this module.

  Examples:
    from arb.portal.utils.db_ingest_util import xl_dict_to_database, dict_to_database
    id_, sector = xl_dict_to_database(db, base, xl_dict)

  Notes:
    - Used by upload and staging routes to process Excel/JSON payloads.
    - The logger emits a debug message when this file is loaded.
"""
import datetime
import logging
from pathlib import Path
from typing import Any

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import AutomapBase
from werkzeug.datastructures import FileStorage

from arb.portal.config.accessors import get_upload_folder
from arb.portal.startup.runtime_info import LOG_DIR
from arb.portal.utils.db_introspection_util import get_ensured_row
from arb.portal.utils.file_upload_util import add_file_to_upload_table
from arb.portal.utils.import_audit import generate_import_audit
from arb.portal.utils.result_types import (
    StagingResult, UploadResult, FileSaveResult, FileConversionResult,
    IdValidationResult, StagedFileResult, DatabaseInsertResult,
    FileUploadResult, FileAuditResult, JsonProcessingResult
)
from arb.utils.excel.xl_parse import convert_upload_to_json, get_json_file_name_old, parse_xl_file, xl_schema_map
from arb.utils.json import extract_id_from_json, json_load_with_meta
from arb.utils.web_html import upload_single_file

logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def extract_tab_and_sector(xl_dict: dict, tab_name: str = "Feedback Form") -> dict:
  """
  Extract form data from Excel-parsed JSON and include sector from metadata.

  Args:
    xl_dict (dict): Parsed Excel document with 'metadata' and 'tab_contents'.
    tab_name (str): Name of the worksheet tab to extract. Defaults to 'Feedback Form'.

  Returns:
    dict: Combined payload with tab_contents and sector included.

  Raises:
    ValueError: If the tab_name is missing or sector cannot be determined.

  Examples:
    form_data = extract_tab_and_sector(xl_dict)
    # Returns a dict with form data and sector

  Notes:
    - Ensures consistency between staged and production uploads.
    - Logs a warning if sector is missing in metadata.
  """
  if "tab_contents" not in xl_dict or tab_name not in xl_dict["tab_contents"]:
    raise ValueError(f"Tab '{tab_name}' not found in xl_dict")

  # Extract sector from metadata
  metadata = xl_dict.get("metadata", {})
  sector = metadata.get("sector")
  if not sector:
    logger.warning(f"No sector found in xl_dict metadata: {metadata}")
    sector = "Unknown"  # Fallback to prevent errors

  # Get form data and add sector
  form_data = xl_dict["tab_contents"][tab_name].copy()
  form_data["sector"] = sector

  logger.debug(f"extract_tab_and_sector: extracted form data with sector '{sector}' from tab '{tab_name}'")
  return form_data


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

  Examples:
    id_, sector = xl_dict_to_database(db, base, xl_dict)
    # Inserts or stages the Excel data

  Notes:
    - For future consistency, consider using extract_tab_and_sector for all ingestion.
  """
  logger.debug(f"xl_dict_to_database() called with {xl_dict=}")
  metadata = xl_dict["metadata"]
  sector = metadata["sector"]
  tab_data = xl_dict["tab_contents"][tab_name]
  tab_data["sector"] = sector

  id_ = dict_to_database(db, base, tab_data, dry_run=dry_run)
  return id_, sector


def validate_payload_for_database(data_dict: dict) -> None:
  """
  Validate that a payload is suitable for database operations.

  Args:
    data_dict (dict): Dictionary payload to validate.

  Raises:
    ValueError: If data_dict is empty or invalid.

  Examples:
    validate_payload_for_database(data_dict)
    # Validates the payload before database operations
  """
  if not data_dict:
    msg = "Attempt to add empty entry to database"
    logger.warning(msg)
    raise ValueError(msg)

  logger.debug(f"Payload validation passed for dict with {len(data_dict)} keys")


def resolve_database_row(db: SQLAlchemy,
                         base: AutomapBase,
                         data_dict: dict,
                         table_name: str = "incidences",
                         primary_key: str = "id_incidence") -> tuple[Any, int, bool]:
  """
  Resolve or create a database row for the given payload.

  Args:
    db (SQLAlchemy): SQLAlchemy DB instance.
    base (AutomapBase): Reflected model metadata.
    data_dict (dict): Dictionary payload containing the primary key.
    table_name (str): Table name to target.
    primary_key (str): Primary key column name.

  Returns:
    tuple[Any, int, bool]: (model, id_, is_new_row)
      - model: SQLAlchemy ORM instance
      - id_: Primary key value
      - is_new_row: Whether a new row was created

  Examples:
    model, id_, is_new = resolve_database_row(db, base, data_dict)
    # Resolves or creates the database row
  """
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

  return model, id_, is_new_row


def update_model_with_payload_and_commit(db: SQLAlchemy,
                                         model: Any,
                                         data_dict: dict,
                                         json_field: str = "misc_json",
                                         dry_run: bool = False) -> None:
  """
  Update a model with payload data and commit to database.

  Args:
    db (SQLAlchemy): SQLAlchemy DB instance.
    model (Any): SQLAlchemy ORM instance to update.
    data_dict (dict): Dictionary payload to apply.
    json_field (str): Name of JSON field for form payload.
    dry_run (bool): If True, simulate logic without writing to DB.

  Examples:
    update_model_with_payload_and_commit(db, model, data_dict)
    # Updates the model and commits changes
  """
  from arb.utils.wtf_forms_util import update_model_with_payload

  update_model_with_payload(model, data_dict, json_field=json_field)

  if not dry_run:
    db.session.add(model)
    db.session.commit()
    logger.debug(f"Model updated and committed to database")


def extract_primary_key_from_model(model: Any, primary_key: str = "id_incidence") -> int:
  """
  Extract the primary key value from a model instance.

  Args:
    model (Any): SQLAlchemy ORM instance.
    primary_key (str): Name of the primary key attribute.

  Returns:
    int: The primary key value.

  Raises:
    AttributeError: If the model doesn't have the specified primary key.

  Examples:
    id_ = extract_primary_key_from_model(model)
    # Extracts the primary key value safely
  """
  try:
    return getattr(model, primary_key)
  except AttributeError as e:
    logger.error(f"Model has no attribute '{primary_key}': {e}")
    raise


def dict_to_database_refactored(db: SQLAlchemy,
                                base: AutomapBase,
                                data_dict: dict,
                                table_name: str = "incidences",
                                primary_key: str = "id_incidence",
                                json_field: str = "misc_json",
                                dry_run: bool = False) -> int:
  """
  Refactored version of dict_to_database that uses smaller, focused functions.

  This function provides the same interface and behavior as dict_to_database,
  but uses the new smaller functions for better maintainability and testing.

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

  Examples:
    id_ = dict_to_database_refactored(db, base, data_dict)
    # Inserts or updates the row in the database using refactored functions

  Notes:
    - This is a refactored version that maintains the same interface as dict_to_database.
    - Uses the new smaller functions for better separation of concerns.
    - Can be used as a drop-in replacement once thoroughly tested.
  """
  logger.debug(f"dict_to_database_refactored() called with {len(data_dict)} keys")

  # Step 1: Validate the payload
  validate_payload_for_database(data_dict)

  # Step 2: Resolve or create the database row
  model, id_, is_new_row = resolve_database_row(
    db=db,
    base=base,
    data_dict=data_dict,
    table_name=table_name,
    primary_key=primary_key
  )

  # Step 3: Update the model and commit
  update_model_with_payload_and_commit(
    db=db,
    model=model,
    data_dict=data_dict,
    json_field=json_field,
    dry_run=dry_run
  )

  # Step 4: Extract and return the primary key
  return extract_primary_key_from_model(model, primary_key)


def dict_to_database(db: SQLAlchemy,
                     base: AutomapBase,
                     data_dict: dict,
                     table_name: str = "incidences",
                     primary_key: str = "id_incidence",
                     json_field: str = "misc_json",
                     dry_run: bool = False) -> int:
  """
  Insert or update a row in the specified table using a dictionary payload.

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

  Examples:
    id_ = dict_to_database(db, base, data_dict)
    # Inserts or updates the row in the database

  Notes:
    - Uses get_ensured_row and update_model_with_payload for safe upsert.
    - Commits the session unless dry_run is True.
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

  Examples:
    id_, sector = json_file_to_db(db, "file.json", base)
    # Loads JSON and inserts or stages the data
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

  Examples:
    file_name, id_, sector = upload_and_update_db_old(db, upload_dir, request_file, base)
    # Handles upload and DB insert (deprecated)

  Notes:
    - If the file is Excel and can be converted to JSON, saves a JSON version and returns the filename.
    - Deprecated in favor of staged upload logic.
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


def upload_and_process_file(db: SQLAlchemy,
                            upload_dir: str | Path,
                            request_file: FileStorage,
                            base: AutomapBase) -> UploadResult:
  """
  Process uploaded Excel file and insert parsed contents directly into the database.

  This function provides a modular, refactored approach to file upload and database
  insertion with improved error handling and clear separation of concerns.

  Args:
      db (SQLAlchemy): SQLAlchemy database instance.
      upload_dir (str | Path): Directory where the uploaded file should be saved.
      request_file (FileStorage): File uploaded via the Flask request.
      base (AutomapBase): SQLAlchemy base object from automap reflection.

  Returns:
      UploadResult: Named tuple containing the result of the upload process with
                   detailed error information and success indicators.

  Examples:
      result = upload_and_process_file(db, upload_dir, request_file, base)
      if result.success:
          # Redirect to incidence update page
          return redirect(url_for('main.incidence_update', id_=result.id_))
      else:
          # Handle specific error types
          if result.error_type == "missing_id":
              return render_template('upload.html', upload_message=result.error_message)
          elif result.error_type == "conversion_failed":
              return render_template('upload.html', upload_message=result.error_message)

  Notes:
      - Performs a full ingest: logs the file, parses Excel → JSON, and inserts the data into the database.
      - Returns detailed error information for better user experience and debugging.
      - Maintains the same functionality as upload_and_update_db but with improved structure.
      - Uses shared helper functions for consistency with stage_uploaded_file_for_review.
  """
  logger.debug(f"upload_and_process_file() called with {request_file=}")

  # Step 1: Save uploaded file
  save_result = save_uploaded_file_with_result(upload_dir, request_file, db, description="Direct upload to database")
  if not save_result.success:
    return UploadResult(
      file_path=Path("unknown"),
      id_=None,
      sector=None,
      success=False,
      error_message=save_result.error_message,
      error_type=save_result.error_type
    )

  # Step 2: Convert file to JSON and extract data
  conversion_result = convert_file_to_json_with_result(save_result.file_path)
  if not conversion_result.success:
    return UploadResult(
      file_path=save_result.file_path,
      id_=None,
      sector=conversion_result.sector,
      success=False,
      error_message=conversion_result.error_message,
      error_type=conversion_result.error_type
    )

  # Step 3: Validate ID from JSON data
  validation_result = validate_id_from_json_with_result(conversion_result.json_data)
  if not validation_result.success:
    return UploadResult(
      file_path=save_result.file_path,
      id_=None,
      sector=conversion_result.sector,
      success=False,
      error_message=validation_result.error_message,
      error_type=validation_result.error_type
    )

  # Step 4: Insert data into database
  insert_result = insert_json_into_database_with_result(conversion_result.json_path, base, db)
  if not insert_result.success:
    return UploadResult(
      file_path=save_result.file_path,
      id_=None,
      sector=conversion_result.sector,
      success=False,
      error_message=insert_result.error_message,
      error_type=insert_result.error_type
    )

  # Success case
  return UploadResult(
    file_path=save_result.file_path,
    id_=insert_result.id_,
    sector=conversion_result.sector,
    success=True,
    error_message=None,
    error_type=None
  )


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

  Examples:
    file_name, id_, sector = upload_and_update_db(db, upload_dir, request_file, base)
    # Handles upload, conversion, and DB insert

  Notes:
    - Performs a full ingest: logs the file, parses Excel → JSON, and inserts the data into the database.
    - If the file cannot be parsed or inserted, None values are returned.
    - Uploads will be blocked if id_incidence is missing or not a valid positive integer.
  """
  logger.debug(f"upload_and_update_db() called with {request_file=}")
  id_ = None
  sector = None

  file_path = upload_single_file(upload_dir, request_file)
  add_file_to_upload_table(db, file_path, status="File Added", description=None)

  json_path, sector = convert_excel_to_json_if_valid(file_path)
  # --- DIAGNOSTIC: Generate import audit ---
  try:
    parse_result = parse_xl_file(file_path)
    audit = generate_import_audit(file_path, parse_result, xl_schema_map, route="upload_file")
    audit_log_path = LOG_DIR / "import_audit.log"
    audit_log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(audit_log_path, "a", encoding="utf-8") as f:
      f.write(audit + "\n\n")
  except Exception as e:
    logging.getLogger(__name__).warning(f"Failed to generate import audit: {e}")
  # --- END DIAGNOSTIC ---
  if json_path:
    json_data, _ = json_load_with_meta(json_path)
    id_candidate = extract_id_from_json(json_data)
    if not (isinstance(id_candidate, int) and id_candidate > 0):
      logger.warning(f"Upload blocked: id_incidence missing or not a valid positive integer in {file_path.name}")
      return file_path, None, None
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
                          ) -> tuple[Path, int | None, str | None, dict, str]:
  """
  Save an uploaded Excel or JSON file, convert to JSON, and stage it for review.

  This function mimics upload_and_update_db() to ensure parity, but differs in that:
    - It does NOT update the database.
    - It returns the parsed JSON dict for review purposes.
    - It saves the current DB misc_json as 'base_misc_json' in the staged file's metadata.
    - It uses a timestamped filename for the staged file.
    - It ensures all values are JSON-serializable (datetime → ISO strings, etc.) before staging.

  Args:
    db (SQLAlchemy): Active SQLAlchemy database instance.
    upload_dir (str | Path): Target upload folder path.
    request_file (FileStorage): Uploaded file from Flask request.
    base (AutomapBase): Reflected metadata (currently unused but passed for consistency).

  Returns:
    tuple[Path, int | None, str | None, dict, str]: Saved file path, extracted id_incidence,
    sector name, parsed JSON contents, and the staged filename (not full path).

  Examples:
    file_path, id_, sector, json_data, staged_filename = upload_and_stage_only(db, upload_dir, request_file, base)
    # Handles upload, conversion, and staging

  Notes:
    - Staging will be blocked if id_incidence is missing or not a valid positive integer.
  """
  from arb.utils.json import json_save_with_meta
  from arb.utils.wtf_forms_util import prep_payload_for_json

  logger.debug(f"upload_and_stage_only() called with {request_file=}")
  id_ = None
  sector = None
  json_data = {}

  file_path = upload_single_file(upload_dir, request_file)
  add_file_to_upload_table(db, file_path, status="File Added", description="Staged only (no DB write)")

  json_path, sector = convert_excel_to_json_if_valid(file_path)
  # --- DIAGNOSTIC: Generate import audit ---
  try:
    parse_result = parse_xl_file(file_path)
    audit = generate_import_audit(file_path, parse_result, xl_schema_map, route="upload_staged")
    audit_log_path = LOG_DIR / "import_audit.log"
    audit_log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(audit_log_path, "a", encoding="utf-8") as f:
      f.write(audit + "\n\n")
  except Exception as e:
    logging.getLogger(__name__).warning(f"Failed to generate import audit: {e}")
  # --- END DIAGNOSTIC ---
  if json_path:
    json_data, _ = json_load_with_meta(json_path)
    id_candidate = extract_id_from_json(json_data)
    if not (isinstance(id_candidate, int) and id_candidate > 0):
      logger.warning(f"Staging blocked: id_incidence missing or not a valid positive integer in {file_path.name}")
      return file_path, None, None, {}, ""
    id_ = extract_id_from_json(json_data)
    # 🆕 Staging logic: write to upload_dir/staging/{id_}_ts_YYYYMMDD_HHMMSS.json
    if id_:
      model, _, _ = get_ensured_row(db, base, table_name="incidences", primary_key_name="id_incidence", id_=id_)
      base_misc_json = getattr(model, "misc_json", {}) or {}
      json_data = prep_payload_for_json(json_data)
      staging_dir = Path(upload_dir) / "staging"
      staging_dir.mkdir(parents=True, exist_ok=True)
      staged_filename = f"id_{id_}_ts_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
      staged_path = staging_dir / staged_filename
      json_save_with_meta(staged_path, json_data, metadata={"base_misc_json": base_misc_json})
      logger.debug(f"Staged JSON saved to: {staged_path}")
      add_file_to_upload_table(db, staged_path, status="Staged JSON", description="Staged file with base_misc_json")
      return file_path, id_, sector, json_data, staged_filename
    else:
      logger.warning("id_incidence could not be extracted. Staging file was not created.")
  return file_path, None, None, {}, ""


# =============================================================================
# REFACTORED STAGING FUNCTIONS - PARALLEL IMPLEMENTATION
# =============================================================================


def _save_uploaded_file(upload_dir: str | Path, request_file: FileStorage, db: SQLAlchemy,
                        description: str | None = None) -> Path:
  """
  Save an uploaded file to the upload directory.

  Args:
      upload_dir (str | Path): Directory to save the file in
      request_file (FileStorage): File uploaded via Flask request
      db (SQLAlchemy): Database instance for logging upload
      description (str | None): Optional description for the upload table entry

  Returns:
      Path: Path to the saved file

  Raises:
      ValueError: If file upload fails

  Examples:
      file_path = _save_uploaded_file(upload_dir, request_file, db)
      # Saves the uploaded file and returns its path
  """
  try:
    file_path = upload_single_file(upload_dir, request_file)
    add_file_to_upload_table(db, file_path, status="File Added", description=description)
    logger.debug(f"Uploaded file saved to: {file_path}")
    return file_path
  except Exception as e:
    logger.error(f"Failed to save uploaded file: {e}")
    raise ValueError(f"File upload failed: {e}")


def _convert_file_to_json(file_path: Path) -> tuple[Path | None, str | None, dict, str | None]:
  """
  Convert uploaded file to JSON format and extract sector and data.

  Args:
      file_path (Path): Path to the uploaded file

  Returns:
      tuple[Path | None, str | None, dict, str | None]: (JSON file path, sector name, json_data, error_message)
      - JSON file path: Path to converted JSON file (None if conversion failed)
      - sector name: Extracted sector name (None if conversion failed)
      - json_data: Parsed JSON data (empty dict if parsing failed)
      - error_message: Error message if conversion failed (None if successful)

  Examples:
      json_path, sector, json_data, error = _convert_file_to_json(file_path)
      if json_path:
          # Conversion successful
      else:
          # Conversion failed, check error message
  """
  try:
    json_path, sector = convert_excel_to_json_if_valid(file_path)

    # Generate import audit for diagnostics
    try:
      parse_result = parse_xl_file(file_path)
      audit = generate_import_audit(file_path, parse_result, xl_schema_map, route="upload_file")
      audit_log_path = LOG_DIR / "import_audit.log"
      audit_log_path.parent.mkdir(parents=True, exist_ok=True)
      with open(audit_log_path, "a", encoding="utf-8") as f:
        f.write(audit + "\n\n")
    except Exception as e:
      logger.warning(f"Failed to generate import audit: {e}")

    if not json_path:
      return None, None, {}, "File could not be converted to JSON format"

    json_data, _ = json_load_with_meta(json_path)
    logger.debug(f"File converted to JSON: {json_path}, sector: {sector}")
    return json_path, sector, json_data, None

  except Exception as e:
    logger.error(f"Error during file conversion: {e}")
    return None, None, {}, f"Error converting file to JSON: {e}"


def _validate_id_from_json(json_data: dict) -> tuple[int | None, str | None]:
  """
  Validate and extract id_incidence from JSON data.

  Args:
      json_data (dict): Parsed JSON data

  Returns:
      tuple[int | None, str | None]: (id_incidence, error_message)
      - id_incidence: Extracted ID (None if missing/invalid)
      - error_message: Error message if validation failed (None if successful)

  Examples:
      id_, error = _validate_id_from_json(json_data)
      if id_:
          # Valid ID found
      else:
          # Missing or invalid ID, check error message
  """
  try:
    id_candidate = extract_id_from_json(json_data)

    if isinstance(id_candidate, int) and id_candidate > 0:
      logger.debug(f"Valid id_incidence found: {id_candidate}")
      return id_candidate, None
    else:
      logger.warning(f"Invalid or missing id_incidence: {id_candidate}")
      return None, "No valid id_incidence found in spreadsheet"
  except Exception as e:
    logger.error(f"Error extracting ID from JSON: {e}")
    return None, f"Error extracting ID from JSON: {e}"


def _create_staged_file(id_: int, json_data: dict, db: SQLAlchemy, base: AutomapBase,
                        upload_dir: str | Path) -> str | None:
  """
  Create a staged file for review with base_misc_json metadata.

  Args:
      id_ (int): Valid incidence ID
      json_data (dict): Parsed JSON data to stage
      db (SQLAlchemy): Database instance
      base (AutomapBase): Reflected metadata
      upload_dir (str | Path): Upload directory

  Returns:
      str | None: Staged filename (None if staging failed)

  Examples:
      staged_filename = _create_staged_file(id_, json_data, db, base, upload_dir)
      if staged_filename:
          # Staging successful
      else:
          # Staging failed
  """
  try:
    from arb.utils.json import json_save_with_meta
    from arb.utils.wtf_forms_util import prep_payload_for_json

    # Get current database state for comparison
    model, _, _ = get_ensured_row(db, base, table_name="incidences", primary_key_name="id_incidence", id_=id_)
    base_misc_json = getattr(model, "misc_json", {}) or {}

    # Prepare JSON data for staging
    json_data = prep_payload_for_json(json_data)

    # Create staging directory and filename
    staging_dir = Path(upload_dir) / "staging"
    staging_dir.mkdir(parents=True, exist_ok=True)
    staged_filename = f"id_{id_}_ts_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    staged_path = staging_dir / staged_filename

    # Save staged file with metadata
    json_save_with_meta(staged_path, json_data, metadata={"base_misc_json": base_misc_json})
    add_file_to_upload_table(db, staged_path, status="Staged JSON", description="Staged file with base_misc_json")

    logger.debug(f"Staged file created: {staged_path}")
    return staged_filename
  except Exception as e:
    logger.error(f"Error creating staged file: {e}")
    return None


def _insert_json_into_database(json_path: Path, base: AutomapBase, db: SQLAlchemy) -> tuple[int | None, str | None]:
  """
  Insert JSON data into the database.

  Args:
      json_path (Path): Path to the JSON file
      base (AutomapBase): SQLAlchemy base object from automap reflection
      db (SQLAlchemy): SQLAlchemy database instance

  Returns:
      tuple[int | None, str | None]: (id_, error_message)
      - id_: Inserted incidence ID (None if insertion failed)
      - error_message: Error message if insertion failed (None if successful)

  Examples:
      id_, error = _insert_json_into_database(json_path, base, db)
      if id_:
          # Insertion successful
      else:
          # Insertion failed, check error message
  """
  try:
    id_, _ = json_file_to_db(db, json_path, base)
    return id_, None
  except Exception as e:
    logger.error(f"Error inserting data into database: {e}")
    return None, f"Database error occurred during insertion: {e}"


def stage_uploaded_file_for_review(db: SQLAlchemy,
                                   upload_dir: str | Path,
                                   request_file: FileStorage,
                                   base: AutomapBase) -> StagingResult:
  """
  Stage an uploaded file for review without committing to database.

  This function handles the complete staging workflow:
  1. Save the uploaded file
  2. Convert to JSON format
  3. Validate and extract id_incidence
  4. Create staged file with metadata

  Args:
      db (SQLAlchemy): Active SQLAlchemy database instance
      upload_dir (str | Path): Target upload folder path
      request_file (FileStorage): Uploaded file from Flask request
      base (AutomapBase): Reflected metadata

  Returns:
      StagingResult: Rich result object with success/failure information

  Examples:
      result = stage_uploaded_file_for_review(db, upload_dir, request_file, base)

      if result.success:
          # Staging successful
          flash(f"File staged successfully: {result.staged_filename}")
      else:
          # Handle specific error
          if result.error_type == "missing_id":
              flash("Please add a valid ID to your spreadsheet")
          elif result.error_type == "conversion_failed":
              flash("Please upload an Excel file")
          else:
              flash(f"Error: {result.error_message}")

  Notes:
      - This function does NOT update the database
      - Staging will be blocked if id_incidence is missing or invalid
      - All values are JSON-serializable before staging
      - Includes current database state as base_misc_json for comparison
  """
  logger.debug(f"stage_uploaded_file_for_review() called with {request_file.filename}")

  # Step 1: Save the uploaded file
  save_result = save_uploaded_file_with_result(upload_dir, request_file, db, description="Staged only (no DB write)")
  if not save_result.success:
    return StagingResult(
      file_path=Path("unknown"),
      id_=None,
      sector=None,
      json_data={},
      staged_filename=None,
      success=False,
      error_message=save_result.error_message,
      error_type=save_result.error_type
    )

  # Step 2: Convert file to JSON and extract sector
  conversion_result = convert_file_to_json_with_result(save_result.file_path)
  if not conversion_result.success:
    return StagingResult(
      file_path=save_result.file_path,
      id_=None,
      sector=None,
      json_data={},
      staged_filename=None,
      success=False,
      error_message=conversion_result.error_message,
      error_type=conversion_result.error_type
    )

  # Step 3: Validate and extract id_incidence
  validation_result = validate_id_from_json_with_result(conversion_result.json_data)
  if not validation_result.success:
    return StagingResult(
      file_path=save_result.file_path,
      id_=None,
      sector=conversion_result.sector,
      json_data=conversion_result.json_data,
      staged_filename=None,
      success=False,
      error_message=validation_result.error_message,
      error_type=validation_result.error_type
    )

  # Step 4: Create staged file
  staging_result = create_staged_file_with_result(validation_result.id_, conversion_result.json_data, db, base, upload_dir)
  if not staging_result.success:
    return StagingResult(
      file_path=save_result.file_path,
      id_=validation_result.id_,
      sector=conversion_result.sector,
      json_data=conversion_result.json_data,
      staged_filename=None,
      success=False,
      error_message=staging_result.error_message,
      error_type=staging_result.error_type
    )

  # Success case
  logger.debug(f"Staging successful: id={validation_result.id_}, sector={conversion_result.sector}, filename={staging_result.staged_filename}")
  return StagingResult(
    file_path=save_result.file_path,
    id_=validation_result.id_,
    sector=conversion_result.sector,
    json_data=conversion_result.json_data,
    staged_filename=staging_result.staged_filename,
    success=True,
    error_message=None,
    error_type=None
  )


def save_uploaded_file_with_result(upload_dir: str | Path, request_file: FileStorage, db: SQLAlchemy,
                                  description: str | None = None) -> FileSaveResult:
    """
    Save an uploaded file to the upload directory with rich result information.

    This function provides a type-safe alternative to _save_uploaded_file with
    detailed error information and clear success/failure indicators.

    Args:
        upload_dir (str | Path): Directory to save the file in
        request_file (FileStorage): File uploaded via Flask request
        db (SQLAlchemy): Database instance for logging upload
        description (str | None): Optional description for the upload table entry

    Returns:
        FileSaveResult: Rich result object with success/failure information

    Examples:
        result = save_uploaded_file_with_result(upload_dir, request_file, db)
        if result.success:
            # File saved successfully
            file_path = result.file_path
        else:
            # Handle error
            if result.error_type == "file_error":
                flash(f"File upload failed: {result.error_message}")
    """
    try:
        file_path = upload_single_file(upload_dir, request_file)
        add_file_to_upload_table(db, file_path, status="File Added", description=description)
        logger.debug(f"Uploaded file saved to: {file_path}")
        return FileSaveResult(
            file_path=file_path,
            success=True,
            error_message=None,
            error_type=None
        )
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        return FileSaveResult(
            file_path=None,
            success=False,
            error_message=f"File upload failed: {e}",
            error_type="file_error"
        )


def convert_file_to_json_with_result(file_path: Path) -> FileConversionResult:
    """
    Convert uploaded file to JSON format with rich result information.

    This function provides a type-safe alternative to _convert_file_to_json with
    detailed error information and clear success/failure indicators.

    Args:
        file_path (Path): Path to the uploaded file

    Returns:
        FileConversionResult: Rich result object with conversion information

    Examples:
        result = convert_file_to_json_with_result(file_path)
        if result.success:
            # Conversion successful
            json_path = result.json_path
            sector = result.sector
            json_data = result.json_data
        else:
            # Handle conversion error
            if result.error_type == "conversion_failed":
                flash(f"File conversion failed: {result.error_message}")
    """
    try:
        json_path, sector = convert_excel_to_json_if_valid(file_path)

        # Generate import audit for diagnostics
        try:
            parse_result = parse_xl_file(file_path)
            audit = generate_import_audit(file_path, parse_result, xl_schema_map, route="upload_file")
            audit_log_path = LOG_DIR / "import_audit.log"
            audit_log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(audit_log_path, "a", encoding="utf-8") as f:
                f.write(audit + "\n\n")
        except Exception as e:
            logger.warning(f"Failed to generate import audit: {e}")

        if not json_path:
            return FileConversionResult(
                json_path=None,
                sector=None,
                json_data={},
                success=False,
                error_message="Unsupported file format. Please upload Excel (.xlsx) file.",
                error_type="conversion_failed"
            )

        json_data, _ = json_load_with_meta(json_path)
        logger.debug(f"File converted to JSON: {json_path}, sector: {sector}")
        return FileConversionResult(
            json_path=json_path,
            sector=sector,
            json_data=json_data,
            success=True,
            error_message=None,
            error_type=None
        )

    except Exception as e:
        logger.error(f"Error during file conversion: {e}")
        return FileConversionResult(
            json_path=None,
            sector=None,
            json_data={},
            success=False,
            error_message=f"Error converting file to JSON: {e}",
            error_type="conversion_failed"
        )


def validate_id_from_json_with_result(json_data: dict) -> IdValidationResult:
    """
    Validate and extract id_incidence from JSON data with rich result information.

    This function provides a type-safe alternative to _validate_id_from_json with
    detailed error information and clear success/failure indicators.

    Args:
        json_data (dict): Parsed JSON data

    Returns:
        IdValidationResult: Rich result object with validation information

    Examples:
        result = validate_id_from_json_with_result(json_data)
        if result.success:
            # Valid ID found
            id_ = result.id_
        else:
            # Handle validation error
            if result.error_type == "missing_id":
                flash(f"ID validation failed: {result.error_message}")
    """
    try:
        id_candidate = extract_id_from_json(json_data)

        if isinstance(id_candidate, int) and id_candidate > 0:
            logger.debug(f"Valid id_incidence found: {id_candidate}")
            return IdValidationResult(
                id_=id_candidate,
                success=True,
                error_message=None,
                error_type=None
            )
        else:
            logger.warning(f"Invalid or missing id_incidence: {id_candidate}")
            return IdValidationResult(
                id_=None,
                success=False,
                error_message="No valid id_incidence found in spreadsheet",
                error_type="missing_id"
            )
    except Exception as e:
        logger.error(f"Error extracting ID from JSON: {e}")
        return IdValidationResult(
            id_=None,
            success=False,
            error_message=f"Error extracting ID from JSON: {e}",
            error_type="validation_error"
        )


def create_staged_file_with_result(id_: int, json_data: dict, db: SQLAlchemy, base: AutomapBase,
                                  upload_dir: str | Path) -> StagedFileResult:
    """
    Create a staged file for review with rich result information.

    This function provides a type-safe alternative to _create_staged_file with
    detailed error information and clear success/failure indicators.

    Args:
        id_ (int): Valid incidence ID
        json_data (dict): Parsed JSON data to stage
        db (SQLAlchemy): Database instance
        base (AutomapBase): Reflected metadata
        upload_dir (str | Path): Upload directory

    Returns:
        StagedFileResult: Rich result object with staging information

    Examples:
        result = create_staged_file_with_result(id_, json_data, db, base, upload_dir)
        if result.success:
            # Staging successful
            staged_filename = result.staged_filename
        else:
            # Handle staging error
            if result.error_type == "database_error":
                flash(f"Staging failed: {result.error_message}")
    """
    try:
        from arb.utils.json import json_save_with_meta
        from arb.utils.wtf_forms_util import prep_payload_for_json

        # Get current database state for comparison
        model, _, _ = get_ensured_row(db, base, table_name="incidences", primary_key_name="id_incidence", id_=id_)
        base_misc_json = getattr(model, "misc_json", {}) or {}

        # Prepare JSON data for staging
        json_data = prep_payload_for_json(json_data)

        # Create staging directory and filename
        staging_dir = Path(upload_dir) / "staging"
        staging_dir.mkdir(parents=True, exist_ok=True)
        staged_filename = f"id_{id_}_ts_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        staged_path = staging_dir / staged_filename

        # Save staged file with metadata
        json_save_with_meta(staged_path, json_data, metadata={"base_misc_json": base_misc_json})
        add_file_to_upload_table(db, staged_path, status="Staged JSON", description="Staged file with base_misc_json")

        logger.debug(f"Staged file created: {staged_path}")
        return StagedFileResult(
            staged_filename=staged_filename,
            success=True,
            error_message=None,
            error_type=None
        )
    except Exception as e:
        logger.error(f"Error creating staged file: {e}")
        return StagedFileResult(
            staged_filename=None,
            success=False,
            error_message=f"Failed to create staged file: {e}",
            error_type="database_error"
        )


def insert_json_into_database_with_result(json_path: Path, base: AutomapBase, db: SQLAlchemy) -> DatabaseInsertResult:
    """
    Insert JSON data into the database with rich result information.

    This function provides a type-safe alternative to _insert_json_into_database with
    detailed error information and clear success/failure indicators.

    Args:
        json_path (Path): Path to the JSON file
        base (AutomapBase): SQLAlchemy base object from automap reflection
        db (SQLAlchemy): SQLAlchemy database instance

    Returns:
        DatabaseInsertResult: Rich result object with insertion information

    Examples:
        result = insert_json_into_database_with_result(json_path, base, db)
        if result.success:
            # Insertion successful
            id_ = result.id_
        else:
            # Handle insertion error
            if result.error_type == "database_error":
                flash(f"Database insertion failed: {result.error_message}")
    """
    try:
        id_, sector = json_file_to_db(db, json_path, base)
        logger.debug(f"JSON data inserted into database: id={id_}, sector={sector}")
        return DatabaseInsertResult(
            id_=id_,
            success=True,
            error_message=None,
            error_type=None
        )
    except Exception as e:
        logger.error(f"Error inserting JSON into database: {e}")
        return DatabaseInsertResult(
            id_=None,
            success=False,
            error_message=f"Database error occurred during insertion: {e}",
            error_type="database_error"
        )


# Phase 6: Enhanced lower-level utility functions with result types

def upload_file_with_result(upload_dir: str | Path, request_file: FileStorage) -> FileUploadResult:
    """
    Enhanced wrapper for upload_single_file with result type return.

    This function provides a robust, type-safe alternative to upload_single_file
    with comprehensive error handling and clear success/failure indicators.

    Args:
        upload_dir (str | Path): Directory where the file should be uploaded
        request_file (FileStorage): File uploaded via Flask request

    Returns:
        FileUploadResult: Rich result object with upload information

    Examples:
        result = upload_file_with_result(upload_dir, request_file)
        if result.success:
            # File uploaded successfully
            file_path = result.file_path
            logger.info(f"File uploaded to: {file_path}")
        else:
            # Handle upload error
            if result.error_type == "validation_error":
                flash("Please select a valid file to upload")
            elif result.error_type == "permission_error":
                flash("Upload failed due to server permissions")

    Notes:
        - Wraps the original upload_single_file function
        - Provides consistent error handling and logging
        - Returns structured result instead of raising exceptions
        - Maintains compatibility with existing upload workflows
    """
    try:
        # Validate inputs
        if not request_file or not request_file.filename:
            return FileUploadResult(
                file_path=None,
                success=False,
                error_message="No file selected or filename is empty",
                error_type="validation_error"
            )

        # Attempt file upload using original function
        file_path = upload_single_file(upload_dir, request_file)
        logger.debug(f"File uploaded successfully to: {file_path}")
        
        return FileUploadResult(
            file_path=file_path,
            success=True,
            error_message=None,
            error_type=None
        )

    except ValueError as e:
        logger.error(f"Validation error during file upload: {e}")
        return FileUploadResult(
            file_path=None,
            success=False,
            error_message=f"File upload validation failed: {e}",
            error_type="validation_error"
        )
    except PermissionError as e:
        logger.error(f"Permission error during file upload: {e}")
        return FileUploadResult(
            file_path=None,
            success=False,
            error_message="Upload failed due to insufficient permissions",
            error_type="permission_error"
        )
    except OSError as e:
        logger.error(f"Disk error during file upload: {e}")
        return FileUploadResult(
            file_path=None,
            success=False,
            error_message=f"Upload failed due to disk error: {e}",
            error_type="disk_error"
        )
    except Exception as e:
        logger.error(f"Unexpected error during file upload: {e}")
        return FileUploadResult(
            file_path=None,
            success=False,
            error_message=f"Unexpected upload error: {e}",
            error_type="unexpected_error"
        )


def audit_file_upload_with_result(db: SQLAlchemy, file_path: Path | str, 
                                 status: str | None = None, 
                                 description: str | None = None) -> FileAuditResult:
    """
    Enhanced wrapper for add_file_to_upload_table with result type return.

    This function provides a robust, type-safe alternative to add_file_to_upload_table
    with comprehensive error handling and clear success/failure indicators.

    Args:
        db (SQLAlchemy): Database instance for audit logging
        file_path (Path | str): Path to the uploaded file
        status (str | None): Optional upload status label
        description (str | None): Optional description for the upload

    Returns:
        FileAuditResult: Rich result object with audit information

    Examples:
        result = audit_file_upload_with_result(db, file_path, "File Added", "Direct upload")
        if result.success:
            logger.info("File upload audit logged successfully")
        else:
            if result.error_type == "database_error":
                logger.warning("Failed to log upload to audit table")

    Notes:
        - Wraps the original add_file_to_upload_table function
        - Provides consistent error handling and logging
        - Returns structured result instead of raising exceptions
        - Non-critical failure - upload can continue even if audit fails
    """
    try:
        # Validate inputs
        if not file_path:
            return FileAuditResult(
                success=False,
                error_message="File path cannot be None or empty",
                error_type="validation_error"
            )

        # Attempt audit logging using original function
        add_file_to_upload_table(db, file_path, status=status, description=description)
        logger.debug(f"File upload audited successfully: {file_path}")
        
        return FileAuditResult(
            success=True,
            error_message=None,
            error_type=None
        )

    except ValueError as e:
        logger.error(f"Validation error during file audit: {e}")
        return FileAuditResult(
            success=False,
            error_message=f"File audit validation failed: {e}",
            error_type="validation_error"
        )
    except Exception as e:
        logger.error(f"Database error during file audit: {e}")
        return FileAuditResult(
            success=False,
            error_message=f"Failed to log file upload: {e}",
            error_type="database_error"
        )


def convert_excel_to_json_with_result(file_path: Path) -> JsonProcessingResult:
    """
    Enhanced wrapper for convert_excel_to_json_if_valid with result type return.

    This function provides a robust, type-safe alternative to convert_excel_to_json_if_valid
    with comprehensive error handling and clear success/failure indicators.

    Args:
        file_path (Path): Path to the uploaded file to convert

    Returns:
        JsonProcessingResult: Rich result object with conversion information

    Examples:
        result = convert_excel_to_json_with_result(file_path)
        if result.success:
            # Conversion successful
            json_path = result.json_path
            sector = result.sector
            logger.info(f"File converted to: {json_path}, sector: {sector}")
        else:
            # Handle conversion error
            if result.error_type == "conversion_failed":
                flash("Please upload an Excel (.xlsx) file")

    Notes:
        - Wraps the original convert_excel_to_json_if_valid function
        - Provides consistent error handling and logging
        - Returns structured result instead of tuple
        - Handles all conversion error scenarios gracefully
    """
    try:
        # Validate input
        if not file_path or not file_path.exists():
            return JsonProcessingResult(
                json_path=None,
                sector=None,
                success=False,
                error_message="File path does not exist or is invalid",
                error_type="file_error"
            )

        # Attempt conversion using original function
        json_path, sector = convert_excel_to_json_if_valid(file_path)
        
        if not json_path:
            return JsonProcessingResult(
                json_path=None,
                sector=None,
                success=False,
                error_message="Unsupported file format. Please upload Excel (.xlsx) file.",
                error_type="conversion_failed"
            )

        logger.debug(f"File converted successfully to: {json_path}, sector: {sector}")
        return JsonProcessingResult(
            json_path=json_path,
            sector=sector,
            success=True,
            error_message=None,
            error_type=None
        )

    except FileNotFoundError as e:
        logger.error(f"File not found during conversion: {e}")
        return JsonProcessingResult(
            json_path=None,
            sector=None,
            success=False,
            error_message=f"File not found: {e}",
            error_type="file_error"
        )
    except PermissionError as e:
        logger.error(f"Permission error during conversion: {e}")
        return JsonProcessingResult(
            json_path=None,
            sector=None,
            success=False,
            error_message="Permission denied while accessing file",
            error_type="file_error"
        )
    except Exception as e:
        logger.error(f"Unexpected error during conversion: {e}")
        return JsonProcessingResult(
            json_path=None,
            sector=None,
            success=False,
            error_message=f"Conversion failed: {e}",
            error_type="unexpected_error"
        )


def save_uploaded_file_enhanced_with_result(upload_dir: str | Path, request_file: FileStorage, 
                                          db: SQLAlchemy, description: str | None = None) -> FileSaveResult:
    """
    Enhanced version of save_uploaded_file_with_result using new Phase 6 utility functions.

    This function demonstrates the improved architecture using enhanced lower-level
    utility functions with proper result types and error handling.

    Args:
        upload_dir (str | Path): Directory to save the file in
        request_file (FileStorage): File uploaded via Flask request
        db (SQLAlchemy): Database instance for logging upload
        description (str | None): Optional description for the upload table entry

    Returns:
        FileSaveResult: Rich result object with success/failure information

    Examples:
        result = save_uploaded_file_enhanced_with_result(upload_dir, request_file, db)
        if result.success:
            # File saved successfully
            file_path = result.file_path
        else:
            # Handle error based on result.error_type
            if result.error_type == "file_error":
                flash(f"File upload failed: {result.error_message}")

    Notes:
        - Uses enhanced Phase 6 utility functions
        - Provides better error handling granularity
        - Continues processing even if audit logging fails (non-critical)
        - Demonstrates the Phase 6 improvement pattern
    """
    logger.debug(f"Enhanced file save called with {request_file.filename}")

    # Step 1: Upload file using enhanced utility function
    upload_result = upload_file_with_result(upload_dir, request_file)
    if not upload_result.success:
        return FileSaveResult(
            file_path=None,
            success=False,
            error_message=upload_result.error_message,
            error_type=upload_result.error_type
        )

    # Step 2: Audit the upload (non-critical - continue even if it fails)
    audit_result = audit_file_upload_with_result(
        db, upload_result.file_path, status="File Added", description=description
    )
    if not audit_result.success:
        # Log audit failure but don't fail the upload
        logger.warning(f"File upload audit failed: {audit_result.error_message}")

    logger.debug(f"Enhanced upload completed successfully: {upload_result.file_path}")
    return FileSaveResult(
        file_path=upload_result.file_path,
        success=True,
        error_message=None,
        error_type=None
    )


def convert_file_to_json_enhanced_with_result(file_path: Path) -> FileConversionResult:
    """
    Enhanced version of convert_file_to_json_with_result using new Phase 6 utility functions.

    This function demonstrates the improved architecture using enhanced lower-level
    utility functions with proper result types and error handling.

    Args:
        file_path (Path): Path to the uploaded file

    Returns:
        FileConversionResult: Rich result object with conversion information

    Examples:
        result = convert_file_to_json_enhanced_with_result(file_path)
        if result.success:
            # Conversion successful
            json_path = result.json_path
            sector = result.sector
            json_data = result.json_data
        else:
            # Handle conversion error
            if result.error_type == "conversion_failed":
                flash("Please upload an Excel (.xlsx) file")

    Notes:
        - Uses enhanced Phase 6 utility functions
        - Provides better error handling granularity
        - Includes import audit generation (non-critical)
        - Demonstrates the Phase 6 improvement pattern
    """
    logger.debug(f"Enhanced file conversion called with {file_path}")

    # Step 1: Convert file using enhanced utility function
    conversion_result = convert_excel_to_json_with_result(file_path)
    if not conversion_result.success:
        return FileConversionResult(
            json_path=None,
            sector=None,
            json_data={},
            success=False,
            error_message=conversion_result.error_message,
            error_type=conversion_result.error_type
        )

    # Step 2: Load JSON data for response
    try:
        json_data, _ = json_load_with_meta(conversion_result.json_path)
    except Exception as e:
        logger.error(f"Error loading converted JSON data: {e}")
        return FileConversionResult(
            json_path=conversion_result.json_path,
            sector=conversion_result.sector,
            json_data={},
            success=False,
            error_message=f"Error loading converted JSON: {e}",
            error_type="conversion_failed"
        )

    # Step 3: Generate import audit for diagnostics (non-critical)
    try:
        parse_result = parse_xl_file(file_path)
        audit = generate_import_audit(file_path, parse_result, xl_schema_map, route="upload_file")
        audit_log_path = LOG_DIR / "import_audit.log"
        audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(audit_log_path, "a", encoding="utf-8") as f:
            f.write(audit + "\n\n")
    except Exception as e:
        # Audit failure is non-critical - log warning but continue
        logger.warning(f"Failed to generate import audit: {e}")

    logger.debug(f"Enhanced conversion completed successfully: {conversion_result.json_path}")
    return FileConversionResult(
        json_path=conversion_result.json_path,
        sector=conversion_result.sector,
        json_data=json_data,
        success=True,
        error_message=None,
        error_type=None
    )


def upload_and_process_file_enhanced(db: SQLAlchemy,
                                    upload_dir: str | Path,
                                    request_file: FileStorage,
                                    base: AutomapBase) -> UploadResult:
    """
    Enhanced version of upload_and_process_file using new Phase 6 utility functions.

    This function demonstrates the improved architecture using enhanced lower-level
    utility functions with proper result types, better error handling, and improved
    consistency throughout the call tree.

    Args:
        db (SQLAlchemy): SQLAlchemy database instance
        upload_dir (str | Path): Directory where the uploaded file should be saved
        request_file (FileStorage): File uploaded via the Flask request
        base (AutomapBase): SQLAlchemy base object from automap reflection

    Returns:
        UploadResult: Rich result object with upload processing information

    Examples:
        result = upload_and_process_file_enhanced(db, upload_dir, request_file, base)
        if result.success:
            # Redirect to incidence update page
            return redirect(url_for('main.incidence_update', id_=result.id_))
        else:
            # Handle specific error types
            if result.error_type == "missing_id":
                return render_template('upload.html', upload_message=result.error_message)
            elif result.error_type == "conversion_failed":
                return render_template('upload.html', upload_message=result.error_message)

    Notes:
        - Uses enhanced Phase 6 utility functions throughout
        - Provides granular error handling at each step
        - Maintains the same functionality as upload_and_process_file
        - Demonstrates the complete Phase 6 improvement pattern
        - Better separation of concerns with result type propagation
    """
    logger.debug(f"Enhanced upload_and_process_file called with {request_file.filename}")

    # Step 1: Save uploaded file using enhanced utility function
    save_result = save_uploaded_file_enhanced_with_result(
        upload_dir, request_file, db, description="Direct upload to database"
    )
    if not save_result.success:
        return UploadResult(
            file_path=Path("unknown"),
            id_=None,
            sector=None,
            success=False,
            error_message=save_result.error_message,
            error_type=save_result.error_type
        )

    # Step 2: Convert file to JSON using enhanced utility function
    conversion_result = convert_file_to_json_enhanced_with_result(save_result.file_path)
    if not conversion_result.success:
        return UploadResult(
            file_path=save_result.file_path,
            id_=None,
            sector=conversion_result.sector,
            success=False,
            error_message=conversion_result.error_message,
            error_type=conversion_result.error_type
        )

    # Step 3: Validate ID from JSON data
    validation_result = validate_id_from_json_with_result(conversion_result.json_data)
    if not validation_result.success:
        return UploadResult(
            file_path=save_result.file_path,
            id_=None,
            sector=conversion_result.sector,
            success=False,
            error_message=validation_result.error_message,
            error_type=validation_result.error_type
        )

    # Step 4: Insert data into database
    insert_result = insert_json_into_database_with_result(conversion_result.json_path, base, db)
    if not insert_result.success:
        return UploadResult(
            file_path=save_result.file_path,
            id_=validation_result.id_,
            sector=conversion_result.sector,
            success=False,
            error_message=insert_result.error_message,
            error_type=insert_result.error_type
        )

    # Success case
    logger.debug(f"Enhanced upload completed successfully: id={insert_result.id_}, sector={conversion_result.sector}")
    return UploadResult(
        file_path=save_result.file_path,
        id_=insert_result.id_,
        sector=conversion_result.sector,
        success=True,
        error_message=None,
        error_type=None
    )


def stage_uploaded_file_for_review_enhanced(db: SQLAlchemy,
                                          upload_dir: str | Path,
                                          request_file: FileStorage,
                                          base: AutomapBase) -> StagingResult:
    """
    Enhanced version of stage_uploaded_file_for_review using new Phase 6 utility functions.

    This function demonstrates the improved architecture using enhanced lower-level
    utility functions with proper result types, better error handling, and improved
    consistency throughout the call tree.

    Args:
        db (SQLAlchemy): Active SQLAlchemy database instance
        upload_dir (str | Path): Target upload folder path
        request_file (FileStorage): Uploaded file from Flask request
        base (AutomapBase): Reflected metadata

    Returns:
        StagingResult: Rich result object with staging information

    Examples:
        result = stage_uploaded_file_for_review_enhanced(db, upload_dir, request_file, base)
        if result.success:
            # Staging successful
            flash(f"File staged successfully: {result.staged_filename}")
        else:
            # Handle specific error
            if result.error_type == "missing_id":
                flash("Please add a valid ID to your spreadsheet")

    Notes:
        - Uses enhanced Phase 6 utility functions throughout
        - Provides granular error handling at each step
        - Maintains the same functionality as stage_uploaded_file_for_review
        - Demonstrates the complete Phase 6 improvement pattern
        - Better separation of concerns with result type propagation
    """
    logger.debug(f"Enhanced stage_uploaded_file_for_review called with {request_file.filename}")

    # Step 1: Save uploaded file using enhanced utility function
    save_result = save_uploaded_file_enhanced_with_result(
        upload_dir, request_file, db, description="Staged only (no DB write)"
    )
    if not save_result.success:
        return StagingResult(
            file_path=Path("unknown"),
            id_=None,
            sector=None,
            json_data={},
            staged_filename=None,
            success=False,
            error_message=save_result.error_message,
            error_type=save_result.error_type
        )

    # Step 2: Convert file to JSON using enhanced utility function
    conversion_result = convert_file_to_json_enhanced_with_result(save_result.file_path)
    if not conversion_result.success:
        return StagingResult(
            file_path=save_result.file_path,
            id_=None,
            sector=None,
            json_data={},
            staged_filename=None,
            success=False,
            error_message=conversion_result.error_message,
            error_type=conversion_result.error_type
        )

    # Step 3: Validate ID from JSON data
    validation_result = validate_id_from_json_with_result(conversion_result.json_data)
    if not validation_result.success:
        return StagingResult(
            file_path=save_result.file_path,
            id_=None,
            sector=conversion_result.sector,
            json_data=conversion_result.json_data,
            staged_filename=None,
            success=False,
            error_message=validation_result.error_message,
            error_type=validation_result.error_type
        )

    # Step 4: Create staged file
    staged_result = create_staged_file_with_result(
        validation_result.id_, conversion_result.json_data, db, base, upload_dir
    )
    if not staged_result.success:
        return StagingResult(
            file_path=save_result.file_path,
            id_=validation_result.id_,
            sector=conversion_result.sector,
            json_data=conversion_result.json_data,
            staged_filename=None,
            success=False,
            error_message=staged_result.error_message,
            error_type=staged_result.error_type
        )

    # Success case
    logger.debug(f"Enhanced staging completed successfully: {staged_result.staged_filename}")
    return StagingResult(
        file_path=save_result.file_path,
        id_=validation_result.id_,
        sector=conversion_result.sector,
        json_data=conversion_result.json_data,
        staged_filename=staged_result.staged_filename,
        success=True,
        error_message=None,
        error_type=None
    )
