"""
User management routes for the Auth Example App.

Demonstrates user self-service functionality and profile management.
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from arb.auth import get_db

bp = Blueprint('user_management', __name__, url_prefix='/user')


from flask import Response, Union

@bp.route('/profile')
@login_required
def profile() -> str:
  """
  User profile page - accessible to logged-in users.
  
  Returns:
      str: Rendered HTML for the user profile page.
      
  Examples:
      # In browser: GET /user/profile (requires login)
      # Returns: HTML user profile page
  """
  return render_template('user_management/profile.html')


@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile() -> Union[str, Response]:
  """
  Edit user profile - accessible to logged-in users.
  
  Returns:
      Union[str, Response]: Rendered HTML for the edit profile page, or redirect after submission.
      
  Examples:
      # In browser: GET /user/profile/edit (requires login)
      # Returns: HTML edit profile page
      # In browser: POST /user/profile/edit (requires login)
      # Returns: Redirect to profile page
  """
  if request.method == 'POST':
    # In a real app, you'd validate and update user data
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('user_management.profile'))

  return render_template('user_management/edit_profile.html')


@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password() -> Union[str, Response]:
  """
  Change password - accessible to logged-in users.
  
  Returns:
      Union[str, Response]: Rendered HTML for the change password page, or redirect after submission.
      
  Examples:
      # In browser: GET /user/change-password (requires login)
      # Returns: HTML change password page
      # In browser: POST /user/change-password (requires login)
      # Returns: Redirect to profile page or error page
  """
  if request.method == 'POST':
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # Validate current password
    if not current_password or not current_user.check_password(current_password):
      flash('Current password is incorrect', 'error')
      return render_template('user_management/change_password.html')

    # Validate new password
    if not new_password or new_password != confirm_password:
      flash('New passwords do not match', 'error')
      return render_template('user_management/change_password.html')

    if len(new_password) < 6:
      flash('New password must be at least 6 characters', 'error')
      return render_template('user_management/change_password.html')

    # Update password
    current_user.set_password(new_password)
    get_db().session.commit()

    flash('Password changed successfully!', 'success')
    return redirect(url_for('user_management.profile'))

  return render_template('user_management/change_password.html')


@bp.route('/activity')
@login_required
def activity() -> str:
  """
  User activity log - accessible to logged-in users.
  
  Returns:
      str: Rendered HTML for the user activity page.
      
  Examples:
      # In browser: GET /user/activity (requires login)
      # Returns: HTML user activity page
  """
  return render_template('user_management/activity.html')


@bp.route('/roles')
@login_required
def view_roles() -> str:
  """
  View user roles - accessible to logged-in users.
  
  Returns:
      str: Rendered HTML for the user roles page.
      
  Examples:
      # In browser: GET /user/roles (requires login)
      # Returns: HTML user roles page
  """
  return render_template('user_management/roles.html')
