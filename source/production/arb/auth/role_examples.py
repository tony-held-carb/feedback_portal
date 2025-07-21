"""
Examples of how to use the enhanced multiple roles functionality.

This file demonstrates various ways to work with multiple roles
in the ARB Feedback Portal authentication system.
"""

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from arb.auth.models import User
from arb.auth.role_decorators import admin_required, all_roles_required, role_required, roles_required

# Example Blueprint for demonstration
example = Blueprint('example', __name__)


# Example 1: Single role check
@example.route('/editor-only')
@role_required('editor')
def editor_only_page():
  """Only users with 'editor' role can access this page."""
  return render_template('editor_only.html')


# Example 2: Any of multiple roles
@example.route('/review-access')
@roles_required('editor', 'reviewer', 'qaqc')
def review_access_page():
  """Users with 'editor' OR 'reviewer' OR 'qaqc' roles can access."""
  return render_template('review_access.html')


# Example 3: All roles required
@example.route('/advanced-edit')
@all_roles_required('editor', 'qaqc')
def advanced_edit_page():
  """Only users with BOTH 'editor' AND 'qaqc' roles can access."""
  return render_template('advanced_edit.html')


# Example 4: Admin access
@example.route('/admin-panel')
@admin_required
def admin_panel():
  """Only users with 'admin' role can access."""
  return render_template('admin_panel.html')


# Example 5: Manual role checking in views
@example.route('/flexible-access')
@login_required
def flexible_access_page():
  """Manual role checking for complex logic."""

  # Check for specific roles
  if current_user.has_role('admin'):
    # Admin gets full access
    return render_template('admin_view.html')
  elif current_user.has_any_role('editor', 'reviewer'):
    # Editors and reviewers get edit access
    return render_template('editor_view.html')
  elif current_user.has_role('viewer'):
    # Viewers get read-only access
    return render_template('viewer_view.html')
  else:
    # Default user access
    return render_template('basic_view.html')


# Example 6: Template-level role checking
@example.route('/dashboard')
@login_required
def dashboard():
  """Dashboard with role-based UI elements."""
  return render_template('dashboard.html')


# Example usage in templates:
"""
{% if current_user.is_authenticated %}
    <h1>Welcome, {{ current_user.email }}</h1>
    
    <p>Your roles: {{ current_user.get_roles() | join(', ') }}</p>
    
    {% if current_user.has_role('admin') %}
        <a href="{{ url_for('admin_panel') }}">Admin Panel</a>
    {% endif %}
    
    {% if current_user.has_any_role('editor', 'reviewer') %}
        <a href="{{ url_for('editor_only_page') }}">Editor Tools</a>
    {% endif %}
    
    {% if current_user.has_all_roles('editor', 'qaqc') %}
        <a href="{{ url_for('advanced_edit_page') }}">Advanced Editing</a>
    {% endif %}
    
    {% if current_user.has_role('qaqc') %}
        <a href="{{ url_for('qaqc_dashboard') }}">QA/QC Dashboard</a>
    {% endif %}
{% endif %}
"""


# Example 7: Programmatic role management
def manage_user_roles_example():
  """Example of how to programmatically manage user roles."""

  # Get a user
  user = User.query.filter_by(email='example@carb.ca.gov').first()

  if user:
    # Check current roles
    print(f"Current roles: {user.get_roles()}")

    # Add a new role
    user.add_role('editor')
    print(f"After adding editor: {user.get_roles()}")

    # Add another role
    user.add_role('qaqc')
    print(f"After adding qaqc: {user.get_roles()}")

    # Check specific roles
    print(f"Has editor role: {user.has_role('editor')}")
    print(f"Has any of editor/reviewer: {user.has_any_role('editor', 'reviewer')}")
    print(f"Has all of editor/qaqc: {user.has_all_roles('editor', 'qaqc')}")

    # Remove a role
    user.remove_role('editor')
    print(f"After removing editor: {user.get_roles()}")

    # Set roles to a specific list
    user.set_roles(['reviewer', 'qaqc'])
    print(f"After setting roles: {user.get_roles()}")


# Example 8: Database migration helper
def migrate_single_role_to_multiple():
  """
  Helper function to migrate existing single-role users to multiple roles.
  Run this once after updating the database schema.
  """
  from arb.auth import get_db

  db = get_db()
  users = User.query.all()

  for user in users:
    # Get current single role
    current_role = user.role

    # If it's already comma-separated, skip
    if ',' in current_role:
      continue

    # Convert single role to list format
    if current_role and current_role.strip():
      user.set_roles([current_role.strip()])
    else:
      user.set_roles(['user'])

  db.session.commit()
  print("Migration completed successfully!")


if __name__ == "__main__":
  # Run examples
  print("Multiple Roles Examples:")
  print("========================")

  # This would be run in a Flask app context
  # manage_user_roles_example()

  print("To use these examples:")
  print("1. Import the decorators: from arb.auth.role_decorators import *")
  print("2. Use them on your routes: @roles_required('editor', 'reviewer')")
  print("3. Check roles in templates: {{ current_user.has_role('editor') }}")
  print("4. Manage roles programmatically: user.add_role('editor')")
