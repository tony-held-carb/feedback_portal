"""
Authentication routes for ARB Feedback Portal.
"""

from functools import wraps
from flask import Blueprint, render_template, abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin-only dashboard page."""
    return render_template('auth/admin_dashboard.html')

# (Move all code from portal/auth_routes.py here, updating imports to use auth.models, auth.forms, auth.email_util) 