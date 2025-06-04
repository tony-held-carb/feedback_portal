"""
Database initialization and reflection routines for the ARB Feedback Portal.

These functions are intended to be called during Flask app startup
(from `create_app()`) to configure SQLAlchemy metadata, initialize models,
and create missing tables.

Usage:
  from startup.db import reflect_database, db_initialize_and_create

Notes:
  - Model registration requires explicit import before table creation.
  - Logging is enabled to trace startup sequence and database state.
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

  This enables access to tables without defining ORM classes.

  Example:
    reflect_database()

  Logs:
    - Emits info and debug logs for traceability.
  """
  logger.info("Reflecting database metadata.")
  db.metadata.reflect(bind=db.engine)
  logger.debug("Reflection complete.")


def db_initialize() -> None:
  """
  Import and register SQLAlchemy model classes.

  This step is necessary to ensure models are registered
  before invoking `db.create_all()`.

  Notes:
    - The model import must be executed, even if unused, to trigger registration.
    - Adjust this function if additional model setup is needed.

  Example:
    import arb.portal.sqla_models as models
  """
  logger.info("Initializing database models.")
  # Add model registration below

  # noinspection PyUnresolvedReferences
  import arb.portal.sqla_models as models


def db_create() -> None:
  """
  Create all missing tables in the database.

  Uses SQLAlchemy’s `create_all()` to ensure schema is present.
  Will skip execution if the `FAST_LOAD` config flag is enabled.

  Logs:
    - Warns if table creation is skipped
    - Info and debug messages upon schema creation
  """
  if current_app.config.get("FAST_LOAD", False) is True:
    logger.warning("Skipping table creation for FAST_LOAD=True.")
    return

  logger.info("Creating all missing tables.")
  db.create_all()
  logger.debug("Database schema created.")


def db_initialize_and_create() -> None:
  """
  Run both model registration and table creation.

  This is a convenience wrapper for calling:
    db_initialize()
    db_create()

  Logs:
    - Indicates database schema is ensured
  """
  db_initialize()
  db_create()
  logger.info("Database initialized and tables ensured.")


