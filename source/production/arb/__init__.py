"""
Initialization module for the `arb.portal` package.

This package implements the web-based feedback portal for ARB operations.
It provides the Flask app instance, route definitions, template rendering,
form generation, data model logic, and configuration setup.

Key Responsibilities:
---------------------
- Sets the `__version__` for the portal subpackage.
- Configures the logger and pretty-printer using `__get_logger`.
- Logs the current file load event for traceability.

Attributes:
-----------
__version__ (str): Semantic version of the portal package.
logger (logging.Logger): Module-level logger instance.
pp_log (Callable): Pretty-print log formatter for structured objects.

Recommendation:
---------------
To use the shared logger and formatter in other modules:

  from arb.portal import logger, pp_log
"""

from pathlib import Path
from arb.__get_logger import get_logger

__version__ = "1.0.0"

root_logger = file_path = Path(__file__).resolve().parents[3] / "logs"
logger, pp_log = get_logger(file_stem="arb_portal", file_path=root_logger, log_to_console=False)
