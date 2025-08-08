"""
Admin routes for the Auth Example App.

Demonstrates admin-only functionality and user management.
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from arb.auth import get_db
from arb.auth.models import get_user_model
from arb.auth.role_decorators import admin_required

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@admin_required
def admin_dashboard() -> str:
  """
  Admin dashboard - accessible only to admins.

  Returns:
      str: Rendered HTML for the admin dashboard.

  Examples:
      # In browser: GET /admin/ (requires admin role)
      # Returns: HTML admin dashboard
  """
  return render_template('admin/dashboard.html')


@bp.route('/users')
@admin_required
def user_list() -> str:
  """
  List all users - admin only.

  Returns:
      str: Rendered HTML for the user list page.

  Examples:
      # In browser: GET /admin/users (requires admin role)
      # Returns: HTML user list page
  """
  User = get_user_model()
  users = User.query.all()
  return render_template('admin/user_list.html', users=users)


@bp.route('/user/<int:user_id>')
@admin_required
def user_detail(user_id: int) -> str:
  """
  View user details - admin only.

  Args:
      user_id (int): The ID of the user to view.

  Returns:
      str: Rendered HTML for the user detail page.

  Examples:
      # In browser: GET /admin/user/123 (requires admin role)
      # Returns: HTML user detail page
  """
  User = get_user_model()
  user = User.query.get_or_404(user_id)
  return render_template('admin/user_detail.html', user=user)


from flask import Response


@bp.route('/user/<int:user_id>/add-role', methods=['POST'])
@admin_required
def add_user_role(user_id: int) -> Response:
  """
  Add a role to a user - admin only.

  Args:
      user_id (int): The ID of the user to add a role to.

  Returns:
      Response: Redirect to the user detail page.

  Examples:
      # In browser: POST /admin/user/123/add-role (requires admin role)
      # Returns: Redirect to user detail page
  """
  user = get_user_model().query.get_or_404(user_id)
  role = request.form.get('role')

  if role:
    user.add_role(role)
    flash(f'Added role "{role}" to user {user.email}', 'success')
  else:
    flash('No role specified', 'error')

  return redirect(url_for('admin.user_detail', user_id=user_id))


@bp.route('/user/<int:user_id>/remove-role', methods=['POST'])
@admin_required
def remove_user_role(user_id: int) -> Response:
  """
  Remove a role from a user - admin only.

  Args:
      user_id (int): The ID of the user to remove a role from.

  Returns:
      Response: Redirect to the user detail page.

  Examples:
      # In browser: POST /admin/user/123/remove-role (requires admin role)
      # Returns: Redirect to user detail page
  """
  user = get_user_model().query.get_or_404(user_id)
  role = request.form.get('role')

  if role:
    user.remove_role(role)
    flash(f'Removed role "{role}" from user {user.email}', 'success')
  else:
    flash('No role specified', 'error')

  return redirect(url_for('admin.user_detail', user_id=user_id))


@bp.route('/user/<int:user_id>/set-roles', methods=['POST'])
@admin_required
def set_user_roles(user_id: int) -> Response:
  """
  Set all roles for a user - admin only.

  Args:
      user_id (int): The ID of the user to set roles for.

  Returns:
      Response: Redirect to the user detail page.

  Examples:
      # In browser: POST /admin/user/123/set-roles (requires admin role)
      # Returns: Redirect to user detail page
  """
  user = get_user_model().query.get_or_404(user_id)
  roles_str = request.form.get('roles', '')

  # Parse comma-separated roles
  roles = [role.strip() for role in roles_str.split(',') if role.strip()]
  user.set_roles(roles)

  flash(f'Updated roles for user {user.email}: {", ".join(roles)}', 'success')
  return redirect(url_for('admin.user_detail', user_id=user_id))


@bp.route('/user/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def toggle_user_active(user_id: int) -> Response:
  """
  Toggle user active status - admin only.

  Args:
      user_id (int): The ID of the user to toggle active status for.

  Returns:
      Response: Redirect to the user detail page.

  Examples:
      # In browser: POST /admin/user/123/toggle-active (requires admin role)
      # Returns: Redirect to user detail page
  """
  User = get_user_model()
  user = User.query.get_or_404(user_id)

  # Don't allow deactivating yourself
  if user.id == current_user.id:
    flash('Cannot deactivate your own account', 'error')
    return redirect(url_for('admin.user_detail', user_id=user_id))

  user.is_active_col = not user.is_active_col
  get_db().session.commit()

  status = 'activated' if user.is_active_col else 'deactivated'
  flash(f'User {user.email} {status}', 'success')

  return redirect(url_for('admin.user_detail', user_id=user_id))


@bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id: int) -> Response:
  """
  Delete a user - admin only.

  Args:
      user_id (int): The ID of the user to delete.

  Returns:
      Response: Redirect to the user list page.

  Examples:
      # In browser: POST /admin/user/123/delete (requires admin role)
      # Returns: Redirect to user list page
  """
  User = get_user_model()
  user = User.query.get_or_404(user_id)

  # Don't allow deleting yourself
  if user.id == current_user.id:
    flash('Cannot delete your own account', 'error')
    return redirect(url_for('admin.user_detail', user_id=user_id))

  # Store email for flash message before deletion
  user_email = user.email

  # Delete the user
  get_db().session.delete(user)
  get_db().session.commit()

  flash(f'User {user_email} has been permanently deleted', 'success')
  return redirect(url_for('admin.user_list'))
