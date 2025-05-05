"""
Module for diagnostic related functions and classes.
"""
import pprint

from bs4 import BeautifulSoup

from arb.__get_logger import get_logger

__version__ = "1.0.0"
logger, pp_log = get_logger(__name__, __file__)


def obj_diagnostics(obj,
                    include_hidden=False,
                    include_functions=False,
                    message=None):
  """
  Log diagnostics about an object for diagnostic purposes.

  Args:
    obj (object): object to diagnose
    include_hidden (bool): if True, include hidden fields in diagnostics
    include_functions (bool): if True, include function fields in diagnostics
    message (str): message to print before diagnostics

  Returns (None):

  """
  logger.debug(f"Diagnostics for: {obj}")
  if message:
    logger.debug(f"{message=}")

  for attr_name in dir(obj):
    attr_value = getattr(obj, attr_name)
    if not attr_name.startswith('_') or include_hidden:
      if callable(attr_value):
        if include_functions:
          logger.debug(f"{attr_name}(): is function")
      else:
        logger.debug(f"{attr_name} {type(attr_value)}:\n\t {attr_value}")


def list_differences(iterable_01,
                     iterable_02,
                     iterable_01_name="List 1",
                     iterable_02_name="List 2",
                     print_warning=False):
  """
  Find the items in iterable_01 that are not in iterable_02 and
  the items in iterable_02 that are not in iterable_01.

  Args:
    iterable_01 (list|dict):
    iterable_02 (list|dict):
    iterable_01_name (str): name of iterable_01 (for diagnostic print statements)
    iterable_02_name (str): name of iterable_02 (for diagnostic print statements)
    print_warning (bool): True if you wish to print diagnostic warnings if iterables are different

  Returns (list, list): in_iterable_1_only, in_iterable_2_only
  """
  in_iterable_1_only = [x for x in iterable_01 if x not in iterable_02]
  in_iterable_2_only = [x for x in iterable_02 if x not in iterable_01]

  if print_warning:
    if in_iterable_1_only:
      logger.warning(
        f"Warning: {iterable_01_name} has {len(in_iterable_1_only)} item(s) not in {iterable_02_name}: \n\t{in_iterable_1_only}")
    if in_iterable_2_only:
      logger.warning(
        f"Warning: {iterable_02_name} has {len(in_iterable_2_only)} item(s) not in {iterable_01_name}: \n\t{in_iterable_2_only}")

  return in_iterable_1_only, in_iterable_2_only


def diag_recursive(x, depth=0, index=0):
  """
  Log diagnostic information about a variable for debugging purposes.
  If the item is a non-string iterable, this function will be called recursively.

  Args:
    x (Iterable|object):  Variable of interest for diagnostic information.
    depth (int): Used to indicate recursion depth.
    index (int): Used to indicate index of an enumeration.
  """
  indent = ' ' * 3 * depth
  if depth == 0:
    logger.debug(f"diag_recursive diagnostics called\n{'-' * 120}")
    logger.debug(f"Type: {type(x)}, Value: {x}")
  else:
    logger.debug(f"{indent} Depth: {depth}, Index: {index}, Type: {type(x)}, Value: {x}")

  # Iterate if possible (except strings)
  if not isinstance(x, str):
    try:
      for i, y in enumerate(x):
        diag_recursive(y, depth + 1, index=i)
    except TypeError:
      pass


def dict_to_str(x, depth=0):
  """
  Output a dictionary to a formatted string for diagnostic information.
  Similar to pretty print, but each line only has one entry

  Args:
    x (dict):  dict interest for diagnostic information.
    depth (int): Used to indicate recursion depth.
  """
  msg = ""
  indent = ' ' * 3 * depth

  for k, v in x.items():
    msg += f"{indent}{k}:\n"
    if isinstance(v, dict):
      msg += dict_to_str(v, depth=depth + 1)
    else:
      msg += f"   {indent}{v}\n"

  return msg


def obj_to_html(obj):
  """
  Convert a python object to an HTML string suitable for web-page diagnostics.

  Args:
    obj: python object to deserialize into html string

  Returns (str): html string representation of object

  Notes:
    * The string will contain html tags that jinja will strip out if you don't mark the variable as safe.
    * Example usage retaining html tags:
        {% if result is defined %}
          {{ result|safe }}     <--- safe allows html tags to persist rather than be stripped
        {% endif %}
  """
  # Pretty print the data to create an indented string
  pp = pprint.PrettyPrinter(indent=4, width=200)
  formatted_data = pp.pformat(obj)

  # Use BeautifulSoup to convert indented string into a formated html string
  soup = BeautifulSoup("<pre></pre>", "html.parser")
  soup.pre.string = formatted_data

  result = soup.prettify()
  return result


def compare_dicts(dict1: dict,
                  dict2: dict,
                  dict1_name=None,
                  dict2_name=None,
                  ) -> bool:
  """
  Compares two dictionaries for equality and prints diagnostics for differing key-value pairs.

  This function checks if two dictionaries are equal by comparing their keys and corresponding
  values. If there are any differences, it prints diagnostic messages highlighting:
  - Keys present in one dictionary but not the other.
  - Keys with differing values.

  Args:
      dict1 (dict): The first dictionary to compare.
      dict2 (dict): The second dictionary to compare.
      dict1_name (str): Name of the first dictionary to compare.
      dict2_name (str): Name of the second dictionary to compare.

  Returns:
      bool: True if the dictionaries are equal, False otherwise.

  Examples:
        dict1 = {"a": 1, "b": 2, "c": 3}
        dict2 = {"a": 1, "b": 4, "d": 5}
        compare_dicts(dict1, dict2)
      Key differences:
      - In dict1 but not in dict2: {'c'}
      - In dict2 but not in dict1: {'d'}
      Value differences:
      - Key: 'b', dict1: 2, dict2: 4
      False
  """
  if dict1_name is None:
    dict1_name = "dict_1"
  if dict2_name is None:
    dict2_name = "dict_2"
  logger.debug(f"compare_dicts called to compare {dict1_name} with {dict2_name}")

  # Keys present in one dictionary but not the other
  keys_in_dict1_not_in_dict2 = set(dict1.keys()) - set(dict2.keys())
  keys_in_dict2_not_in_dict1 = set(dict2.keys()) - set(dict1.keys())

  # Keys with differing values
  differing_values = {
    key: (dict1[key], dict2[key])
    for key in dict1.keys() & dict2.keys()
    if dict1[key] != dict2[key]
  }

  # Print diagnostics
  if keys_in_dict1_not_in_dict2 or keys_in_dict2_not_in_dict1 or differing_values:
    logger.debug("Key differences:")
    if keys_in_dict1_not_in_dict2:
      logger.debug(f"- In {dict1_name} but not in {dict2_name}: {sorted(keys_in_dict1_not_in_dict2)}")
    if keys_in_dict2_not_in_dict1:
      logger.debug(f"- In {dict2_name} but not in {dict1_name}: {sorted(keys_in_dict2_not_in_dict1)}")

    if differing_values:
      logger.debug("Value differences:")
      for key, (value1, value2) in dict(sorted(differing_values.items())).items():
        logger.debug(f"- Key: '{key}', {dict1_name}: {value1}, {dict2_name}: {value2}")

    return False

  return True
