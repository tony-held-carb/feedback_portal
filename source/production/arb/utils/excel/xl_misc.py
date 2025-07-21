"""
Excel address parsing and sorting utilities.

This module provides helper functions for interpreting Excel-style address strings
(such as "$A$1") and using them for sorting data structures. These utilities are
used during schema generation, payload creation, and Excel form manipulation.

Functions:
  - get_excel_row_column(): Parses an Excel address into column and row components.
  - xl_address_sort(): Extracts a sortable row or column value from an Excel address.
  - run_diagnostics(): Test harness for verifying address parsing and sorting behavior.

Typical Use Case:
  These functions are primarily invoked when organizing Excel schema dictionaries
  by their physical layout in the worksheet, either by row or column position.

Notes:
  - Assumes absolute Excel address formatting (e.g., "$A$1").
  - Designed to be used by other modules like xl_create and xl_file_structure.

"""

import logging

from arb.utils.misc import get_nested_value

logger = logging.getLogger(__name__)


def get_excel_row_column(xl_address: str) -> tuple[str, int]:
  """
  Extract the Excel column letters and row number from an address string.

  Excel absolute references take the form "$A$1" or "$BB$12", where both the column and row
  are prefixed with dollar signs.

  Args:
    xl_address (str): The Excel address to parse (must be in absolute format like "$A$1").

  Returns:
    tuple[str, int]: A tuple of (column letters, row number).

  Raises:
    ValueError: If the format is invalid (e.g., not exactly two-dollar signs, or row not an integer).

  Examples:
    Input : "$Z$9"
    Output: ('Z', 9)

    Input : "$AA$105"
    Output: ('AA', 105)
  """

  if xl_address.count('$') != 2:
    raise ValueError(f"Excel address must contain exactly two '$' characters: {xl_address}")

  first_dollar = xl_address.find('$')
  last_dollar = xl_address.rfind('$')

  column = xl_address[first_dollar + 1:last_dollar]
  try:
    row = int(xl_address[last_dollar + 1:])
  except ValueError as e:
    raise ValueError(f"Could not parse row number from Excel address: {xl_address}") from e

  return column, row


def xl_address_sort(
    xl_tuple: tuple,
    address_location: str = "key",
    sort_by: str = "row",
    sub_keys: str | list[str] | None = None
) -> int | str:
  """
  Extract the Excel row or column value from a tuple of key-value pairs for sorting.

  This is used when sorting collections of data where either the key or the value
  contains an Excel-style address string. Supports sorting by either row or column.

  Args:
    xl_tuple (tuple): A (key, value) tuple where one element contains a string like "$A$1".
    address_location (str): Which element contains the Excel address ("key" or "value").
    sort_by (str): Whether to sort by "row" (int) or "column" (str).
    sub_keys (str | list[str] | None): Key(s) to retrieve nested address if inside a dict.

  Returns:
    int | str: The row (int) or column (str) extracted from the address.

  Raises:
    ValueError: If `address_location` or `sort_by` has an invalid value.

  Examples:
    Input : ("$B$3", "data"), address_location="key", sort_by="row"
    Output: 3

    Input : ("item", {"pos": "$C$7"}), address_location="value", sort_by="column", sub_keys="pos"
    Output: 'C'
  """

  if address_location == "key":
    address = xl_tuple[0]
  elif address_location == "value":
    if sub_keys is None:
      address = xl_tuple[1]
    else:
      address = get_nested_value(xl_tuple[1], sub_keys)
  else:
    raise ValueError("address_location must be 'key' or 'value'")

  column, row = get_excel_row_column(address)

  if sort_by == "row":
    return_value = row
  elif sort_by == "column":
    return_value = column
  else:
    raise ValueError("sort_by must be 'row' or 'column'")

  return return_value


def run_diagnostics() -> None:
  """
  Run demonstration tests for get_excel_row_column() and xl_address_sort().
  This function is only called if this module is run directly.

  """
  # pp = pprint.PrettyPrinter(indent=4, sort_dicts=False)

  print("=== Testing get_excel_row_column ===")
  valid_addresses = ["$C$42", "$AA$99"]
  for addr in valid_addresses:
    try:
      result = get_excel_row_column(addr)
      print(f"  Address: {addr} => {result}")
    except Exception as e:
      print(f"  ERROR for {addr}: {e}")

  print("\n=== Testing get_excel_row_column (invalid formats) ===")
  invalid_addresses = ["A$1", "$A1", "$A$1$", "$AB$", "$AB$XYZ"]
  for addr in invalid_addresses:
    try:
      result = get_excel_row_column(addr)
      print(f"  UNEXPECTED SUCCESS: {addr} => {result}")
    except Exception as e:
      print(f"  Expected failure for {addr}: {e}")

  print("\n=== Testing xl_address_sort ===")
  test_tuple = ("$B$10", "Example")
  print(f"  Tuple: {test_tuple} => Row: {xl_address_sort(test_tuple, 'key', 'row')}")

  nested = ("key", {"nested": {"cell": "$D$20"}})
  print(f"  Tuple: {nested} => Row: {xl_address_sort(nested, 'value', 'row', sub_keys=['nested', 'cell'])}")


if __name__ == "__main__":
  run_diagnostics()
