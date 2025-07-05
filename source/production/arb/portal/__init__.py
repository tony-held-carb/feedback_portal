"""
Initialization module for the `arb.portal` package.

This package implements the web-based feedback portal for ARB operations.
It provides the Flask app instance, routes, form definitions, template rendering,
data models, and configuration logic.

Key Responsibilities:
---------------------
- Defines the `__version__` string for the portal subpackage.
- Initializes the shared `logger` and `pp_log` formatter using `__get_logger`.
- Logs file load events to aid diagnostics and traceability.

Recommendation:
---------------
To reuse the package-wide logger and formatter:

from arb.logging.arb_logging import get_pretty_printer
"""
import logging
from pathlib import Path

__version__ = "1.3.0"

logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')
