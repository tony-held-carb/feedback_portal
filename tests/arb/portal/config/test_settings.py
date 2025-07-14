# All meaningful logic in settings.py is covered by these tests. No further tests are needed unless new config logic is added.
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

def test_fast_load_environment_variable_true(monkeypatch):
    """Test FAST_LOAD is set to True when FAST_LOAD=true environment variable is set."""
    monkeypatch.setenv("FAST_LOAD", "true")
    import importlib
    importlib.reload(settings)
    assert settings.BaseConfig.FAST_LOAD is True

def test_fast_load_environment_variable_false(monkeypatch):
    """Test FAST_LOAD remains False when FAST_LOAD is not 'true'."""
    monkeypatch.setenv("FAST_LOAD", "false")
    import importlib
    importlib.reload(settings)
    assert settings.BaseConfig.FAST_LOAD is False

def test_fast_load_environment_variable_not_set(monkeypatch):
    """Test FAST_LOAD remains False when FAST_LOAD environment variable is not set."""
    monkeypatch.delenv("FAST_LOAD", raising=False)
    import importlib
    importlib.reload(settings)
    assert settings.BaseConfig.FAST_LOAD is False

def test_secret_key_from_environment(monkeypatch):
    """Test SECRET_KEY is set from environment variable when available."""
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    import importlib
    importlib.reload(settings)
    assert settings.BaseConfig.SECRET_KEY == "test-secret-key"

def test_secret_key_default_when_not_set(monkeypatch):
    """Test SECRET_KEY defaults to 'secret-key-goes-here' when not set in environment."""
    monkeypatch.delenv("SECRET_KEY", raising=False)
    import importlib
    importlib.reload(settings)
    assert settings.BaseConfig.SECRET_KEY == "secret-key-goes-here" 