"""
Centralized definition of Flask extension instances used throughout the portal.

This module avoids circular imports by creating extension objects (e.g., `db`, `csrf`)
at the top level, without initializing them until `app.init_app()` is called elsewhere.

Extensions Defined:
  - db (SQLAlchemy): SQLAlchemy instance shared across all models and routes.
  - csrf (CSRFProtect): CSRF protection used for form validation.
  - login_manager (LoginManager): User session management for authentication.
  - mail (Mail): Email sending functionality.

Notes:
  - `geoalchemy2.Geometry` must be imported for spatial field introspection,
    even if not directly referenced in code.
  - Use `with app.app_context():` when accessing `db` outside a Flask route.

"""

from pathlib import Path

from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from flask_mail import Mail
# noinspection PyUnresolvedReferences
from geoalchemy2 import Geometry  # <= not used but must be imported for introspection

from arb.__get_logger import get_logger

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')

db = SQLAlchemy()
"""SQLAlchemy: Flask SQLAlchemy instance for managing ORM and schema."""
# print(f"{type(db)=}")

csrf = CSRFProtect()
"""CSRFProtect: Flask-WTF extension for CSRF form protection."""

login_manager = LoginManager()
"""LoginManager: Flask-Login extension for user session management."""

mail = Mail()
"""Mail: Flask-Mail extension for email sending functionality."""
