"""
ARB Portal Package

This package initializes the logging system for the entire application.
Logging is configured here to ensure it's available throughout the application lifecycle.

Key Responsibilities:
---------------------
- Sets the `__version__` for the portal subpackage.
- Initializes application-wide logging system using `get_logger`.
- Provides shared logger and pretty-printer for all modules.

Logging Configuration:
---------------------
- Logger Name: "arb_portal" (used for the main application)
- Log File: feedback_portal/logs/arb_portal.log
- Log Level: DEBUG (configurable)
- Console Output: Disabled (configurable)

This logger will be used by all modules in the application that call get_logger()
without specifying a logger_name, or that import this module's logger directly.

Attributes:
-----------
__version__ (str): Semantic version of the portal package.
logger (logging.Logger): Application-wide logger instance.
pp_log (Callable): Pretty-print log formatter for structured objects.

Usage:
------
To use the shared logger and formatter in other modules:

  from arb import logger, pp_log
  
  # Or use get_logger() which will return the same logger
  from arb.__get_logger import get_logger
  logger, pp_log = get_logger()  # Uses "arb_portal" logger
"""

from pathlib import Path

from arb.__get_logger import get_logger

__version__ = "1.0.0"

# Log directory: 3 levels up from arb/__init__.py to project root, then "logs/"
# From: source/production/arb/__init__.py
# To:   feedback_portal/logs/arb_portal.log
root_logger = Path(__file__).resolve().parents[3] / "logs"
logger, pp_log = get_logger(logger_name="arb_portal", log_dir=root_logger, log_to_console=False)
