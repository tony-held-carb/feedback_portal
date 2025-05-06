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
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import arb.__get_logger as get_logger

logger, pp_log = get_logger.get_logger(__name__, __file__)


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

    Example:
        >>> Globals.load_drop_downs(app, db)
        >>> print(Globals.drop_downs["ogi_performed"])
        ['Please Select', 'Yes', 'No']

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

  @classmethod
  def run_diagnostics(cls) -> None:
    """
    Run diagnostics to verify that global mappings are loaded and properly structured.

    This includes:
        - Ensuring dropdowns are loaded with keys and 'Please Select' as a first value
        - Ensuring contingent dropdown mappings exist and are structured as dict[str, list[str]]
        - Ensuring db_column_types is populated and includes nested type definitions

    Returns:
        None

    Raises:
        AssertionError: If any key mapping is missing or misstructured

    Example:
        >>> Globals.run_diagnostics()
        ✓ Dropdown keys and structure verified
        ✓ Contingent dropdown structure verified
        ✓ DB column types loaded successfully
        ✓ All Globals diagnostics passed.
    """
    print("\n=== Running diagnostics on Globals ===")

    # Dropdown validation
    assert cls.drop_downs, "Globals.drop_downs is empty"
    assert "ogi_performed" in cls.drop_downs, "Missing key 'ogi_performed' in drop_downs"
    assert cls.drop_downs["ogi_performed"][0] == "Please Select", "Missing 'Please Select' in drop_downs"

    print("✓ Dropdown keys and structure verified")

    # Contingent dropdown validation
    assert cls.drop_downs_contingent, "Globals.drop_downs_contingent is empty"
    key = "emission_cause_contingent_on_emission_location"
    assert key in cls.drop_downs_contingent, f"Missing contingent key '{key}'"
    mapping = cls.drop_downs_contingent[key]
    assert isinstance(mapping, dict), "Contingent dropdown is not a dict"
    example_subkey = next(iter(mapping))
    assert isinstance(mapping[example_subkey], list), "Contingent mapping is not a list"

    print("✓ Contingent dropdown structure verified")

    # DB column type mapping validation
    assert cls.db_column_types, "Globals.db_column_types is empty"
    sample_table = next(iter(cls.db_column_types))
    sample_column = next(iter(cls.db_column_types[sample_table]))
    type_entry = cls.db_column_types[sample_table][sample_column]
    assert isinstance(type_entry, dict), "Type entry is not a dict"
    assert "py_type" in type_entry, "Missing 'py_type' in type mapping"

    print("✓ DB column types loaded successfully")
    print("✓ All Globals diagnostics passed.\n")


# Optional CLI entry point
if __name__ == "__main__":
  Globals.run_diagnostics()
