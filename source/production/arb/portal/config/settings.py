"""
Environment-specific configuration classes for the Flask application.

This file defines base and environment-specific configuration classes used
by the ARB portal Flask app. Each class inherits from `BaseConfig` and may
override or extend configuration parameters.

Usage:
  from config.settings import DevelopmentConfig, ProductionConfig, TestingConfig

Notes:
  - All config values here are static or driven by OS environment variables.
  - If a setting depends on runtime context (platform, root paths, etc.),
    it should be defined in `startup/runtime_info.py`.
"""


import os, sys
from pathlib import Path

from arb.__get_logger import get_logger

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


class BaseConfig:
  """
  Base configuration shared across all environments.

  Includes database settings, engine options, and common secrets.

  Attributes:
    POSTGRES_DB_URI (str): Default PostgreSQL URI used if no env var is set.
    SQLALCHEMY_ENGINE_OPTIONS (dict): Custom SQLAlchemy engine settings.
    SECRET_KEY (str): Flask session key.
    SQLALCHEMY_DATABASE_URI (str): Final database URI for the app.
  """
  POSTGRES_DB_URI = (
    'postgresql+psycopg2://methane:methaneCH4@prj-bus-methane-aurora-postgresql-instance-1'
    '.cdae8kkz3fpi.us-west-2.rds.amazonaws.com/plumetracker'
  )

  SQLALCHEMY_ENGINE_OPTIONS = {'connect_args': {
    # 'options': '-c search_path=satellite_tracker_demo1,public -c timezone=UTC'  # practice schema
    'options': '-c search_path=satellite_tracker_new,public -c timezone=UTC'  # dan's live schema
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
  """
  Development-specific configuration.

  - Enables Flask debug mode and testing behaviors.
  - Intended for local use by developers.
  """
  DEBUG = True
  FLASK_ENV = "development"
  # EXPLAIN_TEMPLATE_LOADING = True
  LOG_LEVEL = "DEBUG"


class ProductionConfig(BaseConfig):
  """
  Production-specific configuration.

  - Enables production flags.
  - Should only be used in deployed environments.
  """
  DEBUG = False
  FLASK_ENV = "production"
  WTF_CSRF_ENABLED = True
  LOG_LEVEL = "INFO"


class TestingConfig(BaseConfig):
  """
  Configuration for test environments.

  - Enables isolated testing flags.
  - Should be used when running CI tests or pytest suites.
  """
  TESTING = True
  DEBUG = True
  FLASK_ENV = "testing"
  WTF_CSRF_ENABLED = False
  LOG_LEVEL = "WARNING"
