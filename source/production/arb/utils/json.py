"""
Module for JSON-related utility functions and classes.

Includes custom serialization for datetime and decimal objects,
metadata support, and file comparison diagnostics.

Version:
    1.0.0
"""

import datetime
import decimal
import json
import logging
import pathlib
from zoneinfo import ZoneInfo

from wtforms.fields import DateTimeField, DecimalField

from wtforms import DateTimeField, DecimalField, BooleanField, SelectField, IntegerField, StringField
import datetime
import decimal

from arb.__get_logger import get_logger
from arb.utils.date_and_time import (
  ca_naive_to_utc_datetime,
  datetime_to_ca_naive,
  iso8601_to_utc_dt
)
from arb.utils.diagnostics import compare_dicts

__version__ = "1.0.0"
logger, pp_log = get_logger()


# todo - integrate new json techniques to the website,
#       make sure time are handled using the new time stamps iso strings and native pacific system

def json_serializer(obj) -> dict:
  """
  Custom JSON serializer for objects not natively serializable by `json.dump`.

  Args:
      obj: The object to serialize.

  Returns:
      dict: A dictionary representation of the object.

  Raises:
      TypeError: If the object type is unsupported.

  Example:
      >>> json.dumps(datetime.datetime.now(), default=json_serializer)
  """
  if isinstance(obj, type):
    return {"__class__": obj.__name__, "__module__": obj.__module__}
  elif isinstance(obj, datetime.datetime):
    return {"__type__": "datetime.datetime", "value": obj.isoformat()}
  elif isinstance(obj, decimal.Decimal):
    return {"__type__": "decimal.Decimal", "value": str(obj)}

  raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def json_deserializer(obj: dict) -> object:
  """
  Custom JSON deserializer for known class/type representations.

  Args:
      obj (dict): Dictionary object from JSON file.

  Returns:
      object: Reconstructed Python object.

  Example:
      >>> json.loads(json_string, object_hook=json_deserializer)
  """
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
    else:
      raise TypeError(f"Object of type {type(obj).__name__} is not JSON deserializable")

  elif "__type__" in obj:
    type_tag = obj["__type__"]
    if type_tag == "datetime.datetime":
      new_obj = datetime.datetime.fromisoformat(obj["value"])
    elif type_tag == "decimal.Decimal":
      new_obj = decimal.Decimal(obj["value"])
    else:
      logger.debug(f"No known conversion type for type {obj['__type__']}")

  # logger.debug(f"deserializer() returning type= {type(new_obj)}, new_obj= {new_obj}")

  return new_obj


def json_save(file_path: str | pathlib.Path,
              data,
              json_options: dict | None = None) -> None:
  """
  Save a data object to a JSON file.

  Args:
      file_path (str | Path): Output file path.
      data: Data to serialize and save.
      json_options (dict | None): Options for `json.dump`. If None, defaults to
          {'default': json_serializer, 'indent': 4}.

  Example:
      >>> json_save("output.json", {"x": decimal.Decimal("1.23")})
  """
  logger.debug(f"json_save() called with {file_path=}, {json_options=}, {data=}")

  if json_options is None:
    json_options = {"default": json_serializer, "indent": 4}

  with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, **json_options)

  logger.debug(f"JSON saved to file: '{file_path}'.")


def json_save_with_meta(file_path: str | pathlib.Path,
                        data,
                        metadata: dict | None = None,
                        json_options: dict | None = None) -> None:
  """
  Save data with metadata to a JSON file.

  Args:
      file_path (str | Path): Output JSON file path.
      data: Data to be stored under "_data_".
      metadata (dict | None): Metadata to store under "_metadata_".
      json_options (dict | None): Options for `json.dump`.

  Example:
      >>> json_save_with_meta("log.json", {"key": "value"}, {"source": "generated"})
  """
  logger.debug(f"json_save_with_meta() called with {file_path=}, {json_options=}, {metadata=}, {data=}")

  if metadata is None:
    metadata = {}

  metadata.update({
    "File created at": datetime.datetime.now(ZoneInfo("UTC")).isoformat(),
    "Serialized with": "utils.json.json_save_with_meta",
    "Deserialize with": "utils.json.json_load_with_meta",
  })

  wrapped = {
    "_metadata_": metadata,
    "_data_": data,
  }

  json_save(file_path, wrapped, json_options=json_options)


def json_load(file_path: str | pathlib.Path,
              json_options: dict | None = None):
  """
  Load JSON data from a file.

  Args:
      file_path (str | Path): Path to the JSON file.
      json_options (dict | None): Options for `json.load`.

  Returns:
      object: Deserialized Python object.

  Example:
      >>> json_load("data.json")

  Notes:
    -  encoding="utf-8-sig" will remove (if present) [BOM (Byte Order Mark)] for UTF-8 (\uFEFF)
       if it appears as a special marker at the beginning of some UTF-8 encoded files.
       This marker can cause JSON decoding errors if not handled properly.
  """
  logger.debug(f"json_load() called with {file_path=}, {json_options=}")

  if json_options is None:
    json_options = {"object_hook": json_deserializer}

  with open(file_path, "r", encoding="utf-8-sig") as f:
    return json.load(f, **json_options)


def json_load_with_meta(file_path: str | pathlib.Path,
                        json_options: dict | None = None) -> tuple[object, dict]:
  """
  Load a JSON file and separate data from metadata.

  Args:
      file_path (str | Path): Path to JSON file.
      json_options (dict | None): Optional `json.load` settings.

  Returns:
      tuple:
          - object: Main data under "_data_" (or full file if not present).
          - dict: Metadata under "_metadata_" (or empty if not present).

  Example:
      >>> data, meta = json_load_with_meta("example.json")

  Notes:
      If the json file is a dictionary with a key _data_, then the _data_ and _metadata_
      (if possible) will  be extracted.  Otherwise, the data is assumed
      to be the whole JSON file with no metadata.
  """
  logger.debug(f"json_load_with_meta() called with {file_path=}, {json_options=}")

  all_data = json_load(file_path, json_options=json_options)
  if isinstance(all_data, dict) and "_data_" in all_data:
    return all_data["_data_"], all_data.get("_metadata_", {})

  return all_data, {}


def add_metadata_to_json(file_name_in: str | pathlib.Path,
                         file_name_out: str | pathlib.Path | None = None) -> None:
  """
  Add or update metadata in a JSON file.

  Args:
      file_name_in (str | Path): Input JSON file.
      file_name_out (str | Path | None): Output file. If None, overwrites input.

  Example:
      >>> add_metadata_to_json("schema.json")
  """
  logger.debug(f"add_metadata_to_json() called with {file_name_in=}, {file_name_out=}")

  if file_name_out is None:
    file_name_out = file_name_in

  data = json_load(file_name_in)
  json_save_with_meta(file_name_out, data=data)


def compare_json_files(file_name_1: str | pathlib.Path,
                       file_name_2: str | pathlib.Path) -> None:
  """
  Compare two JSON files' metadata and data content.

  Args:
      file_name_1 (str | Path): Path to first file.
      file_name_2 (str | Path): Path to second file.

  Logs:
      Outputs detailed comparison diagnostics to logger.

  Example:
      >>> compare_json_files("old.json", "new.json")
  """
  logger.debug(f"compare_json_files() comparing {file_name_1} and {file_name_2}")

  data_1, meta_1 = json_load_with_meta(file_name_1)
  data_2, meta_2 = json_load_with_meta(file_name_2)

  logger.debug("Comparing metadata")
  if compare_dicts(meta_1, meta_2, "metadata_01", "metadata_02") is True:
    logger.debug("Metadata are equivalent")
  else:
    logger.debug("Metadata differ")

  logger.debug("Comparing data")
  if compare_dicts(data_1, data_2, "data_01", "data_02") is True:
    logger.debug("Data are equivalent")
  else:
    logger.debug("Data differ")


def cast_model_value(value, value_type, convert_time_to_ca=False):
  """
  Deserialize a value stored in JSON as a string to its Python type for
  use in a WTForm field.

  Args:
      value (string): Model value stored in JSON as a string.
      value_type: Python type of value to be stored in a WTForm.
      convert_time_to_ca (bool): True to convert datetime to California local with no timezone info.
                                 False to leave in UTC with timezone info.

  Returns:
      The value cast to the appropriate Python type.

  Raises:
      ValueError: If the value cannot be cast to the given type.
  """
  try:
    if value_type == str:
      # No need to cast a string
      return value
    elif value_type in [bool, int, float]:
      return value_type(value)
    elif value_type == datetime.datetime:
      dt = iso8601_to_utc_dt(value)
      return datetime_to_ca_naive(dt) if convert_time_to_ca else dt
    elif value_type == decimal.Decimal:
      return decimal.Decimal(value)
    else:
      raise ValueError(f"Unsupported type for casting: {value_type}")
  except Exception as e:
    raise ValueError(f"Failed to cast {value!r} to {value_type}: {e}")


def wtform_types_and_values(wtform) -> tuple[dict[str, type], dict[str, object]]:
  """
  Constructs two dictionaries from a WTForm instance:

  1. A type map for fields requiring explicit type conversion (e.g., datetime, decimal).
  2. A dictionary of field data values for all fields (including 'Please Select').

  Args:
      wtform (FlaskForm): WTForms instance.

  Returns:
      tuple:
          - dict[str, type]: Field name to type mapping for deserialization.
          - dict[str, object]: Field name to current value mapping (may include 'Please Select').
  """
  type_map = {}
  field_data = {}

  for name, field in wtform._fields.items():
    value = field.data
    field_data[name] = value

    # Identify complex field types for type mapping
    if isinstance(field, DateTimeField):
      type_map[name] = datetime.datetime
    elif isinstance(field, DecimalField):
      type_map[name] = decimal.Decimal
    elif isinstance(field, BooleanField):
      type_map[name] = bool
    elif isinstance(field, IntegerField):
      type_map[name] = int
    elif isinstance(field, SelectField):
      type_map[name] = str  # 'Please Select' is valid

  return type_map, field_data

def make_dict_serializeable(
    input_dict: dict,
    type_map: dict[str, type] = None,
    convert_time_to_ca=False,
) -> dict:
  """
  Convert a dictionary to ensure all keys are strings and all values are JSON-serializable.

  Args:
      input_dict (dict): Input dictionary with possibly complex Python objects.
      type_map (dict[str, type], optional): Optional mapping of keys to types to cast values to.
      convert_time_to_ca (bool): True to assume that a timestamp with no timezone info is california time
                                 False to leave in UTC with timezone info.
  Returns:
      dict: A new dictionary with string keys and JSON-serializable values.

  Raises:
      TypeError: If any key is not a string.
  """
  result = {}

  for key, value in input_dict.items():
    if not isinstance(key, str):
      raise TypeError(f"All keys must be strings. Invalid key: {key} ({type(key)})")

    if type_map and key in type_map:
      try:
        value = type_map[key](value)
      except Exception as e:
        raise ValueError(f"Failed to cast key '{key}' to {type_map[key]}: {e}")

    if isinstance(value, datetime.datetime):
      if convert_time_to_ca:
        value = ca_naive_to_utc_datetime(value)
      value = value.isoformat()

    elif isinstance(value, decimal.Decimal):
      value = float(value)

    result[key] = value

  return result


def deserialize_dict(
    input_dict: dict,
    type_map: dict[str, type],
    convert_time_to_ca=False,
) -> dict:
  """
  Deserialize a dictionary's values based on a type map, casting string values to target types.

  Args:
      input_dict (dict): Dictionary with string keys and values to deserialize.
      type_map (dict[str, type]): Mapping of keys to desired types (e.g., int, float, datetime).
      convert_time_to_ca (bool): True to convert datetime to California local with no timezone info.
                                 False to leave in UTC with timezone info.

  Returns:
      dict: A new dictionary with values cast to their specified types.

  Raises:
      TypeError: If any key is not a string.
      ValueError: If value casting fails for a key.
  """
  result = {}

  for key, value in input_dict.items():
    if not isinstance(key, str):
      raise TypeError(f"All keys must be strings. Invalid key: {key} ({type(key)})")

    if key in type_map:
      result[key] = cast_model_value(value, type_map[key], convert_time_to_ca)
    else:
      result[key] = value

  return result


def run_diagnostics() -> None:
  """
  Run diagnostics to validate core JSON utility functionality.

  This includes:
    - Custom serialization and deserialization of datetime and decimal types.
    - Saving and loading JSON with and without metadata.
    - Adding metadata to a plain JSON file.
    - Comparing two JSON files for equivalence.

  Example:
      >>> run_diagnostics()
  """
  import tempfile
  import shutil

  print("Running diagnostics for JSON utilities...")

  temp_dir = pathlib.Path(tempfile.gettempdir()) / "json_utils_test"
  if temp_dir.exists():
    shutil.rmtree(temp_dir)
  temp_dir.mkdir(parents=True)

  try:
    # Test data
    data = {
      "decimal": decimal.Decimal("123.45"),
      "timestamp": datetime.datetime(2025, 5, 5, 13, 30, 0, tzinfo=ZoneInfo("UTC")),
      "nested": {"a": 1, "b": 2},
    }

    # File paths
    json_file_1 = temp_dir / "test_1.json"
    json_file_2 = temp_dir / "test_2.json"
    plain_file = temp_dir / "plain.json"

    # Save and load using json_save/json_load
    json_save(json_file_1, data)
    loaded_1 = json_load(json_file_1)
    assert loaded_1 == data, "Basic save/load failed"

    # Save with metadata and reload
    meta_info = {"note": "test file"}
    json_save_with_meta(json_file_2, data, metadata=meta_info)
    loaded_data, loaded_meta = json_load_with_meta(json_file_2)
    assert loaded_data == data, "Data mismatch in metadata test"
    assert "note" in loaded_meta, "Metadata not found"

    # Write plain file, with serializer included, then enrich with metadata
    with open(plain_file, "w", encoding="utf-8") as f:
      json.dump(data, f, indent=2, default=json_serializer)
    add_metadata_to_json(plain_file)

    # Compare metadata-enriched files
    compare_json_files(json_file_2, plain_file)

    print("All diagnostics completed successfully.")

  except Exception as e:
    print(f"Diagnostics failed: {e}")
    raise


if __name__ == "__main__":
  logging.basicConfig(
    filename="util_json_v01.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="+%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s | "
           "%(filename)s | %(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
  )
  run_diagnostics()
