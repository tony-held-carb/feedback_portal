"""
Database initialization and reflection routines for the ARB Feedback Portal.

These functions are intended to be called during Flask app startup
(from `create_app()`) to configure SQLAlchemy metadata, initialize models,
and create missing tables.

Usage:
  from startup.db import reflect_database, db_initialize_and_create

Notes:
  - SQLAlchemy models must be explicitly imported to register before table creation.
  - Logging is enabled throughout to trace database state and startup flow.
"""

from arb.__get_logger import get_logger
from arb.portal.extensions import db
from flask import current_app
from pathlib import Path

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def reflect_database() -> None:
  """
  Reflect the existing database into SQLAlchemy metadata.

  This enables access to existing tables even without defined ORM models.

  Returns:
    None

  Logs:
    - Info: Start of reflection
    - Debug: Completion of reflection
  """
  logger.info("Reflecting database metadata.")
  db.metadata.reflect(bind=db.engine)
  logger.debug("Reflection complete.")


def db_initialize() -> None:
  """
  Import and register SQLAlchemy ORM models.

  This ensures model classes are registered before calling `db.create_all()`.

  Notes:
    - Import must be executed (even if unused) to register models.

  Example:
    import arb.portal.sqla_models as models
  """
  logger.info("Initializing database models.")
  # Add model registration below

  # noinspection PyUnresolvedReferences
  import arb.portal.sqla_models as models


def db_create() -> None:
  """
  Create all tables defined in SQLAlchemy metadata if they don’t exist.

  Skips creation if `FAST_LOAD=True` is set in the app config.

  Returns:
    None

  Logs:
    - Warn: If creation is skipped due to FAST_LOAD
    - Info: When table creation begins
    - Debug: After schema creation completes
  """
  if current_app.config.get("FAST_LOAD", False) is True:
    logger.warning("Skipping table creation for FAST_LOAD=True.")
    return

  logger.info("Creating all missing tables.")
  db.create_all()
  logger.debug("Database schema created.")


def db_initialize_and_create() -> None:
  """
  Register models and create missing tables in one call.

  Combines `db_initialize()` and `db_create()` for convenience.

  Returns:
    None

  Logs:
    - Info: Upon successful database initialization
  """
  db_initialize()
  db_create()
  logger.info("Database initialized and tables ensured.")


