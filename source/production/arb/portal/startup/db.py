"""
Database initialization and reflection routines.

These functions are meant to be called during `create_app()` to set up
database metadata, create tables, and register models.

Example:
    from startup.db import reflect_database, db_initialize_and_create
"""

from arb.__get_logger import get_logger
from arb.portal.extensions import db

logger, _ = get_logger(__name__, __file__)


def reflect_database() -> None:
  """
  Reflect the existing database into SQLAlchemy's metadata.

  Use this when you want to interact with existing tables
  without defining all models.

  Example:
      reflect_database()
  """
  logger.info("Reflecting database metadata.")
  db.metadata.reflect(bind=db.engine)
  logger.debug("Reflection complete.")


def db_initialize() -> None:
  """
  Initialize or register database models.

  Customize this to bind models or run other initialization routines.

  Example source code for model registration:
    import arb.portal.sqla_models as models

  Notes:
    - You must import models below (even if they are not used) so registration works properly
    - Import all models before calling create_all() if you want them to reflect the database.
  """
  logger.info("Initializing database models.")
  # Add model registration below

  # noinspection PyUnresolvedReferences
  import arb.portal.sqla_models as models


def db_create() -> None:
  """
  Create missing tables in the database.

  Should be safe to run multiple times (uses SQLAlchemy's create_all()).
  """
  logger.info("Creating all missing tables.")
  db.create_all()
  logger.debug("Database schema created.")


def db_initialize_and_create() -> None:
  """
  Combine db_initialize and db_create for convenience.

  Example:
      db_initialize_and_create()
  """
  db_initialize()
  db_create()
  logger.info("Database initialized and tables ensured.")
