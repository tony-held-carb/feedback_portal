"""
HTML and WTForms utility functions for form handling and file uploads.

This module provides helper functions for:
  - Uploading user files with sanitized names
  - Generating WTForms-compatible selector lists
  - Managing triple tuples for dynamic dropdown metadata

Notes:
    - Avoid circular imports by not depending on other utility modules.
    - Other utility modules (e.g., Excel, DB) may safely import this one.
    - Adds "Please Select" logic to dropdowns using `arb.utils.constants`.

Example Usage:
    from arb.utils.web_html import upload_single_file, selector_list_to_tuples
"""
from pathlib import Path

from werkzeug.datastructures import FileStorage

from arb.__get_logger import get_logger
from arb.utils.constants import PLEASE_SELECT
from arb.utils.file_io import get_secure_timestamped_file_name

__version__ = "1.0.0"
logger, pp_log = get_logger()


def upload_single_file(upload_dir: str | Path, request_file: FileStorage) -> Path:
  """
  Save a user-uploaded file to the server using a secure, timestamped filename.

  Args:
      upload_dir (str | Path): Directory to save the uploaded file.
      request_file (FileStorage): Werkzeug object from `request.files['<field>']`.

  Returns:
      Path: Full path to the uploaded file on disk.

  Raises:
      OSError: If the file cannot be written to disk.

  Example:
      >>> file = request.files['data']
      >>> path = upload_single_file("/data/uploads", file)
  """
  logger.debug(f"Attempting to upload {request_file.filename=}")
  file_name = get_secure_timestamped_file_name(upload_dir, request_file.filename)
  logger.debug(f"Upload single file as: {file_name}")
  request_file.save(file_name)
  return file_name


def selector_list_to_tuples(values: list[str]) -> list[tuple[str, str] | tuple[str, str, dict]]:
  """
  Convert a list of values into WTForms-compatible dropdown tuples.

  Adds a disabled "Please Select" entry at the top of the list.

  Args:
      values (list[str]): Dropdown options (excluding "Please Select").

  Returns:
      list[tuple[str, str] | tuple[str, str, dict]]:
          WTForms selector list including a disabled "Please Select" entry.

  Example:
      >>> selector_list_to_tuples(["Red", "Green"])
      [('Please Select', 'Please Select', {'disabled': True}),
       ('Red', 'Red'), ('Green', 'Green')]
  """
  result = [(PLEASE_SELECT, PLEASE_SELECT, {"disabled": True})]
  result += [(v, v) for v in values]
  return result


def list_to_triple_tuple(values: list[str]) -> list[tuple[str, str, dict]]:
  """
  Convert a list of strings into WTForms triple tuples.

  Each tuple contains (value, label, metadata).

  Args:
      values (list[str]): List of form options.

  Returns:
      list[tuple[str, str, dict]]: Triple tuples for WTForms SelectField.

  Example:
      >>> list_to_triple_tuple(["A", "B"])
      [('A', 'A', {}), ('B', 'B', {})]
  """
  return [(v, v, {}) for v in values]


def update_triple_tuple_dict(
    tuple_list: list[tuple[str, str, dict]],
    match_list: list[str],
    match_update_dict: dict,
    unmatch_update_dict: dict | None = None
) -> list[tuple[str, str, dict]]:
  """
  Update the metadata dict of each WTForms triple tuple based on value match.

  Args:
      tuple_list (list[tuple[str, str, dict]]): Existing list of selector tuples.
      match_list (list[str]): Values to match against.
      match_update_dict (dict): Metadata to apply if value is in `match_list`.
      unmatch_update_dict (dict | None): Metadata to apply otherwise (optional).

  Returns:
      list[tuple[str, str, dict]]: Updated list of selector tuples.

  Example:
      >>> update_triple_tuple_dict(
      ...     [('A', 'A', {}), ('B', 'B', {})],
      ...     ['A'],
      ...     {'disabled': True},
      ...     {'class': 'available'}
      ... )
      [('A', 'A', {'disabled': True}), ('B', 'B', {'class': 'available'})]
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

  Each list is transformed to include a "Please Select" disabled option
  followed by (value, label) tuples.

  Args:
      input_dict (dict[str, list[str]]): Dict of dropdown options per field.

  Returns:
      dict[str, list[tuple[str, str] | tuple[str, str, dict]]]:
          Dict with WTForms-ready selector tuples.

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
    item: str = PLEASE_SELECT,
    item_dict: dict = None,
    ensure_first: bool = True
) -> list[tuple[str, str, dict]]:
  """
  Ensure a placeholder entry is present in the tuple list.

  This function ensures that a specified "placeholder" option (typically used to prompt
  users to select a value, such as "Please Select") exists in the given list of
  selector options. If the placeholder is not present, it is inserted at the top. If it
  exists but is not the first item, it is optionally moved to the first position.

  Args:
      tuple_list (list[tuple[str, str, dict]]): Original selector list.
      item (str): Value for the placeholder. Default is "Please Select".
      item_dict (dict): Metadata for the placeholder. Default disables the option.
      ensure_first (bool): If True, move placeholder to top if found elsewhere.

  Returns:
      list[tuple[str, str, dict]]: Updated tuple list with ensured placeholder.

  Example:
      >>> ensure_placeholder_option([("A", "A", {})])
      [('Please Select', 'Please Select', {'disabled': True}), ('A', 'A', {})]
  """

  if item is None:
    item = PLEASE_SELECT

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
    # The Placeholder is not found; insert it at the beginning of the list.
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
  Remove one or more values from a tuple list by matching the first element.

  Args:
      tuple_list (list[tuple[str, str, dict]]): Selector tuples.
      remove_items (str | list[str]): One or more values to remove by key match.

  Returns:
      list[tuple[str, str, dict]]: Filtered list excluding the removed values.

  Example:
      >>> remove_items([("A", "A", {}), ("B", "B", {})], "B")
      [('A', 'A', {})]
  """
  remove_set = {remove_items} if isinstance(remove_items, str) else set(remove_items)
  return [t for t in tuple_list if t[0] not in remove_set]


def run_diagnostics() -> None:
  """
  Run assertions to validate selector utility behavior.

  Tests:
    - Conversion of string lists to selector tuples
    - Tuple updating with metadata
    - Placeholder insertion
    - Value removal from selector lists
    - Dict transformation to tuple selectors

  Returns:
      None

  Example:
      >>> run_diagnostics()
  """
  print("Running diagnostics for web_html.py...")

  test_values = ["A", "B", "C"]

  # Test selector_list_to_tuples
  selector = selector_list_to_tuples(test_values)
  assert selector[0][0] == PLEASE_SELECT
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
  assert PLEASE_SELECT in [x[0] for x in updated_dict["colors"]]

  # Test ensure_placeholder_option
  reordered = ensure_placeholder_option([("X", "X", {})])
  assert reordered[0][0] == PLEASE_SELECT

  # Test remove_items
  cleaned = remove_items(triple, "X")
  assert all(t[0] != "X" for t in cleaned)

  print("All selector diagnostics passed.")


if __name__ == '__main__':
  run_diagnostics()
