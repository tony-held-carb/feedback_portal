# ARB Feedback Portal Authentication Refactor Walkthrough

**Date:** 2024-06-27

---

## Overview

This document provides a comprehensive walkthrough of the authentication system refactor for the ARB Feedback Portal. It covers the rationale, step-by-step implementation, code changes, new features, and testing instructions. The goal is to provide a clear record for future development, onboarding, and QA.

---

## Table of Contents

1. [Background & Initial Request](#background--initial-request)
2. [Authentication Rollout Plan](#authentication-rollout-plan)
3. [Step-by-Step Implementation](#step-by-step-implementation)
    - [Flask-Login Integration](#flask-login-integration)
    - [User Model Enhancements](#user-model-enhancements)
    - [Authentication Forms](#authentication-forms)
    - [Authentication Routes](#authentication-routes)
    - [Email Infrastructure](#email-infrastructure)
    - [Password Reset & Security](#password-reset--security)
    - [Templates & UI](#templates--ui)
    - [Diagnostics & Testing](#diagnostics--testing)
4. [Security Features](#security-features)
5. [Testing Instructions](#testing-instructions)
6. [Summary Table: Impact on Existing Functionality](#summary-table-impact-on-existing-functionality)
7. [Appendix: Key Code Snippets](#appendix-key-code-snippets)
8. [Modular Authentication Package Structure (2024-06-27)](#modular-authentication-package-structure-2024-06-27)
9. [Admin Roles and Generalized Authorization](#admin-roles-and-generalized-authorization)

---

## Background & Initial Request

> The conversation centers on refactoring and improving a Flask-based feedback portal application, focusing on staged file uploads, database updates, and form handling.

> The user proposed refactoring the staging system to use timestamped filenames and a processed directory, with concurrency protection by checking if the database JSON changed before confirming staged updates. ...

> The user then asked about adding authentication consistent with future Okta integration. The assistant outlined a phased approach: implement a simple custom user model and session management with Flask-Login, protect routes with decorators, and abstract authentication logic to allow easy replacement with Okta later.

---

## Authentication Rollout Plan

**Phased Approach:**

1. **Phase 1:** Basic authentication infrastructure (Flask-Login, user model, registration/login/logout routes)
2. **Phase 2:** Enhanced features (password requirements, email confirmation, password reset, session management)
3. **Phase 3:** Okta integration and further security enhancements

---

## Step-by-Step Implementation

### Flask-Login Integration
- Added `flask-login` to environment and initialized in `extensions.py` and `app.py`.
- Configured `login_manager` and session management.

### User Model Enhancements
- Created/extended `User` model in `sqla_models.py`:
    - Email, password hash, timestamps
    - Password reset token/expiration
    - Account lockout fields
    - Email confirmation token/expiration
    - Methods for password hashing, token generation, lockout logic

### Authentication Forms
- Created `wtf_auth.py`:
    - `RegistrationForm`, `LoginForm`, `PasswordResetForm`, `ChangePasswordForm`, `ForgotUsernameForm`
    - WTForms validation for email, password, and confirmation

### Authentication Routes
- Created `auth_routes.py`:
    - `/auth/register`, `/auth/login`, `/auth/logout`, `/auth/profile`
    - `/auth/forgot_password`, `/auth/reset_password/<token>`, `/auth/change_password`, `/auth/confirm_email/<token>`
    - Account lockout, password reset, and email confirmation logic
    - Diagnostic and test user routes

### Email Infrastructure
- Added `flask-mail` to environment and initialized in `extensions.py` and `app.py`.
- Created `utils/email_util.py` for sending:
    - Welcome emails
    - Password reset emails
    - Password change confirmations
    - Account lockout notifications
- Created HTML email templates in `templates/emails/`
- Configurable SMTP settings in `config/settings.py`

### Password Reset & Security
- Secure, one-time-use password reset tokens with expiration
- Automated email sending for password reset
- Self-service password reset via emailed link
- Account lockout after repeated failed logins
- Password change confirmation emails
- Email confirmation system (ready for future use)

### Templates & UI
- Created/updated templates for all authentication flows:
    - Login, registration, profile, password reset, change password, etc.
    - Bootstrap styling and user guidance
    - Professional HTML email templates
- Updated navbar to show login/logout/profile links

### Diagnostics & Testing
- `/auth/diagnostics` route for system health and email config
- `/auth/test_user` for creating a test user
- Logging for all major authentication events

---

## Security Features

- Passwords securely hashed (Werkzeug)
- Account lockout after 5 failed attempts (15 min lock)
- Password reset tokens (1 hour expiration, one-time use)
- Email confirmation tokens (24 hour expiration)
- CSRF protection on all forms
- Session management with Flask-Login
- Email validation and uniqueness enforced
- User-friendly error and info messages

---

## Testing Instructions

1. **Set up SMTP/email config** in `config/settings.py` or environment variables
2. **Start the Flask app**
3. **Register a new user** at `/auth/register` (check for welcome email)
4. **Login** at `/auth/login` (test lockout by failing 5 times)
5. **Forgot password** at `/auth/forgot_password` (check for reset email)
6. **Reset password** via emailed link
7. **Change password** at `/auth/change_password` (while logged in)
8. **Check diagnostics** at `/auth/diagnostics`
9. **Review logs** for authentication events

---

## Summary Table: Impact on Existing Functionality

| Area                | Change?         | Notes                                                                 |
|---------------------|----------------|-----------------------------------------------------------------------|
| Existing routes     | ❌ No           | All current routes remain accessible as before                        |
| New routes          | ✅ Yes          | Adds `/auth/*` endpoints for user management and recovery             |
| User data           | ✅ Yes          | Adds a new `users` table, does not alter existing tables              |
| Email sending       | ✅ Yes (new)    | Only for authentication flows, if SMTP is configured                  |
| Security features   | ✅ Yes (new)    | Account lockout, password reset, etc. for new auth flows              |
| Route protection    | ❌ (by default) | Existing routes are not protected unless you add `@login_required`    |

---

## Appendix: Key Code Snippets

### Example: User Model (sqla_models.py)
```python
class User(UserMixin, db.Model):
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    # ...
    password_reset_token = db.Column(db.String(255), nullable=True, unique=True)
    password_reset_expires = db.Column(db.DateTime(timezone=True), nullable=True)
    # ...
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
    # ...
```

### Example: Sending Password Reset Email (email_util.py)
```python
def send_password_reset_email(user: User, reset_url: str) -> bool:
    subject = "Password Reset Request - ARB Feedback Portal"
    msg = Message(subject=subject, recipients=[user.email], sender=current_app.config['MAIL_DEFAULT_SENDER'])
    msg.html = render_template('emails/password_reset.html', user=user, reset_url=reset_url, expiration_hours=1)
    mail.send(msg)
    return True
```

### Example: Password Reset Route (auth_routes.py)
```python
@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(password_reset_token=token).first()
    if not user or not user.verify_password_reset_token(token):
        flash('Invalid or expired password reset link.', 'error')
        return redirect(url_for('auth.forgot_password'))
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        db.session.commit()
        send_password_changed_email(user)
        flash('Your password has been successfully reset.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form, token=token)
```

---

## Modular Authentication Package Structure (2024-06-27)

**All authentication and email logic is now fully modularized in the `arb/auth/` package.**

### New Structure

- `arb/auth/models.py` — User model and authentication logic
- `arb/auth/forms.py` — WTForms for registration, login, password reset, etc.
- `arb/auth/routes.py` — All authentication-related Flask routes (register, login, logout, profile, password reset, etc.)
- `arb/auth/email_util.py` — Email sending utilities for password reset, welcome, lockout, etc.

**All previous authentication code has been removed from `portal/` modules.**

### Extending for Roles & Permissions

To add admin or role-based access control:
- Add a `role` or `roles` column to `User` in `models.py` (e.g., `role = db.Column(db.String(32), default='user')`)
- Use custom decorators (e.g., `@admin_required`) in `routes.py` to restrict access
- Check `current_user.role` in your views/templates
- For more complex permissions, consider using Flask-Principal or Flask-Security

### Best Practices
- Keep all authentication and email logic in `arb/auth/` for easy maintenance and future Okta integration
- Only import from `arb/auth/` in your main app and blueprints
- Protect sensitive routes with `@login_required` or custom decorators as needed
- Update documentation and onboarding materials to reference the new structure

---

## Admin Roles and Generalized Authorization

- The User model now includes a 'role' column (default 'user').
- Use `@admin_required` decorator to protect admin-only routes.
- Use `current_user.is_admin()` or `current_user.has_role('role_name')` in views and templates.

### Example: Protecting a Route
```python
from arb.auth.routes import admin_required

@auth.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('auth/admin_dashboard.html')
```

### Example: Checking Roles in Templates
```jinja2
{% if current_user.is_authenticated and current_user.is_admin() %}
  <a href="{{ url_for('auth.admin_dashboard') }}">Admin Dashboard</a>
{% endif %}
```

- To assign admin rights, set `user.role = 'admin'` in the database or via a management interface.
- You can extend with more roles (e.g., 'editor', 'reviewer') and use `current_user.has_role('editor')` as needed.

---

**End of Documentation** 