"""
Flask-specific application setup utilities for the ARB Feedback Portal.

This module configures Flask app behavior, including:
  - Jinja2 environment customization
  - Upload limits and paths
  - Flask logger settings
  - Custom template filters and globals

Should be invoked during application factory setup:

Example:
  from startup.flask import configure_flask_app
  app = Flask(__name__)
  configure_flask_app(app)
"""
from pathlib import Path
from zoneinfo import ZoneInfo

import werkzeug
from flask import Flask
from jinja2 import StrictUndefined

from arb.__get_logger import get_logger
from arb.portal.startup.runtime_info import UPLOAD_PATH
from arb.utils.date_and_time import date_to_string, repr_datetime_to_string
from arb.utils.diagnostics import diag_recursive
from arb.utils.misc import args_to_string

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def configure_flask_app(app: Flask) -> None:
  """
  Apply global configuration to the Flask app instance.

  Args:
    app (Flask): The Flask application to configure.

  Configures:
    - Jinja2 environment:
        * Enables strict mode for undefined variables
        * Trims and left-strips whitespace blocks
        * Registers custom filters and timezone globals
    - Upload settings:
        * Sets `UPLOAD_FOLDER` to the shared upload path
        * Limits `MAX_CONTENT_LENGTH` to 16MB
    - Logger:
        * Applies `LOG_LEVEL` from app config
        * Disables Werkzeug color log markup
  """
  logger.debug(f"configure_flask_app() called")

  app.jinja_env.globals["app_name"] = "CARB Feedback Portal"

  # -------------------------------------------------------------------------
  # Logging Configuration
  # -------------------------------------------------------------------------
  logger.setLevel(app.config.get("LOG_LEVEL", "INFO"))
  # Logging: Turn off color coding (avoids special terminal characters in the log file)
  werkzeug.serving._log_add_style = False

  # -------------------------------------------------------------------------
  # Upload Configuration
  # -------------------------------------------------------------------------
  app.config['UPLOAD_FOLDER'] = UPLOAD_PATH
  app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

  # -------------------------------------------------------------------------
  # Jinja Configuration
  # -------------------------------------------------------------------------
  app.jinja_env.undefined = StrictUndefined

  # Jinja: Trim whitespace before/after {{ }} text injection
  app.jinja_env.trim_blocks = True
  app.jinja_env.lstrip_blocks = True

  # Jinja: custom filters for debugging and string manipulation
  app.jinja_env.filters['debug'] = diag_recursive
  # todo - make sure these datetime filters work in light of the use of native and UTC timestamps
  app.jinja_env.filters['date_to_string'] = date_to_string
  app.jinja_env.filters['repr_datetime_to_string'] = repr_datetime_to_string
  app.jinja_env.filters['args_to_string'] = args_to_string

  # Jinja: expose Python ZoneInfo class to templates for local time conversion
  app.jinja_env.globals["california_tz"] = ZoneInfo("America/Los_Angeles")
  logger.debug(f"Flask Jinja2 globals and logging initialized.")
