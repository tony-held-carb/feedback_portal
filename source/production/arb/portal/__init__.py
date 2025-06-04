"""
Initialization for the arb.portal package.

This package defines the Flask portal app, including routes,
forms, templates, configuration, and startup routines.
"""
from pathlib import Path
from arb.__get_logger import get_logger

__version__ = "1.3.0"

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')

