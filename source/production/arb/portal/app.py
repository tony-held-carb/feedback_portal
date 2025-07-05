"""
Application factory for the ARB Feedback Portal (Flask app).

This module defines the `create_app()` function, which initializes and configures
the Flask application with required extensions, startup behavior, routing, and globals.

Key Responsibilities:
---------------------
- Load Flask configuration dynamically using `get_config()`
- Apply global app settings via `configure_flask_app()`
- Initialize SQLAlchemy and optionally CSRF protection
- Reflect and optionally create the application database schema
- Load dropdowns and type mappings into the app context
- Register Flask blueprints (e.g., `main`)

Usage:
------
Used by WSGI, CLI tools, or testing utilities:

import logging
    from arb.portal.app import create_app
    app = create_app()
"""

from pathlib import Path

from flask import Flask
from sqlalchemy.ext.automap import AutomapBase

from arb.portal.config import get_config
from arb.portal.extensions import db
from arb.portal.globals import Globals
from arb.portal.routes import main
from arb.portal.startup.db import db_initialize_and_create, reflect_database
from arb.portal.startup.flask import configure_flask_app
from arb.utils.database import get_reflected_base
from arb_logging import get_pretty_printer

logger = logging.getLogger(__name__)
_, pp_log = get_pretty_printer()

logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


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
  """
  app: Flask = Flask(__name__)

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
    base: AutomapBase = get_reflected_base(db)  # reuse db.metadata without hitting DB again
    app.base = base  # ✅ Attach automap base to app object

    Globals.load_type_mapping(app, db, base)
    Globals.load_drop_downs(app, db)

  # Register route blueprints
  app.register_blueprint(main)

  return app
