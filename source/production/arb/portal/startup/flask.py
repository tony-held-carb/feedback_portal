"""
Flask-related initialization utilities.

This module sets up Jinja environment, logging, and template globals.

Example:
    from startup.flask import configure_flask_app
"""
from pathlib import Path

from flask import Flask
from arb.__get_logger import get_logger
from arb.portal.startup.runtime_info import UPLOAD_PATH
from jinja2 import StrictUndefined
import werkzeug

from arb.utils.date_and_time import date_to_string, repr_datetime_to_string
from arb.utils.diagnostics import diag_recursive
from arb.utils.misc import args_to_string


from arb.__get_logger import get_logger
logger, pp_log = get_logger()
logger.debug(f"{Path(__file__).name} loading")


def configure_flask_app(app: Flask) -> None:
    """
    Configure logging, Jinja, and app-wide settings.

    Args:
        app (Flask): Flask app instance.

    Example:
        configure_flask_app(app)
    """
    logger.debug("configure_flask_app() called")

    app.jinja_env.globals["app_name"] = "CARB Feedback Portal"

    # -------------------------------------------------------------------------
    # Logging Configuration
    # -------------------------------------------------------------------------
    logger.setLevel(app.config.get("LOG_LEVEL", "INFO"))
    # Logging: Turn off color coding (avoids special terminal characters in log file)
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
    app.jinja_env.filters['date_to_string'] = date_to_string
    # todo - repr_datetime_to_string modified and this may no longer work ...
    app.jinja_env.filters['repr_datetime_to_string'] = repr_datetime_to_string
    app.jinja_env.filters['args_to_string'] = args_to_string

    logger.debug("Flask Jinja2 globals and logging initialized.")
