"""
User management routes for the Auth Example App.

Demonstrates user self-service functionality and profile management.
"""

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from arb.auth.models import get_user_model
from arb.auth import get_db

bp = Blueprint('user_management', __name__, url_prefix='/user')

@bp.route('/profile')
@login_required
def profile():
    """User profile page - accessible to logged-in users."""
    return render_template('user_management/profile.html')

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile - accessible to logged-in users."""
    if request.method == 'POST':
        # In a real app, you'd validate and update user data
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_management.profile'))
    
    return render_template('user_management/edit_profile.html')

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password - accessible to logged-in users."""
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
def activity():
    """User activity log - accessible to logged-in users."""
    return render_template('user_management/activity.html')

@bp.route('/roles')
@login_required
def view_roles():
    """View user roles - accessible to logged-in users."""
    return render_template('user_management/roles.html') 