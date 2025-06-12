"""
Global variables and dropdown selector loading for Flask/SQLAlchemy applications.

This module provides the `Globals` class for holding runtime-initialized
data structures such as dropdown selectors and database column type mappings.

Primary Uses:
  - Prevent circular imports in SQLAlchemy/Flask environments
  - Store shared type and dropdown definitions used throughout the app
  - Enable lazy initialization of values dependent on app context

Notes:
  - Globals are not intended to be mutable after initialization.
  - Centralizes dropdown and type mapping logic for app-wide reuse.
  - Static values that do not require runtime context should live in `constants.py`.
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
    db_column_types (dict[str, dict[str, dict[str, Any]]]): Mapping of table.column
      to SQLAlchemy type metadata (includes `db_type`, `sa_type`, `py_type`).
    drop_downs (dict[str, list[str]]): Field name to independent dropdown options.
    drop_downs_contingent (dict[str, dict[str, list[str]]]): Parent-dependent options
      for contingent dropdowns (e.g., county → list of subcounties).
  """

  db_column_types = {}
  drop_downs = {}
  drop_downs_contingent = {}

  @classmethod
  def load_drop_downs(cls, flask_app: Flask, db: SQLAlchemy) -> None:
    """
    Load dropdown data from hardcoded configuration and cache it globally.

    Args:
      flask_app (Flask): The active Flask app instance (not used in this function but passed for consistency).
      db (SQLAlchemy): SQLAlchemy instance (not used in this function but passed for consistency).

    Returns:
      None

    Notes:
      - Uses `get_excel_dropdown_data()` from `db_hardcoded` to populate form options.
      - Populates both `Globals.drop_downs` and `Globals.drop_downs_contingent`.
      - Should be called once after app startup or reflection.
    """

    from arb.portal.db_hardcoded import get_excel_dropdown_data

    logger.debug(f"In load_drop_downs()")

    Globals.drop_downs, Globals.drop_downs_contingent = get_excel_dropdown_data()

    logger.debug(f"Globals.drop_downs={Globals.drop_downs}")
    logger.debug(f"Globals.drop_downs_contingent={Globals.drop_downs_contingent}")

  @classmethod
  def load_type_mapping(cls, flask_app: Flask, db: SQLAlchemy, base) -> None:
    """
    Populate column type metadata for all reflected tables in the SQLAlchemy base.

    Args:
      flask_app (Flask): The current Flask application (used for context scoping).
      db (SQLAlchemy): SQLAlchemy instance, already bound to a live database engine.
      base (AutomapBase): Reflected SQLAlchemy metadata containing all mapped models.

    Returns:
      None

    Notes:
      - Uses `arb.utils.sql_alchemy.get_sa_automap_types()` for reflection.
      - The resulting `Globals.db_column_types` is used in form pre-population and validation.
    """

    from arb.utils.sql_alchemy import get_sa_automap_types

    with flask_app.app_context():
      engine = db.engine
      Globals.db_column_types = get_sa_automap_types(engine, base)

    logger.debug(f"Database type mapping: Globals.db_column_types={Globals.db_column_types}")
