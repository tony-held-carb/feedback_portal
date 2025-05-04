"""
Module to prep xl templates and to create new Excel files based on jinja payloads.
"""
import shutil
import zipfile
from functools import partial
from pathlib import Path

import jinja2

import arb.__get_logger as get_logger
from arb.utils.excel.xl_misc import xl_address_sort
from arb.utils.file_io import ensure_dir_exists, ensure_parent_dirs, get_project_root_dir
from arb.utils.json import compare_json_files, json_load, json_load_with_meta, json_save_with_meta
from arb.utils.misc import ensure_key_value_pair

logger, pp_log = get_logger.get_logger(__name__, __file__)

# default file (not schema) versions for landfill and oil and gas spreadsheet names
LANDFILL_VERSION = "v070"
OIL_AND_GAS_VERSION = "v070"
ENERGY_VERSION = "v002"

# Get the platform independent project root directory knowing the utils directory structure is:
# 'feedback_portal/source/production/arb/utils/'
app_dir_structure = ['feedback_portal', 'source', 'production', 'arb', 'utils']
PROJECT_ROOT = get_project_root_dir(__file__, app_dir_structure)
print(f"PROJECT_ROOT={PROJECT_ROOT}")
logger.debug(f"PROJECT_ROOT={PROJECT_ROOT}")


def sort_xl_schema(xl_schema, sort_by="variable_name"):
  """
  Sorts in place an Excel schema and sub-schema to allow one to easily line-by-line compare a spreadsheet
  and/or inter-compare two different schemas.

  Sub-schema will be sorted in order of "label", "label_address", "value_address", then "value_type".

  Args:
    xl_schema (dict):
    sort_by (str, optional): Schema sorting scheme.
      Can be the html element 'variable_name' or the sub-schema 'label_address'.
  """
  logger.debug(f"sort_xl_schema() called")

  variable_names = list(xl_schema.keys())
  for variable_name in variable_names:
    sub_schema = xl_schema[variable_name]
    new_order = {}
    for field in ("label", "label_address", "value_address", "value_type"):
      if field in sub_schema:
        new_order[field] = sub_schema.pop(field)
    # append all other fields to the end of the dict
    new_order.update(sub_schema)
    xl_schema[variable_name] = new_order

  # Sort the schema by the desired key
  if sort_by == "variable_name":
    logger.debug(f'sorting by variable_name')
    # dict.items returns a sequence of tuples where item[0] is the key and item[1] is the value
    sorted_items = dict(sorted(xl_schema.items(), key=lambda item: item[0]))
    # logger.debug(f"\n\tsorted_items:\n{sorted_items}")
  elif sort_by == "label_address":
    logger.debug(f'sorting by label_address')
    # Create a partial function for use as the sort key
    get_xl_row = partial(xl_address_sort, address_location="value", sort_by="row", sub_keys="label_address")
    sorted_items = dict(sorted(xl_schema.items(), key=get_xl_row))

  else:
    raise ValueError("sort_by must be 'variable_name' or 'label_address'")

  return sorted_items


def schema_to_json_file(data, schema_version, file_name=None):
  """
  Save a schema data to a json file.

  Args:
    data (dict): data to save in a json file.
    schema_version (str): description of the schema for metadata
    file_name (str, optional): json output file path
  """
  logger.debug(f"schema_to_json_file() called with {schema_version=}, {file_name=}")

  if file_name is None:
    file_name = "xl_schemas/" + schema_version + ".json"

  ensure_parent_dirs(file_name)

  # Convert and write JSON object to file
  metadata = {'schema_version': schema_version}

  logger.debug(f"Creating JSON file: {file_name} with metadata: {metadata}")

  json_save_with_meta(file_name,
                      data=data,
                      metadata=metadata,
                      json_options=None)

  # Reload data and metadata to ensure it was saved correctly (may want to comment out in the future)
  read_data, read_metadata = json_load_with_meta(file_name)
  if read_data == data and read_metadata == metadata:
    logger.debug("SUCCESS. JSON data serialized/deserialized are equivalent to the original data.")
  else:
    logger.warning("FAILURE. JSON data serialized/deserialized are NOT equivalent to the original data.")


def update_vba_schema(schema_version,
                      file_name_in=None,
                      file_name_out=None,
                      file_name_default_value_types=None,
                      ):
  """
  Update a schema created with vba routines and add variable type information and metadata.

  Args:
    schema_version (str): schema version
    file_name_in (str|Path, optional): input file name
    file_name_out (str|Path, optional): output file name
    file_name_default_value_types (str|Path, optional): json file with default typing information

  Returns (dict): schema with updated typing
  """
  logger.debug(f"update_vba_schema() called with {schema_version=}, {file_name_in=}, "
               f"{file_name_out=}, {file_name_default_value_types=}")

  if file_name_in is None:
    file_name_in = "xl_schemas/" + schema_version + "_vba.json"
  if file_name_out is None:
    file_name_out = "xl_schemas/" + schema_version + ".json"
  if file_name_default_value_types is None:
    file_name_default_value_types = "xl_schemas/default_value_types_v01_00.json"

  ensure_parent_dirs(file_name_in)
  ensure_parent_dirs(file_name_out)
  ensure_parent_dirs(file_name_default_value_types)

  # load in the default typing
  default_value_types, _ = json_load_with_meta(file_name_default_value_types)

  # load the vba generated json file
  schema = json_load(file_name_in, json_options=None)

  # add default variable typing to the schema file and sort
  ensure_key_value_pair(schema, default_value_types, "value_type")
  schema = sort_xl_schema(schema, sort_by="label_address")

  # Save to updated schema file with metadata
  schema_to_json_file(schema, schema_version, file_name=file_name_out)

  return schema


def update_vba_schemas():
  """
  Update multiple schemas created with vba routines using update_vba_schema.
  """
  logger.debug(f"updated_vba_schemas() called")

  schema_versions = ['landfill_v01_00', 'oil_and_gas_v01_00']

  for schema_version in schema_versions:
    update_vba_schema(schema_version,
                      file_name_in=None,
                      file_name_out=None,
                      file_name_default_value_types=None,
                      )


def schema_to_default_dict(schema_file_name):
  """
  Based on an Excel json schema file created with update_vba_schema, return a
  dictionary with html variable names for keys default values. For drop down cells,
  the default is 'Please Select'; the default is a blank string for non drop down cells.

  Args:
    schema_file_name (str|pathlib.Path): path to json Excel schema file

  Returns
    tuple: A tuple containing the default values and metadata associated with a schema file.
    - defaults (dict):
    - metadata (dict):
  """
  logger.debug(f"schema_to_default_dict() called for {schema_file_name=}")

  defaults = {}

  data, metadata = json_load_with_meta(schema_file_name)
  logger.debug(f"{metadata=}")

  for variable, sub_schema in data.items():
    if sub_schema["is_drop_down"] is True:
      defaults[variable] = "Please Select"
    else:
      defaults[variable] = ""

  return defaults, metadata


def schema_to_default_json(file_name_in,
                           file_name_out=None,
                           ):
  """
  Based on an Excel json schema file created wit update_vba_schema, save a json file
  with default values and return a dictionary with html variable names for keys default values.
  For drop down cells, the default is 'Please Select';
  the default is a blank string for non drop down cells.

  Args:
    file_name_in (str|pathlib.Path): json input file path of an Excel schema
    file_name_out (str|pathlib.Path, optional): json output file path of an Excel schema

  Returns
    tuple: A tuple containing the default values and metadata associated with a schema file.
    - defaults (dict):
    - metadata (dict):
  """
  logger.debug(f"schema_to_default_json() called for {file_name_in=}")

  defaults, metadata = schema_to_default_dict(file_name_in)
  metadata['notes'] = ("Default values are empty strings unless the field is a drop down cell.  "
                       "For drop down cells, the default is 'Please Select'.")

  if file_name_out is None:
    file_name_out = "xl_payloads/" + metadata['schema_version'] + "_defaults.json"

  ensure_parent_dirs(file_name_out)

  json_save_with_meta(file_name_out,
                      data=defaults,
                      metadata=metadata,
                      json_options=None)

  return defaults, metadata


def update_xlsx(file_in, file_out, jinja_dict):
  """
  Rewrite a xlsx file by replacing jinja variable placeholders (e.g. {{ my_variable }}) with
  values from a dictionary of key value pairs.

  Args:
      file_in (str|pathlib.Path): Path to the original XLSX file.
      file_out (str|pathlib.Path): Path to save the processed XLSX file.
      jinja_dict (dict): Dictionary where dict keys represent jinja template variable names and
                         dict values represent the jinja variable value.
  """
  logger.debug(f"Convertion input file: {file_in} to {file_out} with: {jinja_dict}")

  with (zipfile.ZipFile(file_in, 'r') as xlsx,
        zipfile.ZipFile(file_out, 'w') as new_xlsx):
    for filename in xlsx.namelist():
      with xlsx.open(filename) as file:
        contents = file.read()

        if filename == 'xl/sharedStrings.xml':
          # Perform string replacement for the specific file
          contents = jinja2.Template(contents.decode('utf-8')).render(jinja_dict)
          contents = contents.encode('utf-8')

        new_xlsx.writestr(filename, contents)


def update_xlsx_payloads(file_in, file_out, payloads):
  """
  Update an Excel file with key value pairs from payloads.  If the payload is a path
  to a json file, the payload is the file's data.  Payloads will be processed in order,
  and will overwrite key's if they duplicate.

  Note: You will very likely want the default payload created with prep_xl_templates()
  to be your first payload as it will contain default values for the drop-down cells.

  Args:
    file_in (str|pathlib.Path): Path to the original XLSX file.
    file_out (str|pathlib.Path): Path to save the processed XLSX file.
    payloads (list|tuple): Sequence of json file names containing a payload or a dictionary.

  """
  logger.debug(f"update_xlsx_payloads() called with: {file_in=}, {file_out=}, {payloads=}")

  # convert payloads that are json files into dicts
  new_payloads = []
  new_dict = {}

  # Extract payloads from dicts and json files
  for payload in payloads:
    if isinstance(payload, dict):
      new_payloads.append(payload)
    else:
      data, metadata = json_load_with_meta(payload)
      new_payloads.append(data)

  # create single payload from multiple payloads
  # subsequent payload will overwrite previous entries
  for payload in new_payloads:
    new_dict.update(payload)

  update_xlsx(file_in, file_out, new_dict)


def test_update_xlsx_payloads_01():
  """
  Example usage of update_xlsx_payloads.
  """
  logger.debug(f"test_update_xlsx_payloads_01() called")

  # changing to relative references so code will work on ec2, eventually will move to s3
  # base_dir = Path("C:/one_drive/code/pycharm/feedback_portal/source/production/arb/utils/excel")
  base_dir = Path(".")

  file_name_in = base_dir / f"xl_workbooks/landfill_operator_feedback_{LANDFILL_VERSION}_jinja_.xlsx"
  file_name_out = base_dir / f"xl_workbooks/landfill_operator_feedback_{LANDFILL_VERSION}_populated_01.xlsx"
  payload_01 = base_dir / "xl_payloads/landfill_v01_00_defaults.json"
  payload_02 = base_dir / "xl_payloads/landfill_v01_00_payload_01.json"
  update_xlsx_payloads(file_name_in, file_name_out, [payload_01, payload_02])

  file_name_in = base_dir / f"xl_workbooks/landfill_operator_feedback_{LANDFILL_VERSION}_jinja_.xlsx"
  file_name_out = base_dir / f"xl_workbooks/landfill_operator_feedback_{LANDFILL_VERSION}_populated_02.xlsx"
  payload_01 = base_dir / "xl_payloads/landfill_v01_00_payload_01.json"
  payload_02 = {"id_incidence": "123456"}
  update_xlsx_payloads(file_name_in, file_name_out, [payload_01, payload_02])

  file_name_in = base_dir / f"xl_workbooks/oil_and_gas_operator_feedback_{OIL_AND_GAS_VERSION}_jinja_.xlsx"
  file_name_out = base_dir / f"xl_workbooks/oil_and_gas_operator_feedback_{OIL_AND_GAS_VERSION}_populated_01.xlsx"
  payload_01 = base_dir / "xl_payloads/oil_and_gas_v01_00_defaults.json"
  # payload_02 = {"id_incidence": "456789"}
  payload_02 = base_dir / "xl_payloads/oil_and_gas_v01_00_payload_01.json"
  update_xlsx_payloads(file_name_in, file_name_out, [payload_01, payload_02])

  file_name_in = base_dir / f"xl_workbooks/energy_operator_feedback_{ENERGY_VERSION}_jinja_.xlsx"
  file_name_out = base_dir / f"xl_workbooks/energy_operator_feedback_{ENERGY_VERSION}_populated_01.xlsx"
  payload_01 = base_dir / "xl_payloads/energy_v00_01_defaults.json"
  payload_02 = {"id_incidence": "654321"}
  update_xlsx_payloads(file_name_in, file_name_out, [payload_01, payload_02])


def prep_xl_templates():
  """
  Primary entry point to prepare newly created feedback forms into usable templates for
  operator feedback notifications.

  Step 1.  Create spreadsheet version with named ranges as defined in RSDAS usage specification.
  Step 2.  Run VBA subroutine named named_ranges_to_schema_file() to create an initial schema version.
  Step 3.  Run VBA subroutine named save_with_jinja_template() to create a jinja template for the spreadsheet
           that can be modified in python.
  Step 4.  Specify the version, original spreadsheet path, initial schema version path, and jinja template path
           for further processing below.
  Step 5.  Specify the file specs below for each group of files you wish to convert to a usable python template file.
  """
  logger.debug(f"prep_xl_templates() called to create oil & gas, landfill, and energy schemas")

  file_specs = []

  # change input/output at some point for s3 rather than ec2/laptop
  # input_dir = Path("C:/one_drive/code/pycharm/feedback_portal/feedback_forms/current_versions")
  input_dir = PROJECT_ROOT / "feedback_forms/current_versions"
  # output_dir = Path(".")
  output_dir = PROJECT_ROOT / "feedback_forms/processed_versions"

  ensure_dir_exists(output_dir / "xl_schemas")
  ensure_dir_exists(output_dir / "xl_workbooks")
  ensure_dir_exists(output_dir / "xl_payloads")

  schema_version = "landfill_v01_00"
  file_spec = {"schema_version": schema_version,

               "input_schema_vba_path": input_dir / f"{schema_version}_vba.json",
               "input_xl_path": input_dir / f"landfill_operator_feedback_{LANDFILL_VERSION}.xlsx",
               "input_xl_jinja_path": input_dir / f"landfill_operator_feedback_{LANDFILL_VERSION}_jinja_.xlsx",

               "output_schema_vba_path": output_dir / "xl_schemas" / f"{schema_version}_vba.json",
               "output_schema_path": output_dir / "xl_schemas" / f"{schema_version}.json",
               "output_xl_path": output_dir / "xl_workbooks" / f"landfill_operator_feedback_{LANDFILL_VERSION}.xlsx",
               "output_xl_jinja_path": output_dir / "xl_workbooks" / f"landfill_operator_feedback_{LANDFILL_VERSION}_jinja_.xlsx",
               "output_payload_path": output_dir / "xl_payloads" / f"{schema_version}_defaults.json",
               }
  file_specs.append(file_spec)

  schema_version = "oil_and_gas_v01_00"
  file_spec = {"schema_version": schema_version,

               "input_schema_vba_path": input_dir / f"{schema_version}_vba.json",
               "input_xl_path": input_dir / f"oil_and_gas_operator_feedback_{OIL_AND_GAS_VERSION}.xlsx",
               "input_xl_jinja_path": input_dir / f"oil_and_gas_operator_feedback_{OIL_AND_GAS_VERSION}_jinja_.xlsx",

               "output_schema_vba_path": output_dir / "xl_schemas" / f"{schema_version}_vba.json",
               "output_schema_path": output_dir / "xl_schemas" / f"{schema_version}.json",
               "output_xl_path": output_dir / "xl_workbooks" / f"oil_and_gas_operator_feedback_{OIL_AND_GAS_VERSION}.xlsx",
               "output_xl_jinja_path": output_dir / "xl_workbooks" / f"oil_and_gas_operator_feedback_{OIL_AND_GAS_VERSION}_jinja_.xlsx",
               "output_payload_path": output_dir / "xl_payloads" / f"{schema_version}_defaults.json",
               }
  file_specs.append(file_spec)

  schema_version = "energy_v00_01"
  file_spec = {"schema_version": schema_version,

               "input_schema_vba_path": input_dir / f"{schema_version}_vba.json",
               "input_xl_path": input_dir / f"energy_operator_feedback_{ENERGY_VERSION}.xlsx",
               "input_xl_jinja_path": input_dir / f"energy_operator_feedback_{ENERGY_VERSION}_jinja_.xlsx",

               "output_schema_vba_path": output_dir / "xl_schemas" / f"{schema_version}_vba.json",
               "output_schema_path": output_dir / "xl_schemas" / f"{schema_version}.json",
               "output_xl_path": output_dir / "xl_workbooks" / f"energy_operator_feedback_{ENERGY_VERSION}.xlsx",
               "output_xl_jinja_path": output_dir / "xl_workbooks" / f"energy_operator_feedback_{ENERGY_VERSION}_jinja_.xlsx",
               "output_payload_path": output_dir / "xl_payloads" / f"{schema_version}_defaults.json",
               }
  file_specs.append(file_spec)

  for file_spec in file_specs:
    logger.debug(f"Processing schema_version {file_spec['schema_version']}")

    logger.debug(f"Copying file from: {file_spec['input_schema_vba_path']} to: {file_spec['output_schema_vba_path']}")
    shutil.copy(file_spec["input_schema_vba_path"], file_spec["output_schema_vba_path"])

    logger.debug(f"Copying file from: {file_spec['input_xl_path']} to: {file_spec['output_xl_path']}")
    shutil.copy(file_spec["input_xl_path"], file_spec["output_xl_path"])

    logger.debug(f"Copying file from: {file_spec['input_xl_jinja_path']} to: {file_spec['output_xl_jinja_path']}")
    shutil.copy(file_spec["input_xl_jinja_path"], file_spec["output_xl_jinja_path"])

    update_vba_schema(file_spec["schema_version"],
                      file_name_in=file_spec["output_schema_vba_path"],
                      file_name_out=file_spec["output_schema_path"])

    schema_to_default_json(file_name_in=file_spec["output_schema_path"],
                           file_name_out=file_spec["output_payload_path"])


def create_default_types_schema(diagnostics=False):
  """
  Based on the default_value_types_v01_00 dict in xl_hardcoded.py,
  create a json file with the default data type associated with html element names.

  Note, this routine used to use the outdated air campaign schema information that
  was removed from this file and archived 2025-04-23.

  Args:
    diagnostics (bool) : True if you want additional diagnostic info
  """
  from arb.utils.excel.xl_hardcoded import default_value_types_v01_00

  logger.debug(f"create_default_types_schema called to create the default data type dictionary")

  file_name = Path("xl_schemas/default_value_types_v01_00.json")
  file_backup = Path("xl_schemas/default_value_types_v01_00_backup.json")

  field_types = dict(sorted(default_value_types_v01_00.items()))

  # print(field_types)
  # for k, v in field_types.items():
  #   print(f'"{k}": {v.__name__},')

  if diagnostics:
    for variable_name, type_ in field_types.items():
      logger.debug(f"'{variable_name}': {type_.__name__},")

  metadata = {"schema_version": "default_value_types_v01_00"}
  json_save_with_meta(file_name, field_types, metadata=metadata)

  # Check that the json file is equivalent to a backup
  if file_name.is_file() and file_backup.is_file():
    compare_json_files(file_name, file_backup)

  return field_types


def create_payload(payload,
                   file_name,
                   schema_version,
                   metadata=None):
  """
  Create payload with schema version

  Args:
    payload (dict): data to store in json file
    file_name (str, optional): json output file path
    schema_version (str): description of the schema
    metadata (dict, optional): metadata to store in json file
  """
  logger.debug(f"create_payload() called")

  # Convert and write JSON object to file
  if metadata is None:
    metadata = {}

  metadata["schema_version"] = schema_version
  metadata["payload description"] = "Test of Excel jinja templating system"

  logger.debug(f"Creating JSON file: {file_name} with metadata: {metadata}")

  json_save_with_meta(file_name,
                      data=payload,
                      metadata=metadata,
                      )


def create_payloads():
  """
  Create payloads for testing/development.

  Returns:

  """
  logger.debug(f"create_payloads() called")

  from arb.utils.excel.xl_hardcoded import landfill_payload_01, oil_and_gas_payload_01

  payload = landfill_payload_01
  schema_version = "landfill_v01_00"
  file_name = Path("xl_payloads/landfill_v01_00_payload_01.json")
  file_backup = Path("xl_payloads/landfill_v01_00_payload_01_backup.json")

  create_payload(payload, file_name, schema_version, )
  # Check that the json file is equivalent to a backup
  if file_name.is_file() and file_backup.is_file():
    compare_json_files(file_name, file_backup)

  payload = oil_and_gas_payload_01
  schema_version = "oil_and_gas_v01_00"
  file_name = Path("xl_payloads/oil_and_gas_v01_00_payload_01.json")
  file_backup = Path("xl_payloads/oil_and_gas_v01_00_payload_01_backup.json")

  create_payload(payload, file_name, schema_version, )
  # Check that the json file is equivalent to a backup
  if file_name.is_file() and file_backup.is_file():
    compare_json_files(file_name, file_backup)

  # Use oil and gas payload for energy since they share many fields in common
  payload = oil_and_gas_payload_01
  schema_version = "energy_v00_01"
  file_name = Path("xl_payloads/energy_v00_01_payload_01.json")
  file_backup = Path("xl_payloads/energy_v00_01_payload_01_backup.json")

  create_payload(payload, file_name, schema_version, )
  # Check that the json file is equivalent to a backup
  if file_name.is_file() and file_backup.is_file():
    compare_json_files(file_name, file_backup)


def create_schemas_and_payloads():
  """
  Create landfill and oil and gas schema and payload json files.
  """
  logger.debug(f"create_schemas_and_payloads() called")

  output_dir = Path(".")

  ensure_dir_exists(output_dir / "xl_schemas")
  ensure_dir_exists(output_dir / "xl_workbooks")
  ensure_dir_exists(output_dir / "xl_payloads")

  create_default_types_schema(diagnostics=True)
  prep_xl_templates()
  create_payloads()
  test_update_xlsx_payloads_01()


if __name__ == "__main__":
  pass
  create_schemas_and_payloads()
