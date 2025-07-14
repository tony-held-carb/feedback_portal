"""
Unit tests for arb/portal/config/__init__.py

Tests the get_config() function with various environment variable scenarios.
"""

import os
import pytest
from unittest.mock import patch

from arb.portal.config import get_config
from arb.portal.config.settings import DevelopmentConfig, ProductionConfig, TestingConfig


def test_get_config_production_via_config_type():
    """Test get_config returns ProductionConfig when CONFIG_TYPE=production."""
    with patch.dict(os.environ, {'CONFIG_TYPE': 'production'}):
        result = get_config()
        assert result == ProductionConfig


def test_get_config_production_via_flask_env():
    """Test get_config returns ProductionConfig when FLASK_ENV=production."""
    with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
        result = get_config()
        assert result == ProductionConfig


def test_get_config_testing_via_config_type():
    """Test get_config returns TestingConfig when CONFIG_TYPE=testing."""
    with patch.dict(os.environ, {'CONFIG_TYPE': 'testing'}):
        result = get_config()
        assert result == TestingConfig


def test_get_config_testing_via_flask_env():
    """Test get_config returns TestingConfig when FLASK_ENV=testing."""
    with patch.dict(os.environ, {'FLASK_ENV': 'testing'}):
        result = get_config()
        assert result == TestingConfig


def test_get_config_development_default():
    """Test get_config returns DevelopmentConfig when no environment variables are set."""
    with patch.dict(os.environ, {}, clear=True):
        result = get_config()
        assert result == DevelopmentConfig


def test_get_config_development_empty_strings():
    """Test get_config returns DevelopmentConfig when environment variables are empty strings."""
    with patch.dict(os.environ, {'CONFIG_TYPE': '', 'FLASK_ENV': ''}):
        result = get_config()
        assert result == DevelopmentConfig


def test_get_config_development_invalid_values():
    """Test get_config returns DevelopmentConfig when environment variables have invalid values."""
    with patch.dict(os.environ, {'CONFIG_TYPE': 'invalid', 'FLASK_ENV': 'invalid'}):
        result = get_config()
        assert result == DevelopmentConfig


def test_get_config_case_insensitive():
    """Test get_config is case insensitive for environment variable values."""
    with patch.dict(os.environ, {'CONFIG_TYPE': 'PRODUCTION'}):
        result = get_config()
        assert result == ProductionConfig
    
    with patch.dict(os.environ, {'FLASK_ENV': 'TESTING'}):
        result = get_config()
        assert result == TestingConfig


def test_get_config_priority_config_type_over_flask_env():
    """Test that CONFIG_TYPE and FLASK_ENV use OR logic (not priority)."""
    # The implementation uses OR logic, so if either is production, it returns ProductionConfig
    with patch.dict(os.environ, {'CONFIG_TYPE': 'production', 'FLASK_ENV': 'testing'}):
        result = get_config()
        assert result == ProductionConfig  # production OR testing = production
    
    with patch.dict(os.environ, {'CONFIG_TYPE': 'testing', 'FLASK_ENV': 'production'}):
        result = get_config()
        assert result == ProductionConfig  # testing OR production = production
    
    # Test that testing takes precedence over development
    with patch.dict(os.environ, {'CONFIG_TYPE': 'testing', 'FLASK_ENV': 'development'}):
        result = get_config()
        assert result == TestingConfig  # testing OR development = testing


def test_get_config_mixed_case_environment():
    """Test get_config handles mixed case environment variables correctly."""
    with patch.dict(os.environ, {'CONFIG_TYPE': 'Production', 'FLASK_ENV': 'Testing'}):
        result = get_config()
        assert result == ProductionConfig  # CONFIG_TYPE takes priority 