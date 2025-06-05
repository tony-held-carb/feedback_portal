"""
Miscellaneous database utilities.

Includes helpers for dropping tables, executing SQL scripts, auto-reflecting base metadata,
and bulk cleansing of JSON fields across database rows.

Intended for use in migrations, diagnostics, and administrative scripts.

Requires:
  - SQLAlchemy (for model and metadata operations)
  - A `db` object and an automapped or declarative `base` from the Flask app

Functions:
  - db_drop_all(): Drop all database tables
  - execute_sql_script(): Run external SQL script files
  - get_reflected_base(): Return a SQLAlchemy automap base
  - cleanse_misc_json(): Strip "Please Select" values from misc_json fields
"""
from pathlib import Path

from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.automap import AutomapBase, automap_base
from sqlalchemy.orm.attributes import flag_modified
import sqlite3

from arb.__get_logger import get_logger

__version__ = "1.0.0"
logger, pp_log = get_logger()


def db_drop_all(flask_app: Flask, db: SQLAlchemy) -> None:
  """
  Drop all database tables from the configured database.

  Args:
    flask_app (Flask): The Flask application object.
    db (SQLAlchemy): SQLAlchemy instance bound to the Flask app.

  Warning:
    This is irreversible — all tables will be deleted.
  """

  logger.debug("dropping all database tables")

  # Create database within app context
  # with flask_app.app_context():
  #   db.drop_all()


def execute_sql_script(script_path: str | Path = None,
                       connection: sqlite3.Connection | None = None) -> None:
  """
  Execute a SQL script using a provided or default SQLite connection.

  Args:
    script_path (str | Path | None): Path to the `.sql` script. Defaults to `../sql_scripts/script_01.sql`.
    connection (sqlite3.Connection | None): SQLite connection (defaults to `sqlite3.connect('app.db')` if None).
  """
  logger.debug(f"execute_sql_script() called with {script_path=}, {connection=}")

  if script_path is None:
    script_path = '../sql_scripts/script_01.sql'
  if connection is None:
    connection = sqlite3.connect('app.db')

  with open(script_path) as f:
    connection.executescript(f.read())

  connection.commit()
  connection.close()


def get_reflected_base(db: SQLAlchemy) -> AutomapBase:
  """
  Return a SQLAlchemy automap base using the existing metadata (no re-reflection).

  Args:
    db (SQLAlchemy): SQLAlchemy instance with metadata.

  Returns:
    AutomapBase: Reflected base class.
  """
  Base = automap_base(metadata=db.metadata)  # reuse metadata!
  Base.prepare(db.engine, reflect=False)  # no extra reflection
  return Base


def cleanse_misc_json(db: SQLAlchemy,
                      base: AutomapBase,
                      table_name: str,
                      json_column_name: str = "misc_json",
                      remove_value: str = "Please Select",
                      dry_run: bool = False) -> None:
  """
  Remove key/value pairs in a JSON column where value == `remove_value`.

  Args:
    db (SQLAlchemy): SQLAlchemy instance.
    base (AutomapBase): Declarative or automap base.
    table_name (str): Table name to target (e.g., 'incidences').
    json_column_name (str): Column name to scan (default: "misc_json").
    remove_value (str): Value to match for deletion (default: "Please Select").
    dry_run (bool): If True, logs changes but rolls back.

  Raises:
    ValueError: If table or column cannot be found or mapped.
    RuntimeError: On failure to commit or query.
  """

  from arb.utils.sql_alchemy import get_class_from_table_name

  model_cls = get_class_from_table_name(base, table_name)
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
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(row, json_column_name)
        count_modified += 1

    if dry_run:
      logger.info(f"[Dry Run] {count_modified} of {count_total} rows would be modified.")
      db.session.rollback()
    else:
      db.session.commit()
      logger.info(f"[Committed] {count_modified} of {count_total} rows modified.")

  except Exception as e:
    db.session.rollback()
    raise RuntimeError(f"Error during cleansing: {e}")
