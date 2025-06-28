"""
Authentication routes for ARB Feedback Portal.

- The 'auth' Blueprint is defined here and should be registered by the host app (see __init__.py for details).
- This supports both standalone and pluggable usage of the auth package.

Current Implementation:
- Handles user login, logout, registration, and account management using a local database and Flask-Login.
- Provides decorators and routes for access control (e.g., admin-only pages).
- Supports multiple roles per user with flexible role-based access control.

Okta Transition Plan:
- This authentication system is a temporary solution until Okta (OIDC/SAML) is integrated.
- When Okta is adopted, authentication and session management will be delegated to Okta, and user identity will be managed via Okta tokens.
- Role and permission checks (e.g., admin_required) will be mapped from Okta claims or groups.
- Most route logic will remain, but login/logout and user provisioning will be replaced or adapted for Okta.

Key Features:
- Modular design to allow easy replacement of authentication backend.
- All access control decorators and logic are compatible with external identity providers.
- The USE_OKTA flag below controls which authentication backend is used.
- Multiple role support with flexible decorators for different access patterns.
"""

from functools import wraps
from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from flask_login import current_user, login_required, login_user, logout_user
from arb.auth.okta_settings import USE_OKTA
from arb.auth.models import get_user_model, get_auth_config
from arb.auth import get_db
from arb.__get_logger import get_logger

logger, pp_log = get_logger()

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

def roles_required(*roles):
    """
    Decorator to restrict access to users with any of the specified roles.
    - If USE_OKTA is True, checks Okta claims/groups for role access.
    - If USE_OKTA is False, uses local role field.
    
    Args:
        *roles: Variable number of role names to check for.
    
    Example:
        @roles_required('editor', 'reviewer')
        def edit_page():
            # Only users with 'editor' OR 'reviewer' role can access
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if USE_OKTA:
                # TODO: Check Okta token for any of the specified groups/claims.
                # Need: Okta group/claim mapping for role access.
                raise NotImplementedError("Okta role check not implemented yet. Need Okta group/claim mapping.")
            else:
                if not current_user.is_authenticated or not current_user.has_any_role(*roles):
                    abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def all_roles_required(*roles):
    """
    Decorator to restrict access to users with ALL of the specified roles.
    - If USE_OKTA is True, checks Okta claims/groups for all role access.
    - If USE_OKTA is False, uses local role field.
    
    Args:
        *roles: Variable number of role names to check for.
    
    Example:
        @all_roles_required('editor', 'qaqc')
        def qaqc_edit_page():
            # Only users with BOTH 'editor' AND 'qaqc' roles can access
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if USE_OKTA:
                # TODO: Check Okta token for all of the specified groups/claims.
                # Need: Okta group/claim mapping for role access.
                raise NotImplementedError("Okta all roles check not implemented yet. Need Okta group/claim mapping.")
            else:
                if not current_user.is_authenticated or not current_user.has_all_roles(*roles):
                    abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def role_required(role_name):
    """
    Decorator to restrict access to users with the specified role.
    - If USE_OKTA is True, checks Okta claims/groups for role access.
    - If USE_OKTA is False, uses local role field.
    
    Args:
        role_name: The role name to check for.
    
    Example:
        @role_required('editor')
        def edit_page():
            # Only users with 'editor' role can access
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if USE_OKTA:
                # TODO: Check Okta token for the specified group/claim.
                # Need: Okta group/claim mapping for role access.
                raise NotImplementedError("Okta role check not implemented yet. Need Okta group/claim mapping.")
            else:
                if not current_user.is_authenticated or not current_user.has_role(role_name):
                    abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

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

@auth.route('/editor/dashboard')
@role_required('editor')
def editor_dashboard():
    """
    Render the editor-only dashboard page.
    Only users with 'editor' role can access.
    """
    if USE_OKTA:
        # TODO: Render editor dashboard for Okta-authenticated editor users.
        raise NotImplementedError("Okta editor dashboard not implemented yet.")
    else:
        return render_template('auth/editor_dashboard.html')

@auth.route('/qaqc/dashboard')
@role_required('qaqc')
def qaqc_dashboard():
    """
    Render the QA/QC-only dashboard page.
    Only users with 'qaqc' role can access.
    """
    if USE_OKTA:
        # TODO: Render QA/QC dashboard for Okta-authenticated qaqc users.
        raise NotImplementedError("Okta qaqc dashboard not implemented yet.")
    else:
        return render_template('auth/qaqc_dashboard.html')

@auth.route('/review/dashboard')
@roles_required('editor', 'reviewer', 'qaqc')
def review_dashboard():
    """
    Render the review dashboard page.
    Users with 'editor', 'reviewer', OR 'qaqc' roles can access.
    """
    if USE_OKTA:
        # TODO: Render review dashboard for Okta-authenticated users with appropriate roles.
        raise NotImplementedError("Okta review dashboard not implemented yet.")
    else:
        return render_template('auth/review_dashboard.html')

@auth.route('/advanced/edit')
@all_roles_required('editor', 'qaqc')
def advanced_edit():
    """
    Render the advanced editing page.
    Only users with BOTH 'editor' AND 'qaqc' roles can access.
    """
    if USE_OKTA:
        # TODO: Render advanced edit page for Okta-authenticated users with all required roles.
        raise NotImplementedError("Okta advanced edit not implemented yet.")
    else:
        return render_template('auth/advanced_edit.html')

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
    logger.debug(f"Login route accessed - Method: {request.method}")
    
    if USE_OKTA:
        # TODO: Implement Okta login redirect/flow.
        # Need: Okta OIDC/SAML login integration.
        raise NotImplementedError("Okta login not implemented yet. Need Okta OIDC/SAML integration.")
    else:
        if request.method == 'POST':
            logger.debug("Processing login POST request")
            email = request.form.get('email')
            password = request.form.get('password')
            logger.debug(f"Login attempt for email: {email}")
            
            User = get_user_model()
            user = User.query.filter_by(email=email).first()
            
            if user:
                logger.debug(f"User found: {user.email}, checking password")
                if user.check_password(password):
                    logger.debug(f"Password check successful for user: {user.email}")
                    
                    # Check if email is confirmed
                    if not user.is_confirmed:
                        logger.debug(f"Login failed: email not confirmed for user: {user.email}")
                        flash('Please confirm your email address before logging in. Check your email for a confirmation link.', 'warning')
                        return render_template('auth/login.html')
                    
                    login_user(user)
                    flash('Logged in successfully.', 'success')
                    logger.debug(f"User {user.email} logged in successfully")
                    return redirect(url_for('main.index'))
                else:
                    logger.debug(f"Password check failed for user: {user.email}")
                    flash('Invalid email or password.', 'danger')
            else:
                logger.debug(f"No user found for email: {email}")
                flash('Invalid email or password.', 'danger')
        else:
            logger.debug("Rendering login form")
        
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
    logger.debug(f"Register route accessed - Method: {request.method}")
    
    if USE_OKTA:
        # TODO: Implement Okta registration or link to Okta self-service registration.
        # Need: Okta registration endpoint or documentation.
        raise NotImplementedError("Okta registration not implemented yet. Need Okta registration integration.")
    else:
        if request.method == 'POST':
            logger.debug("Processing registration POST request")
            User = get_user_model()
            email = request.form.get('email')
            password = request.form.get('password')
            logger.debug(f"Registration attempt for email: {email}")
            
            if not email or not password:
                logger.debug("Registration failed: missing email or password")
                flash('Email and password are required.', 'danger')
            elif User.query.filter_by(email=email).first():
                logger.debug(f"Registration failed: email {email} already exists")
                flash('Email already registered.', 'warning')
            else:
                logger.debug(f"Creating new user with email: {email}")
                user = User()
                setattr(user, 'email', email)
                user.set_password(password)
                # Keep user unconfirmed until email is verified
                user.is_confirmed_col = False
                get_db().session.add(user)
                get_db().session.commit()
                
                # Generate email confirmation token and send confirmation email
                try:
                    from arb.auth.email_util import send_email_confirmation
                    token = user.generate_email_confirmation_token()
                    send_email_confirmation(user, token)
                    logger.debug(f"Email confirmation sent to user: {email}")
                    flash('Registration successful! Please check your email to confirm your account.', 'success')
                except Exception as e:
                    logger.error(f"Failed to send email confirmation to {email}: {str(e)}")
                    logger.error(f"Error type: {type(e).__name__}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    # Still create the user, but inform them about the email issue
                    flash('Registration successful! However, there was an issue sending the confirmation email. Please contact support.', 'warning')
                
                return redirect(url_for('auth.login'))
        else:
            logger.debug("Rendering registration form")
        
        return render_template('auth/register.html')

@auth.route('/confirm-email/<token>')
def confirm_email(token):
    """
    Email confirmation route.
    Verifies the email confirmation token and confirms the user's account.
    """
    logger.debug(f"Email confirmation route accessed with token: {token[:10]}...")
    
    if USE_OKTA:
        # TODO: Implement Okta email confirmation if needed.
        raise NotImplementedError("Okta email confirmation not implemented yet.")
    else:
        User = get_user_model()
        
        # Find user by email confirmation token
        user = User.query.filter_by(email_confirmation_token=token).first()
        
        if not user:
            logger.debug("Email confirmation failed: invalid token")
            flash('Invalid or expired confirmation link.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Verify the token
        if user.verify_email_confirmation_token(token):
            logger.debug(f"Email confirmed successfully for user: {user.email}")
            flash('Your email has been confirmed successfully! You can now log in.', 'success')
        else:
            logger.debug(f"Email confirmation failed: expired token for user: {user.email}")
            flash('The confirmation link has expired. Please register again or contact support.', 'danger')
        
        return redirect(url_for('auth.login'))

@auth.route('/resend-confirmation', methods=['GET', 'POST'])
def resend_confirmation():
    """
    Resend email confirmation route.
    Allows users to request a new confirmation email if they didn't receive the first one.
    """
    logger.debug(f"Resend confirmation route accessed - Method: {request.method}")
    
    if USE_OKTA:
        # TODO: Implement Okta resend confirmation if needed.
        raise NotImplementedError("Okta resend confirmation not implemented yet.")
    else:
        if request.method == 'POST':
            email = request.form.get('email')
            logger.debug(f"Resend confirmation request for email: {email}")
            
            if not email:
                flash('Please enter your email address.', 'danger')
            else:
                User = get_user_model()
                user = User.query.filter_by(email=email).first()
                
                if not user:
                    # Don't reveal if email exists or not for security
                    flash('If an account with that email exists, a confirmation email has been sent.', 'info')
                elif user.is_confirmed:
                    flash('Your email is already confirmed. You can log in.', 'info')
                else:
                    # Generate new confirmation token and send email
                    try:
                        from arb.auth.email_util import send_email_confirmation
                        token = user.generate_email_confirmation_token()
                        send_email_confirmation(user, token)
                        logger.debug(f"Confirmation email resent to user: {email}")
                        flash('A new confirmation email has been sent. Please check your inbox.', 'success')
                    except Exception as e:
                        logger.error(f"Failed to resend confirmation email to {email}: {e}")
                        flash('There was an issue sending the confirmation email. Please try again later.', 'danger')
            
            return redirect(url_for('auth.login'))
        else:
            return render_template('auth/resend_confirmation.html')

# cleanup: Move all code from portal/auth_routes.py here, updating imports to use auth.models, auth.forms, auth.email_util if not already done. Remove this comment after confirming migration is complete. 