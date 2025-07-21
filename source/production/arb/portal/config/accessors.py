"""
Config accessors for centralized and typed Flask config use.

This module provides centralized access to Flask `current_app.config` settings
using typed functions. Centralizing config usage improves maintainability,
enables easier testing, and reduces repetition across modules.

Args:
  None

Returns:
  None

Attributes:
  get_processed_versions_dir (function): Returns the processed versions directory.
  get_upload_folder (function): Returns the upload folder path.
  get_payload_save_dir (function): Returns the payload save directory.
  get_app_mode (function): Returns the current app mode.
  logger (logging.Logger): Logger instance for this module.

Examples:
  from arb.portal.config.accessors import get_upload_folder
  upload_path = get_upload_folder()

Notes:
  - All accessors raise KeyError if the required config key is missing (except get_app_mode).
  - get_app_mode defaults to 'dev' if not set.
"""

import logging
from pathlib import Path

from flask import current_app

logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def get_processed_versions_dir() -> Path:
  """
  Returns the root directory where processed Excel versions are stored.

  Args:
    None

  Returns:
    Path: Absolute path to the directory.

  Raises:
    KeyError: If 'PROCESSED_VERSIONS_DIR' is not in the config.

  Examples:
    processed_dir = get_processed_versions_dir()
    # Returns Path object for processed versions directory
  """
  return Path(current_app.config["PROCESSED_VERSIONS_DIR"])


def get_upload_folder() -> Path:
  """
  Returns the folder where uploaded files are saved.

  Args:
    None

  Returns:
    Path: Absolute path to the upload directory.

  Raises:
    KeyError: If 'UPLOAD_FOLDER' is not in the config.

  Examples:
    upload_dir = get_upload_folder()
    # Returns Path object for upload directory
  """
  return Path(current_app.config["UPLOAD_FOLDER"])


def get_payload_save_dir() -> Path:
  """
  Returns the default path for saving intermediate JSON payloads.

  Args:
    None

  Returns:
    Path: Directory path where payloads are saved.

  Raises:
    KeyError: If 'PAYLOAD_SAVE_DIR' is not in the config.

  Examples:
    payload_dir = get_payload_save_dir()
    # Returns Path object for payload save directory
  """
  return Path(current_app.config["PAYLOAD_SAVE_DIR"])


def get_app_mode() -> str:
  """
  Returns the mode the app is running in (e.g., 'dev', 'prod').

  Args:
    None

  Returns:
    str: Configured application mode. Defaults to 'dev' if not explicitly set.

  Examples:
    mode = get_app_mode()
    # Returns 'dev' or the configured app mode
  """
  return current_app.config.get("APP_MODE", "dev")


def get_database_uri() -> str:
  """
  Returns the SQLAlchemy database URI from the Flask app configuration.

  Args:
    None

  Returns:
    str: The configured SQLAlchemy database URI.

  Raises:
    KeyError: If 'SQLALCHEMY_DATABASE_URI' is not in the config.

  Examples:
    db_uri = get_database_uri()
    # Returns the database connection string
  """
  return current_app.config["SQLALCHEMY_DATABASE_URI"]
