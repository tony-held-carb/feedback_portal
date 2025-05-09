"""
Environment-specific configuration classes for the Flask application.

This file contains distinct configuration classes for development, production,
and testing environments. Each inherits from the BaseConfig class and can override
or extend configuration values as needed.

Usage:
    from config.settings import DevelopmentConfig
"""

import os
from pathlib import Path

class BaseConfig:
    """Base configuration shared by all environments."""
    BASE_DIR = Path(__file__).resolve().parent.parent
    SECRET_KEY = os.environ.get("SECRET_KEY", "replace-with-a-secure-default")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    WTF_CSRF_ENABLED = True
    LOG_LEVEL = "INFO"
    TIMEZONE = "America/Los_Angeles"

class DevelopmentConfig(BaseConfig):
    """Development-specific settings."""
    DEBUG = True
    FLASK_ENV = "development"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URI", f"sqlite:///{BaseConfig.BASE_DIR}/dev.db"
    )
    EXPLAIN_TEMPLATE_LOADING = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(BaseConfig):
    """Production-specific settings."""
    DEBUG = False
    FLASK_ENV = "production"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    WTF_CSRF_ENABLED = True
    LOG_LEVEL = "INFO"

class TestingConfig(BaseConfig):
    """Settings used for unit tests and CI environments."""
    TESTING = True
    DEBUG = True
    FLASK_ENV = "testing"
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URI", "sqlite:///:memory:"
    )
    LOG_LEVEL = "WARNING"
