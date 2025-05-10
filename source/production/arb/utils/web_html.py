"""
Utility functions associated with website development that do not fit neatly in other modules.

To avoid circular imports, the web_util functions should not import from other util routines.
Instead, other util routines may import this module.

Notes on intended utility usage:
  - db_portal.py        → SQLAlchemy database routines
  - spreadsheet_util.py → Excel-related utilities
  - web_html.py         → HTML + WTForms form helpers (this file)
  - wtf_forms_util.py   → WTForms form structure and validation routines
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import arb.__get_logger as get_logger
from arb.utils.date_and_time import str_to_datetime
from arb.utils.file_io import get_secure_timestamped_file_name

__version__ = "1.0.0"
logger, pp_log = get_logger.get_logger()


def upload_single_file(upload_dir, request_file):
  """
  Save a user-uploaded file to the server using a sanitized and timestamped filename.

  Args:
      upload_dir (str | Path): Destination directory where the file will be saved.
      request_file: A FileStorage object (e.g., request.files['file']) from Flask.

  Returns:
      Path: Path to the uploaded file on disk.

  Example:
      >>> file = request.files['document']
      >>> path = upload_single_file("/uploads", file)
  """
  logger.debug(f"Attempting to upload {request_file.filename=}")
  file_name = get_secure_timestamped_file_name(upload_dir, request_file.filename)
  logger.debug(f"Upload single file as: {file_name}")
  request_file.save(file_name)
  return file_name


def selector_list_to_tuples(values: list[str]) -> list[tuple[str, str] | tuple[str, str, dict]]:
  """
  Convert a list of strings into WTForms-friendly selector tuples.

  Adds a "Please Select" option at the top of the returned list.

  Args:
      values (list[str]): List of string values for the HTML dropdown.

  Returns:
      list: List of (value, label) or (value, label, dict) tuples.

  Example:
      >>> selector_list_to_tuples(["Red", "Green"])
      [('Please Select', 'Please Select', {'disabled': True}),
       ('Red', 'Red'), ('Green', 'Green')]
  """
  result = [("Please Select", "Please Select", {"disabled": True})]
  result += [(v, v) for v in values]
  return result


def list_to_triple_tuple(values: list[str]) -> list[tuple[str, str, dict]]:
  """
  Convert a list of values to WTForms triple tuples: (value, label, metadata).

  Args:
      values (list[str]): Values to convert.

  Returns:
      list[tuple[str, str, dict]]: List of triple tuples.

  Example:
      >>> list_to_triple_tuple(["A", "B"])
      [('A', 'A', {}), ('B', 'B', {})]
  """
  return [(v, v, {}) for v in values]


def update_triple_tuple_dict(tuple_list: list[tuple[str, str, dict]],
                             match_list: list[str],
                             match_update_dict: dict,
                             unmatch_update_dict: dict | None = None
                             ) -> list[tuple[str, str, dict]]:
  """
  Update WTForms selector triple tuples based on match conditions.

  Args:
      tuple_list (list): List of (key, value, dict) tuples.
      match_list (list): List of keys to apply match_update_dict to.
      match_update_dict (dict): Metadata to merge for matched keys.
      unmatch_update_dict (dict | None): Metadata to apply to unmatched keys.

  Returns:
      list: Updated list of selector tuples.

  Example:
      >>> update_triple_tuple_dict(
      ...     [("a", "A", {}), ("b", "B", {})],
      ...     ["a"],
      ...     {"selected": True}
      ... )
      [('a', 'A', {'selected': True}), ('b', 'B', {})]
  """
  if unmatch_update_dict is None:
    unmatch_update_dict = {}

  result = []
  for key, value, meta in tuple_list:
    meta.update(match_update_dict if key in match_list else unmatch_update_dict)
    result.append((key, value, meta))
  return result


def update_selector_dict(input_dict: dict[str, list[str]]) -> dict[str, list[tuple[str, str] | tuple[str, str, dict]]]:
  """
  Convert dictionary of string lists into selector-style tuple lists.

  Args:
      input_dict (dict[str, list[str]]): Dict of dropdown options per field.

  Returns:
      dict[str, list[tuple]]: Dict with WTForms-ready selector tuples.

  Example:
      >>> update_selector_dict({"colors": ["Red", "Blue"]})
      {
        "colors": [
          ("Please Select", "Please Select", {"disabled": True}),
          ("Red", "Red"),
          ("Blue", "Blue")
        ]
      }
  """
  return {key: selector_list_to_tuples(values) for key, values in input_dict.items()}


def ensure_placeholder_option(
    tuple_list: list[tuple[str, str, dict]],
    item: str = 'Please Select',
    item_dict: dict | None = None,
    ensure_first: bool = True
) -> list[tuple[str, str, dict]]:
  """
  Add or reposition a placeholder option in a selector dropdown list.

  This function ensures that a specified "placeholder" option (typically used to prompt
  users to select a value, such as "Please Select") exists in the given list of
  selector options. If the placeholder is not present, it is inserted at the top. If it
  exists but is not the first item, it is optionally moved to the first position.

  Args:
      tuple_list (list[tuple[str, str, dict]]):
          A list of selection options, where each option is a tuple of the form:
          (value, label, metadata_dict). Example: [("CA", "California", {}), ...]
      item (str):
          The value and label to use for the placeholder option. Default is 'Please Select'.
      item_dict (dict | None):
          The metadata dictionary to associate with the placeholder. If None, defaults to
          {"disabled": True}, which is commonly used to disable the option in HTML.
      ensure_first (bool):
          If True (default), and the placeholder is already in the list but not in
          the first position, it will be moved to the top.

  Returns:
      list[tuple[str, str, dict]]:
          The updated list of tuples with the placeholder properly inserted or reordered.

  Example:
      >>> ensure_placeholder_option([("CA", "California", {})])
      [('Please Select', 'Please Select', {'disabled': True}), ('CA', 'California', {})]

      >>> ensure_placeholder_option(
      ...     [("Please Select", "Please Select", {}), ("CA", "California", {})],
      ...     item_dict={"disabled": True}
      ... )
      [('Please Select', 'Please Select', {}), ('CA', 'California', {})]
  """
  if item_dict is None:
    item_dict = {"disabled": True}

  placeholder = (item, item, item_dict)

  # Find the index of any existing placeholder (based on value match)
  # Explanation:
  #   - `enumerate(tuple_list)` produces (index, tuple) pairs.
  #   - `t[0] == item` checks if the first element (value) matches the placeholder value.
  #   - `next(...)` returns the index of the first match, or `None` if no match is found.
  index = next((i for i, t in enumerate(tuple_list) if t[0] == item), None)

  if index is None:
    # Placeholder not found; insert it at the beginning of the list.
    return [placeholder] + tuple_list

  elif ensure_first and index != 0:
    # Placeholder found but not in first position and `ensure_first` is True.
    # Move it to the front while preserving the order of the rest.
    reordered = [t for i, t in enumerate(tuple_list) if i != index]
    return [tuple_list[index]] + reordered

  # Placeholder exists and is already in the correct position; return unchanged.
  return tuple_list


def remove_items(tuple_list: list[tuple[str, str, dict]],
                 remove_items: str | list[str]
                 ) -> list[tuple[str, str, dict]]:
  """
  Remove specified keys from a selector tuple list.

  Args:
      tuple_list (list): List of WTForms triple tuples.
      remove_items (str | list[str]): One or more keys to exclude.

  Returns:
      list: Filtered tuple list.

  Example:
      >>> remove_items([("A", "A", {}), ("B", "B", {})], "B")
      [('A', 'A', {})]
  """
  remove_set = {remove_items} if isinstance(remove_items, str) else set(remove_items)
  return [t for t in tuple_list if t[0] not in remove_set]


def run_diagnostics() -> None:
  """
  Run diagnostics to validate HTML selector utilities.

  This includes:
    - Conversion of string lists to selector tuples
    - Metadata update logic
    - Placeholder addition and ordering
    - Tuple list item removal
    - Dictionary-based selector transformation

  Example:
      >>> run_diagnostics()
  """
  print("Running diagnostics for web_html.py...")

  test_values = ["A", "B", "C"]

  # Test selector_list_to_tuples
  selector = selector_list_to_tuples(test_values)
  assert selector[0][0] == "Please Select"
  assert ("A", "A") in selector

  # Test list_to_triple_tuple
  triple = list_to_triple_tuple(["X", "Y"])
  assert triple == [("X", "X", {}), ("Y", "Y", {})]

  # Test update_triple_tuple_dict
  updated = update_triple_tuple_dict(triple, ["Y"], {"selected": True})
  assert updated[1][2].get("selected") is True

  # Test update_selector_dict
  test_dict = {"colors": ["red", "green"]}
  updated_dict = update_selector_dict(test_dict)
  assert "Please Select" in [x[0] for x in updated_dict["colors"]]

  # Test ensure_placeholder_option
  reordered = ensure_placeholder_option([("X", "X", {})])
  assert reordered[0][0] == "Please Select"

  # Test remove_items
  cleaned = remove_items(triple, "X")
  assert all(t[0] != "X" for t in cleaned)

  print("All selector diagnostics passed.")


if __name__ == '__main__':
  run_diagnostics()
