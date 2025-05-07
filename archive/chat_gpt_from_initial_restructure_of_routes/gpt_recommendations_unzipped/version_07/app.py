"""
Flask app factory and setup logic.

Refactored from original monolithic app.py into a factory pattern
to allow for better testability, scalability, and deployment compatibility.

This file:
  - Initializes the Flask app
  - Loads configuration
  - Registers blueprints
  - Initializes extensions

To run the app:
  Use wsgi.py or an external WSGI server such as gunicorn.

All prior comments and TODOs retained or moved where appropriate.
"""

import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from jinja2 import StrictUndefined

from config import Config
from extensions import db
from globals import Globals
from constants import CA_TIME_ZONE, UTC_TIME_ZONE
from routes import main as main_blueprint

def create_app() -> Flask:
  """
  Application factory function.

  Returns:
    Flask: A configured Flask application instance.
  """
  app = Flask(__name__)
  app.config.from_object(Config)

  # Setup Jinja environment to error on undefined
  app.jinja_env.undefined = StrictUndefined

  # Initialize extensions
  db.init_app(app)

  # Register blueprints
  app.register_blueprint(main_blueprint)

  # Setup shared globals
  with app.app_context():
    Globals.load_drop_downs(app, db)
    Globals.initialize_shared_state(app, db)

  return app
