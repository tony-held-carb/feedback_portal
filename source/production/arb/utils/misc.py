"""
misc.py

Miscellaneous utility functions for common tasks including dictionary traversal,
default injection, argument formatting, exception logging, and safe type casting.

Functions included:
    - get_nested_value: Safely access deeply nested values in a dictionary.
    - ensure_key_value_pair: Add missing keys to sub-dictionaries using defaults.
    - replace_list_occurrences: Modify list elements in-place based on a mapping.
    - args_to_string: Format argument lists into padded strings.
    - log_error: Log full exception tracebacks and re-raise.
    - safe_cast: Convert values to expected types if needed.
    - run_diagnostics: Test suite for all utilities.

Intended Use:
    - Shared helpers for Flask or CLI-based Python applications.
    - Improves code reuse and diagnostic traceability.

Dependencies:
    - Python standard library
    - Logging provided by arb.__get_logger

Version:
    1.0.0
TODO:
    - Consider converting log_error into a structured 500 error response for Flask apps

"""

import traceback
import logging


__version__ = "1.0.0"
logger = logging.getLogger(__name__)
_, pp_log = get_pretty_printer()


def get_nested_value(nested_dict: dict, keys: list | tuple | str) -> object:
  """
  Retrieve a value from a nested dictionary using a key path.

  Args:
      nested_dict (dict): The dictionary to search.
      keys (list | tuple | str): A sequence of keys to traverse the dictionary, or a single key.

  Returns:
      object: The value found at the specified key path.

  Raises:
      KeyError: If a key is missing at any level.
      TypeError: If a non-dictionary value is encountered mid-traversal.

  Examples:
    Input : data = {"a": {"b": {"c": 42}}, "x": 99}, keys = ("a", "b", "c")
    Output: 42

    Input : data = {"a": {"b": {"c": 42}}, "x": 99}, keys = "x"
    Output: 99
  """
  if not isinstance(keys, (list, tuple)):
    # Single key case
    if keys not in nested_dict:
      raise KeyError(f"Key '{keys}' not found in the dictionary")
    return nested_dict[keys]

  current = nested_dict
  for key in keys:
    if not isinstance(current, dict):
      raise TypeError(f"Expected a dictionary at key '{key}', found {type(current).__name__}")
    if key not in current:
      raise KeyError(f"Key '{key}' not found in the dictionary")
    current = current[key]
  return current


def ensure_key_value_pair(dict_: dict[str, dict], default_dict: dict, sub_key: str) -> None:
  """
  Ensure each sub-dictionary in dict_ has a given key, populating it from default_dict if missing.

  Args:
      dict_ (dict[str, dict]): A dictionary whose values are sub-dictionaries.
      default_dict (dict): A lookup dictionary to supply missing key-value pairs.
      sub_key (str): The key that must exist in each sub-dictionary.

  Raises:
      TypeError: If the sub_key is missing, and no fallback is found in default_dict.

  Example:
    Input :
      dict_ = {"a": {"x": 1}, "b": {"x": 2}, "c": {}}
      default_dict = {"c": 99}
      sub_key = "x"
    Output:
      dict_["c"]["x"] == 99
  """
  for key, sub_dict in dict_.items():
    logger.debug(f"{key=}, {sub_dict=}")
    if sub_key not in sub_dict:
      if key in default_dict:
        sub_dict[sub_key] = default_dict[key]
      else:
        raise TypeError(
          f"{sub_key} is not present in sub dictionary for key '{key}' "
          f"and no default provided in default_dict"
        )


def replace_list_occurrences(list_: list, lookup_dict: dict) -> None:
  """
  Replace elements of a list in-place using a lookup dictionary.

  Args:
    list_ (list): The list whose elements may be replaced.
    lookup_dict (dict): A dictionary mapping old values to new values.

  Example:
    Input :
      list_ = ["cat", "dog", "bird"]
      lookup_dict = {"dog": "puppy", "bird": "parrot"}
    Output:
      list_ becomes ['cat', 'puppy', 'parrot']
  """
  for i in range(len(list_)):
    if list_[i] in lookup_dict:
      list_[i] = lookup_dict[list_[i]]


def args_to_string(args: list | tuple | None) -> str:
  """
  Convert a list or tuple of arguments into a single space-separated string with padding.

  Args:
    args (list | tuple | None): Arguments to convert.

  Returns:
    str: Space-separated string representation.

  Example:
    Input : ["--debug", "--log", "file.txt"]
    Output: " --debug --log file.txt "
  """
  if not args:
    return ''
  else:
    args = [str(arg) for arg in args]
    return_string = " " + " ".join(args) + " "
    return return_string


def log_error(e: Exception) -> None:
  """
  Log an exception and its stack trace, then re-raise the exception.

  Args:
      e (Exception): The exception to log.

  Raises:
      Exception: Always re-raises the input exception after logging.

  Notes:
      - Outputs full traceback to logger.
      - Re-raises the original exception.
      - Useful during development or structured exception monitoring.

  TODO:
      Consider wrapping this in Flask to render a 500 error page instead.
  """
  logger.error(e, exc_info=True)
  stack = traceback.extract_stack()
  logger.error(stack)
  raise e


def safe_cast(value, expected_type: type) -> object:
  """
  Cast a value to the expected type only if it's not already of that type.

  Args:
      value (Any): The value to check and potentially cast.
      expected_type (type): The target Python type to cast to.

  Returns:
      object: The original or casted value.

  Raises:
      ValueError: If the cast fails or is inappropriate for the type.
  """

  try:
    if not isinstance(value, expected_type):
      value = expected_type(value)
    return value
  except Exception as e:
    raise ValueError(f"Failed to cast value {value!r} to {expected_type}: {e}")


def run_diagnostics() -> None:
  """
  Run diagnostics to validate functionality of misc.py utilities.

  This includes:
    - Nested dictionary access
    - Default key/value injection into sub-dictionaries
    - In-place replacement of list values
    - Argument string formatting
    - Error logging (non-raising test only)

  """
  print("Running diagnostics for misc.py utilities...")

  # --- Test get_nested_value ---
  test_dict = {"a": {"b": {"c": 42}}, "x": 99}
  assert get_nested_value(test_dict, ("a", "b", "c")) == 42, "Nested dict access failed"
  assert get_nested_value(test_dict, "x") == 99, "Single key access failed"

  # --- Test ensure_key_value_pair ---
  dict_with_sub = {"apple": {"color": "red"}, "banana": {}}
  defaults = {"banana": "yellow"}
  ensure_key_value_pair(dict_with_sub, defaults, "color")
  assert dict_with_sub["banana"]["color"] == "yellow", "Default insertion failed"

  # --- Test replace_list_occurrences ---
  items = ["dog", "cat", "parrot"]
  replace_list_occurrences(items, {"dog": "puppy", "parrot": "bird"})
  assert items == ["puppy", "cat", "bird"], "List replacement failed"

  # --- Test args_to_string ---
  assert args_to_string(["--a", "--b", "value"]) == " --a --b value ", "args_to_string failed"
  assert args_to_string(None) == "", "args_to_string empty case failed"

  # --- Test log_error (without raising) ---
  try:
    try:
      raise ValueError("Test exception for log_error")
    except Exception as e:
      # Simulate logging only — comment out re-raise
      logger.error(e, exc_info=True)
  except Exception:
    assert False, "log_error should not re-raise during diagnostics"

  print("All diagnostics passed.")


if __name__ == "__main__":
  run_diagnostics()
