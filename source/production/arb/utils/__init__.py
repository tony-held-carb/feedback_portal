"""
RSDAS utility package initializer.

Initializes logging and exposes a shared logger for utility modules.
This package contains general-purpose helpers used across the ARB project.
"""

import logging
from arb_logging import get_pretty_printer

__version__ = "1.0.0"
logger = logging.getLogger(__name__)
_, pp_log = get_pretty_printer()
