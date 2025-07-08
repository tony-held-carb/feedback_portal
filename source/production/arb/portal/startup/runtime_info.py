"""
  Provides runtime metadata and dynamic paths for the application.

  This module defines:
    - Project root and key directories (uploads, logs, static)
    - Operating system detection (Windows, Linux, macOS)
    - Platform-level info useful for conditional behavior
    - Diagnostic tools for runtime environment inspection

  Args:
    None

  Returns:
    None

  Attributes:
    PROJECT_ROOT (Path): Path to the project root directory.
    UPLOAD_PATH (Path): Path to the uploads directory.
    LOG_DIR (Path): Path to the logs directory.
    LOG_FILE (Path): Path to the main log file.
    STATIC_DIR (Path): Path to the static assets directory.
    IS_WINDOWS (bool): True if running on Windows.
    IS_LINUX (bool): True if running on Linux.
    IS_MAC (bool): True if running on macOS.
    print_runtime_diagnostics (function): Prints/logs runtime diagnostics.
    logger (logging.Logger): Logger instance for this module.

  Examples:
    from arb.portal.startup.runtime_info import (
      PROJECT_ROOT, UPLOAD_PATH, LOG_DIR, IS_WINDOWS, IS_LINUX, IS_MAC, print_runtime_diagnostics)
    print_runtime_diagnostics()

  Notes:
    - The project root directory is assumed to be named "feedback_portal".
    - Directory resolution is based on the known app structure.
    - The logger emits a debug message when this file is loaded.
    - The project root directory is assumed to be named "feedback_portal".
    - If the app is run from:
        feedback_portal/source/production/arb/wsgi.py
      then directory resolution is:
        Path(__file__).resolve().parents[0] → .../arb
        Path(__file__).resolve().parents[1] → .../production
        Path(__file__).resolve().parents[2] → .../source
        Path(__file__).resolve().parents[3] → .../feedback_portal
"""
import logging
from pathlib import Path
from platform import system

from arb.utils.file_io import get_project_root_dir

logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


# ---------------------------------------------------------------------
# Diagnostics Utility
# ---------------------------------------------------------------------
def print_runtime_diagnostics() -> None:
  """
  Print and log detected runtime paths and platform flags for debugging.

  Args:
    None

  Returns:
    None

  Examples:
    print_runtime_diagnostics()
    # Logs platform, directory, and path info for debugging

  Notes:
    - Outputs platform name, OS flags, and resolved paths.
    - Uses the logger for info-level diagnostics.
  """
  logger.info(f"{'PLATFORM':<20} = {PLATFORM}")
  logger.info(f"{'IS_WINDOWS':<20} = {IS_WINDOWS}")
  logger.info(f"{'IS_LINUX':<20} = {IS_LINUX}")
  logger.info(f"{'IS_MAC':<20} = {IS_MAC}")
  logger.info(f"{'PROJECT_ROOT':<20} = {PROJECT_ROOT}")
  logger.info(f"{'UPLOAD_PATH':<20} = {UPLOAD_PATH}")
  logger.info(f"{'LOG_DIR':<20} = {LOG_DIR}")
  logger.info(f"{'STATIC_DIR':<20} = {STATIC_DIR}")


# ---------------------------------------------------------------------
# System Platform Detection
# ---------------------------------------------------------------------
PLATFORM: str = system().lower()
IS_WINDOWS: bool = PLATFORM.startswith("win")
IS_LINUX: bool = PLATFORM.startswith("linux")
IS_MAC: bool = PLATFORM.startswith("darwin")

# ----------------------------------------------------
# Determine File Structure
# ----------------------------------------------------
# Get the platform independent project root directory knowing the app's directory structure is:
# 'feedback_portal/source/production/arb/portal/'
APP_DIR_STRUCTURE = ['feedback_portal', 'source', 'production', 'arb', 'portal']
PROJECT_ROOT: Path = get_project_root_dir(__file__, APP_DIR_STRUCTURE)
logger.debug(f"PROJECT_ROOT={PROJECT_ROOT}")

# Upload destination
UPLOAD_PATH: Path = PROJECT_ROOT / 'portal_uploads'

# Standard application folders
LOG_DIR: Path = PROJECT_ROOT / "logs"
LOG_FILE: Path = LOG_DIR / "arb_portal.log"

STATIC_DIR: Path = PROJECT_ROOT / "arb" / "portal" / "static"

# ---------------------------------------------------------------------
# Ensure Required Directories Exist
# ---------------------------------------------------------------------
for required_dir in [UPLOAD_PATH, LOG_DIR]:
  required_dir.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------
# Ensure Required Directories Exist
# ---------------------------------------------------------------------

print_runtime_diagnostics()
