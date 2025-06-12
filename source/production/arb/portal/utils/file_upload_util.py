"""
file_upload_util.py

Utility functions for managing uploaded files in the feedback portal.

This module provides functionality to record uploaded files into the
`UploadedFile` table for audit tracking and troubleshooting purposes.
"""
from pathlib import Path

from flask_sqlalchemy import SQLAlchemy

from arb.__get_logger import get_logger
from arb.portal.config.accessors import get_upload_folder

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def add_file_to_upload_table(db: SQLAlchemy,
                             file_name: str | Path,
                             status: str = None,
                             description: str = None) -> None:
  """
  Insert a record into the `UploadedFile` table for audit and diagnostics.

  Args:
    db (SQLAlchemy): SQLAlchemy database instance.
    file_name (str | Path): File path or name to be recorded.
    status (str | None): Optional upload status label.
    description (str | None): Optional notes for the upload event.

  Returns:
    None
  """

  # todo (consider) to wrap commit in log?
  from arb.portal.sqla_models import UploadedFile

  logger.debug(f"Adding uploaded file to upload table: {file_name=}")
  model_uploaded_file = UploadedFile(
    path=str(file_name),
    status=status,
    description=description,
  )
  db.session.add(model_uploaded_file)
  db.session.commit()
  logger.debug(f"{model_uploaded_file=}")
