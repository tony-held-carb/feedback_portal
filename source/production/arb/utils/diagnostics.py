"""
Diagnostic utilities for inspecting and logging Python objects.

Provides:
- Object introspection for development/debugging
- Attribute/value logging (including hidden and callable members)
- Dictionary comparisons and formatting
- Recursive HTML-safe rendering of complex data structures
- Integration with Flask for developer-oriented diagnostics

Intended primarily for use in debug environments, template rendering,
or ad-hoc inspection of application state during development.
"""

import logging
import pprint

from bs4 import BeautifulSoup
from typing import Any

__version__ = "1.0.0"
logger = logging.getLogger(__name__)


def obj_diagnostics(obj: Any,
                    include_hidden: bool = False,
                    include_functions: bool = False,
                    message: str | None = None) -> None:
  """
  Log detailed diagnostics about an object's attributes and values.

  Args:
    obj (Any): The object to inspect. If None, logs 'None' and returns.
    include_hidden (bool): Whether to include private attributes (starting with `_`).
    include_functions (bool): Whether to include methods or callable attributes.
    message (str | None): Optional prefix message to label the diagnostic output.

  Returns:
    None

  Examples:
    Input : obj={'a': 1, 'b': 2}, include_hidden=False, include_functions=False
    Output: Logs all public attributes and their values
    Input : obj=None
    Output: Logs 'None' and returns

  Notes:
    - If `obj` is None, logs 'None' and returns.
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
        logger.debug(f"{attr_name} {type(attr_value)}:\t {attr_value}")


def list_differences(iterable_01: list | dict,
                     iterable_02: list | dict,
                     iterable_01_name: str = "List 1",
                     iterable_02_name: str = "List 2",
                     print_warning: bool = False) -> tuple[list, list]:
  """
  Identify differences between two iterable objects (list or dict).

  Args:
    iterable_01 (list | dict): First iterable object to compare. If None, treated as empty.
    iterable_02 (list | dict): Second iterable object to compare. If None, treated as empty.
    iterable_01_name (str): Label for the first iterable in log messages.
    iterable_02_name (str): Label for the second iterable in log messages.
    print_warning (bool): If True, log warnings for non-overlapping items.

  Returns:
    tuple[list, list]:
      - Items in `iterable_01` but not in `iterable_02`
      - Items in `iterable_02` but not in `iterable_01`

  Examples:
    Input : ["a", "b"], ["b", "c"]
    Output: (["a"], ["c"])
    Input : None, ["b", "c"]
    Output: ([], ["b", "c"])
    Input : ["a", "b"], None
    Output: (["a", "b"], [])

  Notes:
    - If either iterable is None, it is treated as an empty list/dict.
  """
  if iterable_01 is None:
    iterable_01 = []
  if iterable_02 is None:
    iterable_02 = []
  in_iterable_1_only = [x for x in iterable_01 if x not in iterable_02]
  in_iterable_2_only = [x for x in iterable_02 if x not in iterable_01]

  if print_warning:
    if in_iterable_1_only:
      logger.warning(
        f"Warning: {iterable_01_name} has {len(in_iterable_1_only)} item(s) not in {iterable_02_name}:\t{in_iterable_1_only}")
    if in_iterable_2_only:
      logger.warning(
        f"Warning: {iterable_02_name} has {len(in_iterable_2_only)} item(s) not in {iterable_01_name}:\t{in_iterable_2_only}")

  return in_iterable_1_only, in_iterable_2_only


def diag_recursive(x: object, depth: int = 0, index: int = 0) -> None:
  """
  Recursively log the structure and values of a nested iterable.

  Args:
    x (object): Input object to inspect. If None, logs and returns.
    depth (int): Current recursion depth.
    index (int): Index at the current level (if applicable).

  Returns:
    None

  Examples:
    Input : [[1, 2], [3, 4]]
    Output: Logs nested structure and values
    Input : None
    Output: Logs and returns

  Notes:
    - Strings are treated as non-iterables.
    - If `x` is None, logs and returns.
  """
  indent = ' ' * 3 * depth
  if depth == 0:
    logger.debug(f"diag_recursive diagnostics called\n{'-' * 120}")
    logger.debug(f"Type: {type(x)}, Value: {x}")
  else:
    logger.debug(f"{indent} Depth: {depth}, Index: {index}, Type: {type(x)}, Value: {x}")

  if not isinstance(x, str):
    try:
      from collections.abc import Iterable
      if isinstance(x, Iterable):
        for i, y in enumerate(x):
          diag_recursive(y, depth + 1, index=i)
    except TypeError:
      pass


def dict_to_str(x: dict, depth: int = 0) -> str:
  """
  Convert a dictionary to a pretty-printed multiline string.

  Args:
    x (dict): Dictionary to convert. If None, returns an empty string.
    depth (int): Current indentation depth for nested dictionaries.

  Returns:
    str: String representation of dictionary with indentation.

  Examples:
    Input : {"a": 1, "b": {"c": 2}}
    Output:
      a:
         1
      b:
         c:
            2
    Input : None
    Output: ""

  Notes:
    - If `x` is None, returns an empty string.
  """
  if x is None:
    return ""
  msg = ""
  indent = ' ' * 3 * depth
  for k, v in x.items():
    msg += f"{indent}{k}:\n"
    if isinstance(v, dict):
      msg += dict_to_str(v, depth=depth + 1)
    else:
      msg += f"   {indent}{v}\n"
  return msg


def obj_to_html(obj: object) -> str:
  """
  Convert any Python object to a formatted HTML string for Jinja rendering.

  Args:
    obj (object): A Python object suitable for `pprint`. If None, returns an empty <pre> block.

  Returns:
    str: HTML string wrapped in <pre> tags that are safe for use with `|safe` in templates. e.g.,{{ result|safe }}

  Examples:
    Input : {"a": 1, "b": {"c": 2}}
    Output: <pre>{'a': 1, 'b': {'c': 2}}</pre>
    Input : None
    Output: <pre></pre>

  Notes:
    - The HTML content must be marked `|safe` in the template to avoid escaping.
    - If `obj` is None, returns an empty <pre> block.
  """
  pp = pprint.PrettyPrinter(indent=4, width=200)
  formatted_data = pp.pformat(obj)
  soup = BeautifulSoup("<pre></pre>", "html.parser")
  if soup.pre is not None:
    soup.pre.string = formatted_data
  return soup.prettify()


def compare_dicts(dict1: dict,
                  dict2: dict,
                  dict1_name: str | None = None,
                  dict2_name: str | None = None) -> bool:
  """
  Compare two dictionaries and log differences in keys and values.

  Args:
    dict1 (dict): First dictionary. If None, treated as empty dict.
    dict2 (dict): Second dictionary. If None, treated as empty dict.
    dict1_name (str | None): Optional label for first dictionary in logs.
    dict2_name (str | None): Optional label for second dictionary in logs.

  Returns:
    bool: True if dictionaries are equivalent; False otherwise.

  Examples:
    Input :
      dict1 = {"a": 1, "b": 2, "c": 3}
      dict2 = {"a": 1, "b": 4, "d": 5}
    Output: False
    Input : None, {"a": 1}
    Output: False
    Input : {"a": 1}, None
    Output: False
    Input : None, None
    Output: True

  Notes:
    - If either dict is None, it is treated as an empty dict.
  """
  if dict1 is None:
    dict1 = {}
  if dict2 is None:
    dict2 = {}
  dict1_name = dict1_name or "dict_1"
  dict2_name = dict2_name or "dict_2"
  logger.debug(f"compare_dicts called to compare {dict1_name} with {dict2_name}")

  keys_in_dict1_not_in_dict2 = set(dict1) - set(dict2)
  keys_in_dict2_not_in_dict1 = set(dict2) - set(dict1)

  differing_values = {
    key: (dict1[key], dict2[key])
    for key in dict1.keys() & dict2.keys()
    if dict1[key] != dict2[key]
  }

  if keys_in_dict1_not_in_dict2 or keys_in_dict2_not_in_dict1 or differing_values:
    logger.debug(f"Key differences:")
    if keys_in_dict1_not_in_dict2:
      logger.debug(f"- In {dict1_name} but not in {dict2_name}: {sorted(keys_in_dict1_not_in_dict2)}")
    if keys_in_dict2_not_in_dict1:
      logger.debug(f"- In {dict2_name} but not in {dict1_name}: {sorted(keys_in_dict2_not_in_dict1)}")

    if differing_values:
      logger.debug(f"Value differences:")
      for key, (v1, v2) in dict(sorted(differing_values.items())).items():
        logger.debug(f"- Key: '{key}', {dict1_name}: {v1}, {dict2_name}: {v2}")

    return False

  return True


def get_changed_fields(new_dict: dict, old_dict: dict) -> dict:
  """
  Extract fields from new_dict that differ from old_dict.

  Args:
    new_dict (dict): New/updated values (e.g., from a form). If None, treated as empty dict.
    old_dict (dict): Old/reference values (e.g., from model JSON). If None, treated as empty dict.

  Returns:
    dict: Keys with values that have changed.

  Notes:
    - Only keys present in new_dict are considered. This prevents unrelated fields from being overwritten when merging partial form data into a larger stored structure.
    - If either dict is None, it is treated as an empty dict.
  """
  if new_dict is None:
    new_dict = {}
  if old_dict is None:
    old_dict = {}
  changes = {}
  for key in new_dict:
    if new_dict[key] != old_dict.get(key):
      changes[key] = new_dict[key]
  return changes


def run_diagnostics() -> None:
  """
  Run example-based tests for diagnostic functions in this module.

  Logs example output for each function.
  """
  logger.debug(f"Running diagnostics on arb.utils.diagnostics module")

  # obj_diagnostics
  class TestClass:
    def __init__(self):
      self.x = 42
      self.y = "hello"

    def greet(self):
      return "hi"

  obj = TestClass()
  obj_diagnostics(obj, include_hidden=False, include_functions=True)

  # list_differences
  a = ["x", "y", "z"]
  b = ["x", "z", "w"]
  list_differences(a, b, "List A", "List B", print_warning=True)

  # diag_recursive
  diag_recursive([[1, 2], [3, [4, 5]]])

  # dict_to_str
  nested_dict = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
  logger.debug(f"dict_to_str output:\t" + dict_to_str(nested_dict))

  # obj_to_html
  html_result = obj_to_html(nested_dict)
  logger.debug(f"HTML representation of object (truncated):\t" + html_result[:300])

  # compare_dicts
  d1 = {"x": 1, "y": 2, "z": 3}
  d2 = {"x": 1, "y": 99, "w": 0}
  compare_dicts(d1, d2, "First Dict", "Second Dict")


if __name__ == "__main__":
  run_diagnostics()
