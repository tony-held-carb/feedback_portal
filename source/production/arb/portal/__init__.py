"""
Initialization module for the `arb.portal` package.

This package implements the web-based feedback portal for ARB operations.
It provides the Flask app instance, routes, form definitions, template rendering,
data models, and configuration logic.

Key Responsibilities:
---------------------
- Sets the `__version__` for the portal subpackage.
- Configures the package logger using `__get_logger`.
- Logs file load events to aid with diagnostics and traceability.

Recommendation:
---------------
Import `logger` and `pp_log` from this module when working within the portal package:

    from arb.portal import logger, pp_log
"""


from pathlib import Path

from arb.__get_logger import get_logger

__version__ = "1.3.0"

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')
