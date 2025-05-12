"""
Miscellaneous database utilities.

Notes:
"""
from flask import app

import arb.__get_logger as get_logger

__version__ = "1.0.0"
logger, pp_log = get_logger.get_logger(__name__, __file__)


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
