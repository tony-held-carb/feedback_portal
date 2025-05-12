"""
Miscellaneous database utility functions for schema manipulation and raw SQL execution.

Notes:
    - This module was designed of use with the SQLite version of the portal and are no longer in use.
    - These functions are meant for internal administrative use.
    - Use `db_drop_all()` with caution as it permanently deletes all tables.
"""

import sqlite3
from pathlib import Path
from typing import Optional, Union

from flask import Flask
import arb.__get_logger as get_logger

__version__ = "1.0.0"
logger, pp_log = get_logger.get_logger(__name__, __file__)


def db_drop_all(flask_app: Flask, db) -> None:
    """
    Drop all database tables within the context of the provided Flask app.

    Args:
        flask_app (Flask): A Flask app instance, required for application context.
        db (SQLAlchemy): An instance of SQLAlchemy with access to metadata.

    Returns:
        None

    Warnings:
        This function will irreversibly remove all tables in the database. Use with caution.

    Example:
        >>> from flask import Flask
        >>> from flask_sqlalchemy import SQLAlchemy
        >>> app = Flask(__name__)
        >>> db = SQLAlchemy(app)
        >>> db_drop_all(app, db)
    """
    logger.debug("Dropping all database tables")
    with flask_app.app_context():
        db.drop_all()


def execute_sql_script(
    script_path: Optional[Union[str, Path]] = None,
    connection: Optional[sqlite3.Connection] = None
) -> None:
    """
    Execute a raw SQL script using the provided or default SQLite connection.

    Args:
        script_path (str | Path, optional): Path to the SQL script file. Defaults to '../sql_scripts/script_01.sql'.
        connection (sqlite3.Connection, optional): SQLite connection to use. If None, defaults to 'app.db'.

    Returns:
        None

    Example:
        >>> execute_sql_script("schema.sql")
        >>> execute_sql_script(Path("scripts/init.sql"))

    Notes:
        - This function assumes the script contains valid SQLite statements.
        - Commits and closes the connection automatically after execution.
    """
    script_path = Path(script_path or "../sql_scripts/script_01.sql")
    connection = connection or sqlite3.connect("app.db")

    logger.debug(f"Executing SQL script from: {script_path}")
    with open(script_path, encoding="utf-8") as f:
        connection.executescript(f.read())

    connection.commit()
    connection.close()
    logger.debug("SQL script executed and connection closed.")
