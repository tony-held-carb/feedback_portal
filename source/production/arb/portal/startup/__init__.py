"""
Initializes the `startup` subpackage for Flask application setup.

This package provides startup routines for:
  - Flask app configuration
  - SQLAlchemy database initialization
  - Runtime context resolution (e.g., CLI mode, platform info)

Files in this subpackage are invoked by the main application factory (`create_app`)
and by WSGI or CLI entry points to ensure consistent initialization.
"""

