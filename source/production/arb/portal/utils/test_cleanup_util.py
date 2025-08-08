"""
  Test data cleanup utilities for removing testing rows from the database.

  This module provides functions to safely delete testing data from the portal_updates
  and incidences tables based on id_incidence ranges.

  Attributes:
    logger (logging.Logger): Logger instance for this module.

  Examples:
    from arb.portal.utils.test_cleanup_util import delete_testing_rows
    deleted_count = delete_testing_rows(db, base, 2000, 2999)

  Notes:
    - Designed for cleaning up testing data with id_incidence in ranges 2000-2999 or 4000+
    - Provides safety checks and logging for audit trails
    - Should be used carefully in production environments
"""
import logging
from pathlib import Path
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import AutomapBase

logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def delete_testing_rows(db: SQLAlchemy,
                        base: AutomapBase,
                        min_id: int,
                        max_id: int,
                        dry_run: bool = False) -> dict[str, int]:
  """
  Delete rows from portal_updates and incidences tables where id_incidence is in the specified range.

  Args:
    db (SQLAlchemy): Database instance.
    base (AutomapBase): Reflected schema base.
    min_id (int): Minimum id_incidence value (inclusive).
    max_id (int): Maximum id_incidence value (inclusive).
    dry_run (bool): If True, simulate deletion without actually deleting. Defaults to False.

  Returns:
    dict[str, int]: Dictionary with counts of deleted rows from each table.

  Raises:
    ValueError: If min_id > max_id or if range is invalid.
    Exception: If database operations fail.

  Examples:
    # Delete testing rows with id_incidence 2000-2999
    result = delete_testing_rows(db, base, 2000, 2999)
    # Returns: {'portal_updates': 5, 'incidences': 5}

    # Dry run to see what would be deleted
    result = delete_testing_rows(db, base, 4000, 4999, dry_run=True)
    # Returns: {'portal_updates': 3, 'incidences': 3} (without actually deleting)

  Notes:
    - Deletes from portal_updates table first, then incidences table
    - Logs detailed information about what is being deleted
    - Provides safety through dry_run option
    - Commits changes unless dry_run is True
  """
  if min_id > max_id:
    raise ValueError(f"Invalid range: min_id ({min_id}) cannot be greater than max_id ({max_id})")

  if min_id < 0 or max_id < 0:
    raise ValueError("id_incidence values must be non-negative")

  logger.info(f"Starting deletion of testing rows with id_incidence range {min_id}-{max_id} (dry_run={dry_run})")

  result = {'portal_updates': 0, 'incidences': 0}

  try:
    # Get table models
    portal_updates_model = getattr(base.classes, 'portal_updates', None)
    incidences_model = getattr(base.classes, 'incidences', None)

    if not portal_updates_model:
      raise AttributeError("portal_updates table not found in database schema")
    if not incidences_model:
      raise AttributeError("incidences table not found in database schema")

    # Delete from portal_updates table first (foreign key dependency)
    portal_updates_query = db.session.query(portal_updates_model).filter(
      portal_updates_model.id_incidence >= min_id,
      portal_updates_model.id_incidence <= max_id
    )

    portal_updates_count = portal_updates_query.count()
    logger.info(f"Found {portal_updates_count} rows in portal_updates table to delete")

    if not dry_run and portal_updates_count > 0:
      portal_updates_query.delete(synchronize_session=False)
      result['portal_updates'] = portal_updates_count
      logger.info(f"Deleted {portal_updates_count} rows from portal_updates table")
    elif dry_run:
      result['portal_updates'] = portal_updates_count
      logger.info(f"Would delete {portal_updates_count} rows from portal_updates table (dry run)")

    # Delete from incidences table
    incidences_query = db.session.query(incidences_model).filter(
      incidences_model.id_incidence >= min_id,
      incidences_model.id_incidence <= max_id
    )

    incidences_count = incidences_query.count()
    logger.info(f"Found {incidences_count} rows in incidences table to delete")

    if not dry_run and incidences_count > 0:
      incidences_query.delete(synchronize_session=False)
      result['incidences'] = incidences_count
      logger.info(f"Deleted {incidences_count} rows from incidences table")
    elif dry_run:
      result['incidences'] = incidences_count
      logger.info(f"Would delete {incidences_count} rows from incidences table (dry run)")

    # Commit changes unless dry run
    if not dry_run:
      db.session.commit()
      logger.info(f"Successfully committed deletion of {sum(result.values())} total rows")
    else:
      logger.info(f"Dry run completed - would delete {sum(result.values())} total rows")

    return result

  except Exception as e:
    logger.error(f"Error during deletion of testing rows: {e}")
    if not dry_run:
      db.session.rollback()
      logger.info("Database session rolled back due to error")
    raise


def delete_testing_range_2000_2999(db: SQLAlchemy,
                                   base: AutomapBase,
                                   dry_run: bool = False) -> dict[str, int]:
  """
  Convenience function to delete testing rows with id_incidence in range 2000-2999.

  Args:
    db (SQLAlchemy): Database instance.
    base (AutomapBase): Reflected schema base.
    dry_run (bool): If True, simulate deletion without actually deleting. Defaults to False.

  Returns:
    dict[str, int]: Dictionary with counts of deleted rows from each table.

  Examples:
    # Delete testing rows 2000-2999
    result = delete_testing_range_2000_2999(db, base)
    # Returns: {'portal_updates': 5, 'incidences': 5}

  Notes:
    - Calls delete_testing_rows with range 2000-2999
    - Convenient for cleaning up first testing range
  """
  return delete_testing_rows(db, base, 2000, 2999, dry_run=dry_run)


def delete_testing_range_4000_plus(db: SQLAlchemy,
                                   base: AutomapBase,
                                   max_id: Optional[int] = None,
                                   dry_run: bool = False) -> dict[str, int]:
  """
  Convenience function to delete testing rows with id_incidence >= 4000.

  Args:
    db (SQLAlchemy): Database instance.
    base (AutomapBase): Reflected schema base.
    max_id (Optional[int]): Maximum id_incidence value (inclusive). If None, deletes all >= 4000.
    dry_run (bool): If True, simulate deletion without actually deleting. Defaults to False.

  Returns:
    dict[str, int]: Dictionary with counts of deleted rows from each table.

  Examples:
    # Delete all testing rows >= 4000
    result = delete_testing_range_4000_plus(db, base)
    # Returns: {'portal_updates': 10, 'incidences': 10}

    # Delete testing rows 4000-4999
    result = delete_testing_range_4000_plus(db, base, max_id=4999)
    # Returns: {'portal_updates': 5, 'incidences': 5}

  Notes:
    - Calls delete_testing_rows with range 4000 to max_id (or effectively unlimited if max_id is None)
    - Convenient for cleaning up second testing range
  """
  if max_id is None:
    # Use a very large number to effectively delete all >= 4000
    max_id = 999999999

  return delete_testing_rows(db, base, 4000, max_id, dry_run=dry_run)


def list_testing_rows(db: SQLAlchemy,
                      base: AutomapBase,
                      min_id: int = 2000,
                      max_id: Optional[int] = None) -> dict[str, list]:
  """
  List testing rows from portal_updates and incidences tables without deleting them.

  Args:
    db (SQLAlchemy): Database instance.
    base (AutomapBase): Reflected schema base.
    min_id (int): Minimum id_incidence value (inclusive). Defaults to 2000.
    max_id (Optional[int]): Maximum id_incidence value (inclusive). If None, lists all >= min_id.

  Returns:
    dict[str, list]: Dictionary with lists of row data from each table.

  Examples:
    # List all testing rows >= 2000
    result = list_testing_rows(db, base)
    # Returns: {'portal_updates': [...], 'incidences': [...]}

    # List testing rows 4000-4999
    result = list_testing_rows(db, base, 4000, 4999)
    # Returns: {'portal_updates': [...], 'incidences': [...]}

  Notes:
    - Useful for previewing what would be deleted
    - Returns actual row data for inspection
    - Does not modify the database
  """
  if max_id is None:
    max_id = 999999999

  if min_id > max_id:
    raise ValueError(f"Invalid range: min_id ({min_id}) cannot be greater than max_id ({max_id})")

  logger.info(f"Listing testing rows with id_incidence range {min_id}-{max_id}")

  result = {'portal_updates': [], 'incidences': []}

  try:
    # Get table models
    portal_updates_model = getattr(base.classes, 'portal_updates', None)
    incidences_model = getattr(base.classes, 'incidences', None)

    if not portal_updates_model:
      raise AttributeError("portal_updates table not found in database schema")
    if not incidences_model:
      raise AttributeError("incidences table not found in database schema")

    # Query portal_updates table
    portal_updates_rows = db.session.query(portal_updates_model).filter(
      portal_updates_model.id_incidence >= min_id,
      portal_updates_model.id_incidence <= max_id
    ).all()

    result['portal_updates'] = [
      {
        'id_incidence': row.id_incidence,
        'sector': getattr(row, 'sector', None),
        'created_at': getattr(row, 'created_at', None),
        'updated_at': getattr(row, 'updated_at', None)
      }
      for row in portal_updates_rows
    ]

    # Query incidences table
    incidences_rows = db.session.query(incidences_model).filter(
      incidences_model.id_incidence >= min_id,
      incidences_model.id_incidence <= max_id
    ).all()

    result['incidences'] = [
      {
        'id_incidence': row.id_incidence,
        'sector': getattr(row, 'sector', None),
        'created_at': getattr(row, 'created_at', None),
        'updated_at': getattr(row, 'updated_at', None)
      }
      for row in incidences_rows
    ]

    logger.info(
      f"Found {len(result['portal_updates'])} rows in portal_updates and {len(result['incidences'])} rows in incidences")

    return result

  except Exception as e:
    logger.error(f"Error during listing of testing rows: {e}")
    raise
