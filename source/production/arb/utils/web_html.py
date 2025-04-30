"""
Utility functions associated with website development that do not fit neatly in other modules.

To avoid circular imports, the web_util functions should not import from the other util routines,
rather the other util routines should import this package.

Notes on intended usage for utility files
-----------------------------------------

  - db_portal.py - database and SQLAlchemy related
  - spreadsheet_util.py - Excel spreadsheet related
  - web_html.py - a catchall for utility routines that do not fit in the other util files (this file)
  - wtf_forms_util.py - WTForms related.

Notes:

"""
from datetime import datetime
from zoneinfo import ZoneInfo

import arb.__get_logger as get_logger
from arb.utils.date_and_time import str_to_datetime
from arb.utils.file_io import get_secure_timestamped_file_name

__version__ = "1.0.0"
logger, pp_log = get_logger.get_logger(__name__, __file__)


def upload_single_file(upload_dir, request_file):
  """
  Upload a user uploaded file to the server.  The filename used on the server will be similar to the file name
  uploaded by the user, but will be made secure (special characters striped) and will include a timestamp.

  Args:
  request_file:
    - request_file likely created with: request_file = request.files['file']
  upload_dir (str|Path):
    - Path to server directory for file uploads

  Returns (Path): path of file uploaded to the server.

  """
  logger.debug(f"Attempting to upload {request_file.filename=}")
  file_name = get_secure_timestamped_file_name(upload_dir, request_file.filename)
  logger.debug(f"Upload single file as: {file_name}")
  request_file.save(file_name)
  return file_name


def create_html_select(table_name, table_as_list, key_field, display_field):
  """
  Given a list of dictionaries, where each dictionary represents a row of table_name, create
  a list of tuples suitable for an HTML selector where the element value is the key_field and the displayed
  value is the associated display_field.


  Args:
    table_name (str): lower-case sql table name
    table_as_list (list[dict]): list of dictionaries where each dictionary has the column name as the key and the value as the value
    key_field (str): name of the dictionary key that represents the select element's value
    display_field (str): name of the dictionary key that represents the select element's display

  Returns:
    tuple: A tuple containing the drop-down menu items and a reverse dictionary lookup.
      - drop_downs (list[tuple]): lookup dictionary of drop down key values for each table.
      - drop_downs_rev (dict): reverse lookup dictionary of drop down key values for each table
  """
  drop_downs = {}
  drop_downs_rev = {}
  entries = [(-1, 'Please Select', {'disabled': True})]
  entries_rev = {}
  for row in table_as_list:
    value = row[key_field]
    display = row[display_field]
    entries.append((value, display))
    entries_rev[display] = value

  drop_downs[table_name] = entries
  drop_downs_rev[table_name] = entries_rev

  return drop_downs, drop_downs_rev


def selector_list_to_tuples(values):
  """
  Given a list of strings that represent html drop down options,
  return a list of tuples suitable for an HTML selector using WTForms.

  The returned list starts with a static option:
  ("Please Select", "Please Select", {"disabled": True})
  followed by each original string turned into a tuple (value, value).

  Args:
      values (list[str]): A list of string values.

  Returns:
      list[tuple[str, str] | tuple[str, str, dict]]: A transformed list of tuples.
  """
  result = [("Please Select", "Please Select", {"disabled": True})]
  result += [(v, v) for v in values]
  return result


def list_to_triple_tuple(values):
  """
  Converts a list of values into a list of WTForms-compatible triple tuples.

  Each input value is transformed into a tuple of the form (value, value, {}),
  which is commonly used to populate WTForms `SelectField` choices with support
  for additional metadata.

  Args:
      values (list[str]): A list of string values to be converted.

  Returns:
      list[tuple[str, str, dict[str, object]]]: A list of 3-element tuples of the form (value, value, {}).

  Example:
      >>> list_to_triple_tuple(["One", "Two"])
      [('One', 'One', {}), ('Two', 'Two', {})]
  """
  return [(v, v, {}) for v in values]


def update_triple_tuple_dict(tuple_list, match_list, match_update_dict, unmatch_update_dict=None):
  """
  Updates the dictionary part of triple tuples based on whether their key matches a given list.

  This function is intended to work with tuples of the form (key, value, dict) where `dict`
  contains metadata for WTForms fields. If the key exists in `match_list`, `match_update_dict`
  is merged into the existing dict. Otherwise, `unmatch_update_dict` is merged (if provided).

  Args:
      tuple_list (list[tuple[str, str, dict[str, object]]]): List of 3-element tuples (key, value, dict) to update.
      match_list (list[str]): Keys to match against for applying `match_update_dict`.
      match_update_dict (dict[str, object]): Dictionary to update matched items with.
      unmatch_update_dict (dict[str, object] | None): Dictionary to update unmatched items with.
          Defaults to an empty dictionary if not provided.

  Returns:
      list[tuple[str, str, dict[str, object]]]: A new list of updated 3-element tuples.

  Example:
      >>> tuple_list = [("a", "A", {}), ("b", "B", {})]
      >>> match_list = ["a"]
      >>> match_update_dict = {"selected": True}
      >>> update_triple_tuple_dict(tuple_list, match_list, match_update_dict)
      [('a', 'A', {'selected': True}), ('b', 'B', {})]
  """
  if unmatch_update_dict is None:
    unmatch_update_dict = {}

  result = []
  for tuple_key, tuple_value, tuple_dict in tuple_list:
    if tuple_key in match_list:
      tuple_dict.update(match_update_dict)
    else:
      tuple_dict.update(unmatch_update_dict)
    result.append((tuple_key, tuple_value, tuple_dict))
  return result


def update_selector_dict(input_dict):
  """
  Transforms a dictionary where the keys are html selector id's and the values
  are list of string selector options so that the values are now a list of tuples
  suitable for wtforms html selectors.

  The transformation applies `selector_list_to_tuples` to each list of strings,
  creating tuples and prepends a disabled "Please Select" option.

  Args:
      input_dict (dict[str, list[str]]): A dictionary where each value is a list of strings.

  Returns:
      dict[str, list[tuple[str, str] | tuple[str, str, dict]]]:
          A new dictionary with transformed values.

  Example:
      >>> original = {
      ...     "fruits": ["apple", "banana", "cherry"],
      ...     "colors": ["red", "green", "blue"]
      ... }
      >>> transformed = update_selector_dict(original)
      >>> print(transformed["colors"])
      [('Please Select', 'Please Select', {'disabled': True}),
       ('red', 'red'),
       ('green', 'green'),
       ('blue', 'blue')]
  """
  return {key: selector_list_to_tuples(values) for key, values in input_dict.items()}


if __name__ == '__main__':
  now = datetime.now(ZoneInfo("UTC"))
  print(f"{now=}")
  now_string = repr(now)
  new_now = str_to_datetime(now_string)
  print(f"{new_now=}")

  now_string = "Note a valid datetime"
  new_now = str_to_datetime(now_string)
  print(f"{new_now=}")


def ensure_placeholder_option(tuple_list,
                              item='Please Select',
                              item_dict=None,
                              ensure_first=True):
  """
  Ensures that a placeholder option is present at the top of a triple-tuple selector list.

  If a tuple with the given `item` as the key is not already present in `tuple_list`,
  it is prepended using (item, item, item_dict). If `ensure_first` is True and the placeholder
  is already in the list but not first, it is moved to the front.

  Args:
      tuple_list (list[tuple[str, str, dict[str, object]]]): A list of selector tuples,
          typically from list_to_triple_tuple.
      item (str): The placeholder key and label to look for or insert. Defaults to 'Please Select'.
      item_dict (dict[str, object] | None): Dictionary metadata for the placeholder.
          Defaults to {'disabled': True}.
      ensure_first (bool): If True, ensures the placeholder appears as the first item.
          Defaults to True.

  Returns:
      list[tuple[str, str, dict[str, object]]]: Updated list with the placeholder tuple prepended or repositioned.

  Example:
      >>> ensure_placeholder_option([('One', 'One', {})])
      [('Please Select', 'Please Select', {'disabled': True}), ('One', 'One', {})]
  """
  if item_dict is None:
    item_dict = {"disabled": True}

  placeholder = (item, item, item_dict)

  # Find index of existing placeholder if present
  existing_index = next((i for i, t in enumerate(tuple_list) if t[0] == item), None)

  if existing_index is None:
    # Not present, prepend
    return [placeholder] + tuple_list
  elif ensure_first and existing_index != 0:
    # Move to front
    updated_list = [tuple_list[i] for i in range(len(tuple_list)) if i != existing_index]
    return [tuple_list[existing_index]] + updated_list

  return tuple_list


def remove_items(tuple_list, remove_items):
  """
  Removes specified items by key from a list of WTForms-style triple tuples.

  This function returns a new list excluding any tuple where the first element (the key)
  matches one of the `remove_items`.

  Args:
      tuple_list (list[tuple[str, str, dict[str, object]]]): The list of selector tuples to filter.
      remove_items (str | list[str]): A single string or list of strings representing keys to remove.

  Returns:
      list[tuple[str, str, dict[str, object]]]: A new list with specified keys removed.

  Example:
      >>> tuples = [('One', 'One', {}), ('Two', 'Two', {}), ('Three', 'Three', {})]
      >>> remove_items(tuples, 'Two')
      [('One', 'One', {}), ('Three', 'Three', {})]

      >>> remove_items(tuples, ['One', 'Three'])
      [('Two', 'Two', {})]
  """
  if isinstance(remove_items, str):
    remove_set = {remove_items}
  else:
    remove_set = set(remove_items)

  return [t for t in tuple_list if t[0] not in remove_set]
