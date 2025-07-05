"""
Centralized logging utility for use across the ARB portal (or any Python project).

This module should be imported first in any file that requires logging. It is
deliberately named `__get_logger.py` to ensure it appears first when imports
are sorted alphabetically—ensuring logging is configured before any modules emit log messages.

This file is now a thin wrapper around the arb.logging module to maintain
import order while providing a clean modular architecture.

Key Features:
-------------
- Initializes logging once per Python process to prevent redundant configurations.
- Automatically creates log files under a `logs/` directory, named after the entry-point script
  (e.g., running `wsgi.py` results in `logs/wsgi.log`).
- Provides a built-in `PrettyPrinter` helper for human-readable, structured log output.
- Supports console logging (optional) and custom output paths for log files.

Usage Examples:
---------------
Import and initialize the logger in any module:

  from arb import __get_logger as get_logger
  logger, pp_log = get_logger(logger_name=__name__)

  logger.debug(f"Basic log message")
  logger.debug(pp_log({"structured": "data", "for": "inspection"}))

To customize behavior:

  logger, pp_log = get_logger(
    logger_name=__name__,
    log_to_console=True,
    force_command_line=False,
    file_path="custom_logs/")

Configuration Behavior:
-----------------------
- If `file_path` is provided, logs are written to that directory using the provided `file_stem`.
- If `file_path` is not provided, the logger writes to `logs/<stem>.log`.
- If executed from `__main__` or `__init__`, the log file defaults to `logs/app_logger.log`.
- All log files use UTF-8 encoding and include timestamps with millisecond precision.

Recommendation:
---------------
Place `__get_logger.py` near the root of your source tree and import it as early
as possible in each module to guarantee consistent logging setup.

IMPORTANT: Always import __get_logger before any other imports that might trigger
logging events. This ensures logging is properly configured before use.

Example:
  from arb import __get_logger as get_logger  # Import FIRST
  logger, pp_log = get_logger(logger_name=__name__)
  
  # ... other imports ...
  from arb.portal.config.accessors import get_upload_folder

Implementation Note:
-------------------
The actual implementation has been moved to arb.logging module for better
modularity while maintaining backward compatibility and import order.
"""

# Import the actual implementation from the logging module
from arb.logging import get_logger, get_pretty_printer

# Re-export the functions to maintain compatibility
__all__ = ['get_logger', 'get_pretty_printer']
