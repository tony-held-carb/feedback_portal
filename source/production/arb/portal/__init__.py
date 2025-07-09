"""
  Initialization module for the arb.portal package.

  This package implements the web-based feedback portal for ARB operations.
  It defines the package version.

  Args:
    None

  Returns:
    None

  Attributes:
    __version__ (str): Semantic version of the portal package.
    logger (logging.Logger): Logger instance.

"""
import logging
from pathlib import Path

__version__ = "1.3.0"

logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')
