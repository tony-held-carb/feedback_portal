"""
Login manager and user loader for ARB Feedback Portal authentication.

Current Implementation:
- Loads users from the local database using the User model.
- Registers the user_loader function with Flask-Login's LoginManager.

Okta Transition Plan:
- When USE_OKTA is True, user loading will be based on Okta session/token info instead of the local database.
- This file documents the transition plan and provides a single place to update user loading logic for Okta.

How to Identify Okta-Ready Code:
- The user_loader function checks USE_OKTA and raises NotImplementedError for Okta until integration is complete.
"""

from arb.auth.models import get_user_model
from arb.auth.okta_settings import USE_OKTA

def load_user(user_id):
    """
    Load a user for Flask-Login session management.
    - If USE_OKTA is False, loads user from the local database by primary key.
    - If USE_OKTA is True, loads user from Okta session/token (not yet implemented).
    """
    if USE_OKTA:
        # TODO: Implement user loading from Okta session/token.
        # Need: Okta user info endpoint, session/token integration.
        raise NotImplementedError("Okta user loading not implemented yet. Need Okta user info integration.")
    else:
        User = get_user_model()
        return User.query.get(int(user_id))

def register_user_loader():
    """Register the user loader with the login manager after initialization."""
    from arb.auth import get_login_manager
    get_login_manager().user_loader(load_user) 