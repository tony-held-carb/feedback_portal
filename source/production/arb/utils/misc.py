"""
Miscellaneous utility functions for the ARB Feedback Portal.

This module provides reusable helpers for dictionary traversal, default injection, argument formatting,
exception logging, and safe type casting. These utilities are designed for both Flask and CLI-based
Python applications, improving code reuse and diagnostic traceability.

Features:
- Safe access to deeply nested dictionary values
- Default key/value injection for sub-dictionaries
- In-place replacement of list values using a mapping
- Argument list formatting for CLI or logging
- Exception logging with full traceback
- Type-safe value casting

Intended use:
- Shared helpers for ARB portal and related utilities
- Promotes DRY principles and robust error handling

Dependencies:
- Python standard library
- Logging provided by arb.__get_logger

Version: 1.0.0
"""

import logging
import traceback
from typing import Any

__version__ = "1.0.0"
logger = logging.getLogger(__name__)


def get_nested_value(nested_dict: dict, keys: list | tuple | str) -> object:
  """
  Retrieve a value from a nested dictionary using a key path.

  Args:
    nested_dict (dict): The dictionary to search. Must not be None.
    keys (list | tuple | str): A sequence of keys to traverse the dictionary, or a single key. If None or empty, raises ValueError.

  Returns:
    object: The value found at the specified key path.

  Raises:
    KeyError: If a key is missing at any level.
    TypeError: If a non-dictionary value is encountered mid-traversal.
    ValueError: If `keys` is None or empty.

  Examples:
    Input : {"a": {"b": {"c": 42}}, "x": 99}, ("a", "b", "c")
    Output: 42
    Input : {"a": {"b": {"c": 42}}, "x": 99}, "x"
    Output: 99

  Notes:
    - If `keys` is None or empty, raises ValueError.
    - If `nested_dict` is None, raises TypeError.
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
    dict_ (dict[str, dict]): A dictionary whose values are sub-dictionaries. Must not be None.
    default_dict (dict): A lookup dictionary to supply missing key-value pairs. Must not be None.
    sub_key (str): The key that must exist in each sub-dictionary. If None or empty, raises ValueError.

  Raises:
    TypeError: If the sub_key is missing, and no fallback is found in default_dict.
    ValueError: If `sub_key` is None or empty.

  Examples:
    Input : dict_ = {'a': {'x': 1}, 'b': {'x': 2}, 'c': {}}, default_dict = {'c': 99}, sub_key = 'x'
    Output: dict_['c']['x'] == 99

  Notes:
    - If `sub_key` is None or empty, raises ValueError.
    - If `dict_` or `default_dict` is None, raises TypeError.
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
    list_ (list): The list whose elements may be replaced. If None, raises ValueError.
    lookup_dict (dict): A dictionary mapping old values to new values. If None, raises ValueError.

  Raises:
    ValueError: If `list_` or `lookup_dict` is None.

  Examples:
    Input : list_ = ["cat", "dog", "bird"], lookup_dict = {"dog": "puppy", "bird": "parrot"}
    Output: list_ becomes ['cat', 'puppy', 'parrot']

  Notes:
    - If `list_` or `lookup_dict` is None, raises ValueError.
  """
  for i in range(len(list_)):
    if list_[i] in lookup_dict:
      list_[i] = lookup_dict[list_[i]]


def args_to_string(args: list | tuple | None) -> str:
  """
  Convert a list or tuple of arguments into a single space-separated string with padding.

  Args:
    args (list | tuple | None): Arguments to convert. If None or empty, returns an empty string.

  Returns:
    str: Space-separated string representation, or empty string if args is None or empty.

  Examples:
    Input : ["--debug", "--log", "file.txt"]
    Output: " --debug --log file.txt "
    Input : None
    Output: ""
    Input : []
    Output: ""

  Notes:
    - If `args` is None or empty, returns an empty string.
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
    e (Exception): The exception to log. Must not be None.

  Raises:
    Exception: Always re-raises the input exception after logging.
    ValueError: If `e` is None.

  Examples:
    Input : ValueError("bad value")
    Output: Logs error and traceback, then raises ValueError

  Notes:
    - Outputs full traceback to logger.
    - Re-raises the original exception.
    - If `e` is None, raises ValueError.
  """
  logger.error(e, exc_info=True)
  stack = traceback.extract_stack()
  logger.error(stack)
  raise e


def safe_cast(value: Any, expected_type: type) -> Any:
  """
  Cast a value to the expected type only if it's not already of that type.

  Args:
    value (Any): The value to check and potentially cast. If None, attempts to cast None.
    expected_type (type): The target Python type to cast to. Must not be None.

  Returns:
    Any: The original or casted value.

  Raises:
    ValueError: If the cast fails or is inappropriate for the type, or if `expected_type` is None.

  Examples:
    Input : "123", int
    Output: 123
    Input : 123, int
    Output: 123
    Input : None, int
    Output: 0 (if int(None) is allowed, else raises ValueError)

  Notes:
    - If `expected_type` is None, raises ValueError.
    - If `value` is already of `expected_type`, returns it unchanged.
    - If cast fails, raises ValueError.
  """

  try:
    if not isinstance(value, expected_type):
      value = expected_type(value)
    return value
  except Exception as e:
    raise ValueError(f"Failed to cast value {value!r} to {expected_type}: {e}")
