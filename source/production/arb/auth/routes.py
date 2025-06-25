"""
Authentication routes for ARB Feedback Portal.

- The 'auth' Blueprint is defined here and should be registered by the host app (see __init__.py for details).
- This supports both standalone and pluggable usage of the auth package.

Current Implementation:
- Handles user login, logout, registration, and account management using a local database and Flask-Login.
- Provides decorators and routes for access control (e.g., admin-only pages).

Okta Transition Plan:
- This authentication system is a temporary solution until Okta (OIDC/SAML) is integrated.
- When Okta is adopted, authentication and session management will be delegated to Okta, and user identity will be managed via Okta tokens.
- Role and permission checks (e.g., admin_required) will be mapped from Okta claims or groups.
- Most route logic will remain, but login/logout and user provisioning will be replaced or adapted for Okta.

Key Features:
- Modular design to allow easy replacement of authentication backend.
- All access control decorators and logic are compatible with external identity providers.
- The USE_OKTA flag below controls which authentication backend is used.
"""

from functools import wraps
from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from flask_login import current_user, login_required, login_user, logout_user
from arb.auth.okta_settings import USE_OKTA
from arb.auth.models import User, get_auth_config
from arb.auth import get_db

def admin_required(f):
    """
    Decorator to restrict access to admin users only.
    - If USE_OKTA is True, checks Okta claims/groups for admin access.
    - If USE_OKTA is False, uses local role field.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if USE_OKTA:
            # TODO: Check Okta token for 'admin' group/claim.
            # Need: Okta group/claim mapping for admin users.
            raise NotImplementedError("Okta admin check not implemented yet. Need Okta group/claim mapping.")
        else:
            if not current_user.is_authenticated or not current_user.is_admin():
                abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Define the Blueprint at module level for import by host app
auth = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')

# Expose the Blueprint for registration
auth_blueprint = auth

@auth.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """
    Render the admin-only dashboard page.
    In Okta, access would be restricted based on Okta admin group/claim.
    """
    if USE_OKTA:
        # TODO: Render admin dashboard for Okta-authenticated admin users.
        # Need: Okta session and group/claim context.
        raise NotImplementedError("Okta admin dashboard not implemented yet.")
    else:
        return render_template('auth/admin_dashboard.html')

@auth.route('/settings')
@login_required
def settings():
    """
    Render the user account settings page (placeholder).
    In Okta, this page may display Okta-managed profile info or link to Okta profile management.
    """
    if USE_OKTA:
        # TODO: Display Okta profile info or link to Okta profile management.
        # Need: Okta user info endpoint and integration.
        raise NotImplementedError("Okta settings/profile integration not implemented yet.")
    else:
        return render_template('auth/settings.html')

@auth.route('/email_preferences')
@login_required
def email_preferences():
    """
    Render the user email preferences page (placeholder).
    In Okta, notification preferences may be managed in Okta or remain app-specific.
    """
    if USE_OKTA:
        # TODO: Integrate with Okta notification/email preferences if available.
        # Need: Okta notification preferences API or documentation.
        raise NotImplementedError("Okta email preferences integration not implemented yet.")
    else:
        return render_template('auth/email_preferences.html')

@auth.route('/activity_log')
@login_required
def activity_log():
    """
    Render the user activity log page (placeholder).
    In Okta, activity logs may be available via Okta or remain app-specific.
    """
    if USE_OKTA:
        # TODO: Integrate with Okta activity log if available, or display app-specific log.
        # Need: Okta activity log API or documentation.
        raise NotImplementedError("Okta activity log integration not implemented yet.")
    else:
        return render_template('auth/activity_log.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route.
    - If USE_OKTA is False, handles local login form and session creation.
    - If USE_OKTA is True, delegates to Okta login (not yet implemented).
    """
    if USE_OKTA:
        # TODO: Implement Okta login redirect/flow.
        # Need: Okta OIDC/SAML login integration.
        raise NotImplementedError("Okta login not implemented yet. Need Okta OIDC/SAML integration.")
    else:
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('main.index'))
            else:
                flash('Invalid email or password.', 'danger')
        return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    """
    User logout route.
    - If USE_OKTA is False, logs out the user locally.
    - If USE_OKTA is True, delegates to Okta logout (not yet implemented).
    """
    if USE_OKTA:
        # TODO: Implement Okta logout redirect/flow.
        # Need: Okta logout endpoint/integration.
        raise NotImplementedError("Okta logout not implemented yet. Need Okta logout integration.")
    else:
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route.
    - If USE_OKTA is False, handles local registration form and user creation.
    - If USE_OKTA is True, delegates to Okta registration (not yet implemented).
    """
    if USE_OKTA:
        # TODO: Implement Okta registration or link to Okta self-service registration.
        # Need: Okta registration endpoint or documentation.
        raise NotImplementedError("Okta registration not implemented yet. Need Okta registration integration.")
    else:
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            if not email or not password:
                flash('Email and password are required.', 'danger')
            elif User.query.filter_by(email=email).first():
                flash('Email already registered.', 'warning')
            else:
                user = User(email=email)
                user.set_password(password)
                # Optionally set other fields, e.g., is_confirmed_col = True for now
                get_db().session.add(user)
                get_db().session.commit()
                flash('Registration successful. Please log in.', 'success')
                return redirect(url_for('auth.login'))
        return render_template('auth/register.html')

# cleanup: Move all code from portal/auth_routes.py here, updating imports to use auth.models, auth.forms, auth.email_util if not already done. Remove this comment after confirming migration is complete. 