"""
Module for JSON-related utility functions and classes.

Includes:
  - Custom serialization for datetime and decimal objects
  - Metadata support for enhanced JSON files
  - File-based diagnostics and JSON comparison utilities
  - WTForms integration for form data extraction and casting

Version:
    1.0.0

Notes:
    - Designed for structured JSON handling across ARB portal utilities.
    - Emphasizes ISO 8601 datetime formats and consistent value type casting.
    - Supports "Pacific Time naive" conversion via ZoneInfo-aware logic.
"""

import datetime
import decimal
import json
import logging
import pathlib
from typing import Any
from zoneinfo import ZoneInfo

from wtforms import BooleanField, DateTimeField, DecimalField, IntegerField, SelectField

from arb.utils.date_and_time import (
  ca_naive_to_utc_datetime,
  datetime_to_ca_naive,
  iso8601_to_utc_dt, normalize_value
)
from arb.utils.diagnostics import compare_dicts

__version__ = "1.0.0"

from arb.utils.misc import safe_cast
from arb.utils.io_wrappers import save_json_safely, read_json_file
from arb_logging import get_pretty_printer

logger = logging.getLogger(__name__)
_, pp_log = get_pretty_printer()


# todo - integrate new json techniques to the website,
#       make sure time are handled using the new time stamps iso strings and native pacific system

def json_serializer(obj: object) -> dict:
  """
  Custom JSON serializer for objects not natively serializable by `json.dump`.

  Args:
      obj (object): The object to serialize.

  Returns:
      dict: A JSON-compatible dictionary representation of the object.

  Raises:
      TypeError: If the object type is unsupported.

  Example:
    Input : json.dumps(datetime.datetime.now(), default=json_serializer)
    Output: JSON string with ISO datetime object encoded
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
  Custom JSON deserializer for class/type representations created by `json_serializer`.

  Args:
      obj (dict): Dictionary object from JSON with special tags for known types.

  Returns:
      object: Reconstructed Python object.

  Example:
    Input : json.loads(json_string, object_hook=json_deserializer)
    Output: Python object reconstructed from JSON with type tags
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


def json_save(
    file_path: str | pathlib.Path,
    data: object,
    json_options: dict | None = None
) -> None:
  """
  Save a Python object to a JSON file with optional serialization settings.

  Args:
      file_path (str | Path): Path to write the JSON file.
      data (object): Data to serialize and write.
      json_options (dict | None): Options to pass to `json.dump`.

  Example:
    Input : file_path = "output.json", data = {"x": Decimal("1.23")}
    Output: Creates a JSON file with serialized data at the given path
  """
  logger.debug(f"json_save() called with {file_path=}, {json_options=}, {data=}")

  if json_options is None:
    json_options = {"default": json_serializer, "indent": 4}

  save_json_safely(data, file_path, encoding="utf-8", json_options=json_options)

  logger.debug(f"JSON saved to file: '{file_path}'.")


def json_save_with_meta(
    file_path: str | pathlib.Path,
    data: object,
    metadata: dict | None = None,
    json_options: dict | None = None
) -> None:
  """
  Save data with metadata to a JSON file under special keys.

  Args:
      file_path (str | Path): Output JSON file path.
      data (object): Primary data to store under "_data_".
      metadata (dict | None): Optional metadata under "_metadata_".
      json_options (dict | None): Options for `json.dump`.

  Example:
    Input :
      file_path = "log.json"
      data = {"key": "value"}
      metadata = {"source": "generated"}
    Output: Writes JSON with _data_ and _metadata_ fields
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


def json_load(
    file_path: str | pathlib.Path,
    json_options: dict | None = None
) -> object:
  """
  Load and deserialize data from a JSON file.

  Args:
      file_path (str | Path): Path to the JSON file.
      json_options (dict | None): Optional options passed to `json.load`.

  Returns:
      object: Deserialized Python object.

  Example:
    Input : file_path = "data.json"
    Output: Deserialized Python object from JSON

  Notes:
    -  encoding="utf-8-sig" will remove (if present) [BOM (Byte Order Mark)] for UTF-8 (\uFEFF)
       if it appears as a special marker at the beginning of some UTF-8 encoded files.
       This marker can cause JSON decoding errors if not handled properly.
  """
  logger.debug(f"json_load() called with {file_path=}, {json_options=}")

  if json_options is None:
    json_options = {"object_hook": json_deserializer}

  return read_json_file(file_path, encoding="utf-8-sig", json_options=json_options)


def json_load_with_meta(file_path: str | pathlib.Path,
                        json_options: dict | None = None) -> tuple[Any, dict]:
  """
  Load a JSON file and return both data and metadata if present.

  Args:
    file_path (str | Path): Path to the JSON file.
    json_options (dict | None): Optional options passed to `json.load`.

  Returns:
    tuple:
      - Any: Deserialized data from "_data_" (or the entire file if "_data_" is not present).
      - dict: Deserialized metadata from "_metadata_" (or empty dict if not present).

  Example:
    Input : file_path = "example.json"
    Output: tuple (data, metadata) extracted from the file

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


def add_metadata_to_json(
    file_name_in: str | pathlib.Path,
    file_name_out: str | pathlib.Path | None = None
) -> None:
  """
  Add metadata to an existing JSON file or overwrite it in-place.

  Args:
      file_name_in (str | Path): Input JSON file path.
      file_name_out (str | Path | None): Output file path. If None, overwrites input.

  Example:
    Input : file_name_in = "schema.json"
    Output: Adds metadata and writes back to same file
  """
  logger.debug(f"add_metadata_to_json() called with {file_name_in=}, {file_name_out=}")

  if file_name_out is None:
    file_name_out = file_name_in

  data = json_load(file_name_in)
  json_save_with_meta(file_name_out, data=data)


def compare_json_files(
    file_name_1: str | pathlib.Path,
    file_name_2: str | pathlib.Path
) -> None:
  """
  Compare the contents of two JSON files including metadata and values.

  Args:
      file_name_1 (str | Path): Path to the first file.
      file_name_2 (str | Path): Path to the second file.

  Logs:
      Differences or matches are logged at debug level.

  Example:
    Input : file_name_1 = "old.json", file_name_2 = "new.json"
    Output: Logs any differences or confirms matches
  """
  logger.debug(f"compare_json_files() comparing {file_name_1} and {file_name_2}")

  data_1, meta_1 = json_load_with_meta(file_name_1)
  data_2, meta_2 = json_load_with_meta(file_name_2)

  logger.debug(f"Comparing metadata")
  if compare_dicts(meta_1, meta_2, "metadata_01", "metadata_02") is True:
    logger.debug(f"Metadata are equivalent")
  else:
    logger.debug(f"Metadata differ")

  logger.debug(f"Comparing data")
  if compare_dicts(data_1, data_2, "data_01", "data_02") is True:
    logger.debug(f"Data are equivalent")
  else:
    logger.debug(f"Data differ")


def cast_model_value(
    value: str,
    value_type: type,
    convert_time_to_ca: bool = False
) -> object:
  """
  # todo - may want to change name and description of this function it seems misleading
  Cast a stringified JSON value into a Python object of the expected type.

  Args:
      value (str): Input value to cast.
      value_type (type): Python type to cast to.
      convert_time_to_ca (bool): If True, convert UTC to California naive datetime.

  Returns:
      object: Value converted to the target Python type.

  Raises:
      ValueError: If the value cannot be cast to the given type.
  """
  # todo - datetime - may need to update
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


def wtform_types_and_values(
    wtform
) -> tuple[dict[str, type], dict[str, object]]:
  """
  Extract field types and current data values from a WTForm.

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
    type_map: dict[str, type] | None = None,
    convert_time_to_ca: bool = False
) -> dict:
  """
  Transform a dictionary to ensure JSON compatibility of its values.

  Args:
      input_dict (dict): Original dictionary to process.
      type_map (dict[str, type] | None): Optional field-to-type map for casting.
      convert_time_to_ca (bool): Convert datetimes to CA time before serialization.

  Returns:
      dict: A dictionary with only JSON-serializable values.

  Raises:
      TypeError: If any key is not a string.
      ValueError: If value cannot be cast to expected type.
  """
  result = {}

  for key, value in input_dict.items():
    if not isinstance(key, str):
      raise TypeError(f"All keys must be strings. Invalid key: {key} ({type(key)})")

    if type_map and key in type_map:
      try:
        value = safe_cast(value, type_map[key])
      except Exception as e:
        raise ValueError(f"Failed to cast key '{key}' to {type_map[key]}: {e}")

    # todo - datetime - change this to ensure datetime is iso and fail if it is not
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
    convert_time_to_ca: bool = False
) -> dict:
  """
  Args:
      input_dict (dict): Dictionary of raw values.
      type_map (dict[str, type]): Field-to-type mapping for deserialization.
      convert_time_to_ca (bool): If True, converts datetime to CA time.

  Returns:
      dict: Fully deserialized dictionary.

  Raises:
      TypeError: If any key is not a string.
      ValueError: If value casting fails for a key.
  """
  result = {}

  for key, value in input_dict.items():
    if not isinstance(key, str):
      raise TypeError(f"All keys must be strings. Invalid key: {key} ({type(key)})")

    if key in type_map and value is not None:
      result[key] = cast_model_value(value, type_map[key], convert_time_to_ca)
    else:
      result[key] = value

  return result


def safe_json_loads(value: str | dict | None, context_label: str = "") -> dict:
  """
  Safely parse a JSON string into a Python dictionary.

  This utility defensively decodes JSON content from sources like database columns,
  user input, or file contents. It handles malformed or null input gracefully and
  guarantees a dictionary result, logging detailed warnings with context if parsing fails.

  Args:
    value (str | dict | None): JSON-formatted string, pre-decoded dict, or None.
      Common inputs include SQLAlchemy model columns (e.g., `model.misc_json`) that
      may contain raw strings or ORM-decoded dicts.
    context_label (str): Optional label for diagnostics/logging.
      Used in log messages to identify which field or source caused a failure.

  Returns:
    dict: Parsed dictionary from the input, or empty dict if input is None, invalid,
      or already a valid dict.

  Raises:
    TypeError: If `value` is not a str, dict, or None.

  Notes:
    - If `value` is already a dict, it is returned unchanged.
    - If `value` is None, empty, or invalid JSON, an empty dict is returned.
    - If decoding fails, a warning is logged including the context_label.

  Example Usage:
    safe_json_loads(model.misc_json, context_label="model.misc_json")
    safe_json_loads(data, context_label="user_profile_json")
  """
  if value is None or (isinstance(value, str) and value.strip() == ""):
    return {}

  if isinstance(value, dict):
    return value

  if not isinstance(value, str):
    raise TypeError(f"Expected str, dict, or None; got {type(value).__name__}")

  try:
    return json.loads(value)
  except json.JSONDecodeError:
    label_msg = f" ({context_label})" if context_label else ""
    logger.warning(f"Corrupt or invalid JSON string encountered{label_msg}; returning empty dict.")
    return {}


def run_diagnostics() -> None:
  """
  Run internal validation for all JSON utilities.

  Tests:
    - Custom serializer/deserializer
    - JSON saving and loading (with and without metadata)
    - Metadata updating
    - File comparison

  Raises:
      Exception: If any test fails.
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
    save_json_safely(data,
                     plain_file,
                     encoding="utf-8",
                     json_options={"indent": 2, "default": json_serializer})

    add_metadata_to_json(plain_file)

    # Compare metadata-enriched files
    compare_json_files(json_file_2, plain_file)

    print("All diagnostics completed successfully.")

  except Exception as e:
    print(f"Diagnostics failed: {e}")
    raise


def extract_id_from_json(json_data: dict,
                         tab_name: str = "Feedback Form",
                         key_name: str = "id_incidence") -> int | None:
  """
  Safely extract a numeric key (like id_incidence) from a specified tab in Excel-parsed JSON.

  Args:
    json_data (dict): JSON dictionary as parsed from the Excel upload.
    tab_name (str, optional): Name of the tab in 'tab_contents'. Defaults to "Feedback Form".
    key_name (str, optional): Key to extract from the tab. Defaults to "id_incidence".

  Returns:
    int | None: Parsed integer value, or None if not found or invalid.

  Notes:
    - Unlike full ingestion, this does not validate schema or write to the DB.
    - Handles string digits and trims whitespace safely.
    - Logs warning if structure is invalid.
  """
  try:
    tab_data = json_data.get("tab_contents", {}).get(tab_name, {})
    val = tab_data.get(key_name)
    if isinstance(val, int):
      return val
    if isinstance(val, str) and val.strip().isdigit():
      return int(val.strip())
  except Exception as e:
    logger.warning(f"Failed to extract key '{key_name}' from tab '{tab_name}': {e}")
  return None


def extract_tab_payload(json_data: dict,
                        tab_name: str = "Feedback Form") -> dict:
  """
  Extract the contents of a specific tab from a parsed Excel JSON structure.

  Args:
    json_data (dict): Parsed JSON dictionary, typically from `json_load_with_meta()`.
    tab_name (str): Tab name whose contents to extract. Defaults to "Feedback Form".

  Returns:
    dict: The dictionary of field keys/values for the specified tab,
          or an empty dict if the tab is missing or malformed.

  Notes:
    - Mirrors the behavior of `extract_id_from_json()` for consistent JSON access.
    - Logs a warning if extraction fails.
    - Safe for use in staging workflows or diff preview logic.
  """
  try:
    return json_data.get("tab_contents", {}).get(tab_name, {})
  except Exception as e:
    logger.warning(f"extract_tab_payload() failed for tab '{tab_name}': {e}")
    return {}


def compute_field_differences(
    new_data: dict,
    existing_data: dict
) -> list[dict]:
  """
  Generate a field-by-field diff between two dictionaries using keys from `new_data`.

  This is useful when comparing a newly staged or submitted JSON payload
  against an existing record (e.g., from the database), where only the
  fields in `new_data` are relevant for comparison.

  Args:
    new_data (dict): The incoming or modified dictionary (e.g., staged JSON).
    existing_data (dict): The reference or baseline dictionary (e.g., DB row).

  Returns:
    list[dict]: List of field diffs, each with:
      - 'key': The dictionary key being compared
      - 'old': The normalized value from `existing_data`
      - 'new': The normalized value from `new_data`
      - 'changed': True if the values differ after normalization
      - 'is_same': True if values are unchanged
      - 'from_upload': Always True, indicating this field came from uploaded JSON
      - 'requires_confirmation': True if the update adds or overwrites non-trivial data

  Notes:
    - Normalization uses `normalize_value()` for consistent formatting,
      especially for empty strings, None, and datetimes.
    - Keys present in `existing_data` but *not* in `new_data` are ignored.
    - A field requires confirmation if it adds or overwrites non-empty data.
  """
  differences = []

  for key in sorted(new_data.keys()):
    new_value = new_data.get(key)
    old_value = existing_data.get(key)
    norm_new = normalize_value(new_value)
    norm_old = normalize_value(old_value)

    is_same = norm_old == norm_new
    requires_confirmation = (
      norm_new not in (None, "", []) and not is_same
    )

    differences.append({
      "key": key,
      "old": norm_old,
      "new": norm_new,
      "changed": not is_same,
      "is_same": is_same,
      "from_upload": True,
      "requires_confirmation": requires_confirmation,
    })

    logger.debug(f"DIFF KEY={key!r} | DB={type(old_value).__name__}:{norm_old!r} "
                 f"| NEW={type(new_value).__name__}:{norm_new!r} "
                 f"| SAME={is_same} | CONFIRM={requires_confirmation}")

  return differences


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
