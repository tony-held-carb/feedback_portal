"""
Module for diagnostic related functions and utilities.

Provides:
- Attribute introspection and logging (`obj_diagnostics`)
- Dictionary comparisons and diffing
- Recursive structure analysis and formatting
- Object HTML conversion for safe diagnostic display in web environments
"""

import pprint

from bs4 import BeautifulSoup

from arb.__get_logger import get_logger

__version__ = "1.0.0"
logger, pp_log = get_logger(__name__, log_to_console=__file__)


def obj_diagnostics(obj: object,
                    include_hidden: bool = False,
                    include_functions: bool = False,
                    message: str | None = None) -> None:
  """
  Log diagnostics about an object's attributes and values.

  Args:
      obj: The object to diagnose.
      include_hidden: If True, include attributes starting with '_'.
      include_functions: If True, include callable attributes.
      message: Optional message to log before diagnostics.

  Returns:
      None

  Examples:
      >>> class Sample:
      ...     x = 1
      ...     def hello(self): return "hi"
      >>> obj_diagnostics(Sample(), include_functions=True)
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


def list_differences(iterable_01: list | dict,
                     iterable_02: list | dict,
                     iterable_01_name: str = "List 1",
                     iterable_02_name: str = "List 2",
                     print_warning: bool = False) -> tuple[list, list]:
  """
  Identify differences between two iterables.

  Args:
      iterable_01: First list or dict.
      iterable_02: Second list or dict.
      iterable_01_name: Label for first iterable in logs.
      iterable_02_name: Label for second iterable in logs.
      print_warning: If True, emit warnings for non-overlapping items.

  Returns:
      Tuple of items only in iterable_01 and only in iterable_02.

  Examples:
      >>> list_differences(["a", "b"], ["b", "c"])
      (["a"], ["c"])
  """
  in_iterable_1_only = [x for x in iterable_01 if x not in iterable_02]
  in_iterable_2_only = [x for x in iterable_02 if x not in iterable_01]

  if print_warning:
    if in_iterable_1_only:
      logger.warning(
        f"Warning: {iterable_01_name} has {len(in_iterable_1_only)} item(s) not in {iterable_02_name}:\n\t{in_iterable_1_only}")
    if in_iterable_2_only:
      logger.warning(
        f"Warning: {iterable_02_name} has {len(in_iterable_2_only)} item(s) not in {iterable_01_name}:\n\t{in_iterable_2_only}")

  return in_iterable_1_only, in_iterable_2_only


def diag_recursive(x: object, depth: int = 0, index: int = 0) -> None:
  """
  Recursively log structure and contents of an object.

  Args:
      x: Object to introspect.
      depth: Recursion level.
      index: Element index at this level.

  Returns:
      None

  Notes:
      Strings are treated as non-iterables.
  """
  indent = ' ' * 3 * depth
  if depth == 0:
    logger.debug(f"diag_recursive diagnostics called\n{'-' * 120}")
    logger.debug(f"Type: {type(x)}, Value: {x}")
  else:
    logger.debug(f"{indent} Depth: {depth}, Index: {index}, Type: {type(x)}, Value: {x}")

  if not isinstance(x, str):
    try:
      for i, y in enumerate(x):
        diag_recursive(y, depth + 1, index=i)
    except TypeError:
      pass


def dict_to_str(x: dict, depth: int = 0) -> str:
  """
  Convert a dictionary to a string with one entry per line, recursively.

  Args:
      x: Dictionary to format.
      depth: Nesting level for indentation.

  Returns:
      String with one line per key/value.

  Examples:
      >>> d = {"a": 1, "b": {"c": 2}}
      >>> print(dict_to_str(d))
      a:
         1
      b:
         c:
            2
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


def obj_to_html(obj: object) -> str:
  """
  Convert a Python object into HTML-safe string for rendering in Jinja templates.

  Args:
      obj: Any printable Python object.

  Returns:
      HTML string suitable for Jinja `|safe` rendering.

  Notes:
      The HTML content must be marked `|safe` in the template to avoid escaping.

  Example (in Jinja):
      {% if result is defined %}
        {{ result|safe }}
      {% endif %}
  """
  pp = pprint.PrettyPrinter(indent=4, width=200)
  formatted_data = pp.pformat(obj)
  soup = BeautifulSoup("<pre></pre>", "html.parser")
  soup.pre.string = formatted_data
  return soup.prettify()


def compare_dicts(dict1: dict,
                  dict2: dict,
                  dict1_name: str | None = None,
                  dict2_name: str | None = None) -> bool:
  """
  Compare two dictionaries and log differences in keys and values.

  Args:
      dict1: First dictionary.
      dict2: Second dictionary.
      dict1_name: Name label for first dictionary.
      dict2_name: Name label for second dictionary.

  Returns:
      True if dictionaries are equal, False otherwise.

  Examples:
      >>> dict1 = {"a": 1, "b": 2, "c": 3}
      >>> dict2 = {"a": 1, "b": 4, "d": 5}
      >>> compare_dicts(dict1, dict2)
      False
  """
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
    logger.debug("Key differences:")
    if keys_in_dict1_not_in_dict2:
      logger.debug(f"- In {dict1_name} but not in {dict2_name}: {sorted(keys_in_dict1_not_in_dict2)}")
    if keys_in_dict2_not_in_dict1:
      logger.debug(f"- In {dict2_name} but not in {dict1_name}: {sorted(keys_in_dict2_not_in_dict1)}")

    if differing_values:
      logger.debug("Value differences:")
      for key, (v1, v2) in dict(sorted(differing_values.items())).items():
        logger.debug(f"- Key: '{key}', {dict1_name}: {v1}, {dict2_name}: {v2}")

    return False

  return True


def run_diagnostics() -> None:
  """
  Run demonstration of diagnostic utilities with examples.
  """
  logger.debug("\n\nRunning diagnostics on arb.utils.diagnostics module")

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
  logger.debug("dict_to_str output:\n" + dict_to_str(nested_dict))

  # obj_to_html
  html_result = obj_to_html(nested_dict)
  logger.debug("HTML representation of object (truncated):\n" + html_result[:300])

  # compare_dicts
  d1 = {"x": 1, "y": 2, "z": 3}
  d2 = {"x": 1, "y": 99, "w": 0}
  compare_dicts(d1, d2, "First Dict", "Second Dict")


if __name__ == "__main__":
  run_diagnostics()
