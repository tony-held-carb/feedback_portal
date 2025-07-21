"""
Main routes for the Auth Example App.

Demonstrates basic functionality and role-based access control.
"""

from flask import Blueprint, render_template
from flask_login import login_required

from arb.auth.role_decorators import all_roles_required, role_required, roles_required

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
  """Homepage - accessible to everyone."""
  return render_template('main/index.html')


@bp.route('/dashboard')
@login_required
def dashboard():
  """User dashboard - requires login."""
  return render_template('main/dashboard.html')


@bp.route('/editor-tools')
@roles_required('editor', 'admin')
def editor_tools():
  """Editor tools - accessible to editors or admins."""
  return render_template('main/editor_tools.html')


@bp.route('/qaqc-tools')
@role_required('qaqc')
def qaqc_tools():
  """QA/QC tools - accessible only to qaqc users."""
  return render_template('main/qaqc_tools.html')


@bp.route('/advanced-editing')
@all_roles_required('editor', 'qaqc')
def advanced_editing():
  """Advanced editing - requires BOTH editor AND qaqc roles."""
  return render_template('main/advanced_editing.html')


@bp.route('/review-panel')
@roles_required('reviewer', 'manager', 'admin')
def review_panel():
  """Review panel - accessible to reviewers, managers, or admins."""
  return render_template('main/review_panel.html')


@bp.route('/public-info')
def public_info():
  """Public information - accessible to everyone."""
  return render_template('main/public_info.html')
