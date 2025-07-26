"""
SQLAlchemy model definitions for the ARB Feedback Portal.

This module defines ORM classes that map to key tables in the database,
including uploaded file metadata and portal JSON update logs.

Module_Attributes:
  UploadedFile (type): SQLAlchemy model for uploaded file metadata.
  PortalUpdate (type): SQLAlchemy model for portal update logs.
  logger (logging.Logger): Logger instance for this module.

Examples:
  file = UploadedFile(path="uploads/report.xlsx", status="pending")
  db.session.add(file)
  db.session.commit()
  # file is inserted into the uploaded_files table with timestamps autopopulated

Notes:
  - Only models explicitly defined here will be created by SQLAlchemy via `db.create_all()`.
  - Most schema inspection and data access for `incidences` is handled dynamically via reflection.
  - Timezone-aware UTC timestamps are used on all tracked models.
  - All models inherit from `db.Model`, and can be directly queried with SQLAlchemy syntax.
  - The logger emits a debug message when this file is loaded.
"""

import logging
from pathlib import Path

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

from arb.portal.extensions import db

logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


class UploadedFile(db.Model):
  """
    SQLAlchemy model representing a user-uploaded file.

    Table Name:
      uploaded_files

    Attributes:
      id_ (int): Primary key.
      path (str): Filesystem path to the uploaded file.
      description (str | None): Optional human-friendly explanation.
      status (str | None): Upload status, e.g., 'pending', 'processed', or 'error'.
      created_timestamp (datetime): UTC timestamp of initial creation.
      modified_timestamp (datetime): UTC timestamp of last update.

    Examples:
      file = UploadedFile(path="uploads/test.xlsx", status="pending")
      db.session.add(file)
      db.session.commit()
      # file appears in the uploaded_files table with 'pending' status

    Notes:
      - Timestamps use UTC and are timezone-aware.
      - This table is managed by SQLAlchemy directly (not introspected).
  """

  __tablename__ = "uploaded_files"

  id_ = db.Column(db.Integer, primary_key=True)
  path = db.Column(db.Text, nullable=False)
  description = db.Column(db.Text, nullable=True)
  status = db.Column(db.Text, nullable=True)
  created_timestamp = db.Column(
    db.DateTime(timezone=True),
    server_default=func.now()
  )
  modified_timestamp = db.Column(
    db.DateTime(timezone=True),
    server_default=func.now()
  )

  def __repr__(self) -> str:
    """
    Return a human-readable string representation of the uploaded file record.

    Returns:
      str: Summary string showing the ID, path, description, and status.

    Examples:
      file = UploadedFile(id_=3, path="uploads/data.csv", description="Data", status="done")
      print(repr(file))
      # Output: '<Uploaded File: 3, Path: uploads/data.csv, Description: Data, Status: done>'
    """
    return (
      f'<Uploaded File: {self.id_}, Path: {self.path}, '
      f'Description: {self.description}, Status: {self.status}>'
    )


class PortalUpdate(db.Model):
  """
  SQLAlchemy model tracking updates to the misc_json field on incidence records.

  Table Name:
    portal_updates

  Attributes:
    id (int): Primary key.
    timestamp (datetime): UTC time when the change was logged.
    key (str): JSON key that was modified.
    old_value (str | None): Previous value (nullable).
    new_value (str): New value.
    user (str): Username or identifier of the user making the change.
    comments (str): Optional explanatory comment.
    id_incidence (int | None): Foreign key to the modified incidence (nullable).

  Examples:
    update = PortalUpdate(key="field1", old_value="A", new_value="B", user="alice", id_incidence=1)
    db.session.add(update)
    db.session.commit()
    # update appears in the portal_updates table

  Notes:
    - Automatically populated by `apply_json_patch_and_log()`.
    - Used for rendering the `portal_updates.html` table.
  """

  __tablename__ = "portal_updates"

  id = Column(Integer, primary_key=True)
  timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

  key = Column(String(255), nullable=False)
  old_value = Column(Text, nullable=True)
  new_value = Column(Text, nullable=False)
  user = Column(String(255), nullable=False, default="anonymous")
  comments = Column(Text, nullable=False, default="")
  id_incidence = Column(Integer, nullable=True)

  def __repr__(self) -> str:
    """
    Return a human-readable string representation of the portal update record.

    Returns:
      str: Summary string showing the update ID, key, old/new values, user, and timestamp.

    Examples:
      update = PortalUpdate(id=1, key="field1", old_value="A", new_value="B", user="alice")
      print(repr(update))
      # Output: '<PortalUpdate id=1 key='field1' old='A' new='B' user='alice' at=...>'
    """
    return (
      f"<PortalUpdate id={self.id} key={self.key!r} old={self.old_value!r} "
      f"new={self.new_value!r} user={self.user!r} at={self.timestamp}>"
    )


def run_diagnostics() -> None:
  """
  Run a test transaction to validate UploadedFile model functionality.

  Raises:
    RuntimeError: If database access or fetch fails.

  Examples:
    run_diagnostics()
    # Logs diagnostic info and rolls back the transaction

  Notes:
    - Meant for developer use in test environments only.
    - This function leaves no data in the database due to rollback.
    - Logs diagnostic information using the project logger.
    - LIKELY OBSOLETE: This function is not covered by unit tests and is likely obsolete. It requires a real database connection and is not robustly testable with mocks or in CI environments. Change with caution. See documentation/docstring_update_for_testing.md for details.
  """

  logger.info(f"Running UploadedFile diagnostics...")

  try:
    logger.debug(f"Beginning diagnostic transaction...")
    test_file = UploadedFile(
      path="uploads/test_file.xlsx",
      description="Diagnostic test file",
      status="testing"
    )
    db.session.add(test_file)
    db.session.flush()  # Ensures test_file.id_ is populated

    logger.info(f"Inserted test file with ID: {test_file.id_}")
    fetched = UploadedFile.query.get(test_file.id_)

    if fetched is None:
      raise RuntimeError("Failed to retrieve inserted UploadedFile instance.")

    logger.info(f"Fetched file: {fetched}")
    logger.debug(f"repr: {repr(fetched)}")
    logger.debug(f"created_timestamp: {fetched.created_timestamp}")

  except SQLAlchemyError as e:
    logger.exception("SQLAlchemy error during diagnostics.")
    raise RuntimeError("Database error during UploadedFile diagnostics.") from e

  finally:
    logger.debug(f"Rolling back diagnostic transaction.")
    db.session.rollback()
    logger.info(f"Diagnostics completed and transaction rolled back.")
