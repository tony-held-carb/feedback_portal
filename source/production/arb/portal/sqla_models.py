"""
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

  This table stores metadata related to each file uploaded via the feedback portal, such as
  its file system path, optional description, upload status, and creation/modification timestamps.

  Table Name:
      uploaded_files

  Columns:
      id_ (int): Primary key. Unique identifier for each uploaded file.
      path (str): File system path (absolute or relative) to the uploaded file. Required.
      description (str | None): Optional human-readable description of the file.
      status (str | None): Optional status (e.g., 'pending', 'processed', 'error').
      created_timestamp (datetime): Time the record was created (server-default UTC).
      modified_timestamp (datetime): Time the record was last modified (server-default UTC).

  Example:
      >>> file = UploadedFile(
      ...     path="uploads/form_0425.xlsx",
      ...     description="April survey results",
      ...     status="submitted"
      ... )
      >>> db.session.add(file)
      >>> db.session.commit()

      # Fetching it back
      >>> UploadedFile.query.get(file.id_)
      <Uploaded File: 1, Path: uploads/form_0425.xlsx, Description: April survey results, Status: submitted>

  Notes:
      * Timestamps use server-side defaults and should reflect UTC times by default.
      * This model supports automated creation and schema migration using Flask-Migrate/Alembic.

  TODO:
      Consider adding:
        - `user_id` foreign key (for multi-user attribution)
        - `error_log` (if file processing fails)
        - `uploaded_by_ip` for better traceability
        - make sure timezone is consistent across all models and project
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
    Tracks individual updates to the misc_json column of the incidences table.

    Columns:
        id (int): Primary key.
        timestamp (datetime): When the update was made (auto-generated).
        key (str): The misc_json field that was changed.
        old_value (str): The prior value before the update (nullable).
        new_value (str): The new value after the update.
        user (str): The user who made the change (or 'anonymous').
        comments (str): Optional notes or metadata.
        id_incidence (int): Reference to id_incidence (or similar foreign key), nullable.
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
  Run basic diagnostics to validate that the UploadedFile model is functioning correctly.

  This function performs a temporary insert into the database, fetches it back,
  prints the object representation, and rolls back the transaction to leave the database unchanged.

  This should only be run in a development context or inside a test transaction.

  Example:
      >>> run_diagnostics()

  Raises:
      RuntimeError: If the database session is not available or an unexpected error occurs.

  Notes:
      * This test is non-destructive and rolls back all test changes.
      * Ensure the app context is active when calling this function.
      * Useful for verifying migrations, connection health, and basic ORM mappings.
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
