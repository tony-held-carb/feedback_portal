"""
Module for miscellaneous utility functions and classes.
"""
import traceback

from arb.__get_logger import get_logger

__version__ = "1.0.0"
logger, pp_log = get_logger(__name__, __file__)


def get_nested_value(nested_dict, keys):
  """
  Retrieve the value from a nested dictionary using a sequence of keys.

  Args:
      nested_dict (dict): The dictionary to search.
      keys (list, tuple, or any): A sequence (list or tuple) of keys to navigate through the dictionary,
                                  or a single key for direct access.

  Returns:
      The value found at the specified key path, or raises a KeyError if a key is missing.

  Raises:
      KeyError: If any key in the sequence does not exist in the dictionary.
      TypeError: If a non-dictionary value is encountered before the end of the path.

  Example usage:
      data = {
        "a": {
          "b": {
            "c": 42
          }
        },
        "x": 99
      }

      # Using a sequence of keys
      key_path = ("a", "b", "c")
      result = get_nested_value(data, key_path)
      print(result)  # Output: 42

      # Using a single key
      single_key = "x"
      result = get_nested_value(data, single_key)
      print(result)  # Output: 99
  """
  if not isinstance(keys, (list, tuple)):
    # Single key case
    if keys not in nested_dict:
      raise KeyError(f"Key '{keys}' not found in the dictionary")
    return nested_dict[keys]

  current = nested_dict
  for key in keys:
    if not isinstance(current, dict):
      raise TypeError(f"Expected a dictionary at {key} but found {type(current).__name__}")
    if key not in current:
      raise KeyError(f"Key '{key}' not found in the dictionary")
    current = current[key]
  return current


def ensure_key_value_pair(dict_, default_dict, sub_key):
  """
  Given a dictionary (dict_) that has a dictionary for each of its values,
  ensure that the sub dictionary has the key (key_name).  If it is not present,
  use the default_dict as a lookup to populate the key/value.

  Args:
    dict_ (dict): dictionary with a sub dictionary for each of its values
    default_dict  (dict): lookup to populate missing key/value pairs.
    sub_key (str): key name to that must be present in the value dictionary.
  """
  for key, sub_dict in dict_.items():
    logger.debug(f"{key=}, {sub_dict=}")
    if sub_key not in sub_dict:
      if key in default_dict:
        sub_dict[sub_key] = default_dict[key]
      else:
        raise TypeError(f"{sub_key} is not present in sub dictionaries nor is in the default_dict")


def replace_list_occurrences(list_, lookup_dict) -> None:
  """
  Replace elements of list with replacement values specified in lookup_dict.

  Args:
    list_ (list):
      list that you wish to replace occurrences of elements with replacement values in lookup_dict
    lookup_dict (dict):
      dictionary of replacements as key value pairs of old_value: new_value
  """
  for i in range(len(list_)):
    if list_[i] in lookup_dict:
      list_[i] = lookup_dict[list_[i]]


def args_to_string(args):
  """
  args_to_string is not fully implemented and not in practical use"""
  # logger.debug(f"{args=}")
  if not args:
    return ''
  else:
    args = [str(arg) for arg in args]
    return_string = " " + " ".join(args) + " "
    return return_string


# -----------------------------------------------------------------------------
# Initialize module global values
# -----------------------------------------------------------------------------
def log_error(e):
  """
  Log error and stack traceback.

  Args:
    e (Exception): raised exception

  Notes:
    # todo (consider) making this a 500 internal error page
  """
  # Log the exception
  logger.error(e, exc_info=True)
  # re-raise the error for development
  stack = traceback.extract_stack()
  logger.error(stack)
  raise e
