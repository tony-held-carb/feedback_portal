"""
Misc Excel utility functions.
"""
import pprint

import arb.__get_logger as get_logger
from arb.utils.misc import get_nested_value

logger, pp_log = get_logger.get_logger(__name__, __file__)


def get_excel_row_column(xl_address):
  """
  Given a xl address as a string in format $ letter(s) $ number (e.g. "$A$1" or "$BB$15") return
  column letter(s) and integer row.

  Args:
    xl_address (str):

  Returns:
      tuple: A tuple containing the column name and row number associated with the xl address.
    - column (str):
    - row (int):
  """
  last_dollar = xl_address.rfind('$')
  # The address should always start with $ so you can index 1:
  column = xl_address[1:last_dollar]
  row = int(xl_address[last_dollar + 1:])

  return column, row


def xl_address_sort(xl_tuple, address_location="key", sort_by="row", sub_keys=None):
  """
  Given a tuple of key value pairs, where the key or value contains an Excel address as a string,
  return the address column as a string, or the row as an int to allow for sorting.

  The value may also be a dictionary or a nested dictionary.  You can specify the sequence of keys
  to navigate through the dictionary to find the value for searching purposes.

  Args:
    xl_tuple (tuple): key value pair where either the key or value has an xl string address
                  that uses absolute references (both columns and rows have dollar signs).
    address_location (str): "key" or "value" to indicate which has an xl string address
    sort_by (str): "row" or "column" to indicate which should be used for sorting.
    sub_keys (str, optional): if the value has a sub key (if it is a dict) for sorting

  Returns (str|int): row or column for sorting purposes
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

  # logger.debug(f"{return_value=}")
  return return_value


if __name__ == "__main__":
  pp = pprint.PrettyPrinter(indent=4, sort_dicts=False)
