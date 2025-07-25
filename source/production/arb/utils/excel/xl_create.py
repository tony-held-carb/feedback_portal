"""
Module to prepare Excel templates and generate new Excel files using Jinja-rendered payloads.

This module performs schema-based templating of Excel spreadsheets for feedback forms,
injects metadata, applies default values, and renders Excel files based on structured
JSON payloads.

Typical Workflow:
  1. Use a spreadsheet with named ranges and Jinja placeholders.
  2. Generate an initial JSON schema using a VBA macro.
  3. Refine the schema by injecting typing information.
  4. Generate default and test payloads.
  5. Populate Excel files using these payloads.

Run this file directly to create all schema and payload artifacts for landfill,
oil and gas, and energy templates.
"""

import logging
import shutil
import zipfile
from functools import partial
from pathlib import Path

import jinja2

from arb.utils.constants import PLEASE_SELECT
from arb.utils.excel.xl_file_structure import (PROCESSED_VERSIONS, PROJECT_ROOT)
from arb.utils.excel.xl_hardcoded import EXCEL_TEMPLATES
from arb.utils.excel.xl_misc import xl_address_sort
from arb.utils.file_io import ensure_dir_exists, ensure_parent_dirs
from arb.utils.json import (
  compare_json_files,
  json_load,
  json_load_with_meta,
  json_save_with_meta,
)
from arb.utils.misc import ensure_key_value_pair

logger = logging.getLogger(__name__)


def sort_xl_schema(xl_schema: dict,
                   sort_by: str = "variable_name") -> dict:
  """
  Sort an Excel schema and its sub-schema dictionaries for easier comparison.

  This function modifies sub-schemas in place and returns a new dictionary with the
  top-level keys sorted according to the selected strategy.

  Sub-schemas are reordered so that keys appear in the order:
  "label", "label_address", "value_address", "value_type", then others.

  Args:
    xl_schema (dict): Dictionary where keys are variable names and values are sub-schema dicts.
    sort_by (str): Sorting strategy:
      - "variable_name": Sort top-level keys alphabetically (default).
      - "label_address": Sort based on Excel row order of each sub-schema's 'label_address'.

  Returns:
    dict: A new dictionary with reordered sub-schemas and sorted top-level keys.

  Raises:
    ValueError: If an unrecognized sorting strategy is provided.

  Examples:
    Input : schema, sort_by="label_address"
    Output: New dictionary with sorted keys and reordered sub-schemas
  """
  logger.debug(f"sort_xl_schema() called")

  # Reorder each sub-schema dict
  for variable_name, sub_schema in xl_schema.items():
    reordered = {}
    for key in ("label", "label_address", "value_address", "value_type"):
      if key in sub_schema:
        reordered[key] = sub_schema.pop(key)
    reordered.update(sub_schema)
    xl_schema[variable_name] = reordered

  # Sort top-level dictionary
  if sort_by == "variable_name":
    logger.debug(f"Sorting schema by variable_name")
    sorted_items = dict(sorted(xl_schema.items(), key=lambda item: item[0]))
  elif sort_by == "label_address":
    logger.debug(f"Sorting schema by label_address")
    get_xl_row = partial(
      xl_address_sort, address_location="value", sort_by="row", sub_keys="label_address"
    )
    sorted_items = dict(sorted(xl_schema.items(), key=get_xl_row))
  else:
    raise ValueError("sort_by must be 'variable_name' or 'label_address'")

  return sorted_items


def schema_to_json_file(data: dict, schema_version: str, file_name: str | None = None) -> None:
  """
  Save an Excel schema to a JSON file with metadata and validate the round-trip.

  Args:
    data (dict): The Excel schema to be serialized and written to disk.
    schema_version (str): Schema version identifier to include in metadata.
    file_name (str, optional): Output file path. Default to "xl_schemas/{schema_version}.json".

  Returns:
    None

  Examples:
    Input : my_schema, schema_version="v01_00"
    Output: JSON file written to "xl_schemas/v01_00.json" (default path)

  Notes:
    - If `file_name` is not provided, the output will be saved to
      "xl_schemas/{schema_version}.json".
    - Metadata will include the schema version.
    - Performs a round-trip serialization test to verify that the saved data
      and metadata match the originals.
  """

  logger.debug(f"schema_to_json_file() called with {schema_version=}, {file_name=}")

  if file_name is None:
    file_name = f"xl_schemas/{schema_version}.json"

  ensure_parent_dirs(file_name)
  metadata = {'schema_version': schema_version}

  logger.debug(f"Saving schema to: {file_name} with metadata: {metadata}")
  json_save_with_meta(file_name, data=data, metadata=metadata, json_options=None)

  # Verify round-trip serialization
  read_data, read_metadata = json_load_with_meta(file_name)
  if read_data == data and read_metadata == metadata:
    logger.debug(f"SUCCESS: JSON serialization round-trip matches original.")
  else:
    logger.warning(f"FAILURE: Mismatch in JSON serialization round-trip.")


def update_vba_schema(
    schema_version: str,
    file_name_in: Path | None = None,
    file_name_out: Path | None = None,
    file_name_default_value_types: Path | None = None
) -> dict:
  """
  Update a VBA-generated Excel schema with value_type info and re-sort it.

  Args:
    schema_version (str): Identifier for the schema version.
    file_name_in (Path, optional): Path to the raw VBA schema JSON file.
      Default to "processed_versions/xl_schemas/{schema_version}_vba.json".
    file_name_out (Path, optional): Path to output the upgraded schema JSON.
      Default to "processed_versions/xl_schemas/{schema_version}.json".
    file_name_default_value_types (Path, optional): Path to JSON file defining
      default value types. Defaults to "processed_versions/xl_schemas/default_value_types_v01_00.json".

  Returns:
    dict: The updated and sorted schema dictionary.

  Examples:
    Input : "landfill_v01_00"
    Output: Sorted schema dictionary with value types injected

  Notes:
    - This function ensures that all schema entries include a 'value_type'.
    - Applies `sort_xl_schema()` with sort_by="label_address".
    - Use `schema_to_json_file()` to write the result to disk.
  """

  logger.debug(f"update_vba_schema() called with {schema_version=}, {file_name_in=}, "
               f"{file_name_out=}, {file_name_default_value_types=}")

  if file_name_in is None:
    file_name_in = PROCESSED_VERSIONS / "xl_schemas" / f"{schema_version}_vba.json"
  if file_name_out is None:
    file_name_out = PROCESSED_VERSIONS / "xl_schemas" / f"{schema_version}.json"
  if file_name_default_value_types is None:
    file_name_default_value_types = PROCESSED_VERSIONS / "xl_schemas/default_value_types_v01_00.json"

  ensure_parent_dirs(file_name_in)
  ensure_parent_dirs(file_name_out)
  ensure_parent_dirs(file_name_default_value_types)

  default_value_types, _ = json_load_with_meta(file_name_default_value_types)
  schema = json_load(file_name_in, json_options=None)

  ensure_key_value_pair(schema, default_value_types, "value_type")
  schema = sort_xl_schema(schema, sort_by="label_address")

  schema_to_json_file(schema, schema_version, file_name=file_name_out)
  return schema


def update_vba_schemas() -> None:
  """
  Batch update of known VBA-generated schemas using `update_vba_schema()`.

  This function applies schema upgrades to all templates defined in TEMPLATES.

  Returns:
    None

  Notes:
    - Calls `update_vba_schema()` for each template in TEMPLATES.
    - Output schemas are written to the processed_versions/xl_schemas directory.
  """
  logger.debug(f"update_vba_schemas() called")

  for template in EXCEL_TEMPLATES:
    update_vba_schema(template["schema_version"])


def schema_to_default_dict(schema_file_name: Path) -> tuple[dict, dict]:
  """
  Generate default values and metadata from an Excel schema JSON file.

  Args:
    schema_file_name (Path): Path to the schema JSON file.

  Returns:
    tuple[dict, dict]:
      - defaults: Dictionary mapping variable names to default values.
          * Drop-downs get "Please Select".
          * All other fields get an empty string.
      - metadata: Metadata dictionary from the schema file.

  Examples:
    Input : Path("xl_schemas/landfill_v01_00.json")
    Output: (defaults dictionary, metadata dictionary)

  Notes:
    - The schema must include an "is_drop_down" flag for correct default generation.
    - Useful for pre-populating forms with valid placeholder values.
  """
  logger.debug(f"schema_to_default_dict() called for {schema_file_name=}")

  data, metadata = json_load_with_meta(schema_file_name)
  logger.debug(f"{metadata=}")

  defaults = {
    variable: PLEASE_SELECT if sub_schema.get("is_drop_down") else ""
    for variable, sub_schema in data.items()
  }

  return defaults, metadata


def schema_to_default_json(file_name_in: Path, file_name_out: Path | None = None) -> tuple[dict, dict]:
  """
  Save default values extracted from a schema into a JSON file with metadata.

  Args:
    file_name_in (Path): Input path to the schema JSON file.
    file_name_out (Path, optional): Output path for the default JSON.
      If None, defaults to 'xl_payloads/{schema_version}_defaults.json'.

  Returns:
    tuple[dict, dict]:
      - defaults: Dictionary of default values derived from the schema.
      - metadata: Metadata dictionary included in the output JSON.

  Examples:
    Input : Path("xl_schemas/landfill_v01_00.json")
    Output: Tuple of (defaults dict, metadata dict), written to output path

  Notes:
    - Drop-down fields default to "Please Select".
    - Other fields default to an empty string.
    - Adds a note to metadata explaining default value behavior.
    - Ensures output directory exists before writing.
  """
  logger.debug(f"schema_to_default_json() called for {file_name_in=}")

  defaults, metadata = schema_to_default_dict(file_name_in)
  metadata['notes'] = (
    "Default values are empty strings unless the field is a drop-down cell. "
    "For drop-down cells, the default is 'Please Select'."
  )

  if file_name_out is None:
    file_name_out = f"xl_payloads/{metadata['schema_version']}_defaults.json"

  ensure_parent_dirs(file_name_out)

  json_save_with_meta(file_name_out, data=defaults, metadata=metadata, json_options=None)
  return defaults, metadata


def update_xlsx(file_in: Path, file_out: Path, jinja_dict: dict) -> None:
  """
  Render a Jinja-templated Excel (.xlsx) file by replacing placeholders with dictionary values.

  Args:
    file_in (Path): Path to the input Excel file containing Jinja placeholders.
    file_out (Path): Path where the rendered Excel file will be saved.
    jinja_dict (dict): Dictionary mapping Jinja template variables to replacement values.

  Returns:
    None

  Examples:
    Input : template.xlsx, output.xlsx, {"site_name": "Landfill A"}
    Output: output.xlsx with rendered values

  Notes:
    - Only modifies 'xl/sharedStrings.xml' within the XLSX zip archive.
    - All other file contents are passed through unchanged.
    - Useful for populating pre-tagged Excel templates with form data.
  """

  logger.debug(f"Rendering Excel from {file_in} to {file_out} using {jinja_dict}")

  with zipfile.ZipFile(file_in, 'r') as xlsx, zipfile.ZipFile(file_out, 'w') as new_xlsx:
    for filename in xlsx.namelist():
      with xlsx.open(filename) as file:
        contents = file.read()
        if filename == 'xl/sharedStrings.xml':
          contents = jinja2.Template(contents.decode('utf-8')).render(jinja_dict).encode('utf-8')
        new_xlsx.writestr(filename, contents)


def update_xlsx_payloads(file_in: Path, file_out: Path, payloads: list | tuple) -> None:
  """
  Apply multiple payloads to a Jinja-templated Excel file and render the result.

  Args:
    file_in (Path): Path to the input Excel file containing Jinja placeholders.
    file_out (Path): Path where the populated Excel file will be written.
    payloads (list | tuple): Sequence of dictionaries or JSON file paths.
      - Payloads are merged in order, with later values overriding earlier ones.

  Returns:
    None

  Notes:
    - Each payload may be a dictionary or a Path to a JSON file with metadata.
    - Designed to support tiered rendering: default payload + override.
    - Uses `json_load_with_meta()` for file payloads.
    - Passes final merged dictionary to `update_xlsx()`.
  """

  logger.debug(f"update_xlsx_payloads() called with: {file_in=}, {file_out=}, {payloads=}")

  new_dict = {}
  for payload in payloads:
    if isinstance(payload, dict):
      data = payload
    else:
      data, _ = json_load_with_meta(payload)
    new_dict.update(data)

  update_xlsx(file_in, file_out, new_dict)


def test_update_xlsx_payloads_01() -> None:
  """
  Run test cases that populate Jinja-templated Excel files with known payloads.

  This test routine helps validate that Excel generation is functioning correctly
  for all supported sectors (landfill, oil and gas, energy).

  Returns:
    None

  Examples:
    Input : None
    Output: Diagnostic Excel files created in xl_workbooks/

  Notes:
    - Writes populated Excel files to the `xl_workbooks` directory.
    - Uses both file-based and inline payloads.
    - Intended for development and diagnostic use, not production.
  """
  logger.debug(f"test_update_xlsx_payloads_01() called")

  for template in EXCEL_TEMPLATES:
    schema_version = template["schema_version"]
    prefix = template["prefix"]
    version = template["version"]
    # Test with two payloads from file (defaults + payload_01)
    update_xlsx_payloads(
      PROCESSED_VERSIONS / f"xl_workbooks/{prefix}_{version}_jinja_.xlsx",
      PROCESSED_VERSIONS / f"xl_workbooks/{prefix}_{version}_populated_01.xlsx",
      [
        PROCESSED_VERSIONS / f"xl_payloads/{schema_version}_defaults.json",
        PROCESSED_VERSIONS / f"xl_payloads/{schema_version}_payload_01.json",
      ]
    )
    # Test with one file payload and one inline dict
    update_xlsx_payloads(
      PROCESSED_VERSIONS / f"xl_workbooks/{prefix}_{version}_jinja_.xlsx",
      PROCESSED_VERSIONS / f"xl_workbooks/{prefix}_{version}_populated_02.xlsx",
      [
        PROCESSED_VERSIONS / f"xl_payloads/{schema_version}_payload_01.json",
        {"id_incidence": "123456"},
      ]
    )


def prep_xl_templates() -> None:
  """
  Prepare processed Excel templates and payloads for landfill, oil and gas, and energy sectors.

  This function:
    - Copies original schema and Excel files to the processed directory.
    - Converts VBA-generated schema files by injecting type info.
    - Writes upgraded schema and default payload JSON files.
    - Produces Jinja-compatible Excel workbook versions for templating.

  Returns:
    None

  Notes:
    - File paths are derived from structured configs for each sector.
    - Overwrites files in the output directory if they already exist.
    - Output directories are created if they don't exist.
  """
  logger.debug(f"prep_xl_templates() called for all templates in TEMPLATES")

  file_specs = []
  input_dir = PROJECT_ROOT / "feedback_forms/current_versions"
  output_dir = PROJECT_ROOT / "feedback_forms/processed_versions"

  ensure_dir_exists(output_dir / "xl_schemas")
  ensure_dir_exists(output_dir / "xl_workbooks")
  ensure_dir_exists(output_dir / "xl_payloads")

  for template in EXCEL_TEMPLATES:
    schema_version = template["schema_version"]
    prefix = template["prefix"]
    version = template["version"]
    spec = {
      "schema_version": schema_version,
      "input_schema_vba_path": input_dir / f"{schema_version}_vba.json",
      "input_xl_path": input_dir / f"{prefix}_{version}.xlsx",
      "input_xl_jinja_path": input_dir / f"{prefix}_{version}_jinja_.xlsx",
      "output_schema_vba_path": output_dir / "xl_schemas" / f"{schema_version}_vba.json",
      "output_schema_path": output_dir / "xl_schemas" / f"{schema_version}.json",
      "output_xl_path": output_dir / "xl_workbooks" / f"{prefix}_{version}.xlsx",
      "output_xl_jinja_path": output_dir / "xl_workbooks" / f"{prefix}_{version}_jinja_.xlsx",
      "output_payload_path": output_dir / "xl_payloads" / f"{schema_version}_defaults.json",
    }
    file_specs.append(spec)

  for spec in file_specs:
    logger.debug(f"Processing schema_version {spec['schema_version']}")

    file_map = [
      (spec["input_schema_vba_path"], spec["output_schema_vba_path"]),
      (spec["input_xl_path"], spec["output_xl_path"]),
      (spec["input_xl_jinja_path"], spec["output_xl_jinja_path"]),
    ]

    for file_old, file_new in file_map:
      logger.debug(f"Copying file from: {file_old} to: {file_new}")
      shutil.copy(file_old, file_new)

    update_vba_schema(spec["schema_version"],
                      file_name_in=spec["output_schema_vba_path"],
                      file_name_out=spec["output_schema_path"])

    schema_to_default_json(file_name_in=spec["output_schema_path"],
                           file_name_out=spec["output_payload_path"])


def create_default_types_schema(diagnostics: bool = False) -> dict:
  """
  Create a JSON file that maps variable names to their default Python value types.

  Args:
    diagnostics (bool): If True, logs each variable name and its type to the debug logger.

  Returns:
    dict: Dictionary mapping variable names to Python types (e.g., str, int, datetime).

  Examples:
    Input : diagnostics=True
    Output: Dictionary of variable names → value types, logged if diagnostics enabled

  Notes:
    - Output is saved to 'xl_schemas/default_value_types_v01_00.json'.
    - A backup is compared against the newly generated file if present.
    - Field names and types are sourced from `xl_hardcoded.default_value_types_v01_00`.
  """
  from arb.utils.excel.xl_hardcoded import default_value_types_v01_00

  logger.debug(f"create_default_types_schema() called")

  file_name = PROCESSED_VERSIONS / "xl_schemas/default_value_types_v01_00.json"
  file_backup = PROCESSED_VERSIONS / "xl_schemas/default_value_types_v01_00_backup.json"

  field_types = dict(sorted(default_value_types_v01_00.items()))

  if diagnostics:
    for name, typ in field_types.items():
      logger.debug(f"'{name}': {typ.__name__},")

  metadata = {"schema_version": "default_value_types_v01_00"}
  json_save_with_meta(file_name, field_types, metadata=metadata)

  if file_name.is_file() and file_backup.is_file():
    compare_json_files(file_name, file_backup)

  return field_types


def create_payload(payload: dict, file_name: Path, schema_version: str, metadata: dict | None = None) -> None:
  """
  Create a JSON payload file with embedded metadata describing the schema version.

  Args:
    payload (dict): Dictionary of values to serialize to JSON.
    file_name (Path): Path to output the payload JSON file.
    schema_version (str): Identifier for the schema the payload conforms to.
    metadata (dict, optional): Additional metadata to embed. If None, a new dict is created.

  Returns:
    None

  Examples:
    Input : {"id_case": "A42"}, Path("payload.json"), "v01_00"
    Output: JSON file with metadata saved to payload.json

  Notes:
    - Adds 'schema_version' and a default payload description to metadata.
    - Uses `json_save_with_meta()` to embed metadata into the JSON file.
    - Logs all key actions and file paths for diagnostics.
  """

  logger.debug(f"create_payload() called")

  if metadata is None:
    metadata = {}

  metadata["schema_version"] = schema_version
  metadata["payload description"] = "Test of Excel jinja templating system"

  logger.debug(f"Writing payload to {file_name} with metadata: {metadata}")
  json_save_with_meta(file_name, data=payload, metadata=metadata)


def create_payloads() -> None:
  """
  Generate and save example payload files for each supported sector (landfill, oil and gas, energy).

  Returns:
    None

  Examples:
    Input : None
    Output: Sector payloads written to xl_payloads/*.json

  Notes:
    - Each payload is saved to `xl_payloads/{schema_version}_payload_01.json`.
    - If a backup file exists, the new payload is compared against it for consistency.
    - Uses `create_payload()` to handle serialization and metadata embedding.
  """

  logger.debug(f"create_payloads() called")

  import arb.utils.excel.xl_hardcoded as xl_hardcoded

  for template in EXCEL_TEMPLATES:
    schema_version = template["schema_version"]
    payload_name = template["payload_name"]
    # Dynamically get the payload object from xl_hardcoded
    payload = getattr(xl_hardcoded, payload_name)
    file_name = PROCESSED_VERSIONS / f"xl_payloads/{schema_version}_payload_01.json"
    file_backup = PROCESSED_VERSIONS / f"xl_payloads/{schema_version}_payload_01_backup.json"

    create_payload(payload, file_name, schema_version)

    if file_name.is_file() and file_backup.is_file():
      compare_json_files(file_name, file_backup)


def create_schemas_and_payloads() -> None:
  """
  Generate all schema, payload, and Excel artifacts for the feedback system.

  This orchestration function performs the full pipeline:
    - Creates the default value types schema.
    - Processes all sector-specific schema files (landfill, oil and gas, energy).
    - Writes default payloads for each schema.
    - Generates test payloads and renders Excel templates.

  Returns:
    None

  Examples:
    Input : None
    Output: All schema/payload/template artifacts generated under processed_versions/

  Notes:
    - Create all required directories under `processed_versions`.
    - Intended for one-time use during development or deployment setup.
    - Logs each operation and file path for debugging.
  """

  logger.debug(f"create_schemas_and_payloads() called")

  ensure_dir_exists(PROCESSED_VERSIONS / "xl_schemas")
  ensure_dir_exists(PROCESSED_VERSIONS / "xl_workbooks")
  ensure_dir_exists(PROCESSED_VERSIONS / "xl_payloads")

  create_default_types_schema(diagnostics=True)
  prep_xl_templates()
  create_payloads()
  test_update_xlsx_payloads_01()


def run_diagnostics() -> None:
  """
  Execute a full suite of diagnostic routines to verify Excel templating functionality.

  This includes:
    - Creating default value types schema.
    - Generating upgraded schema files and default payloads.
    - Running test payload injection for Jinja-enabled Excel files.

  Returns:
    None

  Notes:
    - Logs each step of the process to the application logger.
    - Catches and logs any exceptions that occur during testing.
    - Intended for developers to verify schema and workbook generation end-to-end.
  """
  logger.info(f"Running diagnostics...")

  try:
    logger.info(f"Step 1: Creating default type schema")
    create_default_types_schema(diagnostics=True)

    logger.info(f"Step 2: Creating and verifying schema files and payloads")
    prep_xl_templates()
    create_payloads()

    logger.info(f"Step 3: Performing test Excel generation")
    test_update_xlsx_payloads_01()

    logger.info(f"Diagnostics complete. Check output directory and logs for details.")

  except Exception as e:
    logger.exception(f"Diagnostics failed: {e}")


if __name__ == "__main__":
  from arb.logging.arb_logging import setup_standalone_logging

  setup_standalone_logging("xl_create")
  create_schemas_and_payloads()
  # Uncomment below line to run additional test harness
  # run_diagnostics()
