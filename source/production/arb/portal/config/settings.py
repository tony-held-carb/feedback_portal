"""
Environment-specific configuration classes for the Flask application.

This file contains distinct configuration classes for development, production,
and testing environments. Each inherits from the BaseConfig class and can override
or extend configuration values as needed.

Usage:
    from config.settings import DevelopmentConfig

Notes:
  - All variables in this file are not dependent on runtime conditions and are static.
  - If a variable is a setting defined at runtime, such as platform type or root directory,
    it should be defined and initialized in the startup/runtime_info.py file.
"""

import os
from pathlib import Path

class BaseConfig:
    """Base configuration shared by all environments."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "replace-with-a-secure-default")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    LOG_LEVEL = "INFO"
    TIMEZONE = "America/Los_Angeles"

class DevelopmentConfig(BaseConfig):
    """Development-specific settings."""
    DEBUG = True
    FLASK_ENV = "development"
    # EXPLAIN_TEMPLATE_LOADING = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(BaseConfig):
    """Production-specific settings."""
    DEBUG = False
    FLASK_ENV = "production"
    WTF_CSRF_ENABLED = True
    LOG_LEVEL = "INFO"

class TestingConfig(BaseConfig):
    """Settings used for unit tests and CI environments."""
    TESTING = True
    DEBUG = True
    FLASK_ENV = "testing"
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = "WARNING"
