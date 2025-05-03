"""
Flask app factory and setup logic.

Refactored from original monolithic app.py into a factory pattern
to allow for better testability, scalability, and deployment compatibility.

This file:
  - Initializes the Flask app
  - Loads configuration
  - Reflects the Postgres database schema
  - Registers blueprints and initializes extensions

To run the app:
  Use wsgi.py or an external WSGI server like Gunicorn.

All prior comments and TODOs retained or moved where appropriate.
"""

from flask import Flask
from jinja2 import StrictUndefined

import arb.__get_logger as get_logger
from arb.portal.config import Config, db_create, reflect_database
from arb.portal.extensions import db
from arb.portal.globals import Globals
from arb.portal.routes import main as main_blueprint

logger, pp_log = get_logger.get_logger(__name__, __file__)


def create_app() -> Flask:
  """
  Application factory function.

  Returns:
    Flask: A configured Flask application instance.
  """
  app = Flask(__name__)

  # Load configuration into the app
  Config.configure_flask_app(app)

  # Jinja2 should raise errors for undefined variables
  app.jinja_env.undefined = StrictUndefined

  # Bind SQLAlchemy to the app
  db.init_app(app)

  with app.app_context():
    # Create database structure if needed
    db_create(app, db)

    # Reflect the current Postgres schema into SQLAlchemy
    base = reflect_database(app, db)
    app.base = base  # Store for use in routes via current_app.base

    # Load globals
    Globals.load_type_mapping(app, db, base)
    Globals.load_drop_downs(app, db)

  # Register application blueprints
  app.register_blueprint(main_blueprint)

  return app
