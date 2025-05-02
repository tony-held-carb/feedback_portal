"""
Global variables for a Flask/SQLAlchemy application.
Primarily used to for dropdown selectors and to avoid recursion issues of imports.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import arb.__get_logger as get_logger

logger, pp_log = get_logger.get_logger(__name__, __file__)


class Globals:
  """
  Global variables for a Flask/SQLAlchemy application.
  """
  db_column_types = {}
  drop_downs = {}
  drop_downs_contingent = {}

  @classmethod
  def load_drop_downs(cls, flask_app, db):
    """
    Loads dropdown values into the Flask application.

    Args:
      flask_app (Flask): The Flask application instance.
      db (SQLAlchemy): The SQLAlchemy database instance.

    Returns:
      None
    """
    from arb.portal.db_hardcoded import get_excel_dropdown_data

    logger.debug(f"In load_drop_downs()")

    Globals.drop_downs, Globals.drop_downs_contingent = get_excel_dropdown_data()

    logger.debug(f"{Globals.drop_downs=}")
    logger.debug(f"{Globals.drop_downs_contingent=}")

  @classmethod
  def load_type_mapping(cls, flask_app, db, base) -> None:
    """
    Save the flask_app, database, and base to global variables and determine
    the DB, SQLAlchemy, and python types associated with each database table

    Args:
      flask_app (Flask): flask app that will access database
      db (SQLAlchemy): SQLAlchemy database associated with a flask app
      base (DeclarativeMeta): SQLAlchemy declarative base
    """
    from arb.utils.sql_alchemy import get_sa_automap_types

    with flask_app.app_context():
      engine = db.engine
      Globals.db_column_types = get_sa_automap_types(engine, base)
    logger.debug(f"Database type mapping: {Globals.db_column_types=}")
