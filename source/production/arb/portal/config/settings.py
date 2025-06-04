"""
Environment-specific configuration classes for the Flask application.

Defines base and derived configuration classes used by the ARB portal.
Each config class inherits from `BaseConfig` and may override environment-specific values.

Usage:
  from config.settings import DevelopmentConfig, ProductionConfig, TestingConfig

Notes:
  - Static and environment-derived values belong here.
  - Runtime-dependent settings (platform, CLI, etc.) should go in `startup/runtime_info.py`.
"""


import os, sys
from pathlib import Path

from arb.__get_logger import get_logger

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


class BaseConfig:
  """
  Base configuration shared across all environments.

  Attributes:
    POSTGRES_DB_URI (str): Default PostgreSQL URI if DATABASE_URI is unset.
    SQLALCHEMY_ENGINE_OPTIONS (dict): Connection settings for SQLAlchemy.
    SECRET_KEY (str): Flask session key.
    SQLALCHEMY_DATABASE_URI (str): Final URI used by the app.
    SQLALCHEMY_TRACK_MODIFICATIONS (bool): SQLAlchemy event system flag.
    EXPLAIN_TEMPLATE_LOADING (bool): Whether to trace template resolution errors.
    WTF_CSRF_ENABLED (bool): Cross-site request forgery protection toggle.
    LOG_LEVEL (str): Default logging level.
    TIMEZONE (str): Target timezone for timestamp formatting.
    FAST_LOAD (bool): Enables performance optimizations at startup.
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
  Configuration for local development.

  Attributes:
    DEBUG (bool): Enables debug mode.
    FLASK_ENV (str): Flask environment indicator.
    LOG_LEVEL (str): Logging level (default: "DEBUG").
  """
  DEBUG = True
  FLASK_ENV = "development"
  # EXPLAIN_TEMPLATE_LOADING = True
  LOG_LEVEL = "DEBUG"


class ProductionConfig(BaseConfig):
  """
  Configuration for deployed production environments.

  Attributes:
    DEBUG (bool): Disables debug features.
    FLASK_ENV (str): Environment label for Flask runtime.
    WTF_CSRF_ENABLED (bool): Enables CSRF protection.
    LOG_LEVEL (str): Logging level (default: "INFO").
  """
  DEBUG = False
  FLASK_ENV = "production"
  WTF_CSRF_ENABLED = True
  LOG_LEVEL = "INFO"


class TestingConfig(BaseConfig):
  """
  Configuration for isolated testing environments.

  Attributes:
    TESTING (bool): Enables Flask test mode.
    DEBUG (bool): Enables debug logging.
    FLASK_ENV (str): Flask environment label.
    WTF_CSRF_ENABLED (bool): Disables CSRF for test convenience.
    LOG_LEVEL (str): Logging level (default: "WARNING").
  """
  TESTING = True
  DEBUG = True
  FLASK_ENV = "testing"
  WTF_CSRF_ENABLED = False
  LOG_LEVEL = "WARNING"
