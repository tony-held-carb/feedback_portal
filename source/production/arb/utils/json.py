"""
JSON utilities for the ARB Feedback Portal.

This module centralizes JSON serialization, deserialization, metadata handling, and diagnostics for
ARB portal utilities. It ensures consistent handling of ISO 8601 datetimes, decimals, and custom types,
and provides helpers for file-based workflows, WTForms integration, and contract-compliant value
normalization.

Features:
- Custom serialization/deserialization for datetime, decimal, and class/type objects
- Metadata support for enhanced JSON files (with _data_ and _metadata_ fields)
- File-based diagnostics, JSON comparison, and safe file I/O
- WTForms integration for extracting and casting form data
- Value normalization and diffing for ingestion and audit workflows

Contract notes:
- Emphasizes ISO 8601 datetime formats and Pacific Time handling where required
- Designed for robust, structured JSON handling across ARB portal utilities
- Logging is used for diagnostics, warnings, and error reporting

Extensible for new types and workflows as the portal evolves.
"""

import datetime
import decimal
import json
import logging
import pathlib
from typing import Any
from zoneinfo import ZoneInfo

from wtforms import BooleanField, DateTimeField, DecimalField, IntegerField, SelectField

from arb.utils.date_and_time import ca_naive_datetime_to_utc_datetime, iso_str_to_utc_datetime, utc_datetime_to_ca_naive_datetime
from arb.utils.diagnostics import compare_dicts

__version__ = "1.0.0"

from arb.utils.misc import safe_cast
from arb.utils.io_wrappers import save_json_safely, read_json_file

logger = logging.getLogger(__name__)


# todo - integrate new json techniques to the website,
#       make sure time are handled using the new time stamps iso strings and native pacific system

def json_serializer(obj: object) -> dict:
  """
  Custom JSON serializer for objects not natively serializable by `json.dump`.

  Args:
    obj (object): The object to serialize. Supported: datetime, decimal, class/type objects. If None, raises TypeError.

  Returns:
    dict: A JSON-compatible dictionary representation of the object.

  Raises:
    TypeError: If the object type is unsupported or if obj is None.

  Examples:
    Input : datetime.datetime.now()
    Output: {"__type__": "datetime.datetime", "value": "2025-07-04T12:34:56.789012"}
    Input : decimal.Decimal("1.23")
    Output: {"__type__": "decimal.Decimal", "value": "1.23"}

  Notes:
    - Only supports specific types; all others raise TypeError.
    - If obj is None, raises TypeError.
  """
  if isinstance(obj, type):
    return {"__class__": obj.__name__, "__module__": obj.__module__}
  elif isinstance(obj, datetime.datetime):
    return {"__type__": "datetime.datetime", "value": obj.isoformat()}
  elif isinstance(obj, decimal.Decimal):
    return {"__type__": "decimal.Decimal", "value": str(obj)}

  raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def json_deserializer(obj: dict[str, Any]) -> Any:
  """
  Custom JSON deserializer for class/type representations created by `json_serializer`.

  Args:
    obj (dict[str, Any]): Dictionary object from JSON with special tags for known types. If None, returns None.

  Returns:
    Any: Reconstructed Python object (datetime, decimal, or class/type), or original dict if no tags found.

  Raises:
    TypeError: If the type tag is unknown or unsupported.

  Examples:
    Input : {"__type__": "datetime.datetime", "value": "2025-07-04T12:34:56.789012"}
    Output: datetime.datetime(2025, 7, 4, 12, 34, 56, 789012)
    Input : {"__class__": "int", "__module__": "builtins"}
    Output: int

  Notes:
    - If obj is None, returns None.
    - If no recognized tags, returns obj unchanged.
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
    file_path (str | Path): Path to write the JSON file. If None or empty, raises ValueError.
    data (object): Data to serialize and write. If None, writes 'null' to the file.
    json_options (dict | None): Options to pass to `json.dump` (e.g., indent, default).

  Returns:
    None

  Raises:
    ValueError: If file_path is None or empty.
    OSError: If the file cannot be written.

  Examples:
    Input : "output.json", {"x": decimal.Decimal("1.23")}
    Output: Creates a JSON file with serialized data at the given path

  Notes:
    - If file_path is None or empty, raises ValueError.
    - If data is None, writes 'null' to the file.
  """
  logger.debug(f"json_save() called with {file_path=}, {json_options=}, {data=}")

  if not file_path:
    raise ValueError("file_path must not be None or empty.")
  file_path = pathlib.Path(file_path)

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
  Save data with metadata to a JSON file under special keys (_data_, _metadata_).

  Args:
    file_path (str | Path): Output JSON file path. If None or empty, raises ValueError.
    data (object): Primary data to store under "_data_". If None, writes 'null' under "_data_".
    metadata (dict | None): Optional metadata under "_metadata_". If None, auto-generated.
    json_options (dict | None): Options for `json.dump`.

  Returns:
    None

  Raises:
    ValueError: If file_path is None or empty.
    OSError: If the file cannot be written.

  Examples:
    Input : "log.json", {"key": "value"}, metadata={"source": "generated"}
    Output: Writes JSON with _data_ and _metadata_ fields

  Notes:
    - If metadata is None, a default metadata dict is generated.
    - If file_path is None or empty, raises ValueError.
  """
  logger.debug(f"json_save_with_meta() called with {file_path=}, {json_options=}, {metadata=}, {data=}")

  if not file_path:
    raise ValueError("file_path must not be None or empty.")
  file_path = pathlib.Path(file_path)

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
    file_path (str | Path): Path to the JSON file. If None or empty, raises ValueError.
    json_options (dict | None): Optional options passed to `json.load`.

  Returns:
    object: Deserialized Python object (dict, list, etc.).

  Raises:
    ValueError: If file_path is None or empty.
    FileNotFoundError: If the file does not exist.
    json.JSONDecodeError: If the file is not valid JSON.

  Examples:
    Input : "data.json"
    Output: Deserialized Python object from JSON

  Notes:
    - Uses utf-8-sig encoding to handle BOM if present.
    - If the file is not valid JSON, an exception is raised.
    - If file_path is None or empty, raises ValueError.
  """
  logger.debug(f"json_load() called with {file_path=}, {json_options=}")

  file_path = pathlib.Path(file_path)

  if json_options is None:
    json_options = {"object_hook": json_deserializer}

  return read_json_file(file_path, encoding="utf-8-sig", json_options=json_options)


def json_load_with_meta(file_path: str | pathlib.Path,
                        json_options: dict | None = None) -> tuple[Any, dict]:
  """
  Load a JSON file and return both data and metadata if present.

  Args:
    file_path (str | Path): Path to the JSON file. If None or empty, raises ValueError.
    json_options (dict | None): Optional options passed to `json.load`.

  Returns:
    tuple:
      - Any: Deserialized data from "_data_" (or the entire file if "_data_" is not present).
      - dict: Deserialized metadata from "_metadata_" (or empty dict if not present).

  Raises:
    ValueError: If file_path is None or empty.
    FileNotFoundError: If the file does not exist.
    json.JSONDecodeError: If the file is not valid JSON.

  Examples:
    Input : "example.json"
    Output: tuple (data, metadata) extracted from the file

  Notes:
    - If the JSON file is a dictionary with a key _data_, then the _data_ and _metadata_ (if possible) will be extracted. Otherwise, the data is assumed to be the entire file contents and metadata is an empty dict.
    - If file_path is None or empty, raises ValueError.
  """
  logger.debug(f"json_load_with_meta() called with {file_path=}, {json_options=}")

  file_path = pathlib.Path(file_path)

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
    file_name_in (str | Path): Input JSON file path. If None or empty, raises ValueError.
    file_name_out (str | Path | None): Output file path. If None, overwrites input. If empty, raises ValueError.

  Returns:
    None

  Raises:
    ValueError: If file_name_in is None or empty, or if file_name_out is empty.
    FileNotFoundError: If the input file does not exist.
    OSError: If the file cannot be written.

  Examples:
    Input : "schema.json"
    Output: Adds metadata and writes back to same file
    Input : "input.json", "output.json"
    Output: Adds metadata and writes to output.json

  Notes:
    - If file_name_out is None, input file is overwritten.
    - If file_name_in or file_name_out is empty, raises ValueError.
  """
  logger.debug(f"add_metadata_to_json() called with {file_name_in=}, {file_name_out=}")

  file_name_in = pathlib.Path(file_name_in)
  if file_name_out is not None:
    file_name_out = pathlib.Path(file_name_out)
  else:
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
    file_name_1 (str | Path): Path to the first file. If None or empty, raises ValueError.
    file_name_2 (str | Path): Path to the second file. If None or empty, raises ValueError.

  Returns:
    None

  Logs:
    Differences or matches are logged at debug level.

  Raises:
    ValueError: If file_name_1 or file_name_2 is None or empty.
    FileNotFoundError: If either file does not exist.
    json.JSONDecodeError: If either file is not valid JSON.

  Examples:
    Input : "old.json", "new.json"
    Output: Logs any differences or confirms matches

  Notes:
    - If either file is missing or invalid, raises an exception.
    - Only logs differences; does not return a value.
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
) -> Any:
  """
  Cast a stringified JSON value into a Python object of the expected type.

  Args:
    value (str): Input value to cast. If None, raises ValueError.
    value_type (type): Python type to cast to (str, int, float, bool, datetime, decimal). If None, raises ValueError.
    convert_time_to_ca (bool): If True, convert UTC to California naive datetime.

  Returns:
    Any: Value converted to the target Python type.

  Raises:
    ValueError: If the value cannot be cast to the given type, type is unsupported, or value_type is None.

  Examples:
    Input : "2025-01-01T12:00:00Z", datetime.datetime
    Output: datetime.datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
    Input : "123.45", decimal.Decimal
    Output: decimal.Decimal("123.45")
    Input : "true", bool
    Output: True

  Notes:
    - If value_type is None, raises ValueError.
    - If value is None, raises ValueError.
    - If type is unsupported, raises ValueError.
  """
  # todo - datetime - may need to update
  try:
    if value_type == str:
      # No need to cast a string
      return value
    elif value_type in [bool, int, float]:
      return value_type(value)
    elif value_type == datetime.datetime:
      dt = iso_str_to_utc_datetime(value)
      return utc_datetime_to_ca_naive_datetime(dt) if convert_time_to_ca else dt
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
    wtform (FlaskForm): WTForms instance. Must not be None.

  Returns:
    tuple:
      - dict[str, type]: Field name to type mapping for deserialization.
      - dict[str, object]: Field name to current value mapping (may include 'Please Select').

  Raises:
    ValueError: If wtform is None or does not have _fields attribute.

  Examples:
    Input : form (WTForms instance)
    Output: (type_map, field_data) where type_map is a dict of field types and field_data is a dict of field values

  Notes:
    - If wtform is None or invalid, raises ValueError.
    - 'Please Select' is a valid value for SelectField.
  """
  if wtform is None or not hasattr(wtform, '_fields'):
    raise ValueError("wtform must have a _fields attribute")
  type_map = {}
  field_data = {}

  for name, field in wtform._fields.items():
    value = field.data
    field_data[name] = value
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
    input_dict (dict): Original dictionary to process. If None, raises ValueError.
    type_map (dict[str, type] | None): Optional field-to-type map for casting. If not provided, no casting is performed.
    convert_time_to_ca (bool): Convert datetimes to CA time before serialization.

  Returns:
    dict: Dictionary with all values JSON-serializable.

  Raises:
    ValueError: If input_dict is None.

  Examples:
    Input : {"amount": decimal.Decimal("1.23"), "date": datetime.datetime(2025, 7, 4, 12, 0)}
    Output: {"amount": "1.23", "date": "2025-07-04T12:00:00"}

  Notes:
    - If input_dict is None, raises ValueError.
    - If type_map is provided, values are cast to the specified types before serialization.
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
        value = ca_naive_datetime_to_utc_datetime(value)
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
  Deserialize a dictionary of raw values using a type map.

  Args:
    input_dict (dict): Dictionary of raw values. If None, raises ValueError.
    type_map (dict[str, type]): Field-to-type mapping for deserialization. If None or empty, no casting is performed.
    convert_time_to_ca (bool): If True, converts datetime to CA time.

  Returns:
    dict: Fully deserialized dictionary.

  Raises:
    TypeError: If any key is not a string.
    ValueError: If value casting fails for a key or if input_dict is None.

  Examples:
    Input : {"dt": "2025-01-01T12:00:00Z"}, {"dt": datetime.datetime}
    Output: {"dt": datetime.datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))}

  Notes:
    - If input_dict is None, raises ValueError.
    - If type_map is None or empty, no casting is performed.
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

  Args:
    value (str | dict | None): JSON-formatted string, pre-decoded dict, or None. If not str, dict, or None, raises TypeError.
    context_label (str): Optional label for diagnostics/logging.

  Returns:
    dict: Parsed dictionary from the input, or empty dict if input is None, invalid, or already a valid dict.

  Raises:
    TypeError: If `value` is not a str, dict, or None.

  Examples:
    Input : '{"a": 1, "b": 2}'
    Output: {"a": 1, "b": 2}
    Input : {"a": 1, "b": 2}
    Output: {"a": 1, "b": 2}
    Input : None
    Output: {}
    Input : ""
    Output: {}
    Input : "not valid json"
    Output: {}

  Notes:
    - If `value` is already a dict, it is returned unchanged.
    - If `value` is None, empty, or invalid JSON, an empty dict is returned.
    - If decoding fails, a warning is logged including the context_label.
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


def extract_id_from_json(json_data: dict,
                         tab_name: str = "Feedback Form",
                         key_name: str = "id_incidence") -> int | None:
  """
  Safely extract a numeric key (like id_incidence) from a specified tab in Excel-parsed JSON.

  Args:
    json_data (dict): JSON dictionary as parsed from the Excel upload. If None, returns None.
    tab_name (str, optional): Name of the tab in 'tab_contents'. Defaults to "Feedback Form". If None or empty, uses default.
    key_name (str, optional): Key to extract from the tab. Defaults to "id_incidence". If None or empty, uses default.

  Returns:
    int | None: Parsed integer value, or None if not found or invalid.

  Examples:
    Input : {"tab_contents": {"Feedback Form": {"id_incidence": "123"}}}, tab_name="Feedback Form", key_name="id_incidence"
    Output: 123
    Input : {"tab_contents": {"Feedback Form": {}}}, tab_name="Feedback Form", key_name="id_incidence"
    Output: None

  Notes:
    - Unlike full ingestion, this does not validate schema or write to the DB.
    - Handles string digits and trims whitespace safely.
    - Logs warning if structure is invalid.
    - If json_data is None, returns None.
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
    json_data (dict): Parsed JSON dictionary, typically from `json_load_with_meta()`. If None, returns empty dict.
    tab_name (str): Tab name whose contents to extract. Defaults to "Feedback Form". If None or empty, uses default.

  Returns:
    dict: The dictionary of field keys/values for the specified tab, or an empty dict if the tab is missing or malformed.

  Examples:
    Input : {"tab_contents": {"Feedback Form": {"field1": "value1"}}}, tab_name="Feedback Form"
    Output: {"field1": "value1"}
    Input : {"tab_contents": {}}, tab_name="Feedback Form"
    Output: {}
    Input : None, tab_name="Feedback Form"
    Output: {}

  Notes:
    - If json_data is None, returns empty dict.
    - If tab_name is None or empty, uses default.
    - If the tab is missing or malformed, returns empty dict.
  """
  try:
    return json_data.get("tab_contents", {}).get(tab_name, {})
  except Exception as e:
    logger.warning(f"extract_tab_payload() failed for tab '{tab_name}': {e}")
    return {}


def normalize_value(val: Any) -> str:
  """
  Normalize a value for string-based diffing or comparison.

  Args:
    val: Value to normalize (any type). If None or empty string, returns "". If datetime, returns ISO string.

  Returns:
    str: Normalized string value. None and empty string become "". Datetimes are ISO strings.

  Examples:
    Input : None
    Output: ""
    Input : ""
    Output: ""
    Input : datetime.datetime(2025, 1, 1, 12, 0)
    Output: "2025-01-01T12:00:00"
    Input : 123
    Output: "123"

  Notes:
    - None and empty strings ("") are treated identically, returning "".
    - Naive datetime values are assumed to be in California time and converted to UTC.
    - All other types are stringified using str(val).
    - Ensures fields that were previously None but now filled with an empty string (or vice versa) are not falsely flagged as changed. Datetime normalization is contract-compliant.
  """
  from datetime import datetime
  from arb.utils.date_and_time import is_datetime_naive, ca_naive_datetime_to_utc_datetime
  if val is None or val == "":
    return ""
  if isinstance(val, datetime):
    if is_datetime_naive(val):
      val = ca_naive_datetime_to_utc_datetime(val)
    return val.isoformat()
  return str(val)


def compute_field_differences(
    new_data: dict,
    existing_data: dict
) -> list[dict]:
  """
  Generate a field-by-field diff between two dictionaries using keys from `new_data`.

  Args:
    new_data (dict): The incoming or modified dictionary (e.g., staged JSON). If None, treated as empty dict.
    existing_data (dict): The reference or baseline dictionary (e.g., DB row). If None, treated as empty dict.

  Returns:
    list[dict]: List of field diffs, each with:
      - 'key': The dictionary key being compared
      - 'old': The normalized value from `existing_data`
      - 'new': The normalized value from `new_data`
      - 'changed': True if the values differ after normalization
      - 'is_same': True if values are unchanged
      - 'from_upload': Always True, indicating this field came from uploaded JSON
      - 'requires_confirmation': True if the update adds or overwrites non-trivial data

  Examples:
    Input : {"a": 1}, {"a": 2}
    Output: [{"key": "a", "old": "2", "new": "1", "changed": True, ...}]
    Input : {"a": None}, {"a": ""}
    Output: [{"key": "a", "old": "", "new": "", "changed": False, ...}]

  Notes:
    - Normalization uses `normalize_value()` for consistent formatting, especially for empty strings, None, and datetimes.
    - Keys present in `existing_data` but *not* in `new_data` are ignored.
    - A field requires confirmation if it adds or overwrites non-empty data.
    - If either input dict is None, it is treated as empty dict.
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
