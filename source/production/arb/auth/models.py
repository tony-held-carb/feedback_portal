"""
User model and authentication/authorization logic for ARB Feedback Portal.

Current Implementation:
- Uses a local database for user authentication and management.
- Handles password hashing, email confirmation, and role-based access.
- Supports multiple roles per user using comma-separated values.

Okta Transition Plan:
- This system is a temporary solution until Okta (OIDC/SAML) is integrated.
- When Okta is adopted, authentication will be delegated to Okta, and user sessions will be managed via Okta tokens.
- User roles and permissions will be mapped from Okta claims or groups.
- The User model and authorization checks are designed to be compatible with Okta-provided user info.
- Minimal changes will be needed outside the login and user provisioning logic.

Key Features:
- Inherits from UserMixin (Flask-Login) to provide default implementations for authentication state.
- Stores user credentials, account status, and role for access control.
- Supports password hashing, password reset, email confirmation, and account lockout.
- Provides methods for role-based authorization (e.g., is_admin, has_role).
- Supports multiple roles per user (comma-separated).
"""

import datetime
import logging

from flask import current_app
from flask_login import UserMixin
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func
from werkzeug.security import check_password_hash, generate_password_hash

from arb.auth import get_db

logger = logging.getLogger(__name__)


from typing import Any, Optional

def get_auth_config(key: str, default: Any = None) -> Any:
  """
  Helper to fetch auth-related config from app.config, falling back to default_settings.py if not set.
  
  Args:
      key (str): The config key to fetch (without 'AUTH_' prefix).
      default (Any): Default value to return if config is not found.
      
  Returns:
      Any: The config value or default if not found.
      
  Examples:
      get_auth_config('PASSWORD_RESET_EXPIRATION', 3600)
      get_auth_config('MAX_LOGIN_ATTEMPTS', 5)
  """
  try:
    return current_app.config.get(f'AUTH_{key}', default)
  except Exception:
    return default


_UserModel = None


def get_user_model():
  """
  Get the User model class, creating it if it doesn't exist.
  
  This function implements a singleton pattern to ensure the User model
  is created only once and reused throughout the application.
  
  Returns:
      Type[User]: The User model class.
      
  Examples:
      User = get_user_model()
      users = User.query.all()
  """
  global _UserModel
  if _UserModel is not None:
    return _UserModel
  db = get_db()

  class User(UserMixin, db.Model):
    """
    User model for authentication and authorization.
    Inherits from UserMixin, which provides default implementations for:
      - is_authenticated: True if the user is authenticated
      - is_active: True if the user is allowed to log in
      - is_anonymous: True if the user is not logged in
      - get_id(): Returns the unique user ID
    This class stores user credentials, account status, and role for access control.
    Role and permission logic is compatible with Okta claims/groups when USE_OKTA is enabled.
    Supports multiple roles per user using comma-separated values.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active_col = Column('is_active', Boolean, default=True, nullable=False)
    is_confirmed_col = Column('is_confirmed', Boolean, default=False, nullable=False)
    created_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login_timestamp = Column(DateTime(timezone=True), nullable=True)
    password_reset_token = Column(String(255), nullable=True, unique=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    account_locked_until = Column(DateTime(timezone=True), nullable=True)
    email_confirmation_token = Column(String(255), nullable=True, unique=True)
    email_confirmation_expires = Column(DateTime(timezone=True), nullable=True)
    role = Column(String(255), default='user', nullable=False)  # Increased size for multiple roles

    @property
    def is_active(self) -> bool:
      """Return True if the user account is active (allowed to log in)."""
      return bool(self.is_active_col)

    @property
    def is_confirmed(self) -> bool:
      """Return True if the user's email has been confirmed."""
      return bool(self.is_confirmed_col)

    def set_password(self, password: str) -> None:
      """Hash and set the user's password."""
      self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
      """Check if the provided password matches the stored hash."""
      logger.debug(f"Checking password for user {self.id}")
      result = check_password_hash(str(getattr(self, 'password_hash', '')), password)
      logger.debug(f"Password check result: {result}")
      return result

    def is_account_locked(self) -> bool:
      """Return True if the account is currently locked due to failed login attempts."""
      account_locked_until = getattr(self, 'account_locked_until', None)
      if account_locked_until and account_locked_until > datetime.datetime.utcnow():
        return True
      elif account_locked_until is not None and account_locked_until <= datetime.datetime.utcnow():
        self.account_locked_until = None
        self.failed_login_attempts = 0
        get_db().session.commit()
      return False

    def record_failed_login(self, max_attempts=None, lockout_duration=None) -> None:
      """Increment failed login attempts and lock account if threshold is reached."""
      if max_attempts is None:
        max_attempts = get_auth_config('MAX_LOGIN_ATTEMPTS', 5)
      if lockout_duration is None:
        lockout_duration = get_auth_config('ACCOUNT_LOCKOUT_DURATION', 900)
      failed_login_attempts = getattr(self, 'failed_login_attempts', 0) or 0
      failed_login_attempts = int(failed_login_attempts) + 1
      self.failed_login_attempts = failed_login_attempts
      if failed_login_attempts >= max_attempts:
        self.account_locked_until = datetime.datetime.utcnow() + datetime.timedelta(seconds=lockout_duration)
      get_db().session.commit()

    def record_successful_login(self) -> None:
      """Reset failed login attempts and update last login timestamp on successful login."""
      self.failed_login_attempts = 0
      self.account_locked_until = None
      self.last_login_timestamp = datetime.datetime.utcnow()
      get_db().session.commit()

    def generate_password_reset_token(self, expiration_hours=None) -> str:
      """Generate a password reset token valid for a limited time."""
      import secrets
      if expiration_hours is None:
        expiration_seconds = get_auth_config('PASSWORD_RESET_EXPIRATION', 3600)
        expiration_hours = expiration_seconds / 3600
      token = secrets.token_urlsafe(32)
      self.password_reset_token = token
      self.password_reset_expires = datetime.datetime.utcnow() + datetime.timedelta(hours=expiration_hours)
      get_db().session.commit()
      return token

    def verify_password_reset_token(self, token: str) -> bool:
      """Verify the password reset token and clear it if valid."""
      password_reset_token = getattr(self, 'password_reset_token', None)
      password_reset_expires = getattr(self, 'password_reset_expires', None)
      if (password_reset_token == token and
          password_reset_expires and
          password_reset_expires > datetime.datetime.utcnow()):
        self.password_reset_token = None
        self.password_reset_expires = None
        get_db().session.commit()
        return True
      return False

    def generate_email_confirmation_token(self, expiration_hours: int = 24) -> str:
      """Generate an email confirmation token valid for a limited time."""
      import secrets
      token = secrets.token_urlsafe(32)
      self.email_confirmation_token = token
      self.email_confirmation_expires = datetime.datetime.utcnow() + datetime.timedelta(hours=expiration_hours)
      get_db().session.commit()
      return token

    def verify_email_confirmation_token(self, token: str) -> bool:
      """Verify the email confirmation token and confirm the user if valid."""
      email_confirmation_token = getattr(self, 'email_confirmation_token', None)
      email_confirmation_expires = getattr(self, 'email_confirmation_expires', None)
      if (email_confirmation_token == token and
          email_confirmation_expires and
          email_confirmation_expires > datetime.datetime.utcnow()):
        self.is_confirmed_col = True
        self.email_confirmation_token = None
        self.email_confirmation_expires = None
        get_db().session.commit()
        return True
      return False

    def get_roles(self) -> list:
      """Get list of user's roles as a list of strings."""
      roles_str = str(getattr(self, 'role', 'user'))
      if not roles_str:
        return ['user']
      return [role.strip() for role in roles_str.split(',') if role.strip()]

    def has_role(self, role_name: str) -> bool:
      """Return True if the user has the specified role."""
      roles = self.get_roles()
      return role_name in roles

    def has_any_role(self, *role_names: str) -> bool:
      """Return True if the user has any of the specified roles."""
      roles = self.get_roles()
      return any(role in roles for role in role_names)

    def has_all_roles(self, *role_names: str) -> bool:
      """Return True if the user has all of the specified roles."""
      roles = self.get_roles()
      return all(role in roles for role in role_names)

    def add_role(self, role_name: str) -> None:
      """Add a role to the user's existing roles."""
      if not role_name or not role_name.strip():
        return

      role_name = role_name.strip()
      current_roles = self.get_roles()

      if role_name not in current_roles:
        current_roles.append(role_name)
        self.role = ','.join(current_roles)
        get_db().session.commit()

    def remove_role(self, role_name: str) -> None:
      """Remove a role from the user's roles."""
      if not role_name or not role_name.strip():
        return

      role_name = role_name.strip()
      current_roles = self.get_roles()

      if role_name in current_roles:
        current_roles.remove(role_name)
        # Ensure user always has at least the 'user' role
        if not current_roles:
          current_roles = ['user']
        self.role = ','.join(current_roles)
        get_db().session.commit()

    def set_roles(self, role_names: list) -> None:
      """Set user's roles to the provided list."""
      if not role_names:
        role_names = ['user']

      # Clean and validate roles
      clean_roles = [role.strip() for role in role_names if role and role.strip()]
      if not clean_roles:
        clean_roles = ['user']

      self.role = ','.join(clean_roles)
      get_db().session.commit()

    def is_admin(self) -> bool:
      """Return True if the user has the 'admin' role."""
      return self.has_role('admin')

    def __repr__(self) -> str:
      """Return a string representation of the user object for debugging."""
      roles_str = ','.join(self.get_roles())
      return f'<User: {self.id}, Email: {self.email}, Roles: {roles_str}, Active: {self.is_active}, Confirmed: {self.is_confirmed}>'

  _UserModel = User
  return User
