"""
Main routes for the Auth Example App.

Demonstrates basic functionality and role-based access control.
"""

from flask import Blueprint, render_template
from flask_login import login_required

from arb.auth.role_decorators import all_roles_required, role_required, roles_required

bp = Blueprint('main', __name__)


@bp.route('/')
def index() -> str:
  """
  Homepage - accessible to everyone.
  
  Returns:
      str: Rendered HTML for the homepage.
      
  Examples:
      # In browser: GET /
      # Returns: HTML homepage
  """
  return render_template('main/index.html')


@bp.route('/dashboard')
@login_required
def dashboard() -> str:
  """
  User dashboard - requires login.
  
  Returns:
      str: Rendered HTML for the user dashboard.
      
  Examples:
      # In browser: GET /dashboard (requires login)
      # Returns: HTML dashboard
  """
  return render_template('main/dashboard.html')


@bp.route('/editor-tools')
@roles_required('editor', 'admin')
def editor_tools() -> str:
  """
  Editor tools - accessible to editors or admins.
  
  Returns:
      str: Rendered HTML for the editor tools page.
      
  Examples:
      # In browser: GET /editor-tools (requires editor or admin role)
      # Returns: HTML editor tools page
  """
  return render_template('main/editor_tools.html')


@bp.route('/qaqc-tools')
@role_required('qaqc')
def qaqc_tools() -> str:
  """
  QA/QC tools - accessible only to qaqc users.
  
  Returns:
      str: Rendered HTML for the QA/QC tools page.
      
  Examples:
      # In browser: GET /qaqc-tools (requires qaqc role)
      # Returns: HTML QA/QC tools page
  """
  return render_template('main/qaqc_tools.html')


@bp.route('/advanced-editing')
@all_roles_required('editor', 'qaqc')
def advanced_editing() -> str:
  """
  Advanced editing - requires BOTH editor AND qaqc roles.
  
  Returns:
      str: Rendered HTML for the advanced editing page.
      
  Examples:
      # In browser: GET /advanced-editing (requires both editor and qaqc roles)
      # Returns: HTML advanced editing page
  """
  return render_template('main/advanced_editing.html')


@bp.route('/review-panel')
@roles_required('reviewer', 'manager', 'admin')
def review_panel() -> str:
  """
  Review panel - accessible to reviewers, managers, or admins.
  
  Returns:
      str: Rendered HTML for the review panel page.
      
  Examples:
      # In browser: GET /review-panel (requires reviewer, manager, or admin role)
      # Returns: HTML review panel page
  """
  return render_template('main/review_panel.html')


@bp.route('/public-info')
def public_info() -> str:
  """
  Public information - accessible to everyone.
  
  Returns:
      str: Rendered HTML for the public info page.
      
  Examples:
      # In browser: GET /public-info
      # Returns: HTML public info page
  """
  return render_template('main/public_info.html')
