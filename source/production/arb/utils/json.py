"""
Module for json related utility functions and classes.
"""
import datetime
import decimal
import json
import logging
import pathlib
from zoneinfo import ZoneInfo

from arb.__get_logger import get_logger
from arb.utils.diagnostics import compare_dicts

# from datetime import datetime
__version__ = "1.0.0"
logger, pp_log = get_logger(__name__, __file__)


# todo - clean up and integrate new json techniques to the website
def json_serializer(obj):
  """
  Custom JSON serializer for objects not serializable by default
  """
  # logger.debug(f"custom_serializer() called with type= {type(obj)}, obj={obj}")
  # Check if a variable is a class type (not an object instances)
  if isinstance(obj, type):
    return_val = {"__class__": obj.__name__, "__module__": obj.__module__}
    # logger.debug(f"{return_val=}")
    return return_val
  elif isinstance(obj, datetime.datetime):
    return_val = {"__type__": "datetime.datetime", "value": obj.isoformat()}
    # logger.debug(f"{return_val=}")
    return return_val
  elif isinstance(obj, decimal.Decimal):
    # Serialize decimal.Decimal as a string
    return {"__type__": "decimal.Decimal", "value": str(obj)}

  raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def json_deserializer(obj):
  """
  Custom JSON deserializer for RSDAS objects
  """
  # logger.debug(f"deserializer() called with type= {type(obj)}, obj={obj}")

  new_obj = obj

  if "__class__" in obj:
    # logger.debug(f"{obj['__class__']=} detected in object deserializer.")
    if obj["__class__"] == "str":
      new_obj = str
    elif obj["__class__"] == "int":
      new_obj = int
    elif obj["__class__"] == "float":
      new_obj = float
    elif obj["__class__"] == "bool":
      new_obj = bool
    elif obj["__class__"] == "datetime":
      new_obj = datetime.datetime

  elif "__type__" in obj:
    # logger.debug(f"{obj['__type__']=} detected in object deserializer.")
    if obj["__type__"] == "datetime.datetime":
      new_obj = datetime.datetime.fromisoformat(obj["value"])
    elif obj["__type__"] == "decimal.Decimal":
      # Deserialize to decimal.Decimal
      new_obj = decimal.Decimal(obj["value"])
    else:
      logger.debug(f"No known conversion type for type {obj['__type__']}")

  # logger.debug(f"deserializer() returning type= {type(new_obj)}, new_obj= {new_obj}")

  return new_obj


def json_save(file_path, data, json_options=None):
  """
  Save a data object to a JSON file.

  Args:
      file_path (str): Path to the JSON file.
      data: The data to save.
      json_options (dict): JSON options to include with dump function.
  """
  logger.debug(f"json_save() called with {file_path=}, {json_options=}, {data=}")

  if json_options is None:
    json_options = {'default': json_serializer, 'indent': 4}

  # Write to JSON file
  with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, **json_options)
  logger.debug(f"JSON saved to file: '{file_path}'.")


def json_save_with_meta(file_path, data, metadata=None, json_options=None):
  """
  Save a data object to a JSON file with metadata such as save time and notes.

  Args:
      file_path (str|pathlib.Path): Path to the JSON file.
      data: The data to save.
      metadata (dict|None): metadata describing the data.
      json_options (dict|None): JSON options to include with dump function.
  """
  logger.debug(f"json_save_with_meta() called with {file_path=}, {json_options=}, {metadata=}, {data=}")

  if metadata is None:
    metadata = {}

  metadata["File created at"] = datetime.datetime.now(ZoneInfo("UTC")).isoformat()
  metadata["Serialized with"] = "utils.json.json_save_with_meta"
  metadata["Deserialize with"] = "utils.json.json_load_with_meta"

  # Add meta information to the data
  data_with_meta = {
    "_metadata_": metadata,
    "_data_": data
  }

  # Write to JSON file
  json_save(file_path, data_with_meta, json_options=json_options)


def json_load(file_path, json_options=None):
  """
  Load a JSON file to a python variable.

  Args:
      file_path (str): Path to the JSON file.
      json_options (dict | None): Options passed to the `json.load` function.

  Returns:
    data (dict): The deserialized JSON data.

  Notes:
    -  encoding="utf-8-sig" will remove (if present) [BOM (Byte Order Mark)] for UTF-8 (\uFEFF)
       if it appears as a special marker at the beginning of some UTF-8 encoded files.
       This marker can cause JSON decoding errors if not handled properly.
  """
  logger.debug(f"json_load() called with {file_path=}, {json_options=}")

  if json_options is None:
    json_options = {'object_hook': json_deserializer}

  # Read JSON file
  with open(file_path, "r", encoding="utf-8-sig") as f:
    data = json.load(f, **json_options)

  return data


def json_load_with_meta(file_path, json_options=None):
  """
  Load a JSON file separating returning the data and metadata
  as separate variables (if possible).

  If the json file is a dictionary with a key _data_, then the _data_ and _metadata_
  (if possible) will  be extracted.  Otherwise, the data is assumed
  to be the whole JSON file with no metadata.

  Args:
      file_path (str, Path): Path to the JSON file.
      json_options (dict | None): Options passed to the `json.load` function.

  Returns:
      tuple[dict, dict]: A tuple containing:
          - data (dict): The deserialized JSON data without metadata.
          - metadata (dict): The deserialized JSON metadata.
  """
  logger.debug(f"json_load_with_meta() called with {file_path=}, {json_options=}")

  all_data = json_load(file_path, json_options=json_options)
  data = all_data
  metadata = {}

  if isinstance(all_data, dict):
    if "_data_" in all_data:
      data = all_data["_data_"]
      if "_metadata_" in all_data:
        metadata = all_data["_metadata_"]

  return data, metadata


def add_metadata_to_json(file_name_in, file_name_out=None):
  """
  Add metadata to JSON file.

  Args:
    file_name_in (str|Path): Path to the JSON input file.
    file_name_out (str|Path|None): Path to the JSON output file.

  """
  logger.debug(f"add_metadata_to_json() called with {file_name_in=}, {file_name_out=}")

  if file_name_out is None:
    file_name_out = file_name_in
  data = json_load(file_name_in)
  json_save_with_meta(file_name_out,
                      data=data,
                      metadata=None,
                      json_options=None)


def compare_json_files(file_name_1, file_name_2):
  """
  Compare two json files to see if they have equivalent content.

  Diagnostics are output to logger.

  Args:
    file_name_1 (str|Path):
    file_name_2 (str|Path):

  """
  logger.debug(f"compare_json_files() called to compare json file contents."
               f"File Name 1: {file_name_1}, File Name 2: {file_name_2}")

  data_01, metadata_01 = json_load_with_meta(file_name_1)
  data_02, metadata_02 = json_load_with_meta(file_name_2)

  logger.debug(f"Comparing metadata")
  result = compare_dicts(metadata_01, metadata_02, "metadata_01", "metadata_02")

  if result is True:
    logger.debug(f"Metadata are equivalent")
  else:
    logger.debug(f"Metadata differ")

  logger.debug(f"Comparing data")
  result = compare_dicts(data_01, data_02, "data_01", "data_02")

  if result is True:
    logger.debug(f"Data are equivalent")
  else:
    logger.debug(f"Data differ")


if __name__ == "__main__":
  logging.basicConfig(filename="util_json_v01.log",
                      encoding="utf-8",
                      level=logging.DEBUG,
                      format="+%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s | %(filename)s | %(lineno)d | %(message)s",
                      datefmt="%Y-%m-%d %H:%M:%S",
                      )
