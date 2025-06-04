"""
Application factory for the ARB Feedback Portal Flask app.

This module defines the `create_app()` function, which initializes the
Flask application with configuration, extensions, routes, and startup routines.

Key responsibilities:
  - Load configuration dynamically using get_config()
  - Configure Jinja2 and logging
  - Initialize database and CSRF protection
  - Reflect database schema and create tables if needed
  - Register Flask Blueprints

Usage:
    from arb.portal.app import create_app
    app = create_app()
"""

from pathlib import Path

from flask import Flask

from arb.__get_logger import get_logger
from arb.portal.config import get_config
from arb.portal.extensions import db
from arb.portal.globals import Globals
from arb.portal.routes import main  # Replace with modular blueprints if separated
from arb.portal.startup.db import db_initialize_and_create, reflect_database
from arb.portal.startup.flask import configure_flask_app
from arb.utils.database import get_reflected_base

logger, pp_log = get_logger()

logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def create_app() -> Flask:
  """
  Creates and configures the Flask application.

  Args:
    config_object (str): Import path to a configuration class.

  Returns:
    Flask: Configured Flask application instance.
  """
  app = Flask(__name__)

  # Load configuration from config/settings.py
  app.config.from_object(get_config())

  # Setup Jinja2, logging, and app-wide config
  configure_flask_app(app)

  # Initialize Flask extensions
  db.init_app(app)
  # GPT recommends this, but I'm commenting it out for now
  # csrf.init_app(app)

  # Database initialization and reflection (within app context)
  with app.app_context():
    db_initialize_and_create()
    reflect_database()

    # Load dropdowns, mappings, and other global data
    base = get_reflected_base(db)  # reuse db.metadata without hitting DB again
    app.base = base  # ✅ Attach automap base to app object

    Globals.load_type_mapping(app, db, base)
    Globals.load_drop_downs(app, db)

  # Register route blueprints
  app.register_blueprint(main)

  return app
