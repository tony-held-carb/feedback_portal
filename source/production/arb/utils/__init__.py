"""
RSDAS utility package initializer.

Initializes logging and exposes a shared logger for utility modules.
This package contains general-purpose helpers used across the ARB project.
"""

from arb.__get_logger import get_logger

__version__ = "1.0.0"
logger, pp_log = get_logger()
