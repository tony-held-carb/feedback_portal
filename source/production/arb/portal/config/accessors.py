"""
Config accessors for centralized and typed Flask config use.

This module provides centralized access to Flask `current_app.config` settings
using typed functions. Centralizing config usage improves maintainability,
enables easier testing, and reduces repetition across modules.

Typical usage:
    from arb.portal.config.accessors import get_upload_folder

    upload_path = get_upload_folder()
"""

from pathlib import Path

from flask import current_app

from arb.__get_logger import get_logger

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def get_processed_versions_dir() -> Path:
  """
  Returns the root directory where processed Excel versions are stored.

  Returns:
    Path: Absolute path to the directory.

  Raises:
    KeyError: If 'PROCESSED_VERSIONS_DIR' is not in the config.
  """
  return Path(current_app.config["PROCESSED_VERSIONS_DIR"])


def get_upload_folder() -> Path:
  """
  Returns the folder where uploaded files are saved.

  Returns:
    Path: Absolute path to the upload directory.

  Raises:
    KeyError: If 'UPLOAD_FOLDER' is not in the config.
  """
  return Path(current_app.config["UPLOAD_FOLDER"])


def get_payload_save_dir() -> Path:
  """
  Returns the default path for saving intermediate JSON payloads.

  Returns:
    Path: Directory path where payloads are saved.

  Raises:
    KeyError: If 'PAYLOAD_SAVE_DIR' is not in the config.
  """
  return Path(current_app.config["PAYLOAD_SAVE_DIR"])


def get_app_mode() -> str:
  """
  Returns the mode the app is running in (e.g., 'dev', 'prod').

  Returns:
    str: Configured application mode. Defaults to 'dev' if not explicitly set.
  """
  return current_app.config.get("APP_MODE", "dev")
