"""
  Database utility functions for dynamic schema operations using SQLAlchemy reflection.

  This module allows runtime access to models and retrieval or creation of rows
  using flexible table and column identifiers.

  Attributes:
    get_ensured_row (function): Retrieve or create a row in a table by primary key.
    logger (logging.Logger): Logger instance for this module.

  Examples:
    from arb.portal.utils.db_introspection_util import get_ensured_row
    model, id_, is_new = get_ensured_row(db, base, table_name="incidences", id_=123)

  Notes:
    - Used by ingestion and upload utilities for safe upsert operations.
    - The logger emits a debug message when this file is loaded.
"""

import logging
from pathlib import Path
from typing import Any

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import AutomapBase

from arb.utils.sql_alchemy import get_class_from_table_name

logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def get_ensured_row(db: SQLAlchemy,
                    base: AutomapBase,
                    table_name: str = "incidences",
                    primary_key_name: str = "id_incidence",
                    id_: int | None = None,
                    add_to_session: bool = False) -> tuple[Any, bool]:
  """
  Retrieve or create a row in the specified table using a primary key.

  Args:
    db (SQLAlchemy): SQLAlchemy database instance.
    base (AutomapBase): Reflected SQLAlchemy base metadata.
    table_name (str): Table name to operate on. Defaults to 'incidences'.
    primary_key_name (str): Name of the primary key column. Defaults to 'id_incidence'.
    id_ (int | None): Primary key value. If None, a new row is created.
    add_to_session (bool): If True, add new model instances to the session for tracking.
                          Defaults to False for backward compatibility with upload_file.
                          Set to True for staged uploads that need session tracking.

  Returns:
    tuple[Any, bool]: (model, is_new_row)
      - model: SQLAlchemy ORM instance
      - is_new_row: Whether a new row was created (True/False)

  Raises:
    AttributeError: If the model class lacks the specified primary key.
    UnmappedClassError: If the table name is not mapped in metadata.

  Examples:
    model, id_, is_new = get_ensured_row(db, base, table_name="incidences", id_=123)
    # Retrieves or creates a row in the incidences table

  Notes:
    - MODIFIED FOR STAGED UPLOADS: Added add_to_session parameter to support staged upload
      functionality without breaking existing upload_file behavior.
    - When add_to_session=True, new models are added to the session for proper tracking.
    - When add_to_session=False (default), behavior remains unchanged for upload_file compatibility.
    - Logs detailed diagnostics for debugging and session state.
  """

  # 🆕 DIAGNOSTIC: Log function entry
  logger.info(f"[get_ensured_row] ENTRY: table_name={table_name}, "
              f"primary_key_name={primary_key_name}, id_={id_}, add_to_session={add_to_session}")

  is_new_row = False

  session = db.session
  table = get_class_from_table_name(base, table_name)  # type: ignore  # mapped ORM class
  if table is None:
    raise ValueError(f"Table '{table_name}' not found or not mapped in metadata.")

  logger.info(f"[get_ensured_row] Table class: {table}, Session: {session is not None}")

  if id_ is not None:
    logger.info(f"[get_ensured_row] Attempting to retrieve existing row with {primary_key_name}={id_}")
    model = session.get(table, id_)  # type: ignore

    if model is None:
      is_new_row = True
      logger.info(f"[get_ensured_row] No existing row found; creating new {table_name} row with {primary_key_name}={id_}")
      model = table(**{primary_key_name: id_})  # type: ignore
      # 🆕 CONDITIONAL: Add to session only if requested (for staged uploads)
      if add_to_session:
        session.add(model)
        logger.info(f"[get_ensured_row] Added new model to session for tracking")
      logger.info(f"[get_ensured_row] Created model instance: {model}, "
                  f"model.{primary_key_name}={getattr(model, primary_key_name, 'N/A')}")
    else:
      logger.info(f"[get_ensured_row] Found existing row: {model}, "
                  f"model.{primary_key_name}={getattr(model, primary_key_name, 'N/A')}")
  else:
    is_new_row = True
    logger.info(f"[get_ensured_row] Creating new {table_name} row with auto-generated {primary_key_name}")
    model = table(**{primary_key_name: None})  # type: ignore
    session.add(model)

    logger.info(f"[get_ensured_row] About to commit new row to database")
    try:
      session.commit()
      logger.info(f"[get_ensured_row] ✅ Successfully committed new row to database")
    except Exception as e:
      logger.error(f"[get_ensured_row] ❌ Failed to commit new row: {e}")
      logger.exception(f"[get_ensured_row] Full exception details:")
      raise

    id_ = getattr(model, primary_key_name)
    logger.info(f"[get_ensured_row] New row created with {primary_key_name}={id_}")

  # 🆕 DIAGNOSTIC: Final state check
  logger.info(f"[get_ensured_row] RETURN: model={model}, id_={id_}, is_new_row={is_new_row}")

  # Check if model is in session
  from sqlalchemy.orm import object_session
  model_session = object_session(model)
  logger.info(f"[get_ensured_row] Model session check: {model_session is not None}, "
              f"Model in session: {model in model_session if model_session else False}")

  return model, id_, is_new_row
