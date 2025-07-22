"""
Centralized definition of Flask extension instances used throughout the auth example app.

This module avoids circular imports by creating extension objects (e.g., `db`, `mail`, `login_manager`)
at the top level, without initializing them until `app.init_app()` is called elsewhere.

Extensions Defined:
  - db (SQLAlchemy): SQLAlchemy instance for database operations
  - mail (Mail): Email sending functionality
  - login_manager (LoginManager): User session management for authentication

Notes:
  - Use `with app.app_context():` when accessing `db` outside a Flask route.
  - Extensions are initialized in the app factory pattern.
"""

from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

# Initialize extension instances
db = SQLAlchemy()
"""SQLAlchemy: Flask SQLAlchemy instance for managing ORM and schema."""

mail = Mail()
"""Mail: Flask-Mail extension for email functionality."""

login_manager = LoginManager()
"""LoginManager: Flask-Login extension for user session management."""
