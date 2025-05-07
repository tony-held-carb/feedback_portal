"""
SQLAlchemy related utilities.

Provides tools for:
  - Model diagnostics
  - Column and type inspection
  - Table-level introspection
  - Row operations and logging
  - Foreign key traversal and PK/sequence lookup

Version:
    1.0.0

Notes:
    - All type hints use Python 3.10+ modern syntax (e.g., str | None).
    - Assumes SQLAlchemy ORM with automap or declarative base integration.
    - Logs all major operations for debugging and auditing.
"""
from sqlalchemy import desc, inspect, text

import arb.__get_logger as get_logger
from arb.utils.misc import log_error

__version__ = "1.0.0"
logger, pp_log = get_logger.get_logger(__name__, __file__)


def sa_model_diagnostics(model, comment: str = "") -> None:
  """
  Log diagnostic details about a SQLAlchemy model instance.

  Args:
      model: SQLAlchemy model instance.
      comment (str): Optional header for logs.

  Example:
      >>> sa_model_diagnostics(user, comment="Inspecting User")
  """
  logger.debug(f"Diagnostics for model of type {type(model)=}")
  if comment:
    logger.debug(f"{comment}")
  logger.debug(f"{model=}\n")

  fields = get_sa_fields(model)
  for key in fields:
    value = getattr(model, key)
    logger.debug(f"{key} {type(value)} = ({value})")


def get_sa_fields(model) -> list[str]:
  """
  Get sorted list of column names for a SQLAlchemy model.

  Args:
      model: SQLAlchemy ORM model instance or class.

  Returns:
      list[str]: List of column/attribute names.

  Example:
      >>> get_sa_fields(user)
      ['email', 'id', 'name']
  """
  inst = inspect(model)
  model_fields = [c_attr.key for c_attr in inst.mapper.column_attrs]
  model_fields.sort()
  return model_fields


def get_sa_column_types(model, is_instance: bool = True) -> dict[str, dict]:
  """
  Get SQLAlchemy and Python types for each column of a model.

  Args:
      model: SQLAlchemy model instance or class.
      is_instance (bool): True if model is an instance, False if a class.

  Returns:
      dict: Mapping of column names to type information.
  """

  # Get the table inspector for the model
  if is_instance:
    inspector = inspect(type(model))
  else:
    inspector = inspect(model)

  logger.debug(f"\n\t{model=}")
  logger.debug(f"\n\t{inspector=}")

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


def get_sa_automap_types(engine, base):
  """
  Return the automap types associated with a sqlalchemy model to determine underlying DB, SQLAlchemy, and python
  data types associated with each column's data.

  Args:
    engine (sqlalchemy.engine.Engine): SQLAlchemy engine instance
    base (DeclarativeMeta): SQLAlchemy declarative base

  Notes:
    base likely created with:
      base = automap_base()
      base.prepare(db.engine, reflect=True)

  Returns (dict): Dictionary of database table names, columns names, and datatypes with the structure:
    result[table_name][column_name][kind] = type
    where: kind can be 'database_type', 'sqlalchemy_type', or 'python_type',
  """
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


def sa_model_to_dict(model):
  """
  Convert a sqlalchemy model to a python dictionary.

  Args:
    model: SQLAlchemy model

  Returns (dict): python dictionary with model column names as keys and column values as values.
  """
  model_as_dict = {}
  fields = get_sa_fields(model)
  for field in fields:
    value = getattr(model, field)
    model_as_dict[field] = value

  return model_as_dict


def table_to_list(base, session, table_name: str) -> list[dict]:
  """
  Convert all rows of a mapped table to a list of dicts.

  Args:
      base: Automap base.
      session: SQLAlchemy session.
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


def get_class_from_table_name(base, table_name):
  """
  Retrieves the table from SQLAlchemy's metadata by the table_name.
  If the table is not mapped, this returns None.

  Args:
    base (DeclarativeMeta): SQLAlchemy declarative base
    table_name (str): database table name

  Returns (Mapper): table as mapped class of database

  Notes:
    * To access the class mapped to a specific table name in SQLAlchemy without directly using _class_registry,
    you can use the Base.metadata object, which stores information about all mapped tables.

    * get_class_from_table_name seems to fail from gpt refactor, so i kept my original code here.
    * it failed because my old test of is not None was changed to if - be on the lookout for other subtle bugs like this
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


def get_rows_by_table_name(db,
                           base,
                           table_name: str,
                           colum_name_pk: str | None = None,
                           ascending: bool = True
                           ):
  """
  Retrieve all rows from a table, optionally sorted by a column.

  Args:
      db: SQLAlchemy db object.
      base: Declarative base.
      table_name (str): Table name.
      colum_name_pk (str | None): Column to sort by.
      ascending (bool): Sort order.

  Returns:
      list: List of ORM model instances.
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


def delete_commit_and_log_model(db, model_row, comment: str = "") -> None:
  """
  Delete a model instance, log it, and commit the change.

  Args:
      db: SQLAlchemy db.
      model_row: ORM model instance.
      comment (str): Optional log comment.
  """
  logger.info(f"Deleting model {comment=}: {sa_model_to_dict(model_row)}")

  try:
    db.session.delete(model_row)
    db.session.commit()
  except Exception as e:
    log_error(e)


def add_commit_and_log_model(db,
                             model_row,
                             comment: str = "",
                             model_before: dict | None = None
                             ) -> None:
  """
  Add or update a model instance, log changes, and commit.

  Args:
      db: SQLAlchemy db.
      model_row: ORM model instance.
      comment (str): Optional log comment.
      model_before (dict | None): Optional snapshot before changes.
  """
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


def get_table_row_and_column(db,
                             base,
                             table_name: str,
                             column_name: str,
                             id_: int
                             ) -> tuple | None:
  """
  Fetch a row and column value given table name and primary key.

  Args:
      db: SQLAlchemy db.
      base: Declarative base.
      table_name (str): Table name.
      column_name (str): Column of interest.
      id_ (int): Primary key value.

  Returns:
      tuple: (row, value) or (None, None)
  """
  logger.debug(f"Getting {column_name} from {table_name} where pk={id_}")
  column_value = None
  table = get_class_from_table_name(base, table_name)
  row = db.session.query(table).get(id_)

  if row:
    column_value = getattr(row, column_name)

  logger.debug(f"{row=}, {column_value=}")
  return row, column_value


def get_foreign_value(db,
                      base,
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
      db: SQLAlchemy db.
      base: Declarative base.
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


def find_auto_increment_value(db, table_name: str, column_name: str) -> str:
  """
  Find the next auto-increment value for a table column (PostgreSQL only).

  Args:
      db: SQLAlchemy db.
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


def run_diagnostics(db, base, session) -> None:
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
      db: SQLAlchemy db object
      base: Declarative or automap base
      session: Active SQLAlchemy session

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
