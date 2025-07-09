"""
  ARB utility package initializer.

  This module initializes logging and exposes a shared logger for utility modules.
  It also defines the package version. The utils package contains general-purpose
  helpers used across the ARB project.

  Args:
    None

  Returns:
    None

  Attributes:
    logger (logging.Logger): Shared logger instance for all utility modules.
    __version__ (str): Version of the utils package.

  Examples:
    # Access the shared logger in a utility module
    from arb.utils import logger
    logger.info("Utility module loaded.")

  Notes:
    - The logger is configured at the package level for consistency.
    - No additional initialization is performed here.
"""

import logging

__version__ = "1.0.0"
logger = logging.getLogger(__name__)
