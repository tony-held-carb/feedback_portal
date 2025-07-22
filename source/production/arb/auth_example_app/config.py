"""
Configuration for the Auth Example App.

This demonstrates how to configure the auth package in a Flask application.

SECURITY NOTE: Never commit real passwords or sensitive credentials to version control.
Use environment variables for all sensitive settings in production.
"""

import os


class Config:
  """Base configuration for the example app."""

  # Flask configuration
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
  DEBUG = True

  # Database configuration (using SQLite for simplicity)
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///auth_example.db'
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  # Auth configuration
  USE_AUTH = True  # Enable authentication

  # ============================================================================
  # EMAIL CONFIGURATION
  # ============================================================================
  #
  # Flask-Mail Settings (these are the actual settings Flask-Mail uses)
  #
  # For Gmail:
  # - MAIL_SERVER = 'smtp.gmail.com'
  # - MAIL_PORT = 587
  # - MAIL_USE_TLS = True
  # - You'll need to enable "Less secure app access" or use App Passwords
  #
  # For Outlook/Office365:
  # - MAIL_SERVER = 'smtp-mail.outlook.com'
  # - MAIL_PORT = 587
  # - MAIL_USE_TLS = True
  #
  # For custom SMTP server:
  # - MAIL_SERVER = 'your-smtp-server.com'
  # - MAIL_PORT = 587 (or your server's port)
  # - MAIL_USE_TLS = True (or False depending on your server)

  # SMTP Server Configuration
  MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
  MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
  MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
  MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'

  # Email Authentication (use environment variables for security)
  MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'example@carb.ca.gov')
  MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'your-email-password')
  MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'example@carb.ca.gov')

  # Development Settings
  # Set MAIL_SUPPRESS_SEND = True to print emails to console instead of sending
  # This is useful for development and testing
  MAIL_SUPPRESS_SEND = os.environ.get('MAIL_SUPPRESS_SEND', 'True').lower() == 'true'

  # ============================================================================
  # AUTH PACKAGE EMAIL SETTINGS (Legacy - kept for compatibility)
  # ============================================================================
  # These settings are used by the auth package itself
  # They should match the Flask-Mail settings above
  AUTH_MAIL_SERVER = MAIL_SERVER
  AUTH_MAIL_PORT = MAIL_PORT
  AUTH_MAIL_USE_TLS = MAIL_USE_TLS
  AUTH_MAIL_USERNAME = MAIL_USERNAME
  AUTH_MAIL_PASSWORD = MAIL_PASSWORD
  AUTH_MAIL_DEFAULT_SENDER = MAIL_DEFAULT_SENDER

  # Security settings
  AUTH_MAX_LOGIN_ATTEMPTS = 5
  AUTH_ACCOUNT_LOCKOUT_DURATION = 900  # 15 minutes
  AUTH_SESSION_TIMEOUT = 3600  # 1 hour
  AUTH_PASSWORD_RESET_EXPIRATION = 3600  # 1 hour


class DevelopmentConfig(Config):
  """Development configuration."""
  DEBUG = True
  SQLALCHEMY_DATABASE_URI = 'sqlite:///auth_example_dev.db'

  # In development, suppress email sending and print to console
  MAIL_SUPPRESS_SEND = True


class TestingConfig(Config):
  """Testing configuration."""
  TESTING = True
  SQLALCHEMY_DATABASE_URI = 'sqlite:///auth_example_test.db'
  WTF_CSRF_ENABLED = False

  # In testing, suppress email sending
  MAIL_SUPPRESS_SEND = True


class ProductionConfig(Config):
  """Production configuration."""
  DEBUG = False

  # In production, use environment variables for ALL sensitive settings
  SECRET_KEY = os.environ.get('SECRET_KEY')
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')

  # Production email settings - MUST use environment variables
  MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
  MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
  MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

  # In production, actually send emails
  MAIL_SUPPRESS_SEND = False


# Configuration mapping
config = {
  'development': DevelopmentConfig,
  'testing': TestingConfig,
  'production': ProductionConfig,
  'default': DevelopmentConfig
}
