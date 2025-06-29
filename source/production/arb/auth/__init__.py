"""
ARB Feedback Portal authentication package initializer.

- Ensures all authentication logic (including user loader) is registered when the auth package is imported.
- Designed to be a generalizable, drop-in authentication system for other projects.

Refactor (2024-07):
- Adds `init_auth` function to support both standalone and pluggable usage.
- Allows injection of db, mail, login_manager, and app for maximum flexibility.
- All internal modules should use these injected instances, not hardcoded imports.

Usage:
    from arb.auth import init_auth
    init_auth(app=app, db=db, mail=mail, login_manager=login_manager)

- If running standalone, you can call init_auth with a minimal Flask app and extensions.
- If using as a package, call init_auth from your main app's factory/setup.

-------------------------------------------------------------------------------
IMPORTANT: login_manager module import and instance distinction
-------------------------------------------------------------------------------
- The line 'from . import login_manager' at the end of this file ensures that any setup code in login_manager.py
  (such as the @login_manager.user_loader registration) is executed as soon as the auth package is imported.
  This is a common Flask pattern to guarantee that user loader and other Flask-Login setup is always registered,
  even if you never directly import login_manager elsewhere.

- The name 'login_manager' here refers to the MODULE (login_manager.py), not the injected instance.

- The injected LoginManager instance (passed via init_auth and stored as _login_manager) is the one that should be
  used throughout the package via get_login_manager().

- This distinction is important: the module import is for side effects (setup/registration), while the variable is
  for dependency injection and runtime flexibility.

Best Practice:
  - Keep this import as the last line of the file to ensure setup code runs.
  - Always use get_login_manager() to access the injected instance.
  - Document this pattern for future maintainers.

-------------------------------------------------------------------------------
Summary Table
-------------------------------------------------------------------------------
| Name                | What is it?                | Why is it needed?                        |
|---------------------|----------------------------|------------------------------------------|
| 'from . import 
| login_manager'      | Imports the module         | Ensures user loader is registered        |
| _login_manager      | Variable in __init__.py    | Stores the injected LoginManager instance|
| get_login_manager() | Function in __init__.py    | Returns the injected instance            |
-------------------------------------------------------------------------------
"""

# Store extension references for use throughout the package
_db = None
_mail = None
_login_manager = None
_app = None


def init_auth(app=None, db=None, mail=None, login_manager=None, config=None):
    """
    Initialize the ARB Auth package for standalone or pluggable use.

    Args:
        app (Flask, optional): The Flask app instance. Required for standalone use.
        db (SQLAlchemy, optional): The SQLAlchemy instance to use for models.
        mail (Mail, optional): The Flask-Mail instance for email sending.
        login_manager (LoginManager, optional): The Flask-Login manager for session handling.
        config (dict, optional): Optional config overrides for auth settings.

    Notes:
        - If running standalone, provide all extensions and app.
        - If using as a package, pass in the host app's extensions.
        - All internal modules should import these via `from arb.auth import get_db`, etc.
    """
    global _db, _mail, _login_manager, _app
    _db = db
    _mail = mail
    _login_manager = login_manager
    _app = app

    # Register the user loader after initialization
    from .login_manager import register_user_loader
    register_user_loader()

    # Optionally register blueprint, models, etc. here if needed
    # Example: if app is not None: app.register_blueprint(auth_blueprint)
    # (Blueprint registration can also be left to the host app for flexibility)

    # Optionally apply config overrides
    if app is not None and config is not None:
        app.config.update(config)


def get_db():
    """Return the injected SQLAlchemy db instance. Raises RuntimeError if not initialized."""
    if _db is None:
        raise RuntimeError("Auth package not initialized: call init_auth(app, db, ...) before using get_db().")
    return _db

def get_mail():
    """Return the injected Flask-Mail instance. Raises RuntimeError if not initialized."""
    if _mail is None:
        raise RuntimeError("Auth package not initialized: call init_auth(app, ..., mail=mail, ...) before using get_mail().")
    return _mail

def get_login_manager():
    """Return the injected Flask-Login manager instance. Raises RuntimeError if not initialized."""
    if _login_manager is None:
        raise RuntimeError("Auth package not initialized: call init_auth(app, ..., login_manager=login_manager, ...) before using get_login_manager().")
    return _login_manager

def get_app():
    """Return the injected Flask app instance (if any). Raises RuntimeError if not initialized."""
    if _app is None:
        raise RuntimeError("Auth package not initialized: call init_auth(app, ...) before using get_app().")
    return _app

# Make sure this is the last line of the file (see header comments for details)
# from . import login_manager  # Removed - now handled in init_auth()

# Import and expose the auth Blueprint for registration by the host app
from .routes import auth_blueprint

def register_auth_blueprint(app):
    """
    Register the auth Blueprint with the given Flask app.
    Usage:
        from arb.auth import register_auth_blueprint
        register_auth_blueprint(app)
    """
    app.register_blueprint(auth_blueprint) 