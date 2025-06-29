"""
Default authentication and email settings for ARB Feedback Portal.

This file provides default values for all authentication and email-related configuration variables.

How to use:
- These defaults are imported into your main config/settings.py.
- To override any value, set it in your settings.py after importing from this file.
- All variables are documented below. Only override what you need to change for your deployment.

Variables:
- AUTH_MAIL_SERVER: SMTP server address for outgoing email.
- AUTH_MAIL_PORT: SMTP server port (usually 587 for TLS, 465 for SSL).
- AUTH_MAIL_USE_TLS: Enable TLS encryption for SMTP.
- AUTH_MAIL_USE_SSL: Enable SSL encryption for SMTP (mutually exclusive with TLS).
- AUTH_MAIL_USERNAME: Username for SMTP authentication (usually the sender email address).
- AUTH_MAIL_PASSWORD: Password for SMTP authentication.
- AUTH_MAIL_DEFAULT_SENDER: Default "From" address for all outgoing emails.
- AUTH_MAIL_MAX_EMAILS: Maximum emails to send per connection (for batching).
- AUTH_PASSWORD_RESET_EXPIRATION: Time (in seconds) before a password reset token expires.
- AUTH_MAX_PASSWORD_RESET_ATTEMPTS: Maximum allowed password reset requests before cooldown.
- AUTH_PASSWORD_RESET_COOLDOWN: Cooldown period (in seconds) after too many reset attempts.
- AUTH_MAX_LOGIN_ATTEMPTS: Maximum failed login attempts before account lockout.
- AUTH_ACCOUNT_LOCKOUT_DURATION: Lockout duration (in seconds) after too many failed logins.
- AUTH_SESSION_TIMEOUT: Session expiration time (in seconds) for user logins.
- AUTH_REMEMBER_ME_DURATION: Duration (in seconds) for "remember me" logins.

Security notes:
- Never commit real SMTP credentials to version control.
- Use environment variables or secrets management for production overrides.
- These defaults are safe for development but should be reviewed for production.
"""

# Email Configuration
AUTH_MAIL_SERVER = 'smtp.gmail.com'  # SMTP server address for outgoing email
AUTH_MAIL_PORT = 587  # SMTP server port (587 for TLS, 465 for SSL)
AUTH_MAIL_USE_TLS = True  # Enable TLS encryption for SMTP
AUTH_MAIL_USE_SSL = False  # Enable SSL encryption for SMTP (mutually exclusive with TLS)
AUTH_MAIL_USERNAME = 'portal@carb.ca.gov'  # Username for SMTP authentication
AUTH_MAIL_PASSWORD = 'your-email-password'  # Password for SMTP authentication
AUTH_MAIL_DEFAULT_SENDER = 'portal@carb.ca.gov'  # Default 'From' address for all outgoing emails
AUTH_MAIL_MAX_EMAILS = 10  # Maximum emails to send per connection

# Password Reset Configuration
AUTH_PASSWORD_RESET_EXPIRATION = 3600  # 1 hour (in seconds) before a password reset token expires
AUTH_MAX_PASSWORD_RESET_ATTEMPTS = 5  # Maximum allowed password reset requests before cooldown
AUTH_PASSWORD_RESET_COOLDOWN = 300  # 5 minutes (in seconds) cooldown after too many reset attempts

# Account Security Configuration
AUTH_MAX_LOGIN_ATTEMPTS = 5  # Maximum failed login attempts before account lockout
AUTH_ACCOUNT_LOCKOUT_DURATION = 900  # 15 minutes (in seconds) lockout after too many failed logins
AUTH_SESSION_TIMEOUT = 3600  # 1 hour (in seconds) session expiration for user logins
AUTH_REMEMBER_ME_DURATION = 2592000  # 30 days (in seconds) for 'remember me' logins 