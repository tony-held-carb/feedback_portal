"""
file_upload_util.py

Utility functions for managing uploaded files in the feedback portal.

This module provides functionality to record uploaded files into the
`UploadedFile` table for audit tracking and troubleshooting purposes.

Args:
  None

Returns:
  None

Attributes:
  add_file_to_upload_table (function): Insert a record into the UploadedFile table.
  logger (logging.Logger): Logger instance for this module.

Examples:
  from arb.portal.utils.file_upload_util import add_file_to_upload_table
  add_file_to_upload_table(db, file_name="uploads/test.xlsx", status="success")

Notes:
  - Used for audit trails and diagnostics of file uploads.
  - The logger emits a debug message when this file is loaded.
"""
import logging
from pathlib import Path
from typing import Optional

from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def add_file_to_upload_table(db: SQLAlchemy,
                             file_name: str | Path,
                             status: Optional[str] = None,
                             description: Optional[str] = None) -> None:  # noqa
  """
  Insert a record into the `UploadedFile` table for audit and diagnostics.

  Args:
    db (SQLAlchemy): SQLAlchemy database instance.
    file_name (str | Path): File path or name to be recorded.
    status (str | None): Optional upload status label.
    description (str | None): Optional notes for the upload event.

  Returns:
    None

  Examples:
    add_file_to_upload_table(db, file_name="uploads/test.xlsx", status="success")
    # Records the file upload event in the UploadedFile table

  Notes:
    - Commits the new record immediately to the database.
    - Used for troubleshooting and audit trails of uploads.
  """

  # todo (consider) to wrap commit in log?
  from arb.portal.sqla_models import UploadedFile

  if file_name is None:
    raise ValueError("file_name cannot be None; must be a valid file path or name.")
  logger.debug(f"Adding uploaded file to upload table: {file_name=}")
  model_uploaded_file = UploadedFile(
    path=str(file_name),
    status=status if status is not None else None,
    description=description if description is not None else None,
  )  # type: ignore
  db.session.add(model_uploaded_file)
  db.session.commit()
  logger.debug(f"{model_uploaded_file=}")
