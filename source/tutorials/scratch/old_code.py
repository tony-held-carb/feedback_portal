def query_to_dict(drop_down_dict,
                  model,
                  html_name,
                  key_field="id_",
                  value_field="description"
                  ):
  """
  Add a table's content to a drop-down dictionary for html select elements.

  Args:
    drop_down_dict (dict):
    model (db.Model): SQLAlchemy model
    html_name (str): name of html element
    key_field (str): name of key field
    value_field (str): name of value field

  Returns (None):

  Notes:
    1) key_field and value_field will be the same if you are not using foreign keys
  """
  rows = model.query.all()
  drop_down_dict[html_name] = {}
  for row in rows:
    key = getattr(row, key_field)
    value = getattr(row, value_field)
    drop_down_dict[html_name][key] = value

  # logger.debug(f"\n\t{drop_down_dict=}\n")


def query_to_dict_v02(drop_down_dict,
                      model,
                      html_name,
                      key_field="id_",
                      value_field="description"
                      ):
  """
  Add a table's content to a drop-down dictionary for html select elements.

  Args:
    drop_down_dict (dict):
    model (db.Model): SQLAlchemy model
    html_name (str): name of html element
    key_field (str): name of key field
    value_field (str): name of value field

  Returns (None):

  Notes:
    1) key_field and value_field will be the same if you are not using foreign keys
  """
  rows = model.query.all()
  drop_down_dict[html_name] = {}
  for row in rows:
    key = getattr(row, key_field)
    value = getattr(row, value_field)
    drop_down_dict[html_name][key] = value

  # logger.debug(f"\n\t{drop_down_dict=}\n")


def attribute_names(cls):
  """
  Not fully implemented

  Args:
    cls:

  Returns:

  Notes:
    based on: https://stackoverflow.com/questions/2537471/method-of-iterating-over-sqlalchemy-models-defined-columns

  """
  return [prop.key for prop in class_mapper(cls).iterate_properties
          if isinstance(prop, sqlalchemy.orm.ColumnProperty)]


def load_spreadsheet_field_mappings():
  # todo implement once we decide on a revised naming scheme ...
  result = None
  return result


def dict_serializer(dict_):
  result = {}
  for key, value in dict_.items():
    result[serializer(key)] = serializer(value)
  return result


def str_to_datetime(datetime_str):
  """
  Convert a string to a datetime object, if possible.

  String should be in format (not all numbers required) of:
    datetime.datetime(2024, 11, 15, 14, 30, 45)

  Args:
    datetime_str (str): The string to convert to a datetime object

  Returns (None|datetime): A datetime object.

  Notes:
    - An example string produced by repr
        datetime_str = "datetime.datetime(2024, 11, 15, 14, 30, 45)"
  """
  # Extract the numbers using regex
  match = re.search(r"datetime\.datetime\(([\d, ]+)\)", datetime_str)
  if match:
    date_parts = map(int, match.group(1).split(", "))
    dt = datetime(*date_parts)
    # print(dt)  # Output: 2024-11-15 14:30:45
    return dt
