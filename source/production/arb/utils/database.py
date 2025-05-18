"""
Miscellaneous database utilities.

Notes:
"""
from flask import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm.attributes import flag_modified

from arb.__get_logger import get_logger

__version__ = "1.0.0"
logger, pp_log = get_logger()


def db_drop_all(flask_app: app, db) -> None:
  """
  Drop all database tables.  WARNING, you will lose all database tables (use with caution).
  """
  logger.debug("dropping all database tables")

  # Create database within app context
  with flask_app.app_context():
    db.drop_all()


def execute_sql_script(script_path=None, connection=None) -> None:
  """
  Execute SQL script for a connection.

  Args:
    script_path (str, Path): sql script to execute.
    connection:
  """
  import sqlite3
  logger.debug(f"execute_sql_script() called with {script_path=}, {connection=}")

  if script_path is None:
    script_path = '../sql_scripts/script_01.sql'
  if connection is None:
    connection = sqlite3.connect('app.db')

  with open(script_path) as f:
    connection.executescript(f.read())

  connection.commit()
  connection.close()


def get_reflected_base(db: SQLAlchemy) -> object:
  """
  Return an automapped base using already-reflected metadata if available.

  Args:
      db (SQLAlchemy): SQLAlchemy instance.

  Returns:
      base (DeclarativeMeta): Reflected base.
  """
  Base = automap_base(metadata=db.metadata)  # reuse metadata!
  Base.prepare(db.engine, reflect=False)  # no extra reflection
  return Base


def cleanse_misc_json(db,
                      table_name: str,
                      json_column_name: str = "misc_json",
                      remove_value: str = "Please Select",
                      dry_run: bool = False) -> None:
  """
  Remove key/value pairs from a JSON column where the value matches `remove_value`.

  Args:
      db: Flask-SQLAlchemy `db` object.
      table_name (str): Table name as a string (e.g., "incidences").
      json_column_name (str): JSON column on the table to clean (default = "misc_json").
      remove_value (str): Value to remove from the JSON dict.
      dry_run (bool): If True, makes no changes to the DB.

  Raises:
      ValueError: If the model class or column does not exist.
  """
  # 👇 Use your helper here
  from arb.utils.sql_alchemy import get_class_from_table_name

  model_cls = get_class_from_table_name(db.Model, table_name)
  if model_cls is None:
    raise ValueError(f"Table '{table_name}' not found or not mapped.")

  if not hasattr(model_cls, json_column_name):
    raise ValueError(f"Column '{json_column_name}' not found on model for table '{table_name}'.")

  try:
    rows = db.session.query(model_cls).all()
    count_total = len(rows)
    count_modified = 0

    for row in rows:
      json_data = getattr(row, json_column_name) or {}
      if not isinstance(json_data, dict):
        continue

      filtered = {k: v for k, v in json_data.items() if v != remove_value}
      if filtered != json_data:
        setattr(row, json_column_name, filtered)
        flag_modified(row, json_column_name)
        count_modified += 1

    if dry_run:
      print(f"[Dry Run] {count_modified} of {count_total} rows would be modified.")
      db.session.rollback()
    else:
      db.session.commit()
      print(f"[Committed] {count_modified} of {count_total} rows modified.")

  except SQLAlchemyError as e:
    db.session.rollback()
    raise RuntimeError(f"Database error during cleanse: {e}")
