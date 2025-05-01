"""
The following are code that are no longer used, perhaps they are too outdated.
Rather than deleting, the code is moved here in case it becomes relevant again at some point.
"""


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