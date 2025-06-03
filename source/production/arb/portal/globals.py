"""
Global variables and dropdown selector loading for Flask/SQLAlchemy applications.

This module provides the `Globals` class for holding runtime-initialized
data structures such as dropdown selectors and database column type mappings.

Primary Uses:
  - Prevent circular imports in SQLAlchemy/Flask environments
  - Store shared type and dropdown definitions used throughout the app

Notes:
    * Globals are not intended to be mutable after initialization.
    * This pattern centralizes dropdown and type mapping logic for app-wide reuse.
    * If a value does not need to be initialized at runtime and does not change, it
      should be in the constants.py file instead.
"""
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from arb.__get_logger import get_logger

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


class Globals:
  """
  Central class for holding runtime-global mappings used in the Flask app.

  Attributes:
      db_column_types (dict): Mapping of database columns to SQLAlchemy and Python types.
      drop_downs (dict): HTML <select> dropdown mappings for form fields.
      drop_downs_contingent (dict): Conditional dropdown logic for dependent selectors.
  """

  db_column_types = {}
  drop_downs = {}
  drop_downs_contingent = {}

  @classmethod
  def load_drop_downs(cls, flask_app: Flask, db: SQLAlchemy) -> None:
    """
    Load dropdown data from hardcoded configuration and cache it in the Globals class.

    Args:
        flask_app (Flask): The Flask application instance (used for context safety).
        db (SQLAlchemy): SQLAlchemy database instance (not used here but included for consistency).

    Returns:
        None

    Notes:
        - This function imports a dynamic dropdown generator from `db_hardcoded`.
        - Cached values are used globally for all WTForms rendering.
    """
    from arb.portal.db_hardcoded import get_excel_dropdown_data

    logger.debug("In load_drop_downs()")

    Globals.drop_downs, Globals.drop_downs_contingent = get_excel_dropdown_data()

    logger.debug(f"Globals.drop_downs={Globals.drop_downs}")
    logger.debug(f"Globals.drop_downs_contingent={Globals.drop_downs_contingent}")

  @classmethod
  def load_type_mapping(cls, flask_app: Flask, db: SQLAlchemy, base) -> None:
    """
    Determine and store the SQLAlchemy and Python types for each database column.

    Args:
        flask_app (Flask): The Flask application instance.
        db (SQLAlchemy): SQLAlchemy instance bound to a live DB.
        base (DeclarativeMeta): Reflected SQLAlchemy automap base.

    Returns:
        None

    Example:
        >>> Globals.load_type_mapping(app, db, base)
        >>> print(Globals.db_column_types["incidence"]["id_plume"])
        {'db_type': 'INTEGER', 'sa_type': Integer, 'py_type': <class 'int'>}

    Notes:
        - This routine relies on `arb.utils.sql_alchemy.get_sa_automap_types`
          to extract engine metadata for all tables in the reflected base.
    """
    from arb.utils.sql_alchemy import get_sa_automap_types

    with flask_app.app_context():
      engine = db.engine
      Globals.db_column_types = get_sa_automap_types(engine, base)

    logger.debug(f"Database type mapping: Globals.db_column_types={Globals.db_column_types}")
