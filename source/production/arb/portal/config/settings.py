"""
Environment-specific configuration classes for the Flask application.

This file contains distinct configuration classes for development, production,
and testing environments. Each inherits from the BaseConfig class and can override
or extend configuration values as needed.

Usage:
    from config.settings import DevelopmentConfig

Notes:
  - All variables in this file are not dependent on runtime conditions other than
    OS environment variables.
  - If a variable is a setting defined at runtime, such as platform type or root directory,
    it should be defined and initialized in the startup/runtime_info.py file.
"""

import os, sys
from pathlib import Path

from arb.__get_logger import get_logger

logger, pp_log = get_logger()
logger.debug(f"{Path(__file__)} loading")


class BaseConfig:
  """Base configuration shared by all environments."""
  POSTGRES_DB_URI = (
    'postgresql+psycopg2://methane:methaneCH4@prj-bus-methane-aurora-postgresql-instance-1'
    '.cdae8kkz3fpi.us-west-2.rds.amazonaws.com/plumetracker'
  )

  SQLALCHEMY_ENGINE_OPTIONS = {'connect_args': {
    'options': '-c search_path=satellite_tracker_demo1,public -c timezone=UTC'  # practice schema
    # 'options': '-c search_path=satellite_tracker_new,public -c timezone=UTC'  # dan's live schema
  }
  }

  SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key-goes-here'
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or POSTGRES_DB_URI
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  # When enabled, Flask will log detailed information about templating files
  # consider setting to True if you're getting TemplateNotFound errors.
  EXPLAIN_TEMPLATE_LOADING = False  # Recommended setting for most use cases.

  WTF_CSRF_ENABLED = True
  LOG_LEVEL = "INFO"
  TIMEZONE = "America/Los_Angeles"

  # ---------------------------------------------------------------------
  # Get other relevant environmental variables here and commandline flags here
  # for example: set FAST_LOAD=true
  # ---------------------------------------------------------------------
  FAST_LOAD = False
  # flask does not allow for custom arguments so the next block is commented out
  # if "--fast-load" in sys.argv:
  #   print(f"--fast-load detected in CLI arguments")
  #   FAST_LOAD = True
  if os.getenv("FAST_LOAD") == "true":
    logger.info(f"FAST_LOAD detected in CLI arguments")
    FAST_LOAD = True
  logger.info(f"{FAST_LOAD = }")


class DevelopmentConfig(BaseConfig):
  """Development-specific settings."""
  DEBUG = True
  FLASK_ENV = "development"
  # EXPLAIN_TEMPLATE_LOADING = True
  LOG_LEVEL = "DEBUG"


class ProductionConfig(BaseConfig):
  """Production-specific settings."""
  DEBUG = False
  FLASK_ENV = "production"
  WTF_CSRF_ENABLED = True
  LOG_LEVEL = "INFO"


class TestingConfig(BaseConfig):
  """Settings used for unit tests and CI environments."""
  TESTING = True
  DEBUG = True
  FLASK_ENV = "testing"
  WTF_CSRF_ENABLED = False
  LOG_LEVEL = "WARNING"
