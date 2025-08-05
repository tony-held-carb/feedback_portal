"""
  Environment-specific configuration classes for the ARB Feedback Portal Flask application.

  Defines base and derived configuration classes used by the ARB portal.
  Each config class inherits from `BaseConfig` and may override environment-specific values.

  Attributes:
    BaseConfig (class): Base configuration shared across all environments.
    DevelopmentConfig (class): Configuration for local development.
    ProductionConfig (class): Configuration for deployed production environments.
    TestingConfig (class): Configuration for isolated testing environments.
    logger (logging.Logger): Logger instance for this module.

  Examples:
    from arb.portal.config.settings import DevelopmentConfig, ProductionConfig, TestingConfig
    app.config.from_object(DevelopmentConfig)

  Notes:
    - Static and environment-derived values belong here.
    - Runtime-dependent settings (platform, CLI, etc.) should go in `startup/runtime_info.py`.
"""

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


class BaseConfig:
  """
  Base configuration shared across all environments.

  Attributes:
    POSTGRES_DB_URI (str): Default PostgresQL URI if DATABASE_URI is unset.
    SQLALCHEMY_ENGINE_OPTIONS (dict): Connection settings for SQLAlchemy.
    SECRET_KEY (str): Flask session key.
    SQLALCHEMY_DATABASE_URI (str): Final URI used by the app.
    SQLALCHEMY_TRACK_MODIFICATIONS (bool): SQLAlchemy event system flag.
    EXPLAIN_TEMPLATE_LOADING (bool): Whether to trace template resolution errors.
    WTF_CSRF_ENABLED (bool): Cross-site request forgery protection toggle.
    LOG_LEVEL (str): Default logging level.
    TIMEZONE (str): Target timezone for timestamp formatting.
    FAST_LOAD (bool): Enables performance optimizations at startup.
    logger (logging.Logger): Logger instance for this module.

  Examples:
    app.config.from_object(BaseConfig)

  Notes:
    - All environment-specific configs inherit from this class.
    - FAST_LOAD can be set via the FAST_LOAD environment variable.
  """
  # noinspection SpellCheckingInspection
  POSTGRES_DB_URI = (
    'postgresql+psycopg2://methane:methaneCH4@prj-bus-methane-aurora-postgresql-instance-1'
    '.cdae8kkz3fpi.us-west-2.rds.amazonaws.com/plumetracker'
  )
  # "prj-sandbox-smdms-postgresql-serverless.cluster-cjqb8tty130x.us-west-2.rds.amazonaws.com"

  POSTGRES_ENGINE_OPTIONS = {'connect_args': {
    'options': '-c search_path=satellite_tracker_demo1,public -c timezone=UTC'  # practice schema
    # 'options': '-c search_path=satellite_tracker_new,public -c timezone=UTC'  # dan's live schema
  }
  }

  SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key-goes-here'
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or POSTGRES_DB_URI
  # Parse SQLALCHEMY_ENGINE_OPTIONS from environment if set, otherwise use default
  _engine_options_env = os.environ.get('DATABASE_ENGINE_OPTIONS')
  if _engine_options_env:
    try:
      SQLALCHEMY_ENGINE_OPTIONS = json.loads(_engine_options_env)
    except Exception as e:
      print(f"[ERROR] Could not parse DATABASE_ENGINE_OPTIONS env var as JSON: {e}")
      SQLALCHEMY_ENGINE_OPTIONS = POSTGRES_ENGINE_OPTIONS
  else:
    SQLALCHEMY_ENGINE_OPTIONS = POSTGRES_ENGINE_OPTIONS
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  # When enabled, Flask will log detailed information about templating files
  # consider setting to True if you're getting TemplateNotFound errors.
  EXPLAIN_TEMPLATE_LOADING = False  # Recommended setting for most use cases.

  WTF_CSRF_ENABLED = True
  LOG_LEVEL = "INFO"
  TIMEZONE = "America/Los_Angeles"

  # ---------------------------------------------------------------------
  # Get/Set other relevant environmental variables here and commandline arguments.
  # for example: set FAST_LOAD=true
  # ---------------------------------------------------------------------
  FAST_LOAD = False
  # flask does not allow for custom arguments, so the next block is commented out
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

  Examples:
    app.config.from_object(DevelopmentConfig)

  Notes:
    - Inherits from BaseConfig.
    - Sets DEBUG to True and LOG_LEVEL to "DEBUG".
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

  Examples:
    app.config.from_object(ProductionConfig)

  Notes:
    - Inherits from BaseConfig.
    - Sets DEBUG to False and LOG_LEVEL to "INFO".
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

  Examples:
    app.config.from_object(TestingConfig)

  Notes:
    - Inherits from BaseConfig.
    - Sets TESTING to True and LOG_LEVEL to "WARNING".
  """
  TESTING = True
  DEBUG = True
  FLASK_ENV = "testing"
  WTF_CSRF_ENABLED = False
  LOG_LEVEL = "WARNING"
