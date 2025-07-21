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
import logging
import sqlite3
from pathlib import Path

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import AutomapBase, automap_base

__version__ = "1.0.0"
logger = logging.getLogger(__name__)


# def db_drop_all(flask_app: Flask, db: SQLAlchemy) -> None:
#   """
#   Drop all database tables from the configured database.
#
#   Args:
#     flask_app (Flask): The Flask application object.
#     db (SQLAlchemy): SQLAlchemy instance bound to the Flask app.
#
#   Warning:
#     This is irreversible — all tables will be deleted.
#   """
#
#   logger.debug(f"dropping all database tables")
#
#   # Create a database within app context
#   with flask_app.app_context():
#     db.drop_all()


def execute_sql_script(script_path: str | Path | None = None,
                       connection: sqlite3.Connection | None = None) -> None:
  """
  Execute an SQL script using a provided or default SQLite connection.

  Args:
    script_path (str | Path | None): Path to the `.sql` script. If None, defaults to '../sql_scripts/script_01.sql'.
      If an empty string is provided, a FileNotFoundError will be raised.
    connection (sqlite3.Connection | None): SQLite connection (defaults to `sqlite3.connect('app.db')` if None).

  Notes:
    - If `script_path` is None, a default path is used. If it is an empty string or invalid, FileNotFoundError will occur.
    - If `connection` is None, a new connection to 'app.db' is created.

  Raises:
    FileNotFoundError: If the script file does not exist or is an empty string.
    sqlite3.DatabaseError: If there is an error executing the script.

  Examples:
    Input : script_path=None, connection=None
    Output: Executes default script on 'app.db'
    Input : script_path="/tmp/test.sql", connection=None
    Output: Executes /tmp/test.sql on 'app.db'
    Input : script_path="", connection=None
    Output: FileNotFoundError
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
    db (SQLAlchemy): SQLAlchemy instance with metadata. Must not be None.

  Returns:
    AutomapBase: Reflected base class.

  Raises:
    AttributeError: If `db` is None or does not have valid metadata.

  Examples:
    Input : db (valid SQLAlchemy instance)
    Output: AutomapBase instance
    Input : db=None
    Output: AttributeError
  """
  base = automap_base(metadata=db.metadata)  # reuse metadata!
  base.prepare(db.engine, reflect=False)  # no extra reflection
  return base


def cleanse_misc_json(db: SQLAlchemy,
                      base: AutomapBase,  # base is a mapped base, not to be passed directly to query
                      table_name: str,
                      json_column_name: str = "misc_json",
                      remove_value: str = "Please Select",
                      dry_run: bool = False) -> None:
  """
  Remove key/value pairs in a JSON column where value == `remove_value`.

  Args:
    db (SQLAlchemy): SQLAlchemy instance. Must not be None.
    base (AutomapBase): Declarative or automap base. Must not be None.
    table_name (str): Table name to target (e.g., 'incidences'). If None or empty, raises ValueError.
    json_column_name (str): Column name to scan (default: "misc_json"). If None or empty, raises ValueError.
    remove_value (str): Value to match for deletion (default: "Please Select"). If None, removes all keys with value None.
    dry_run (bool): If True, logs changes but rolls back.

  Notes:
    - If `table_name` or `json_column_name` are invalid, a ValueError is raised.
    - If `remove_value` is None, all keys with value None are removed.
    - If the JSON column is not a dict, the row is skipped.
    - If `dry_run` is True, changes are rolled back after logging.

  Raises:
    ValueError: If table or column cannot be found or mapped.
    RuntimeError: On failure to commit or query.

  Examples:
    Input : db, base, table_name="incidences", json_column_name="misc_json", remove_value="Please Select", dry_run=True
    Output: Logs how many rows would be modified, rolls back changes
    Input : db, base, table_name="incidences", json_column_name="misc_json", remove_value=None, dry_run=False
    Output: Removes all keys with value None, commits changes
    Input : db, base, table_name=None
    Output: ValueError
    Input : db, base, table_name="incidences", json_column_name=None
    Output: ValueError
  """

  from arb.utils.sql_alchemy import get_class_from_table_name

  model_cls = get_class_from_table_name(base, table_name)
  if model_cls is None:
    raise ValueError(f"Table '{table_name}' not found or not mapped.")

  if not hasattr(model_cls, json_column_name):
    raise ValueError(f"Column '{json_column_name}' not found on model for table '{table_name}'.")

  try:
    rows = db.session.query(model_cls).all()  # type: ignore
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
