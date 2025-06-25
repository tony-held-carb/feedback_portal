"""
Environment-specific configuration classes for the Flask application.

Defines base and derived configuration classes used by the ARB portal.
Each config class inherits from `BaseConfig` and may override environment-specific values.

---
USE_AUTH flag (for maintainers):
- If True, enables authentication/authorization (arb.auth).
- If False, disables all auth and runs the app in open mode (no login, registration, or user checks).
- Set in config or via environment variable.
- Used in app factory to control registration/binding of auth system.
---

---
AUTH_ Configuration Pattern (for maintainers):
- All authentication/email/security config defaults are provided by arb.auth.default_settings.py.
- You only need to set AUTH_ variables here if you want to override them for this deployment.
- If an AUTH_ variable is not set here, arb.auth will use its own default.
- This keeps config DRY and makes it clear what is customized for this deployment.
---

Usage:
  from config.settings import DevelopmentConfig, ProductionConfig, TestingConfig

Notes:
  - Static and environment-derived values belong here.
  - Runtime-dependent settings (platform, CLI, etc.) should go in `startup/runtime_info.py`.
"""

import os
from pathlib import Path

from arb.__get_logger import get_logger
# (No need to import AUTH_ variables from arb.auth.default_settings unless you want to override a specific value)

logger, pp_log = get_logger()
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
    USE_AUTH (bool): Enables or disables authentication/authorization (arb.auth).
  """
  # noinspection SpellCheckingInspection
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

  USE_AUTH = False  # Set to True to enable authentication/authorization (arb.auth)

  # --- AUTH/EMAIL/SECURITY CONFIG (see arb.auth.default_settings) ---
  # Only set AUTH_ variables here if you want to override the default for this deployment.
  # Example:
  # AUTH_MAIL_SERVER = os.environ.get('AUTH_MAIL_SERVER') or 'smtp.example.com'
  # AUTH_MAIL_USERNAME = os.environ.get('AUTH_MAIL_USERNAME') or 'myuser@example.com'
  # --- END AUTH CONFIG ---

  # ---------------------------------------------------------------------
  # Get/Set other relevant environmental variables here and commandline arguments.
  # for example: set FAST_LOAD=true
  # ---------------------------------------------------------------------
  FAST_LOAD = False
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
