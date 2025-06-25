"""
Application factory for the ARB Feedback Portal (Flask app).

This module defines the `create_app()` function, which initializes and configures
the Flask application with required extensions, startup behavior, routing, and globals.

Key Responsibilities:
---------------------
- Load Flask configuration dynamically using `get_config()`
- Apply global app settings via `configure_flask_app()`
- Initialize SQLAlchemy and optionally CSRF protection
- Initialize Flask-Login for user authentication
- Reflect and optionally create the application database schema
- Load dropdowns and type mappings into the app context
- Register Flask blueprints (e.g., `main`, `auth`)

Usage:
------
Used by WSGI, CLI tools, or testing utilities:

    from arb.portal.app import create_app
    app = create_app()
"""

from pathlib import Path

from flask import Flask
from sqlalchemy.ext.automap import AutomapBase

from arb.__get_logger import get_logger
from arb.portal.config import get_config
from arb.portal.extensions import db
from arb.portal.globals import Globals
from arb.portal.routes import main
from arb.portal.startup.db import db_initialize_and_create, reflect_database
from arb.portal.startup.flask import configure_flask_app
from arb.utils.database import get_reflected_base

logger, pp_log = get_logger()

logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')

# Define mail and login_manager as None for linter compatibility
mail = None
login_manager = None

def create_app() -> Flask:
  """
  Create and configure the ARB Feedback Portal Flask application.

  Follows the Flask application factory pattern. This function loads configuration,
  initializes extensions, binds SQLAlchemy to the app, and registers the
  route blueprints and global utilities.

  Returns:
    Flask: A fully initialized Flask application instance with:
      - App context globals (dropdowns, types)
      - SQLAlchemy base metadata (`app.base`)
      - Registered routes via blueprints
      - User authentication via Flask-Login
  """
  app: Flask = Flask(__name__)

  # Load configuration from config/settings.py
  app.config.from_object(get_config())

  # Setup Jinja2, logging, and app-wide config
  configure_flask_app(app)

  # Initialize Flask extensions
  db.init_app(app)
  # Only set up mail and login_manager if auth is enabled
  if app.config.get('USE_AUTH', True):
      global mail, login_manager
      from arb.portal.extensions import mail as _mail, login_manager as _login_manager
      mail = _mail
      login_manager = _login_manager
      mail.init_app(app)
      login_manager.init_app(app)
      login_manager.login_view = 'auth.login'
      login_manager.login_message = 'Please log in to access this page.'
      login_manager.login_message_category = 'info'
      try:
          from arb.auth import register_auth_blueprint
          register_auth_blueprint(app)
      except ImportError:
          raise RuntimeError("USE_AUTH is True but arb.auth is not available.")
  # else: run in open mode (no auth)

  # Register main blueprint (always)
  app.register_blueprint(main)

  # Database initialization and reflection (within app context)
  with app.app_context():
    db_initialize_and_create()
    reflect_database()

    # Load dropdowns, mappings, and other global data
    base: AutomapBase = get_reflected_base(db)  # reuse db.metadata without hitting DB again
    app.base = base  # ✅ Attach automap base to app object

    Globals.load_type_mapping(app, db, base)
    Globals.load_drop_downs(app, db)

  # Inject USE_AUTH into all templates
  @app.context_processor
  def inject_use_auth():
      return {'USE_AUTH': app.config.get('USE_AUTH', True)}

  return app
