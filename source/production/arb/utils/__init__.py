"""
RSDAS utility package initializer.

Initializes logging and exposes a shared logger for utility modules.
This package contains general-purpose helpers used across the ARB project.
"""

import logging

__version__ = "1.0.0"
logger = logging.getLogger(__name__)
