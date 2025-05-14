"""
Provides runtime metadata and dynamic paths for the application.

This module defines:
  - Project root and key directories (uploads, logs, static)
  - Operating system detection (Windows, Linux, macOS)
  - Platform-level info useful for conditional behavior
  - Diagnostic tools for runtime environment inspection

Example usage:
    from startup.runtime_info import (
        PROJECT_ROOT, UPLOAD_PATH, LOG_DIR,
        IS_WINDOWS, IS_LINUX, IS_MAC,
        print_runtime_diagnostics
    )
Notes:
  - The project root directory is "feedback_portal"
  - if the app is run from wsgi.py file with path: feedback_portal/source/production/arb/wsgi.py
    - Path(__file__).resolve().parents[0] → .../arb
    - Path(__file__).resolve().parents[1] → .../production
    - Path(__file__).resolve().parents[2] → .../source
    - Path(__file__).resolve().parents[3] → .../feedback_portal
"""
from platform import system

from arb.__get_logger import get_logger
from arb.utils.file_io import get_project_root_dir

logger, pp_log = get_logger()


# ---------------------------------------------------------------------
# Diagnostics Utility
# ---------------------------------------------------------------------
def print_runtime_diagnostics() -> None:
  """
  Print detected runtime paths and platform flags for debugging.

  Example:
      >>> print_runtime_diagnostics()
  """
  print(f"{'PLATFORM':<20} = {PLATFORM}")
  print(f"{'IS_WINDOWS':<20} = {IS_WINDOWS}")
  print(f"{'IS_LINUX':<20} = {IS_LINUX}")
  print(f"{'IS_MAC':<20} = {IS_MAC}")
  print(f"{'PROJECT_ROOT':<20} = {PROJECT_ROOT}")
  print(f"{'UPLOAD_PATH':<20} = {UPLOAD_PATH}")
  print(f"{'LOG_DIR':<20} = {LOG_DIR}")
  print(f"{'STATIC_DIR':<20} = {STATIC_DIR}")


# ---------------------------------------------------------------------
# System Platform Detection
# ---------------------------------------------------------------------
PLATFORM = system().lower()
IS_WINDOWS = PLATFORM.startswith("win")
IS_LINUX = PLATFORM.startswith("linux")
IS_MAC = PLATFORM.startswith("darwin")

# ----------------------------------------------------
# Determine File Structure
# ----------------------------------------------------
# Get the platform independent project root directory knowing the apps directory structure is:
# 'feedback_portal/source/production/arb/portal/'
APP_DIR_STRUCTURE = ['feedback_portal', 'source', 'production', 'arb', 'portal']
PROJECT_ROOT = get_project_root_dir(__file__, APP_DIR_STRUCTURE)
logger.debug(f"PROJECT_ROOT={PROJECT_ROOT}")

# Upload destination
UPLOAD_PATH = PROJECT_ROOT / 'portal_uploads'

# Standard application folders
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "arb_portal.log"

STATIC_DIR = PROJECT_ROOT / "arb" / "portal" / "static"

# ---------------------------------------------------------------------
# Ensure Required Directories Exist
# ---------------------------------------------------------------------
for required_dir in [UPLOAD_PATH, LOG_DIR]:
  required_dir.mkdir(parents=True, exist_ok=True)

print_runtime_diagnostics()
