"""
Miscellaneous database utilities.

Notes:
"""
from flask import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.automap import automap_base

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
                      dry_run: bool = True) -> None:
  """
  Remove key/value pairs from a JSON column where the value matches `remove_value`.

  Args:
      db: Flask-SQLAlchemy `db` object containing the model registry and session.
      table_name (str): Name of the table to query.
      json_column_name (str): Name of the JSON column to cleanse.
      remove_value (str): Value to match for deletion. Matching key/value pairs will be removed.
      dry_run (bool): If True, shows what would be done without committing changes.

  Raises:
      ValueError: If table or column is not found.
  """
  logger.debug(f"cleanse_misc_json called")

  try:
    Base = db.Model._decl_class_registry
    model_cls = next((cls for cls in Base.values()
                      if hasattr(cls, "__tablename__") and cls.__tablename__ == table_name), None)
    if model_cls is None:
      raise ValueError(f"Table '{table_name}' not found in model registry.")

    if not hasattr(model_cls, json_column_name):
      raise ValueError(f"Column '{json_column_name}' not found in table '{table_name}'.")

    rows = db.session.query(model_cls).all()
    count_total = len(rows)
    count_modified = 0

    for row in rows:
      json_data = getattr(row, json_column_name) or {}

      original_keys = set(json_data.keys())
      filtered = {k: v for k, v in json_data.items() if v != remove_value}
      filtered_keys = set(filtered.keys())

      if original_keys != filtered_keys:
        setattr(row, json_column_name, filtered)
        from sqlalchemy.orm.attributes import flag_modified
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
