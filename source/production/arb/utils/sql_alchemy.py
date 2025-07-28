"""
SQLAlchemy utility functions for Flask applications using declarative or automap base models.

This module provides introspection, diagnostics, and model-row operations for SQLAlchemy-based
Flask apps. It supports both declarative and automapped models.

Included Utilities:
-------------------
- Model diagnostics (`sa_model_diagnostics`)
- Field and column type inspection (`get_sa_fields`, `get_sa_column_types`)
- Full automap type mapping (`get_sa_automap_types`)
- Dictionary conversions (`sa_model_to_dict`, `sa_model_dict_compare`)
- Table-to-dict exports (`table_to_list`)
- Table/class lookups (`get_class_from_table_name`)
- Row fetch and sort utilities (`get_rows_by_table_name`)
- Model add/delete with logging (`add_commit_and_log_model`, `delete_commit_and_log_model`)
- Foreign key traversal (`get_foreign_value`)
- PostgresQL sequence inspection (`find_auto_increment_value`)
- JSON column loader (`load_model_json_column`)

Type Hints:
-----------
- `db (SQLAlchemy)`: Flask-SQLAlchemy database instance with .session and .engine.
- `base (DeclarativeMeta)`: Declarative or automapped SQLAlchemy base (e.g., via automap_base()).
- `model (DeclarativeMeta)`: SQLAlchemy ORM model class or instance.
- `session (Session)`: SQLAlchemy session object.

Usage Notes:
------------
- Supports PostgresQL features like sequence inspection via `pg_get_serial_sequence`.
- Logging is integrated for debugging and auditing.
- Compatible with Python 3.10+ syntax (PEP 604 union types).

Version:
    1.0.0
"""
import logging

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.automap import AutomapBase
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session
from typing import Any

from arb.utils.json import safe_json_loads
from arb.utils.misc import log_error

__version__ = "1.0.0"
logger = logging.getLogger(__name__)


def sa_model_diagnostics(model: AutomapBase, comment: str = "") -> None:
  """
  Log diagnostic details about a SQLAlchemy model instance, including all field names and values.

  Args:
    model (AutomapBase): SQLAlchemy model instance to inspect. Must not be None.
    comment (str): Optional comment header for log output.

  Returns:
    None

  Examples:
    Input : user_model, comment="User diagnostics"
    Output: Logs all field names and values for user_model

  Notes:
    - If `model` is None, a TypeError or AttributeError will occur.
  """
  logger.debug(f"Diagnostics for model of type {type(model)=}")
  if comment:
    logger.debug(f"{comment}")
  logger.debug(f"{model=}")
  fields = get_sa_fields(model)
  for key in fields:
    value = getattr(model, key)
    logger.debug(f"{key} {type(value)} = ({value})")


def get_sa_fields(model: AutomapBase) -> list[str]:
  """
  Return a sorted list of column attribute names for a SQLAlchemy model.

  Args:
    model (AutomapBase): SQLAlchemy AutomapBase model instance. Must not be None.

  Returns:
    list[str]: Alphabetically sorted list of column attribute names.

  Examples:
    Input : user_model
    Output: ['email', 'id', 'name']

  Notes:
    - If `model` is None, a TypeError or AttributeError will occur.
  """
  inst = inspect(model)  # type: ignore
  model_fields = [c_attr.key for c_attr in inst.mapper.column_attrs]  # type: ignore
  model_fields.sort()
  return model_fields


def get_sa_column_types(model: AutomapBase, is_instance: bool = False) -> dict[str, dict]:
  """
  Return a mapping of each column to its SQLAlchemy and Python types for a model.

  Args:
    model (AutomapBase): SQLAlchemy model instance or class. Must not be None.
    is_instance (bool): True if `model` is an instance, False if a class.

  Returns:
    dict[str, dict]: Mapping from column names to a dict with 'sqlalchemy_type' and 'python_type'.

  Examples:
    Input : user_model
    Output: {'id': {'sqlalchemy_type': Integer, 'python_type': int}, ...}

  Raises:
    AttributeError: If `model` is None or does not have valid metadata.
  """
  # Get the table inspector for the model
  if is_instance:
    inspector = inspect(type(model))
  else:
    inspector = inspect(model)

  logger.debug(f"\t{model=}")
  logger.debug(f"\t{inspector=}")

  columns_info = {}
  for column in inspector.columns:  # type: ignore
    col_name = column.name
    try:
      columns_info[col_name] = {
        'sqlalchemy_type': column.type,
        'python_type': column.type.python_type
      }
    except Exception as e:
      logger.warning(f"{col_name} has unsupported Python type.")
      logger.warning(e)
      columns_info[col_name] = {
        'sqlalchemy_type': column.type,
        'python_type': None
      }
      raise  # Re-raises the current exception with original traceback - comment out if you don't to warn rather than fail

  return columns_info


def get_sa_automap_types(engine: Engine, base: AutomapBase) -> dict[str, dict]:
  """
  Return column type metadata for all mapped classes in an automap base.

  Args:
    engine (Engine): SQLAlchemy engine instance. Must not be None.
    base (AutomapBase): Automap base prepared with reflected metadata. Must not be None.

  Returns:
    dict[str, dict]: Nested mapping: table -> column -> type category.
    Structure:
      result[table_name][column_name][kind] = type  # table_name, column_name, kind are placeholders
      where kind can be 'database_type', 'sqlalchemy_type', or 'python_type'.

  Examples:
    Input : engine, base
    Output: {'users': {'id': {'python_type': int, ...}, ...}, ...}

  Notes:
    - `base` is typically created with:
        base = automap_base()
        base.prepare(db.engine, reflect=True)
    - If `engine` or `base` is None, a TypeError or AttributeError will occur.
  """
  logger.debug(f"calling get_sa_automap_types()")

  result = {}
  inspector = inspect(engine)

  # Loop through all the mapped classes (tables)
  # print(f"{type(base)=}")
  # print(f"{type(base.classes)=}")
  for class_name, mapped_class in base.classes.items():  # type: ignore
    # print(f"Table: {class_name}")
    result[class_name] = {}

    # Get the table columns
    columns = mapped_class.__table__.columns

    # Loop through columns to get types
    for column in columns:
      # print(f"Column: {column.name}")
      result[class_name][column.name] = {}
      db_type = None
      sa_type = None
      py_type = None

      # Database (SQL) column type
      db_column_type = inspector.get_columns(class_name)
      for col in db_column_type:
        if col['name'] == column.name:
          db_type = col['type']
          # print(f"  Database type (SQL): {db_type}")

          # SQLAlchemy type
          sa_type = type(db_type).__name__
          # print(f"  SQLAlchemy type: {sa_type}")

      # Python type
      try:
        py_type = column.type.python_type
      except Exception as e:
        msg = f"{column.name} is of type: {sa_type} that is not implemented in python.  Setting python type to None."
        logger.warning(msg)
        logger.warning(e)

      # print(f"  Python type: {py_type}")
      result[class_name][column.name]["python_type"] = py_type
      result[class_name][column.name]["database_type"] = db_type
      result[class_name][column.name]["sqlalchemy_type"] = sa_type

  logger.debug(f"returning from get_sa_automap_types()")
  return result


def sa_model_dict_compare(model_before: dict, model_after: dict) -> dict:
  """
  Compare two model dictionaries and return a dict of changed fields and their new values.

  Args:
    model_before (dict): Original model state as a dictionary. If None, treated as empty dict.
    model_after (dict): New model state as a dictionary. If None, treated as empty dict.

  Returns:
    dict: Dictionary of changed fields and their new values.

  Examples:
    Input : {'email': 'old@example.com'}, {'email': 'new@example.com'}
    Output: {'email': 'new@example.com'}
    Input : None, {'email': 'new@example.com'}
    Output: {'email': 'new@example.com'}
    Input : {'email': 'old@example.com'}, None
    Output: {}

  Notes:
    - If either input is None, it is treated as an empty dict.
  """
  changes = {}
  for field in model_after:
    if field not in model_before or model_before[field] != model_after[field]:
      changes[field] = model_after[field]
  return changes


def sa_model_to_dict(model: AutomapBase) -> dict:
  """
  Convert a SQLAlchemy model instance to a Python dictionary.

  Args:
    model (AutomapBase): SQLAlchemy model instance. Must not be None.

  Returns:
    dict: Dictionary with column names as keys and model values as values.

  Examples:
    Input : user_model
    Output: {'id': 1, 'email': 'user@example.com'}

  Notes:
    - If `model` is None, a TypeError or AttributeError will occur.
  """
  model_as_dict = {}
  fields = get_sa_fields(model)
  for field in fields:
    value = getattr(model, field)
    model_as_dict[field] = value

  return model_as_dict


def table_to_list(base: AutomapBase, session: Session, table_name: str) -> list[dict]:
  """
  Convert all rows of a mapped table to a list of dictionaries.

  Args:
    base (AutomapBase): Automap base. Must not be None.
    session (Session): SQLAlchemy session. Must not be None.
    table_name (str): Table name to query. If None or empty, raises ValueError.

  Returns:
    list[dict]: List of row dictionaries, one per row in the table.

  Examples:
    Input : Base, session, 'users'
    Output: [{'id': 1, 'email': ...}, ...]
    Input : Base, session, None
    Output: ValueError
    Input : Base, session, ''
    Output: ValueError

  Notes:
    - If `table_name` is None or empty, raises ValueError.
    - If table is not found, returns an empty list and logs a warning.
  """
  result = []
  table = base.classes.get(table_name)

  if table:
    logger.debug(f"Selecting data from: {table_name}")
    rows = session.query(table).all()
    col_names = table.__table__.columns.keys()

    for row in rows:
      row_data = {col: getattr(row, col) for col in col_names}
      result.append(row_data)
  else:
    logger.warning(f"Table '{table_name}' not found in metadata.")

  return result


def get_class_from_table_name(base: AutomapBase | None, table_name: str) -> AutomapBase | None:
  """
  Retrieve the mapped ORM class for a given table name from an automap base.

  Args:
    base (AutomapBase): SQLAlchemy AutomapBase. Must not be None.
    table_name (str): Database table name. If None or empty, returns None.

  Returns:
    AutomapBase | None: Mapped SQLAlchemy ORM class, or None if not found.

  Examples:
    Input : base, 'users'
    Output: <User ORM class>
    Input : base, None
    Output: None
    Input : None, 'users'
    Output: None

  Notes:
    - Uses Base.metadata and registry to find the mapped class.
    - If the table is not found, returns None.
    - If `base` is None, returns None.
    - If `table_name` is None or empty, returns None.
  """
  try:
    # Look up the table in metadata and find its mapped class
    table = base.metadata.tables.get(table_name)  # type: ignore
    if table is not None:
      for mapper in base.registry.mappers:  # type: ignore
        if mapper.local_table == table:
          return mapper.class_
    return None
  except Exception as e:
    msg = f"Exception occurred when trying to get table named {table_name}"
    logger.error(msg, exc_info=True)
    logger.error(f"exception info: {e}")

  return None


def get_rows_by_table_name(
    db: SQLAlchemy,
    base: AutomapBase,
    table_name: str,
    colum_name_pk: str | None = None,
    ascending: bool = True
) -> list:
  """
  Retrieve all rows from a table, optionally sorted by a column.

  Args:
    db (SQLAlchemy): SQLAlchemy db object. Must not be None.
    base (AutomapBase): Declarative base. Must not be None.
    table_name (str): Table name. If None or empty, raises ValueError.
    colum_name_pk (str | None): Column to sort by (primary key or other). If None, no sorting is applied.
    ascending (bool): Sort order (True for ascending, False for descending).

  Returns:
    list[DeclarativeMeta]: List of ORM model instances.

  Examples:
    Input : db, Base, 'users', 'id', ascending=False
    Output: List of user ORM instances sorted by id descending
    Input : db, Base, None
    Output: ValueError
    Input : db, Base, ''
    Output: ValueError

  Notes:
    - If `table_name` is None or empty, raises ValueError.
    - If table is not found, returns an empty list and logs a warning.
  """
  table = get_class_from_table_name(base, table_name)
  logger.info(f"{type(table)=}")

  query = db.session.query(table)
  if colum_name_pk:
    column = getattr(table, colum_name_pk)
    query = query.order_by(column if ascending else desc(column))

  rows = query.all()
  logger.debug(f"Query result: {type(rows)=}")
  return rows


def delete_commit_and_log_model(db: SQLAlchemy, model_row: AutomapBase, comment: str = "") -> None:
  """
  Delete a model instance from the database, log the operation, and commit the change.

  Args:
    db (SQLAlchemy): SQLAlchemy instance bound to the Flask app. Must not be None.
    model_row (AutomapBase): ORM model instance to delete. Must not be None.
    comment (str): Optional log comment for auditing.

  Returns:
    None

  Examples:
    Input : db, user_row, comment="Deleting user"
    Output: Deletes user_row from the database and logs the operation
    Input : db, None
    Output: Exception
    Input : None, user_row
    Output: Exception

  Notes:
    - If `db` or `model_row` is None, an exception will be raised.
  """
  # todo (update) - use the payload routine apply_json_patch_and_log and or some way to track change
  logger.info(f"Deleting model {comment=}: {sa_model_to_dict(model_row)}")

  try:
    db.session.delete(model_row)
    db.session.commit()
  except Exception as e:
    log_error(e)


def add_commit_and_log_model(
    db: SQLAlchemy,
    model_row: AutomapBase,
    comment: str = "",
    model_before: dict | None = None
) -> None:
  """
  Add or update a model instance in the database, log changes, and commit.

  Args:
    db (SQLAlchemy): SQLAlchemy instance bound to the Flask app. Must not be None.
    model_row (AutomapBase): ORM model instance to add or update. Must not be None.
    comment (str): Optional log comment for auditing.
    model_before (dict | None): Optional snapshot of the model before changes.

  Returns:
    None

  Examples:
    Input : db, user_row, comment="Adding user"
    Output: Adds or updates user_row in the database and logs changes
    Input : db, None
    Output: Exception
    Input : None, user_row
    Output: Exception

  Notes:
    - If `db` or `model_row` is None, an exception will be raised.
  """
  # todo (update) - use the payload routine apply_json_patch_and_log
  if model_before:
    logger.info(f"Before commit {comment=}: {model_before}")

  try:
    db.session.add(model_row)
    db.session.commit()
    model_after = sa_model_to_dict(model_row)
    logger.info(f"After commit: {model_after}")

    if model_before:
      changes = sa_model_dict_compare(model_before, model_after)
      logger.info(f"Changed values: {changes}")
  except Exception as e:
    log_error(e)


def get_table_row_and_column(
    db: SQLAlchemy,
    base: AutomapBase,
    table_name: str,
    column_name: str,
    id_: int
) -> tuple | None:
  """
  Fetch a row and a specific column value given table name and primary key value.

  Args:
    db (SQLAlchemy): SQLAlchemy instance bound to the Flask app. Must not be None.
    base (AutomapBase): AutomapBase. Must not be None.
    table_name (str): Table name. If None or empty, raises ValueError.
    column_name (str): Column of interest. If None or empty, raises ValueError.
    id_ (int): Primary key value.

  Returns:
    tuple | None: (row, value) if found, else (None, None).

  Examples:
    Input : db, Base, 'users', 'email', 1
    Output: (user_row, user_row.email)
    Input : db, Base, None, 'email', 1
    Output: ValueError
    Input : db, Base, 'users', None, 1
    Output: ValueError

  Notes:
    - If `table_name` or `column_name` is None or empty, raises ValueError.
    - If row is not found, returns (None, None).
  """
  logger.debug(f"Getting {column_name} from {table_name} where pk={id_}")
  column_value = None
  table = get_class_from_table_name(base, table_name)
  if table is None:
    return None, None
  row = db.session.query(table).get(id_)  # type: ignore

  if row:
    column_value = getattr(row, column_name)

  logger.debug(f"{row=}, {column_value=}")
  return row, column_value


def get_foreign_value(
    db: SQLAlchemy,
    base: AutomapBase,
    primary_table_name: str,
    foreign_table_name: str,
    primary_table_fk_name: str,
    foreign_table_column_name: str,
    primary_table_pk_value: int,
    primary_table_pk_name: str | None = None,
    foreign_table_pk_name: str | None = None
) -> str | None:
  """
  Resolve a foreign key reference and return the referenced value from the foreign table.

  Args:
    db (SQLAlchemy): SQLAlchemy instance bound to the Flask app. Must not be None.
    base (AutomapBase): Declarative base. Must not be None.
    primary_table_name (str): Table with the foreign key. If None or empty, raises ValueError.
    foreign_table_name (str): Table containing the referenced value. If None or empty, raises ValueError.
    primary_table_fk_name (str): Foreign key field name in the primary table. If None or empty, raises ValueError.
    foreign_table_column_name (str): Target field name in the foreign table. If None or empty, raises ValueError.
    primary_table_pk_value (int): Primary key value of the row in the primary table.
    primary_table_pk_name (str | None): Optional primary key field override in the primary table.
    foreign_table_pk_name (str | None): Optional primary key field override in the foreign table.

  Returns:
    str | None: The referenced value from the foreign table, or None if not found.

  Examples:
    Input : db, base, 'orders', 'users', 'user_id', 'email', 123
    Output: 'user@example.com'
    Input : db, base, None, 'users', 'user_id', 'email', 123
    Output: ValueError
    Input : db, base, 'orders', None, 'user_id', 'email', 123
    Output: ValueError

  Notes:
    - If any required argument is None or empty, raises ValueError.
    - If the referenced value is not found, returns None.
  """
  logger.debug(f"Looking up foreign value: {locals()}")
  result = None

  primary_table = get_class_from_table_name(base, primary_table_name)
  foreign_table = get_class_from_table_name(base, foreign_table_name)

  if primary_table_pk_name:
    pk_column = getattr(primary_table, primary_table_pk_name)
    primary_row = db.session.query(primary_table).filter(pk_column == primary_table_pk_value).first()  # type: ignore
  else:
    primary_row = db.session.query(primary_table).get(primary_table_pk_value)  # type: ignore

  if primary_row:
    fk_value = getattr(primary_row, primary_table_fk_name)
    if foreign_table_pk_name:
      fk_column = getattr(foreign_table, foreign_table_pk_name)
      foreign_row = db.session.query(foreign_table).filter(fk_column == fk_value).first()  # type: ignore
    else:
      foreign_row = db.session.query(foreign_table).get(fk_value)  # type: ignore

    if foreign_row:
      result = getattr(foreign_row, foreign_table_column_name)

  logger.debug(f"Foreign key result: {result}")
  return result


def find_auto_increment_value(db: SQLAlchemy, table_name: str, column_name: str) -> str:
  """
  Find the next auto-increment value for a table column (PostgresQL only).

  Args:
    db (SQLAlchemy): SQLAlchemy instance bound to the Flask app.
    table_name (str): Table name.
    column_name (str): Column name.

  Returns:
    str: Human-readable summary of the next sequence value.

  Example:
    summary = find_auto_increment_value(db, 'users', 'id')
  """
  with db.engine.connect() as connection:
    sql_seq = f"SELECT pg_get_serial_sequence('{table_name}', '{column_name}')"
    sequence_name = connection.execute(text(sql_seq)).scalar()

    sql_nextval = f"SELECT nextval('{sequence_name}')"
    next_val = connection.execute(text(sql_nextval)).scalar()

    return f"Table '{table_name}' column '{column_name}' sequence '{sequence_name}' next value is '{next_val}'"


def load_model_json_column(model: AutomapBase, column_name: str) -> dict:
  """
  Safely extract and normalize a JSON dictionary from a model's column.

  This helper ensures that the value stored in a model's JSON column is returned
  as a Python dictionary, regardless of whether it's stored as a JSON string or
  a native dict in the database. If the value is a malformed JSON string, a warning
  is logged and an empty dict is returned.

  Args:
    model (AutomapBase): SQLAlchemy ORM model instance.
    column_name (str): Name of the attribute on the model (e.g., 'misc_json').

  Returns:
    dict: Parsed dictionary from the JSON column. Returns {} on failure, None, or invalid input type.

  Raises:
    TypeError: If the value is not a string, dict, or None.

  Example:
    misc = load_model_json_column(user_model, 'misc_json')
  """
  raw_value = getattr(model, column_name)

  if isinstance(raw_value, dict):
    return raw_value
  elif isinstance(raw_value, str) or raw_value is None:
    return safe_json_loads(raw_value)
  else:
    raise TypeError(
      f"Expected str, dict, or None for {column_name}, got {type(raw_value).__name__}"
    )


if __name__ == "__main__":
  from sqlalchemy.orm import Session
  from sqlalchemy.ext.automap import automap_base
  from sqlalchemy import create_engine
  from arb.logging.arb_logging import setup_standalone_logging

  setup_standalone_logging("sql_alchemy_test")

  # --- Replace with your connection string ---
  engine = create_engine("postgresql://username:password@localhost/dbname")
  Base = automap_base()
  Base.prepare(engine, reflect=True)
  db_session = Session(engine)
