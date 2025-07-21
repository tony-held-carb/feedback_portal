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
def admin_dashboard():
  """Admin dashboard - accessible only to admins."""
  return render_template('admin/dashboard.html')


@bp.route('/users')
@admin_required
def user_list():
  """List all users - admin only."""
  User = get_user_model()
  users = User.query.all()
  return render_template('admin/user_list.html', users=users)


@bp.route('/user/<int:user_id>')
@admin_required
def user_detail(user_id):
  """View user details - admin only."""
  User = get_user_model()
  user = User.query.get_or_404(user_id)
  return render_template('admin/user_detail.html', user=user)


@bp.route('/user/<int:user_id>/add-role', methods=['POST'])
@admin_required
def add_user_role(user_id):
  """Add a role to a user - admin only."""
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
def remove_user_role(user_id):
  """Remove a role from a user - admin only."""
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
def set_user_roles(user_id):
  """Set all roles for a user - admin only."""
  user = get_user_model().query.get_or_404(user_id)
  roles_str = request.form.get('roles', '')

  # Parse comma-separated roles
  roles = [role.strip() for role in roles_str.split(',') if role.strip()]
  user.set_roles(roles)

  flash(f'Updated roles for user {user.email}: {", ".join(roles)}', 'success')
  return redirect(url_for('admin.user_detail', user_id=user_id))


@bp.route('/user/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def toggle_user_active(user_id):
  """Toggle user active status - admin only."""
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
def delete_user(user_id):
  """Delete a user - admin only."""
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
