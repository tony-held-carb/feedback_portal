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
"""

from flask import Flask
from jinja2 import StrictUndefined

import arb.__get_logger as get_logger
# from arb.portal.config import Config, db_create, reflect_database
from arb.portal.extensions import db
from arb.portal.globals import Globals
from arb.portal.routes import main as main_blueprint

logger, pp_log = get_logger.get_logger(__name__, __file__)


def create_app() -> Flask:
  """
  Flask application factory.

  This function creates and configures an instance of the Flask application.
  It is meant to be used with a WSGI server and follows the Flask application
  factory pattern.

  Returns:
      Flask: A fully configured Flask application instance.


  Raises:
      RuntimeError: If schema reflection or globals loading fails.
  """
  app = Flask(__name__)

  # Load Flask settings (e.g., SECRET_KEY, SQLALCHEMY_DATABASE_URI)
  Config.configure_flask_app(app)

  # Raise template errors for missing Jinja2 variables
  app.jinja_env.undefined = StrictUndefined

  # Initialize SQLAlchemy extension
  db.init_app(app)

  with app.app_context():
    # Create or upgrade database structure
    db_create(app, db)

    # Reflect database schema into SQLAlchemy ORM
    base = reflect_database(app, db)
    app.base = base  # Required for runtime use via current_app.base

    # Load dropdowns, mappings, and other global data
    Globals.load_type_mapping(app, db, base)
    Globals.load_drop_downs(app, db)

  # Register blueprints with the Flask app
  app.register_blueprint(main_blueprint)

  return app


def run_diagnostics():
  """
  Run diagnostics to test key aspects of the app factory setup.

  This function performs a dry-run of the app factory to ensure that
  core components are initialized properly. It does not start the
  Flask server.

  Tests performed:
      - App creation and configuration
      - Database initialization and schema reflection
      - Runtime globals loading
      - Blueprint registration

  Warnings:
      - This is not a substitute for full integration testing.
      - Assumes that the target database URI is reachable and valid.

  Raises:
      AssertionError: If any diagnostic step fails unexpectedly.
  """
  print("Starting diagnostics for app factory...\n")

  app = create_app()

  with app.app_context():
    # Check config
    assert app.config.get("SQLALCHEMY_DATABASE_URI"), "Missing SQLALCHEMY_DATABASE_URI"
    print("✓ Configuration loaded.")

    # Check that SQLAlchemy was initialized
    assert db.engine is not None, "SQLAlchemy engine is not initialized"
    print("✓ SQLAlchemy engine initialized.")

    # Check that reflected base was attached
    assert hasattr(app, "base"), "Reflected database base is not attached to app"
    print("✓ Database schema reflected and attached to app.base.")

    # Check Globals
    assert Globals.drop_downs, "Dropdowns not loaded into Globals"
    print("✓ Runtime globals loaded .")

    # Check blueprint
    registered = any(bp.name == "main" for bp in app.blueprints.values())
    assert registered, "Main blueprint not registered"
    print("✓ Main blueprint registered.\n")

  print("App factory diagnostics completed successfully.")


if __name__ == "__main__":
  run_diagnostics()
