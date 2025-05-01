"""
Global variables for a Flask/SQLAlchemy application.
Primarily used to for dropdown selectors and to avoid recursion issues of imports.
"""
from zoneinfo import ZoneInfo

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

  # consider
  # flask_app, base, and engine are initialized with load_type_mapping(), they are not used
  # elsewhere and are candidates for removal to make the code cleaner.
  flask_app: Flask = None
  base = None
  engine = None

  GPS_RESOLUTION = 5  # decimal digits required of users for GPS lat/long data
  PLEASE_SELECT = 'Please Select'  # select element value for disabled 'Please Select' option

  # Formatting schema for spreadsheet parsing
  XL_NUMBER_OF_TABS_CELL = "$B$7"
  XL_FORMATTING_SCHEMA_CELL = "$B$10"
  XL_FIRST_TAB_NAME_CELL = "$A$10"

  # California lat longs should be between 32° 30' N to 42° N and 114° 8' W to 124° 24' W
  MIN_LATITUDE = 32
  MAX_LATITUDE = 42
  MIN_LONGITUDE = -125
  MAX_LONGITUDE = -114

  # Datetime/timezone information
  UTC_TIME_ZONE = ZoneInfo("UTC")
  CA_TIME_ZONE = ZoneInfo("America/Los_Angeles")
  HTML_LOCAL_TIME_FORMAT = "%Y-%m-%dT%H:%M"

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
  def load_logger(cls, flask_app) -> None:
    """
    Loads logger to the global variable.  Likely an outdated usage.

    Args:
      flask_app (Flask): The Flask application instance.
    """
    Globals.logger = flask_app.logger
    Globals.logger.debug(f"{type(Globals.logger)=}, {Globals.logger=}")

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
      Globals.flask_app = flask_app
      Globals.engine = engine
      Globals.base = base
      Globals.db_column_types = get_sa_automap_types(engine, base)
    logger.debug(f"Database type mapping: {Globals.db_column_types=}")
