import pytest
import os
from unittest.mock import patch
import arb.portal.config.settings as settings

def test_base_config_defaults():
    cfg = settings.BaseConfig
    assert hasattr(cfg, "POSTGRES_DB_URI")
    assert hasattr(cfg, "SQLALCHEMY_DATABASE_URI")
    assert cfg.SQLALCHEMY_TRACK_MODIFICATIONS is False
    assert cfg.WTF_CSRF_ENABLED is True
    assert cfg.LOG_LEVEL in ("INFO", "DEBUG", "WARNING")
    assert cfg.TIMEZONE == "America/Los_Angeles"

def test_development_config_inherits():
    cfg = settings.DevelopmentConfig
    assert cfg.DEBUG is True
    assert cfg.FLASK_ENV == "development"
    assert cfg.LOG_LEVEL == "DEBUG"
    assert issubclass(cfg, settings.BaseConfig)

def test_production_config_inherits():
    cfg = settings.ProductionConfig
    assert cfg.DEBUG is False
    assert cfg.FLASK_ENV == "production"
    assert cfg.WTF_CSRF_ENABLED is True
    assert cfg.LOG_LEVEL == "INFO"
    assert issubclass(cfg, settings.BaseConfig)

def test_testing_config_inherits():
    cfg = settings.TestingConfig
    assert cfg.TESTING is True
    assert cfg.DEBUG is True
    assert cfg.FLASK_ENV == "testing"
    assert cfg.WTF_CSRF_ENABLED is False
    assert cfg.LOG_LEVEL == "WARNING"
    assert issubclass(cfg, settings.BaseConfig)

def test_env_override_sqlalchemy_database_uri(monkeypatch):
    monkeypatch.setenv("DATABASE_URI", "postgresql://test/test")
    import importlib
    importlib.reload(settings)
    assert settings.BaseConfig.SQLALCHEMY_DATABASE_URI == "postgresql://test/test" 