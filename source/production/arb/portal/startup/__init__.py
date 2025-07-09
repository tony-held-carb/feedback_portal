"""
  Initializes the `startup` subpackage for Flask application setup.

  This package provides startup routines for:
    - Flask app configuration
    - SQLAlchemy database initialization
    - Runtime context resolution (e.g., CLI mode, platform info)

  Args:
    None

  Returns:
    None

  Attributes:
    None

  Examples:
    # This package is imported by the main application factory
    from arb.portal.startup import db, flask

  Notes:
    - Files in this subpackage are invoked by the main application factory (`create_app`)
      and by WSGI or CLI entry points to ensure consistent initialization.
"""
