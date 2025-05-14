"""
Dynamic configuration loader for the Flask application.

This module provides a function `get_config()` to dynamically determine which
configuration class to use based on an environment variable.

Usage:
    from config import get_config
    app.config.from_object(get_config())
"""
import os
from pathlib import Path

from arb.__get_logger import get_logger
from arb.portal.config.settings import DevelopmentConfig, ProductionConfig, TestingConfig

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def get_config():
  """
  Return the appropriate configuration class based on FLASK_ENV or CONFIG_TYPE.

  Returns:
      (type): A configuration class object.
  """
  env = os.environ.get("FLASK_ENV", "").lower()
  override = os.environ.get("CONFIG_TYPE", "").lower()

  if override == "production" or env == "production":
    return ProductionConfig
  elif override == "testing" or env == "testing":
    return TestingConfig
  else:
    return DevelopmentConfig
