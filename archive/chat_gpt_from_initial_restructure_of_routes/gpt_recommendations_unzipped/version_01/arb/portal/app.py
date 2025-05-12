from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from arb.portal.extensions import db  # assumes you are initializing db in extensions.py
from arb.portal.routes import register_routes
from arb.portal.shared import initialize_shared_state
from arb.portal.constants import DEFAULT_UPLOAD_FOLDER


def create_app() -> Flask:
  """
  Flask application factory function.

  This function initializes and returns a Flask application instance.
  It sets configuration options, initializes extensions like SQLAlchemy,
  registers blueprints or routes, and prepares global/shared state.

  Returns:
    Flask: A configured Flask application instance.

  Example:
    >>> from arb.portal.app import create_app
    >>> app = create_app()
    >>> app.run(debug=True)
  """
  app = Flask(__name__)
  app.config.from_object("arb.portal.config")
  app.config.setdefault("UPLOAD_FOLDER", DEFAULT_UPLOAD_FOLDER)

  # Initialize extensions
  db.init_app(app)

  # Initialize shared state (e.g., Globals)
  with app.app_context():
    initialize_shared_state(app, db)

  # Register route handlers
  register_routes(app)

  return app


if __name__ == '__main__':
  app = create_app()
  app.run(host="0.0.0.0", port=5150, debug=True)
