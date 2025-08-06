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
def editor_only_page() -> str:
  """
  Only users with 'editor' role can access this page.
  
  Returns:
      str: Rendered HTML for the editor-only page.
      
  Examples:
      # In browser: GET /editor-only (requires editor role)
      # Returns: HTML editor-only page
  """
  return render_template('editor_only.html')


# Example 2: Any of multiple roles
@example.route('/review-access')
@roles_required('editor', 'reviewer', 'qaqc')
def review_access_page() -> str:
  """
  Users with 'editor' OR 'reviewer' OR 'qaqc' roles can access.
  
  Returns:
      str: Rendered HTML for the review access page.
      
  Examples:
      # In browser: GET /review-access (requires editor, reviewer, or qaqc role)
      # Returns: HTML review access page
  """
  return render_template('review_access.html')


# Example 3: All roles required
@example.route('/advanced-edit')
@all_roles_required('editor', 'qaqc')
def advanced_edit_page() -> str:
  """
  Only users with BOTH 'editor' AND 'qaqc' roles can access.
  
  Returns:
      str: Rendered HTML for the advanced edit page.
      
  Examples:
      # In browser: GET /advanced-edit (requires both editor and qaqc roles)
      # Returns: HTML advanced edit page
  """
  return render_template('advanced_edit.html')


# Example 4: Admin access
@example.route('/admin-panel')
@admin_required
def admin_panel() -> str:
  """
  Only users with 'admin' role can access.
  
  Returns:
      str: Rendered HTML for the admin panel page.
      
  Examples:
      # In browser: GET /admin-panel (requires admin role)
      # Returns: HTML admin panel page
  """
  return render_template('admin_panel.html')


# Example 5: Manual role checking in views
@example.route('/flexible-access')
@login_required
def flexible_access_page() -> str:
  """
  Manual role checking for complex logic.
  
  Returns:
      str: Rendered HTML for the appropriate view based on user roles.
      
  Examples:
      # In browser: GET /flexible-access (requires login)
      # Returns: HTML view based on user roles
  """

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
def dashboard() -> str:
  """
  Dashboard with role-based UI elements.
  
  Returns:
      str: Rendered HTML for the dashboard page.
      
  Examples:
      # In browser: GET /dashboard (requires login)
      # Returns: HTML dashboard page
  """
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
def manage_user_roles_example() -> None:
  """
  Example of how to programmatically manage user roles.
  
  Returns:
      None: This function demonstrates role management but doesn't return anything.
      
  Examples:
      manage_user_roles_example()
  """

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
def migrate_single_role_to_multiple() -> None:
  """
  Helper function to migrate existing single-role users to multiple roles.
  Run this once after updating the database schema.
  
  Returns:
      None: This function migrates data but doesn't return anything.
      
  Examples:
      migrate_single_role_to_multiple()
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
