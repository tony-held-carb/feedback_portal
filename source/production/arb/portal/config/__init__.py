"""
Dynamic configuration loader for the Flask application.

This module provides the `get_config()` function to dynamically determine
which Flask configuration class to use based on environment variables.

Key Features:
-------------
- Supports switching between Development, Testing, and Production modes.
- Prioritizes the `CONFIG_TYPE` environment variable for overrides.
- Falls back to `FLASK_ENV` if no override is provided.

Usage:
------
import logging
    from config import get_config
    app.config.from_object(get_config())

Environment Variables:
----------------------
- CONFIG_TYPE (str): Explicit config selector (e.g., "production", "testing").
- FLASK_ENV (str): Flask's default config selector, used if CONFIG_TYPE is unset.
"""

import os
from pathlib import Path
import logging

from arb.portal.config.settings import DevelopmentConfig, ProductionConfig, TestingConfig

logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def get_config() -> type:
  """
  Return the appropriate Flask configuration class.

  Resolution Order:
    1. CONFIG_TYPE (highest priority)
    2. FLASK_ENV (fallback)

  Returns:
    type: One of ProductionConfig, TestingConfig, or DevelopmentConfig.
  """
  env = os.environ.get("FLASK_ENV", "").lower()
  override = os.environ.get("CONFIG_TYPE", "").lower()

  if override == "production" or env == "production":
    return ProductionConfig
  elif override == "testing" or env == "testing":
    return TestingConfig
  else:
    return DevelopmentConfig
