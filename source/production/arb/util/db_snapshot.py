"""
db_snapshot.py

Utilities and documentation for using a Postgres-to-SQLite snapshot workflow for integration testing.

This module provides:
  - Documentation and helper functions for exporting a Postgres database and converting it to SQLite.
  - Functions to check and switch SQLALCHEMY_DATABASE_URI for testing.
  - Validation helpers for SQLite test snapshots.

Note: Actual DB conversion is performed with external tools (see docstring).
"""
import os
import logging
from sqlalchemy.engine.url import make_url

logger = logging.getLogger(__name__)

SNAPSHOT_SQLITE_PATH = os.environ.get('SQLITE_SNAPSHOT_PATH', 'arb_test_snapshot.sqlite')


def get_sqlalchemy_uri_for_testing() -> str:
  """
  Return the SQLAlchemy URI for the SQLite snapshot, for use in test configs.

  Returns:
    str: SQLAlchemy URI for the local SQLite snapshot file.

  Example:
    >>> get_sqlalchemy_uri_for_testing()
    'sqlite:///arb_test_snapshot.sqlite'
  """
  return f"sqlite:///{SNAPSHOT_SQLITE_PATH}"


def is_sqlite_uri(uri: str) -> bool:
  """
  Check if a given SQLAlchemy URI points to a SQLite database.

  Args:
    uri (str): SQLAlchemy database URI.

  Returns:
    bool: True if the URI is for SQLite, False otherwise.
  """
  try:
    url = make_url(uri)
    return url.drivername.startswith('sqlite')
  except Exception as e:
    logger.warning(f"Could not parse URI: {uri}. Error: {e}")
    return False


def print_snapshot_workflow():
  """
  Print step-by-step instructions for exporting a Postgres DB and converting it to SQLite for local testing.

  Steps:
    1. At work, export the Postgres DB (schema + data):
       pg_dump --data-only --inserts --column-inserts -U <user> -h <host> <dbname> > db_dump.sql
    2. Convert the dump to SQLite using a tool like pg2sqlite or pgloader:
       pg2sqlite db_dump.sql arb_test_snapshot.sqlite
       # or
       pgloader postgres://user:pass@host/dbname sqlite:///arb_test_snapshot.sqlite
    3. Copy arb_test_snapshot.sqlite to your home machine.
    4. Set your test config to use:
       SQLALCHEMY_DATABASE_URI = 'sqlite:///arb_test_snapshot.sqlite'
    5. Run your tests as usual.

  Notes:
    - Not all Postgres features are supported in SQLite. Mark/skip tests as needed.
    - Resync the snapshot as needed to keep data fresh.
  """
  print("""
  === Postgres to SQLite Snapshot Workflow ===
  1. At work, export the Postgres DB (schema + data):
     pg_dump --data-only --inserts --column-inserts -U <user> -h <host> <dbname> > db_dump.sql
  2. Convert the dump to SQLite using a tool like pg2sqlite or pgloader:
     pg2sqlite db_dump.sql arb_test_snapshot.sqlite
     # or
     pgloader postgres://user:pass@host/dbname sqlite:///arb_test_snapshot.sqlite
  3. Copy arb_test_snapshot.sqlite to your home machine.
  4. Set your test config to use:
     SQLALCHEMY_DATABASE_URI = 'sqlite:///arb_test_snapshot.sqlite'
  5. Run your tests as usual.

  Notes:
    - Not all Postgres features are supported in SQLite. Mark/skip tests as needed.
    - Resync the snapshot as needed to keep data fresh.
  """)


def validate_sqlite_snapshot(path: str = SNAPSHOT_SQLITE_PATH) -> bool:
  """
  Check if the SQLite snapshot file exists and is a valid SQLite DB.

  Args:
    path (str): Path to the SQLite file.

  Returns:
    bool: True if the file exists and is a valid SQLite DB, False otherwise.
  """
  import sqlite3
  if not os.path.exists(path):
    logger.warning(f"SQLite snapshot file not found: {path}")
    return False
  try:
    with sqlite3.connect(path) as conn:
      conn.execute('SELECT name FROM sqlite_master LIMIT 1;')
    return True
  except Exception as e:
    logger.error(f"Failed to validate SQLite DB at {path}: {e}")
    return False 