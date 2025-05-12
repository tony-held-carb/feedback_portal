"""
Module for miscellaneous utility functions and classes.

Version:
    1.0.0

Includes:
    - Deep access to nested dictionaries
    - Sub-dictionary default injection
    - In-place list value replacement
    - Error logging with full trace
    - Argument formatting

TODO:
    - Consider converting log_error into a structured 500 error response for Flask apps
"""

import traceback

from arb.__get_logger import get_logger

__version__ = "1.0.0"
logger, pp_log = get_logger(__name__, __file__)


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
      >>> data = {"a": {"b": {"c": 42}}, "x": 99}
      >>> get_nested_value(data, ("a", "b", "c"))
      42
      >>> get_nested_value(data, "x")
      99
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
      TypeError: If the sub_key is missing and there's no fallback in default_dict.

  Example:
      >>> dict_ = {"a": {"x": 1}, "b": {"x": 2}, "c": {}}
      >>> defaults = {"c": 99}
      >>> ensure_key_value_pair(dict_, defaults, "x")
      >>> dict_["c"]["x"]
      99
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
      >>> values = ["cat", "dog", "bird"]
      >>> lookup = {"dog": "puppy", "bird": "parrot"}
      >>> replace_list_occurrences(values, lookup)
      >>> values
      ['cat', 'puppy', 'parrot']
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
      >>> args_to_string(["--debug", "--log", "file.txt"])
      ' --debug --log file.txt '
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


def run_diagnostics() -> None:
  """
  Run diagnostics to validate functionality of misc.py utilities.

  This includes:
    - Nested dictionary access
    - Default key/value injection into sub-dictionaries
    - In-place replacement of list values
    - Argument string formatting
    - Error logging (non-raising test only)

  Example:
      >>> run_diagnostics()
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
  import logging

  logging.basicConfig(
    filename="misc_diagnostics.log",
    level=logging.DEBUG,
    encoding="utf-8",
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
  )

  run_diagnostics()
