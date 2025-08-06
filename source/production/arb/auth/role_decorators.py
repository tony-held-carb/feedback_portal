"""
Enhanced role decorators for ARB Feedback Portal.

This module provides decorators for flexible role-based access control
that supports multiple roles per user.

Decorators:
- roles_required: Access if user has ANY of the specified roles
- all_roles_required: Access if user has ALL of the specified roles
- role_required: Access if user has the specified role
- admin_required: Access if user has admin role (existing functionality)
"""

from functools import wraps
from typing import Callable, TypeVar, Any

from flask import abort
from flask_login import current_user

from arb.auth.okta_settings import USE_OKTA

F = TypeVar('F', bound=Callable[..., Any])


def roles_required(*roles: str):
  """
  Decorator to restrict access to users with any of the specified roles.
  - If USE_OKTA is True, checks Okta claims/groups for role access.
  - If USE_OKTA is False, uses local role field.

  Args:
      *roles (str): Variable number of role names to check for.

  Returns:
      Callable[[F], F]: A decorator function that takes a function and returns the decorated function.

  Examples:
      @roles_required('editor', 'reviewer')
      def edit_page():
          # Only users with 'editor' OR 'reviewer' role can access
          pass
  """

  def decorator(f: F) -> F:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
      if USE_OKTA:
        # TODO: Check Okta token for any of the specified groups/claims.
        # Need: Okta group/claim mapping for role access.
        raise NotImplementedError("Okta role check not implemented yet. Need Okta group/claim mapping.")
      else:
        if not current_user.is_authenticated or not current_user.has_any_role(*roles):
          abort(403)
      return f(*args, **kwargs)

    return decorated_function  # type: ignore[return-value]

  return decorator


def all_roles_required(*roles: str):
  """
  Decorator to restrict access to users with ALL of the specified roles.
  - If USE_OKTA is True, checks Okta claims/groups for all role access.
  - If USE_OKTA is False, uses local role field.

  Args:
      *roles (str): Variable number of role names to check for.

  Returns:
      Callable[[F], F]: A decorator function that takes a function and returns the decorated function.

  Examples:
      @all_roles_required('editor', 'qaqc')
      def qaqc_edit_page():
          # Only users with BOTH 'editor' AND 'qaqc' roles can access
          pass
  """

  def decorator(f: F) -> F:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
      if USE_OKTA:
        # TODO: Check Okta token for all of the specified groups/claims.
        # Need: Okta group/claim mapping for role access.
        raise NotImplementedError("Okta all roles check not implemented yet. Need Okta group/claim mapping.")
      else:
        if not current_user.is_authenticated or not current_user.has_all_roles(*roles):
          abort(403)
      return f(*args, **kwargs)

    return decorated_function  # type: ignore[return-value]

  return decorator


def role_required(role_name: str):
  """
  Decorator to restrict access to users with the specified role.
  - If USE_OKTA is True, checks Okta claims/groups for role access.
  - If USE_OKTA is False, uses local role field.

  Args:
      role_name (str): The role name to check for.

  Returns:
      Callable[[F], F]: A decorator function that takes a function and returns the decorated function.

  Examples:
      @role_required('editor')
      def edit_page():
          # Only users with 'editor' role can access
          pass
  """

  def decorator(f: F) -> F:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
      if USE_OKTA:
        # TODO: Check Okta token for the specified group/claim.
        # Need: Okta group/claim mapping for role access.
        raise NotImplementedError("Okta role check not implemented yet. Need Okta group/claim mapping.")
      else:
        if not current_user.is_authenticated or not current_user.has_role(role_name):
          abort(403)
      return f(*args, **kwargs)

    return decorated_function  # type: ignore[return-value]

  return decorator


def admin_required(f: F) -> F:
  """
  Decorator to restrict access to admin users only.
  - If USE_OKTA is True, checks Okta claims/groups for admin access.
  - If USE_OKTA is False, uses local role field.

  Args:
      f (F): The function to decorate.

  Returns:
      F: The decorated function.

  Examples:
      @admin_required
      def admin_only_page():
          # Only admin users can access this
          pass
  """

  @wraps(f)
  def decorated_function(*args: Any, **kwargs: Any) -> Any:
    if USE_OKTA:
      # TODO: Check Okta token for 'admin' group/claim.
      # Need: Okta group/claim mapping for admin users.
      raise NotImplementedError("Okta admin check not implemented yet. Need Okta group/claim mapping.")
    else:
      if not current_user.is_authenticated or not current_user.is_admin():
        abort(403)
    return f(*args, **kwargs)

  return decorated_function  # type: ignore[return-value]
