"""
Module to parse and ingest Excel spreadsheet contents.

Notes on usage.
  - A schema_file_map is a dictionary where the keys are schema name and the values
    are the path to the json file associated with the schema.
  - A schema_map is a dictionary where the keys are schema name values are a sub-dictionary
    of the form: {"schema": schema, "metadata": metadata}
  - Example usage:
      xl_schema_map["oil_and_gas_v03"]["schema"]   <--- results in the schema dict for oil and gas

"""

import copy
import datetime
import logging
from pathlib import Path

import openpyxl

import arb.__get_logger as get_logger
from arb.utils.date_and_time import parse_unknown_datetime
from arb.utils.json import json_load_with_meta, json_save_with_meta

logger, pp_log = get_logger.get_logger(__name__, __file__)

# Spreadsheet formatting constants
EXCEL_SCHEMA_TAB_NAME = '_json_schema'
EXCEL_METADATA_TAB_NAME = '_json_metadata'
EXCEL_TOP_LEFT_KEY_VALUE_CELL = '$B$15'

# Default location of schema files that are initialized with initialize_module()
xl_base_path = Path()
xl_base_schema_path = Path()
xl_schema_file_map = {}
xl_schema_map = {}


def initialize_module():
  logger.debug(f"initialize_module() called")
  set_globals()


def set_globals(xl_base_path_=None, xl_base_schema_path_=None, xl_schema_file_map_=None):
  """
  Set global variables.

  Notes:
    - Best practice would be to set all global variables in a single call,
      otherwise you may get unexpected results (such as the xl_schema_map updating to defaults).
    - if you want to change some of the globals, but not all of them, pass the existing value of the
      global you don't want to change as an argument.
      for example:
        - set_globals(xl_base_path_="my_path", xl_schema_file_map_=xl_schema_map)
        - This will update both xl_base_path and xl_base_schema_path, but xl_schema_file_map will not be updated.
  """
  global xl_base_path, xl_base_schema_path, xl_schema_file_map, xl_schema_map

  logger.debug(f"set_globals() called with {xl_base_path_=}, {xl_base_schema_path_=}, {xl_schema_file_map_=}")

  if xl_base_path_ is None:
    # todo - consider changing to the gpt recommended way of
    # Set the project root based on the location of app.py
    # PROJECT_ROOT = Path(__file__).resolve().parent.parent
    # changing to relative references so code will work on ec2, eventually will move to s3
    # my_path1 = Path(__file__).parent
    # print(f"{my_path1=}")
    xl_base_path = Path.cwd()

    logger.debug(f"{xl_base_path=}")
  else:
    xl_base_path = xl_base_path_

  if xl_base_path.name == 'portal':
    logger.debug(f"Looks like this is run from a flask app ... changing the base directory")
    xl_base_path = xl_base_path.parent / "utils" / "excel"
    logger.debug(f"{xl_base_path=}")

  if xl_base_schema_path_ is None:
    xl_base_schema_path = xl_base_path / "xl_schemas"
  else:
    xl_base_schema_path = xl_base_schema_path_

  # todo - not sure if these should be hard coded here ...
  if xl_schema_file_map_ is None:
    xl_schema_file_map = {
      "landfill_v01_00": xl_base_schema_path / "landfill_v01_00.json",
      "oil_and_gas_v01_00": xl_base_schema_path / "oil_and_gas_v01_00.json",
      "energy_v00_01": xl_base_schema_path / "energy_v00_01.json",
    }
  else:
    xl_schema_file_map = xl_schema_file_map_

  # load all the schemas
  if xl_schema_file_map:
    xl_schema_map = load_schema_file_map(xl_schema_file_map)

  logger.debug(f"globals are now: {xl_base_path=}, {xl_base_schema_path=}, "
               f"{xl_schema_file_map=}, {xl_schema_map=}")


def load_schema_file_map(schema_file_map):
  """
  Return the schema and metadata given a dict where keys are schema names
  and values are the path the json file associated with that schema.

  Args:
    schema_file_map (dict): dict of schema names and associated json file paths

  Returns (dict): dict of schema names and the schema and metadata associated from json files.
  """
  logger.debug(f"load_schema_file_map() called with {schema_file_map=}")

  schema_map = {}

  for schema_name, json_path in schema_file_map.items():
    schema, metadata = json_load_with_meta(json_path)
    schema_map[schema_name] = {"schema": schema, "metadata": metadata}

  return schema_map


def create_schema_file_map(schema_path=None, schema_names=None):
  """
  Create a map of schema names and json file locations that can be loaded with load_schema_file_map.
  Assumes that the json file name is the same as the schema name (with .json appended).

  Args:
    schema_path (str, Path, optional): Path to json schema directory.
    schema_names (list[str], optional): List of schema names.

  Returns (dict): dict of schema names and associated json file paths
  """
  logger.debug(f"create_schema_file_map() called with {schema_path=}, {schema_names=}")
  if schema_path is None:
    schema_path = xl_base_schema_path
  if schema_names is None:
    schema_names = ["landfill_v01_00",
                    "oil_and_gas_v01_00",
                    "energy_v00_01", ]

  schema_file_map = {}

  for schema_name in schema_names:
    schema_file_name = schema_name + ".json"
    schema_file_path = schema_path / schema_file_name
    schema_file_map[schema_name] = schema_file_path

  return schema_file_map


def load_xl_schema(file_name):
  """
  Load an Excel schemas from a json file into a dictionary.

  Args:
    file_name (str, Path): Path to json schema.

  Returns:
      tuple[dict, dict]: A tuple containing:
          - schema (dict): The xl schema.
          - metadata (dict): The JSON metadata associated with the schema file.

  """
  logger.debug(f"load_xl_schema() called with {file_name=}")
  schema, metadata = json_load_with_meta(file_name)
  return schema, metadata


def parse_xl_file(xl_path, schema_map=None):
  """
  Parse a spreadsheet path and return a dictionary representation of the spreadsheet
  based on a schema dictionary.

  Args:
    xl_path (str|Path): Path to the spreadsheet file
    schema_map (dict): xl schema dictionary

  Returns (dict): A dictionary representation of the spreadsheet

  Notes:
    * tutorial on openpyxl: https://openpyxl.readthedocs.io/en/stable/tutorial.html
  """
  logger.debug(f"parse_xl_with_schema_dict() called with {xl_path=}, {schema_map=}")

  if schema_map is None:
    schema_map = xl_schema_map

  # Dictionary data structure to store Excel contents
  result = {}
  result['metadata'] = {}
  result['schemas'] = {}
  result['tab_contents'] = {}

  # Notes on data_only argument.  By default, .value returns the 'formula' in the cell.
  # If data_only=True, then .value  returns the last 'value' that was evaluated at the cell.
  wb = openpyxl.load_workbook(xl_path, keep_vba=False, data_only=True)

  # Extract metadata and schema information from hidden tabs
  if EXCEL_METADATA_TAB_NAME in wb.sheetnames:
    logger.debug(f"metadata tab detected in Excel file")
    result['metadata'] = get_spreadsheet_key_value_pairs(wb, EXCEL_METADATA_TAB_NAME, EXCEL_TOP_LEFT_KEY_VALUE_CELL)

  if EXCEL_SCHEMA_TAB_NAME in wb.sheetnames:
    logger.debug(f"Schema tab detected in Excel file")
    result['schemas'] = get_spreadsheet_key_value_pairs(wb, EXCEL_SCHEMA_TAB_NAME, EXCEL_TOP_LEFT_KEY_VALUE_CELL)
  else:
    ValueError(f'Spreadsheet must have a {EXCEL_SCHEMA_TAB_NAME} tab')

  # extract data tabs content using specified schemas
  new_result = extract_tabs(wb, schema_map, result)

  return new_result


def extract_tabs(wb, schema_map, xl_as_dict, drop_downs_rev=None):
  """
  Extract data from the data tabs that are enumerated in the schema tab.

  Args:
    wb (openpyxl.workbook.workbook.Workbook): openpyxl workbook
    schema_map (dict): xl schema dictionary
    xl_as_dict (dict): dictionary with schema tab where keys are the data tab names and values are the formatting_schema to
                parse the tab
    drop_downs_rev (dict): Reverse drop down dictionary to convert drop down values to their keys 
                          for html select elements. 
  """
  # todo - this had to be updated because drop downs are no longer foreign keys, test that it still works
  # todo - payloads may be expressing as datetime objects rather than utc strings, which may lead to inconsistencies

  result = copy.deepcopy(xl_as_dict)

  for tab_name, formatting_schema in result['schemas'].items():
    logger.debug(f"Extracting data from '{tab_name}', using the formatting schema '{formatting_schema}'")
    result['tab_contents'][tab_name] = {}

    ws = wb[tab_name]
    format_dict = schema_map[formatting_schema]['schema']

    for html_field_name, lookup in format_dict.items():
      value_address = lookup['value_address']
      value_type = lookup['value_type']
      value = ws[value_address].value

      # Try to cast the spreadsheet data to the desired type if possible
      if value is not None:
        if not isinstance(value, value_type):
          # if it is not supposed to be of type string, but it is a zero length string, turn it to None
          if value == "":
            value = None
          else:
            logger.warning(f"Warning: <{html_field_name}> value at <{lookup['value_address']}> is <{value}> "
                           f"and is of type <{type(value)}> whereas it should be of type <{value_type}>.  "
                           f"Attempting to convert the value to the correct type")
            try:
              # convert to datetime using a parser if possible
              if value_type == datetime.datetime:
                local_datetime = parse_unknown_datetime(value)
                # utc_datetime = local_datetime.astimezone(ZoneInfo("UTC")) # If you wanted to cast
                value = local_datetime
              else:
                # Use default repr-like conversion if not a datetime
                value = value_type(value)
              logger.info(f"Type conversion successful.  value is now <{value}> with type: <{type(value)}>")
            except (ValueError, TypeError) as e:
              logger.warning(f"Type conversion failed, resetting value to None")
              value = None

      result['tab_contents'][tab_name][html_field_name] = value

      if 'label_address' in lookup and 'label' in lookup:
        label_address = lookup['label_address']
        label_xl = ws[label_address].value
        label_schema = lookup['label']
        if label_xl != label_schema:
          logger.warning(f"Schema data label and spreadsheet data label differ."
                         f"\n\tschema label = {label_schema}\n\tspreadsheet label ({label_address}) = {label_xl}")

    logger.debug(f"Initial spreadsheet extraction of '{tab_name}' yields {result['tab_contents'][tab_name]}")
    # Some cells should be spit into multiple dictionary entries (such as full name, lat/log)
    split_compound_keys(result['tab_contents'][tab_name])
    # Excel drop-downs save the value not the key, so you have to reverse lookup their values

    logger.debug(f"Final corrected spreadsheet extraction of '{tab_name}' yields {result['tab_contents'][tab_name]}")

  return result


def split_compound_keys(dict_) -> None:
  """
  Remove key/value pairs of entries that potentially contain compound keys and replace them with key value pairs
  that are more atomic.

  Args:
    dict_ (dict): dictionary representation of the spreadsheet key/value pairs that may have compound keys
  """
  for html_field_name in list(dict_.keys()):
    value = dict_[html_field_name]

    if html_field_name == 'lat_and_long':
      if value:
        lat_longs = value.split(',')
        if len(lat_longs) == 2:
          dict_['lat_arb'] = lat_longs[0]
          dict_['long_arb'] = lat_longs[1]
        else:
          raise ValueError(f"Lat long must be a blank or a comma separated list of lat/long pairs")
      del dict_[html_field_name]


def get_spreadsheet_key_value_pairs(wb, tab_name, top_left_cell):
  """
  Starting in the top left cell of a worksheet table, read in key value pairs
  until a blank key is detected.

  Args:
    wb (openpyxl.workbook.workbook.Workbook): worksheet with key value pairs
    tab_name (str): name of tab with key value pairs
    top_left_cell (str): top left cell of key value pair table

  Returns (dict): dictionary of key value pairs detected in the spreadsheet tab

  """
  # logger.debug(f"{type(wb)=}, ")
  ws = wb[tab_name]

  # logger.debug(f"{type(ws)=}, ")

  return_dict = {}

  row_offset = 0
  while True:
    key = ws[top_left_cell].offset(row=row_offset).value
    value = ws[top_left_cell].offset(row=row_offset, column=1).value
    if key not in ["", None]:
      return_dict[key] = value
      row_offset += 1
    else:
      break

  return return_dict


# todo - make sure this still works in the website
#          likely should be broken up into sub components
def get_json_file_name(file_name: Path):
  """
  Given a file_name on the server, return its json file name if possible.

  If the file_name is a json file (has .json extension), the file_name is the json_file_name.
  If the file is an Excel file (.xlsx extension), try to parse it into a json file and return the json file name
  of the parsed contents.
  If the file is neither a json file nr a spreadsheet that can be parsed into a json file, return None.

  Returns (Path|None):
    If the file was already a json file, return the file name unaltered.
    If the file was an Excel file, return the json file that its data was extracted to.
    For all other file types return None.

  """
  json_file_name = None

  extension = file_name.suffix
  # logger.debug(f"{extension=}")
  if extension == ".xlsx":
    logger.debug(f"Excel file upload detected.  File name: {file_name}")
    # xl_as_dict = xl_path_to_dict(file_name)
    xl_as_dict = parse_xl_file(file_name)
    logger.debug(f"{xl_as_dict=}")
    json_file_name = file_name.with_suffix('.json')
    logger.debug(f"Saving extracted data from Excel as: {json_file_name}")
    json_save_with_meta(json_file_name, xl_as_dict)
  elif extension == ".json":
    logger.debug(f"Json file upload detected.  File name: {file_name}")
    json_file_name = Path(file_name)
  else:
    logger.debug(f"Unknown file type upload detected.  File name: {file_name}")

  return json_file_name


def test_load_schema_file_map():
  logger.debug(f"test_load_schema_file_map() called")
  schema_map = create_schema_file_map()
  schemas = load_schema_file_map(schema_map)
  logger.debug(f"{schemas=}")


def test_load_xl_schemas():
  logger.debug(f"Testing load_xl_schemas() with test_load_xl_schemas")
  schemas = load_schema_file_map(xl_schema_file_map)
  logger.debug(f"Testing load_xl_schemas() with test_load_xl_schemas")
  logging.debug(f"\nschemas=\n{pp_log(schemas)}")
  # logging.debug(f"\nschemas=\n{dict_to_str(schemas)}")


def test_parse_xl_file():
  """
  Parse a spreadsheet path and return a dictionary representation of the spreadsheet
  based on a json file with schema data.

  Notes:
    xl_path (str|Path): Path to the spreadsheet file
    schema_path (str|Path): Path to the JSON file with schema data
  """
  logger.debug(f"test_parse_xl_file() called")
  xl_path = xl_base_path / "xl_workbooks/landfill_operator_feedback_v070_populated_01.xlsx"
  result = parse_xl_file(xl_path, xl_schema_map)
  logger.debug(f"{result=}")


# todo - may want to create a pretty printer with the logger since they go together well
def main():
  # test_load_xl_schemas()
  # test_xl_to_dict()
  # test_load_schema_file_map()
  test_parse_xl_file()
  # initialize_module()


# -----------------------------------------------------------------------------
# Initialize module global values
# -----------------------------------------------------------------------------
initialize_module()

if __name__ == "__main__":
  main()
