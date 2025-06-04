"""
# todo - resume documentation here ...

sqla_models.py stores the SQLAlchemy class/models to allow for Python interaction with databases.

Notes:
    * Since the migration from SQLite to PostgreSQL, most database models have been discovered and
      loaded through SQLAlchemy introspection rather than explicit class definitions.
    * Only classes defined here that inherit from db.Model will have corresponding tables created
      by SQLAlchemy migrations.
    * To introspect the rest of the schema, use `db.Model.metadata.reflect()` or automap techniques.

Example:
    >>> new_file = UploadedFile(
    ...     path="/uploads/report1.xlsx",
    ...     description="Monthly emissions report",
    ...     status="pending"
    ... )
    >>> db.session.add(new_file)
    >>> db.session.commit()
"""

from pathlib import Path

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

from arb.__get_logger import get_logger
from arb.portal.extensions import db

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


class UploadedFile(db.Model):
  """
  SQLAlchemy model representing an uploaded file record.

  This model stores metadata for files uploaded via the portal, including file path,
  optional description, processing status, and timestamps.

  Table Name:
    uploaded_files

  Columns:
    id_ (int): Primary key.
    path (str): File system path to the uploaded file.
    description (str | None): Optional human-readable file description.
    status (str | None): Status such as 'pending', 'processed', or 'error'.
    created_timestamp (datetime): UTC timestamp of record creation.
    modified_timestamp (datetime): UTC timestamp of last modification.

  Example:
    >>> file = UploadedFile(path="uploads/test.xlsx", status="pending")
    >>> db.session.add(file)
    >>> db.session.commit()

  Notes:
    - Timestamps are in UTC.
    - Consider adding user tracking fields in future iterations.
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

    Example:
        >>> repr(UploadedFile(id_=3, path="uploads/data.csv", description="Data", status="done"))
        '<Uploaded File: 3, Path: uploads/data.csv, Description: Data, Status: done>'
    """
    return (
      f'<Uploaded File: {self.id_}, Path: {self.path}, '
      f'Description: {self.description}, Status: {self.status}>'
    )


class PortalUpdate(db.Model):
  """
  Tracks JSON updates to the misc_json field of an incidence record.

  This audit log model stores the history of individual key/value changes
  applied to the JSON column of the 'incidences' table.

  Columns:
    id (int): Primary key.
    timestamp (datetime): UTC time the update was recorded.
    key (str): JSON field key that was modified.
    old_value (str): Previous value.
    new_value (str): New value.
    user (str): User who made the change.
    comments (str): Optional note or reason for the change.
    id_incidence (int): Foreign key to associated incidence record.

  Notes:
    - Used by apply_json_patch_and_log() for change tracking.
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

  def __repr__(self):
    return (
      f"<PortalUpdate id={self.id} key={self.key!r} old={self.old_value!r} "
      f"new={self.new_value!r} user={self.user!r} at={self.timestamp}>"
    )


def run_diagnostics() -> None:
  """
  Runs a test insert/fetch/rollback sequence to validate the UploadedFile model.

  This is used to confirm that model definitions and database connectivity are
  working as expected. All actions are rolled back at the end of the test.

  Example:
    >>> run_diagnostics()

  Raises:
    RuntimeError: If session errors or connection issues are detected.

  Notes:
    - Use only in test or dev environments.
    - Ensures model mappings and migrations are functional.
  """
  logger.info("Running UploadedFile diagnostics...")

  try:
    logger.debug("Beginning diagnostic transaction...")
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
    logger.debug("Rolling back diagnostic transaction.")
    db.session.rollback()
    logger.info("Diagnostics completed and transaction rolled back.")
