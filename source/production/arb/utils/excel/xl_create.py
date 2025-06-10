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

import shutil
import zipfile
from functools import partial
from pathlib import Path

import jinja2

from arb.__get_logger import get_logger
from arb.utils.constants import PLEASE_SELECT
from arb.utils.excel.xl_file_structure import (PROCESSED_VERSIONS, PROJECT_ROOT)
from arb.utils.excel.xl_misc import xl_address_sort
from arb.utils.file_io import ensure_dir_exists, ensure_parent_dirs
from arb.utils.json import (
  compare_json_files,
  json_load,
  json_load_with_meta,
  json_save_with_meta,
)
from arb.utils.misc import ensure_key_value_pair

logger, pp_log = get_logger()

# default file (not schema) versions for landfill and oil and gas spreadsheet names
LANDFILL_VERSION = "v070"
OIL_AND_GAS_VERSION = "v070"
ENERGY_VERSION = "v003"


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

  Example:
    >>> sorted_schema = sort_xl_schema(schema, sort_by="label_address")
  """
  logger.debug("sort_xl_schema() called")

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
    logger.debug("Sorting schema by variable_name")
    sorted_items = dict(sorted(xl_schema.items(), key=lambda item: item[0]))
  elif sort_by == "label_address":
    logger.debug("Sorting schema by label_address")
    get_xl_row = partial(
      xl_address_sort, address_location="value", sort_by="row", sub_keys="label_address"
    )
    sorted_items = dict(sorted(xl_schema.items(), key=get_xl_row))
  else:
    raise ValueError("sort_by must be 'variable_name' or 'label_address'")

  return sorted_items


def schema_to_json_file(data: dict, schema_version: str, file_name: str = None) -> None:
  """
  Save an Excel schema to a JSON file with metadata and validate the round-trip.

  Args:
    data (dict): The Excel schema to be serialized and written to disk.
    schema_version (str): Schema version identifier to include in metadata.
    file_name (str, optional): Output file path. Default to "xl_schemas/{schema_version}.json".

  Returns:
    None

  Example:
    >>> schema_to_json_file(my_schema, schema_version="v01_00")

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
    logger.debug("SUCCESS: JSON serialization round-trip matches original.")
  else:
    logger.warning("FAILURE: Mismatch in JSON serialization round-trip.")


def update_vba_schema(
    schema_version: str,
    file_name_in: Path = None,
    file_name_out: Path = None,
    file_name_default_value_types: Path = None
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

  Example:
    >>> updated = update_vba_schema("landfill_v01_00")

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

  This function applies schema upgrades to a predefined list of versions,
  typically for supported sectors like landfill and oil and gas.

  Returns:
    None

  Notes:
    - Automatically processes "landfill_v01_00" and "oil_and_gas_v01_00".
    - Calls `update_vba_schema()` for each version.
    - Output schemas are written to the processed_versions/xl_schemas directory.
  """
  logger.debug("update_vba_schemas() called")

  for schema_version in ["landfill_v01_00", "oil_and_gas_v01_00"]:
    update_vba_schema(schema_version)


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

  Example:
    >>> defaults, meta = schema_to_default_dict(Path("xl_schemas/landfill_v01_00.json"))

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


def schema_to_default_json(file_name_in: Path, file_name_out: Path = None) -> tuple[dict, dict]:
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

  Example:
    >>> schema_to_default_json(Path("xl_schemas/landfill_v01_00.json"))

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

  Example:
    >>> update_xlsx(Path("template.xlsx"), Path("output.xlsx"), {"site_name": "Landfill A"})

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

  Example:
    >>> test_update_xlsx_payloads_01()

  Notes:
    - Writes populated Excel files to the `xl_workbooks` directory.
    - Uses both file-based and inline payloads.
    - Intended for development and diagnostic use, not production.
  """
  logger.debug("test_update_xlsx_payloads_01() called")

  # Landfill test with two payloads from the file
  update_xlsx_payloads(
    PROCESSED_VERSIONS / f"xl_workbooks/landfill_operator_feedback_{LANDFILL_VERSION}_jinja_.xlsx",
    PROCESSED_VERSIONS / f"xl_workbooks/landfill_operator_feedback_{LANDFILL_VERSION}_populated_01.xlsx",
    [
      PROCESSED_VERSIONS / "xl_payloads/landfill_v01_00_defaults.json",
      PROCESSED_VERSIONS / "xl_payloads/landfill_v01_00_payload_01.json",
    ]
  )

  # Landfill test with one file payload and one inline dict
  update_xlsx_payloads(
    PROCESSED_VERSIONS / f"xl_workbooks/landfill_operator_feedback_{LANDFILL_VERSION}_jinja_.xlsx",
    PROCESSED_VERSIONS / f"xl_workbooks/landfill_operator_feedback_{LANDFILL_VERSION}_populated_02.xlsx",
    [
      PROCESSED_VERSIONS / "xl_payloads/landfill_v01_00_payload_01.json",
      {"id_incidence": "123456"},
    ]
  )

  # Oil and gas test
  update_xlsx_payloads(
    PROCESSED_VERSIONS / f"xl_workbooks/oil_and_gas_operator_feedback_{OIL_AND_GAS_VERSION}_jinja_.xlsx",
    PROCESSED_VERSIONS / f"xl_workbooks/oil_and_gas_operator_feedback_{OIL_AND_GAS_VERSION}_populated_01.xlsx",
    [
      PROCESSED_VERSIONS / "xl_payloads/oil_and_gas_v01_00_defaults.json",
      PROCESSED_VERSIONS / "xl_payloads/oil_and_gas_v01_00_payload_01.json",
    ]
  )

  # Energy test with inline payload
  update_xlsx_payloads(
    PROCESSED_VERSIONS / f"xl_workbooks/energy_operator_feedback_{ENERGY_VERSION}_jinja_.xlsx",
    PROCESSED_VERSIONS / f"xl_workbooks/energy_operator_feedback_{ENERGY_VERSION}_populated_01.xlsx",
    [
      PROCESSED_VERSIONS / "xl_payloads/energy_v00_01_defaults.json",
      {"id_incidence": "654321"},
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

  Example:
    >>> prep_xl_templates()

  Notes:
    - File paths are derived from structured configs for each sector.
    - Overwrites files in the output directory if they already exist.
    - Output directories are created if they don't exist.
  """
  logger.debug("prep_xl_templates() called for landfill, oil and gas, and energy schemas")

  file_specs = []
  input_dir = PROJECT_ROOT / "feedback_forms/current_versions"
  output_dir = PROJECT_ROOT / "feedback_forms/processed_versions"

  ensure_dir_exists(output_dir / "xl_schemas")
  ensure_dir_exists(output_dir / "xl_workbooks")
  ensure_dir_exists(output_dir / "xl_payloads")

  template_configs = [
    ("landfill_v01_00", "landfill_operator_feedback", LANDFILL_VERSION),
    ("oil_and_gas_v01_00", "oil_and_gas_operator_feedback", OIL_AND_GAS_VERSION),
    ("energy_v00_01", "energy_operator_feedback", ENERGY_VERSION),
  ]

  for schema_version, prefix, version in template_configs:
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

    file_map = [(spec["input_schema_vba_path"], spec["output_schema_vba_path"]),
                (spec["input_xl_path"], spec["output_xl_path"]),
                (spec["input_xl_jinja_path"], spec["output_xl_jinja_path"]), ]

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

  Example:
    >>> types = create_default_types_schema(diagnostics=True)

  Notes:
    - Output is saved to 'xl_schemas/default_value_types_v01_00.json'.
    - A backup is compared against the newly generated file if present.
    - Field names and types are sourced from `xl_hardcoded.default_value_types_v01_00`.
  """
  from arb.utils.excel.xl_hardcoded import default_value_types_v01_00

  logger.debug("create_default_types_schema() called")

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


def create_payload(payload: dict, file_name: Path, schema_version: str, metadata: dict = None) -> None:
  """
  Create a JSON payload file with embedded metadata describing the schema version.

  Args:
    payload (dict): Dictionary of values to serialize to JSON.
    file_name (Path): Path to output the payload JSON file.
    schema_version (str): Identifier for the schema the payload conforms to.
    metadata (dict, optional): Additional metadata to embed. If None, a new dict is created.

  Returns:
    None

  Example:
    >>> create_payload({"id_case": "A42"}, Path("payload.json"), "v01_00")

  Notes:
    - Adds 'schema_version' and a default payload description to metadata.
    - Uses `json_save_with_meta()` to embed metadata into the JSON file.
    - Logs all key actions and file paths for diagnostics.
  """

  logger.debug("create_payload() called")

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

  Example:
    >>> create_payloads()

  Notes:
    - Each payload is saved to `xl_payloads/{schema_version}_payload_01.json`.
    - If a backup file exists, the new payload is compared against it for consistency.
    - The energy payload reuses the oil and gas example data for demonstration purposes.
    - Uses `create_payload()` to handle serialization and metadata embedding.
  """

  logger.debug("create_payloads() called")

  from arb.utils.excel.xl_hardcoded import landfill_payload_01, oil_and_gas_payload_01

  test_sets = [
    ("landfill_v01_00", landfill_payload_01),
    ("oil_and_gas_v01_00", oil_and_gas_payload_01),
    ("energy_v00_01", oil_and_gas_payload_01),  # Reuse oil and gas payload
  ]

  for schema_version, payload in test_sets:
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

  Example:
    >>> create_schemas_and_payloads()

  Notes:
    - Create all required directories under `processed_versions`.
    - Intended for one-time use during development or deployment setup.
    - Logs each operation and file path for debugging.
  """

  logger.debug("create_schemas_and_payloads() called")

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

  Example:
    >>> run_diagnostics()

  Notes:
    - Logs each step of the process to the application logger.
    - Catches and logs any exceptions that occur during testing.
    - Intended for developers to verify schema and workbook generation end-to-end.
  """
  logger.info("Running diagnostics...")

  try:
    logger.info("Step 1: Creating default type schema")
    create_default_types_schema(diagnostics=True)

    logger.info("Step 2: Creating and verifying schema files and payloads")
    prep_xl_templates()
    create_payloads()

    logger.info("Step 3: Performing test Excel generation")
    test_update_xlsx_payloads_01()

    logger.info("Diagnostics complete. Check output directory and logs for details.")

  except Exception as e:
    logger.exception(f"Diagnostics failed: {e}")


if __name__ == "__main__":
  create_schemas_and_payloads()
  # Uncomment below line to run additional test harness
  # run_diagnostics()
