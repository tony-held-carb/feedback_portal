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
- PostgreSQL sequence inspection (`find_auto_increment_value`)
- JSON column loader (`load_model_json_column`)

Type Hints:
-----------
- `db (SQLAlchemy)`: Flask-SQLAlchemy database instance with .session and .engine.
- `base (DeclarativeMeta)`: Declarative or automapped SQLAlchemy base (e.g., via automap_base()).
- `model (DeclarativeMeta)`: SQLAlchemy ORM model class or instance.
- `session (Session)`: SQLAlchemy session object.

Usage Notes:
------------
- Supports PostgreSQL features like sequence inspection via `pg_get_serial_sequence`.
- Logging is integrated for debugging and auditing.
- Compatible with Python 3.10+ syntax (PEP 604 union types).

Version:
    1.0.0
"""

import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, inspect, text
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine

from arb.__get_logger import get_logger
from arb.utils.misc import log_error

__version__ = "1.0.0"
logger, pp_log = get_logger()


def sa_model_diagnostics(model: DeclarativeMeta, comment: str = "") -> None:
  """
  Log diagnostic details about a SQLAlchemy model instance.

  Args:
      model (DeclarativeMeta): SQLAlchemy model instance.
      comment (str): Optional comment header for log output.

  Returns:
      None

  Example:
    >>> sa_model_diagnostics(user, comment="Inspecting User")
  """
  logger.debug(f"Diagnostics for model of type {type(model)=}")
  if comment:
    logger.debug(f"{comment}")
  logger.debug(f"{model=}")

  fields = get_sa_fields(model)
  for key in fields:
    value = getattr(model, key)
    logger.debug(f"{key} {type(value)} = ({value})")


def get_sa_fields(model: DeclarativeMeta) -> list[str]:
  """
  Get a sorted list of column names for a SQLAlchemy model.

  Args:
      model (DeclarativeMeta): SQLAlchemy model instance or class.

  Returns:
      list[str]: Alphabetically sorted list of column attribute names.

  Example:
    >>> get_sa_fields(User)
    ['email', 'id', 'name']
  """
  inst = inspect(model)
  model_fields = [c_attr.key for c_attr in inst.mapper.column_attrs]
  model_fields.sort()
  return model_fields


def get_sa_column_types(model: DeclarativeMeta, is_instance: bool = False) -> dict:
  """
  Return a mapping of each column to its SQLAlchemy and Python types.

  Args:
      model (DeclarativeMeta): SQLAlchemy model instance or class.
      is_instance (bool): True if `model` is an instance, False if a class.

  Returns:
      dict: Mapping from column names to a dict with 'sqlalchemy_type' and 'python_type'.

  Example:
    >>> get_sa_column_types(User)
    {
      'id': {'sa_type': 'Integer', 'py_type': 'int'},
      'email': {'sa_type': 'String', 'py_type': 'str'}
    }
  """

  # Get the table inspector for the model
  if is_instance:
    inspector = inspect(type(model))
  else:
    inspector = inspect(model)

  logger.debug(f"\t{model=}")
  logger.debug(f"\t{inspector=}")

  columns_info = {}
  for column in inspector.columns:
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


def get_sa_automap_types(engine: Engine, base: DeclarativeMeta) -> dict:
  """
  Return column type metadata for all mapped classes.

  Args:
      engine (Engine): SQLAlchemy engine instance.
      base (DeclarativeMeta): Automap base prepared with reflected metadata.

  Returns:
      dict: Nested mapping: table -> column -> type category.
            The dict is database table names, columns names, and datatypes with the structure:
              result[table_name][column_name][kind] = type
              where: kind can be 'database_type', 'sqlalchemy_type', or 'python_type'

  Notes:
    - base likely created with:
        base = automap_base()
        base.prepare(db.engine, reflect=True)
  """
  logger.debug(f"calling get_sa_automap_types()")

  result = {}
  inspector = inspect(engine)

  # Loop through all the mapped classes (tables)
  # print(f"{type(base)=}")
  # print(f"{type(base.classes)=}")
  for class_name, mapped_class in base.classes.items():
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
  Compare two model dictionaries and return changed fields.

  Args:
      model_before (dict): Original state.
      model_after (dict): New state.

  Returns:
      dict: Changed fields and their new values.
  """
  changes = {}
  for field in model_after:
    if field not in model_before or model_before[field] != model_after[field]:
      changes[field] = model_after[field]
  return changes


def sa_model_to_dict(model: DeclarativeMeta) -> dict:
  """
  Convert a SQLAlchemy model to a Python dictionary.

  Args:
      model (DeclarativeMeta): SQLAlchemy model.

  Returns:
      dict: Dictionary with column names as keys and values from the model.
  """
  model_as_dict = {}
  fields = get_sa_fields(model)
  for field in fields:
    value = getattr(model, field)
    model_as_dict[field] = value

  return model_as_dict


def table_to_list(base: DeclarativeMeta, session: Session, table_name: str) -> list[dict]:
  """
  Convert all rows of a mapped table to a list of dicts.

  Args:
      base (DeclarativeMeta): Automap base.
      session (Session): SQLAlchemy session.
      table_name (str): Table name to query.

  Returns:
      list[dict]: List of row dictionaries.
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


def get_class_from_table_name(base: DeclarativeMeta| None, table_name: str):
  """
  Retrieves the mapped class for a given table name.

  Args:
      base (DeclarativeMeta): SQLAlchemy declarative base.
      table_name (str): Database table name.

  Returns:
      DeclarativeMeta | None: Mapped SQLAlchemy ORM class, or None if not found.

  Notes:
  - To access the class mapped to a specific table name in SQLAlchemy without directly using _class_registry,
    you can use the Base.metadata object, which stores information about all mapped tables.

  - get_class_from_table_name seems to fail from gpt refactor, so i kept my original code here.
  - it failed because my old test of is not None was changed to if - be on the lookout for other subtle bugs like this
  """
  try:
    # Look up the table in metadata and find its mapped class
    table = base.metadata.tables.get(table_name)
    if table is not None:
      for mapper in base.registry.mappers:
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
    base: DeclarativeMeta,
    table_name: str,
    colum_name_pk: str | None = None,
    ascending: bool = True
) -> list:
  """
    Retrieve all rows from a table, optionally sorted by a column.

    Args:
        db: SQLAlchemy db object.
        base (DeclarativeMeta): Declarative base.
        table_name (str): Table name.
        colum_name_pk (str | None): Column to sort by.
        ascending (bool): Sort order.

    Returns:
        list[DeclarativeMeta]: List of ORM model instances.
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


def delete_commit_and_log_model(db: SQLAlchemy, model_row: DeclarativeMeta, comment: str = "") -> None:
  """
  Delete a model instance, log it, and commit the change.

  Args:
      db (SQLAlchemy): SQLAlchemy instance bound to the Flask app.
      model_row (DeclarativeMeta): ORM model instance.
      comment (str): Optional log comment.
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
    model_row: DeclarativeMeta,
    comment: str = "",
    model_before: dict | None = None
) -> None:
  """
  Add or update a model instance, log changes, and commit.

  Args:
      db (SQLAlchemy): SQLAlchemy instance bound to the Flask app.
      model_row (DeclarativeMeta): ORM model instance.
      comment (str): Optional log comment.
      model_before (dict | None): Optional snapshot before changes.
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
    base: DeclarativeMeta,
    table_name: str,
    column_name: str,
    id_: int
) -> tuple | None:
  """
  Fetch a row and column value given table name and primary key.

  Args:
      db (SQLAlchemy): SQLAlchemy instance bound to the Flask app.
      base (DeclarativeMeta): Declarative base.
      table_name (str): Table name.
      column_name (str): Column of interest.
      id_ (int): Primary key value.

  Returns:
      tuple | None: (row, value) if found, else (None, None).
  """
  logger.debug(f"Getting {column_name} from {table_name} where pk={id_}")
  column_value = None
  table = get_class_from_table_name(base, table_name)
  row = db.session.query(table).get(id_)

  if row:
    column_value = getattr(row, column_name)

  logger.debug(f"{row=}, {column_value=}")
  return row, column_value


def get_foreign_value(
    db: SQLAlchemy,
    base: DeclarativeMeta,
    primary_table_name: str,
    foreign_table_name: str,
    primary_table_fk_name: str,
    foreign_table_column_name: str,
    primary_table_pk_value: int,
    primary_table_pk_name: str | None = None,
    foreign_table_pk_name: str | None = None
) -> str | None:
  """
    Resolve a foreign key reference and return its value.

    Args:
        db (SQLAlchemy): SQLAlchemy instance bound to the Flask app.
        base (DeclarativeMeta): Declarative base.
        primary_table_name (str): Table with FK.
        foreign_table_name (str): Table with desired value.
        primary_table_fk_name (str): FK field name.
        foreign_table_column_name (str): Target field name in foreign table.
        primary_table_pk_value (int): PK value of row in primary table.
        primary_table_pk_name (str | None): Optional PK field override.
        foreign_table_pk_name (str | None): Optional PK override in foreign table.

    Returns:
        str | None: Foreign value if found, else None.
  """
  logger.debug(f"Looking up foreign value: {locals()}")
  result = None

  primary_table = get_class_from_table_name(base, primary_table_name)
  foreign_table = get_class_from_table_name(base, foreign_table_name)

  if primary_table_pk_name:
    pk_column = getattr(primary_table, primary_table_pk_name)
    primary_row = db.session.query(primary_table).filter(pk_column == primary_table_pk_value).first()
  else:
    primary_row = db.session.query(primary_table).get(primary_table_pk_value)

  if primary_row:
    fk_value = getattr(primary_row, primary_table_fk_name)
    if foreign_table_pk_name:
      fk_column = getattr(foreign_table, foreign_table_pk_name)
      foreign_row = db.session.query(foreign_table).filter(fk_column == fk_value).first()
    else:
      foreign_row = db.session.query(foreign_table).get(fk_value)

    if foreign_row:
      result = getattr(foreign_row, foreign_table_column_name)

  logger.debug(f"Foreign key result: {result}")
  return result


def find_auto_increment_value(db: SQLAlchemy, table_name: str, column_name: str) -> str:
  """
  Find the next auto-increment value for a table column (PostgreSQL only).

  Args:
      db (SQLAlchemy): SQLAlchemy instance bound to the Flask app.
      table_name (str): Table name.
      column_name (str): Column name.

  Returns:
      str: Human-readable summary of the next sequence value.
  """
  with db.engine.connect() as connection:
    sql_seq = f"SELECT pg_get_serial_sequence('{table_name}', '{column_name}')"
    sequence_name = connection.execute(text(sql_seq)).scalar()

    sql_nextval = f"SELECT nextval('{sequence_name}')"
    next_val = connection.execute(text(sql_nextval)).scalar()

    return f"Table '{table_name}' column '{column_name}' sequence '{sequence_name}' next value is '{next_val}'"


def load_model_json_column(model: DeclarativeMeta, column_name: str) -> dict:
  """
  Safely extract and normalize a JSON dictionary from a model's column.

  This helper ensures that the value stored in a model's JSON column is returned
  as a Python dictionary, regardless of whether it's stored as a JSON string or
  native dict in the database.

  If the value is a malformed JSON string, a warning is logged and an empty dict is returned.

  Args:
      model (DeclarativeMeta): SQLAlchemy ORM model instance.
      column_name (str): Name of the attribute on the model (e.g., 'misc_json').

  Returns:
      dict: Parsed dictionary from the JSON column. Defaults to {} on failure or None.
  """
  raw_value = getattr(model, column_name)
  if isinstance(raw_value, str):
    try:
      return json.loads(raw_value)
    except json.JSONDecodeError:
      logger.warning(f"Corrupt JSON found in {column_name}, resetting to empty dict.")
      return {}
  elif raw_value is None:
    return {}
  elif isinstance(raw_value, dict):
    return raw_value
  else:
    raise TypeError(f"Expected str, dict, or None for {column_name}, got {type(raw_value).__name__}")


def run_diagnostics(db: SQLAlchemy, base: DeclarativeMeta, session: Session) -> None:
  """
  Run diagnostics to validate SQLAlchemy utilities in this module.

  This function performs:
    - Model diagnostics
    - Type inspection
    - Conversion to dictionary
    - Change detection
    - Table row extraction
    - Primary and foreign key access

  Args:
      db: SQLAlchemy db object.
      base (DeclarativeMeta): Declarative or automap base.
      session (Session): Active SQLAlchemy session.

  Example:
      >>> run_diagnostics(db, base, db.session)
  """
  print("Running diagnostics for sqlalchemy_util.py...")

  # Use first available mapped class
  class_names = list(base.classes.keys())
  assert class_names, "No mapped tables found"

  test_table = class_names[0]
  cls = base.classes[test_table]

  row = session.query(cls).first()
  assert row, f"No rows in table '{test_table}'"

  print(f"Using table: {test_table}")

  # Field listing
  fields = get_sa_fields(row)
  print(f"Fields: {fields}")

  # Type info
  types = get_sa_column_types(row)
  print(f"Column types: {types}")

  # Dict conversion and comparison
  d1 = sa_model_to_dict(row)
  d2 = d1.copy()
  d2[fields[0]] = "__CHANGED__"
  changes = sa_model_dict_compare(d1, d2)
  assert fields[0] in changes, "Change detection failed"

  # Table to list
  all_rows = table_to_list(base, session, test_table)
  assert isinstance(all_rows, list) and all_rows, "table_to_list failed"

  # Try auto-increment value if PK exists
  pk_column = fields[0]
  if hasattr(cls, pk_column):
    result = find_auto_increment_value(db, test_table, pk_column)
    print(f"Auto-increment: {result}")

  print("All diagnostics completed successfully.")


if __name__ == "__main__":
  from sqlalchemy.orm import Session
  from sqlalchemy.ext.automap import automap_base
  from sqlalchemy import create_engine
  import logging

  logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
  )

  # --- Replace with your connection string ---
  engine = create_engine("postgresql://username:password@localhost/dbname")
  Base = automap_base()
  Base.prepare(engine, reflect=True)
  db_session = Session(engine)


  class DummyDB:
    engine = engine
    session = db_session


  run_diagnostics(DummyDB, Base, db_session)
