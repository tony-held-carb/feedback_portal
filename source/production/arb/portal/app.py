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

from flask import Flask

from arb.portal.config import get_config
from arb.portal.extensions import csrf, db
from arb.portal.routes import main  # Replace with modular blueprints if separated
from arb.portal.startup.db import db_initialize_and_create, reflect_database
from arb.portal.startup.flask import configure_flask_app
from arb.portal.globals import Globals

import arb.__get_logger as get_logger
logger, pp_log = get_logger.get_logger(__name__, __file__)


def create_app() -> Flask:
  """
  Application factory for creating a Flask app instance.

  Returns:
      app (Flask): The configured Flask application instance.
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
    Globals.load_type_mapping(app, db, base)
    Globals.load_drop_downs(app, db)

  # Register route blueprints
  app.register_blueprint(main)

  return app
