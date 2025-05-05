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

import arb.__get_logger as get_logger
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

logger, pp_log = get_logger.get_logger(__name__, __file__)

# default file (not schema) versions for landfill and oil and gas spreadsheet names
LANDFILL_VERSION = "v070"
OIL_AND_GAS_VERSION = "v070"
ENERGY_VERSION = "v002"


def sort_xl_schema(xl_schema: dict, sort_by: str = "variable_name") -> dict:
  """
  Sort a JSON Excel schema in-place, reordering sub-schema keys and sorting top-level keys.

  Args:
      xl_schema (dict): Schema with variable names as keys and sub-schema dicts as values.
      sort_by (str, optional): Determines sorting strategy: 'variable_name' (default)
                               sorts alphabetically by variable name; 'label_address'
                               sorts by row order of the label address.

  Returns:
      dict: Sorted schema dictionary.

  Raises:
      ValueError: If sort_by is not recognized.

  Example:
      >>> sorted_schema = sort_xl_schema(schema, sort_by='label_address')
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
  Save an Excel schema to a JSON file with metadata.

  Args:
      data (dict): The schema to serialize.
      schema_version (str): Version identifier for the schema.
      file_name (str, optional): Path to output JSON file. Defaults to "xl_schemas/{schema_version}.json".

  Example:
      >>> schema_to_json_file(my_schema, schema_version="v01_00")
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
  Update schema generated from VBA with value_type info and re-sort.

  Args:
      schema_version (str): Identifier for the schema version.
      file_name_in (Path, optional): Path to raw VBA-generated schema JSON.
      file_name_out (Path, optional): Path to output updated schema JSON.
      file_name_default_value_types (Path, optional): Path to JSON containing default value types.

  Returns:
      dict: The updated and sorted schema.

  Example:
      >>> updated = update_vba_schema("landfill_v01_00")
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

  Example:
      >>> update_vba_schemas()
  """
  logger.debug("update_vba_schemas() called")

  for schema_version in ["landfill_v01_00", "oil_and_gas_v01_00"]:
    update_vba_schema(schema_version)


def schema_to_default_dict(schema_file_name: Path) -> tuple[dict, dict]:
  """
  Generate default values from a schema. Dropdowns default to "Please Select", others to "".

  Args:
      schema_file_name (Path): Path to the schema JSON file.

  Returns:
      tuple:
          - defaults (dict): Mapping of HTML variable names to default values.
          - metadata (dict): Metadata from the schema file.

  Example:
      >>> defaults, meta = schema_to_default_dict(Path("xl_schemas/landfill_v01_00.json"))
  """
  logger.debug(f"schema_to_default_dict() called for {schema_file_name=}")

  data, metadata = json_load_with_meta(schema_file_name)
  logger.debug(f"{metadata=}")

  defaults = {
    variable: "Please Select" if sub_schema.get("is_drop_down") else ""
    for variable, sub_schema in data.items()
  }

  return defaults, metadata


def schema_to_default_json(file_name_in: Path, file_name_out: Path = None) -> tuple[dict, dict]:
  """
  Save default values extracted from a schema into a separate JSON file.

  Args:
      file_name_in (Path): Input schema JSON path.
      file_name_out (Path, optional): Output JSON path. Defaults to 'xl_payloads/{schema_version}_defaults.json'.

  Returns:
      tuple:
          - defaults (dict): Generated default values.
          - metadata (dict): Metadata used for output JSON.

  Example:
      >>> schema_to_default_json(Path("xl_schemas/landfill_v01_00.json"))
  """
  logger.debug(f"schema_to_default_json() called for {file_name_in=}")

  defaults, metadata = schema_to_default_dict(file_name_in)
  metadata['notes'] = (
    "Default values are empty strings unless the field is a drop down cell. "
    "For drop down cells, the default is 'Please Select'."
  )

  if file_name_out is None:
    file_name_out = f"xl_payloads/{metadata['schema_version']}_defaults.json"

  ensure_parent_dirs(file_name_out)

  json_save_with_meta(file_name_out, data=defaults, metadata=metadata, json_options=None)
  return defaults, metadata


def update_xlsx(file_in: Path, file_out: Path, jinja_dict: dict) -> None:
  """
  Render a Jinja-templated XLSX file by replacing placeholders with values from a dictionary.

  Args:
      file_in (Path): Path to the Jinja-enabled XLSX file.
      file_out (Path): Path to write the rendered Excel file.
      jinja_dict (dict): Dictionary mapping Jinja variable names to replacement values.

  Example:
      >>> update_xlsx(Path("template.xlsx"), Path("output.xlsx"), {"id": "123"})
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
  Merge multiple payloads and use them to render a Jinja-templated Excel file.

  Args:
      file_in (Path): Input XLSX file with Jinja placeholders.
      file_out (Path): Output rendered XLSX file.
      payloads (list | tuple): Sequence of dicts or JSON file paths. Later payloads override earlier ones.

  Note:
      Typical usage includes a default payload followed by one or more overrides.

  Example:
      >>> update_xlsx_payloads(
      >>>     Path("template.xlsx"),
      >>>     Path("final.xlsx"),
      >>>     [Path("defaults.json"), {"id_case": "A42"}]
      >>> )
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
  Run sample tests that apply known payloads to known Jinja-templated Excel workbooks.

  This helps verify that the Jinja replacement system is functioning correctly.

  Example:
      >>> test_update_xlsx_payloads_01()
  """
  logger.debug("test_update_xlsx_payloads_01() called")

  # Landfill test with two payloads from file
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
  Create and populate the working directory with schemas, workbooks, and default payloads.

  This is the main entry point for initial Excel form conversion. It:
    - Copies base Excel files
    - Copies VBA-generated schema files
    - Converts and upgrades schema files with types
    - Creates Jinja-compatible workbook versions
    - Writes default payloads for web use

  Example:
      >>> prep_xl_templates()
  """
  logger.debug("prep_xl_templates() called for landfill, oil & gas, and energy schemas")

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

    shutil.copy(spec["input_schema_vba_path"], spec["output_schema_vba_path"])
    shutil.copy(spec["input_xl_path"], spec["output_xl_path"])
    shutil.copy(spec["input_xl_jinja_path"], spec["output_xl_jinja_path"])

    update_vba_schema(spec["schema_version"],
                      file_name_in=spec["output_schema_vba_path"],
                      file_name_out=spec["output_schema_path"])

    schema_to_default_json(file_name_in=spec["output_schema_path"],
                           file_name_out=spec["output_payload_path"])


def create_default_types_schema(diagnostics: bool = False) -> dict:
  """
  Create and optionally log a JSON file that maps variable names to default value types.

  Args:
      diagnostics (bool): If True, print each variable and type to logger.

  Returns:
      dict: Mapping of field names to Python types.

  Example:
      >>> create_default_types_schema(diagnostics=True)
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
  Create a JSON payload file with embedded metadata.

  Args:
      payload (dict): Data to store in JSON.
      file_name (Path): Output file path.
      schema_version (str): Schema version the payload conforms to.
      metadata (dict, optional): Additional metadata. Will be updated with schema version and description.

  Example:
      >>> create_payload({"id_case": "123"}, Path("payload.json"), "v01_00")
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
  Write predefined payloads to disk for landfill, oil & gas, and energy forms.

  Note:
      These payloads support development and QA for XLSX rendering and form field population.

  Example:
      >>> create_payloads()
  """
  logger.debug("create_payloads() called")

  from arb.utils.excel.xl_hardcoded import landfill_payload_01, oil_and_gas_payload_01

  test_sets = [
    ("landfill_v01_00", landfill_payload_01),
    ("oil_and_gas_v01_00", oil_and_gas_payload_01),
    ("energy_v00_01", oil_and_gas_payload_01),  # Reuse oil & gas payload
  ]

  for schema_version, payload in test_sets:
    file_name = PROCESSED_VERSIONS / f"xl_payloads/{schema_version}_payload_01.json"
    file_backup = PROCESSED_VERSIONS / f"xl_payloads/{schema_version}_payload_01_backup.json"

    create_payload(payload, file_name, schema_version)

    if file_name.is_file() and file_backup.is_file():
      compare_json_files(file_name, file_backup)


def create_schemas_and_payloads() -> None:
  """
  Entry point to create schema files, default value payloads, and test population of Excel files.

  This orchestrates:
    - default types schema
    - upgraded schema files
    - default value payloads
    - test payloads
    - test XLSX rendering

  Example:
      >>> create_schemas_and_payloads()
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
  Run a battery of diagnostic checks to verify schema parsing, default value generation,
  payload creation, and Excel file population functionality.

  This function is meant to be called interactively or during development to
  quickly verify that major routines are working as expected.

  Example:
      >>> run_diagnostics()
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
