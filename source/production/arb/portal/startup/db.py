"""
  Database initialization and reflection routines for the ARB Feedback Portal.

  These functions are intended to be called during Flask app startup
  (from `create_app()`) to configure SQLAlchemy metadata, initialize models,
  and create missing tables.

  Args:
    None

  Returns:
    None

  Attributes:
    logger (logging.Logger): Logger instance for this module.

  Examples:
    from arb.portal.startup.db import reflect_database, db_initialize_and_create
    reflect_database()
    db_initialize_and_create()

  Notes:
    - SQLAlchemy models must be explicitly imported to register before table creation.
    - Logging is enabled throughout to trace database state and startup flow.
    - The logger emits a debug message when this file is loaded.
"""

import logging
from pathlib import Path

from flask import current_app

from arb.portal.extensions import db

logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def reflect_database() -> None:
  """
  Reflect the existing database into SQLAlchemy metadata.

  Args:
    None

  Returns:
    None

  Examples:
    reflect_database()
    # Reflects all tables into SQLAlchemy metadata

  Notes:
    - Enables access to existing tables even without defined ORM models.
    - Logs info and debug messages for tracing.
  """
  logger.info(f"Reflecting database metadata.")
  try:
    logger.info(f"Database engine URI: {db.engine.url}")
    db.metadata.reflect(bind=db.engine)
    logger.debug(f"Reflection complete.")
    logger.info(f"Reflected tables: {list(db.metadata.tables.keys())}")
  except Exception as e:
    logger.error(f"Error during database reflection: {e}")


def db_initialize() -> None:
  """
  Import and register SQLAlchemy ORM models.

  Args:
    None

  Returns:
    None

  Examples:
    db_initialize()
    # Registers all models for table creation

  Notes:
    - Import must be executed (even if unused) to register models.
  """
  logger.info(f"Initializing database models.")
  # Add model registration below

  # noinspection PyUnresolvedReferences
  import arb.portal.sqla_models as models


def db_create() -> None:
  """
  Create all tables defined in SQLAlchemy metadata if they don’t exist.

  Args:
    None

  Returns:
    None

  Examples:
    db_create()
    # Creates all missing tables in the database

  Notes:
    - Skips creation if FAST_LOAD=True is set in the app config.
    - Logs warnings and info for tracing.
  """
  if current_app.config.get("FAST_LOAD", False) is True:
    logger.warning(f"Skipping table creation for FAST_LOAD=True.")
    return

  logger.info(f"Creating all missing tables.")
  db.create_all()
  logger.debug(f"Database schema created.")


def db_initialize_and_create() -> None:
  """
  Register models and create missing tables in one call.

  Args:
    None

  Returns:
    None

  Examples:
    db_initialize_and_create()
    # Registers models and ensures all tables exist

  Notes:
    - Combines db_initialize() and db_create() for convenience.
    - Logs info upon successful database initialization.
  """
  db_initialize()
  db_create()
  logger.info(f"Database initialized and tables ensured.")
