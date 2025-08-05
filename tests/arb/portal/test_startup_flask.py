"""
Comprehensive tests for arb.portal.startup.flask

Tests all functionality including Flask app configuration, Jinja2 setup, logging configuration,
and edge cases. Covers both basic configuration and runtime behavior.
"""
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
import werkzeug
from flask import Flask
from jinja2 import StrictUndefined

from arb.portal.startup.flask import configure_flask_app
from arb.utils.date_and_time import utc_iso_str_to_ca_str
from arb.utils.diagnostics import diag_recursive
from arb.utils.misc import args_to_string


@pytest.fixture(scope="module")
def app():
  """Create a test Flask app with basic configuration."""
  app = Flask(__name__)
  app.config["SECRET_KEY"] = "test-secret-key"
  app.config["LOG_LEVEL"] = "DEBUG"
  return app


@pytest.fixture
def fresh_app():
  """Create a fresh Flask app for each test to avoid state pollution."""
  app = Flask(__name__)
  app.config["SECRET_KEY"] = "test-secret-key"
  return app


def test_configure_flask_app_can_be_called(app):
  """configure_flask_app() can be called without error."""
  configure_flask_app(app)
  # Should not raise


def test_configure_flask_app_returns_none(app):
  """configure_flask_app() returns None as documented."""
  result = configure_flask_app(app)
  assert result is None


def test_upload_configuration_applied(app):
  """Upload configuration is applied to the app."""
  configure_flask_app(app)
  assert app.config.get('UPLOAD_FOLDER') is not None
  assert app.config.get('MAX_CONTENT_LENGTH') == 16 * 1024 * 1024  # 16MB


def test_upload_configuration_overwrites_existing(app):
  """Upload configuration overwrites any existing values."""
  app.config['UPLOAD_FOLDER'] = '/old/path'
  app.config['MAX_CONTENT_LENGTH'] = 1024
  configure_flask_app(app)
  assert app.config.get('UPLOAD_FOLDER') != '/old/path'
  assert app.config.get('MAX_CONTENT_LENGTH') == 16 * 1024 * 1024


def test_jinja_configuration_applied(app):
  """Jinja configuration is applied to the app."""
  configure_flask_app(app)
  assert app.config.get("TEMPLATES_AUTO_RELOAD") is True
  assert app.jinja_env.auto_reload is True
  assert app.jinja_env.trim_blocks is True
  assert app.jinja_env.lstrip_blocks is True


def test_jinja_undefined_behavior_set(app):
  """Jinja undefined behavior is set to StrictUndefined."""
  configure_flask_app(app)
  assert app.jinja_env.undefined == StrictUndefined


def test_jinja_globals_applied(app):
  """Jinja globals are applied to the app."""
  configure_flask_app(app)
  assert app.jinja_env.globals.get("app_name") == "CARB Feedback Portal"
  assert app.jinja_env.globals.get("california_tz") is not None


def test_california_timezone_is_zoneinfo(app):
  """California timezone global is a ZoneInfo object."""
  configure_flask_app(app)
  california_tz = app.jinja_env.globals.get("california_tz")
  assert isinstance(california_tz, ZoneInfo)
  assert str(california_tz) == "America/Los_Angeles"


def test_jinja_filters_applied(app):
  """Jinja filters are applied to the app."""
  configure_flask_app(app)
  assert 'debug' in app.jinja_env.filters
  assert 'args_to_string' in app.jinja_env.filters
  assert 'utc_iso_str_to_ca_str' in app.jinja_env.filters


def test_jinja_filters_are_correct_functions(app):
  """Jinja filters are the correct function references."""
  configure_flask_app(app)
  assert app.jinja_env.filters['debug'] == diag_recursive
  assert app.jinja_env.filters['args_to_string'] == args_to_string
  assert app.jinja_env.filters['utc_iso_str_to_ca_str'] == utc_iso_str_to_ca_str


def test_logging_level_set_from_config(app):
  """Logger level is set from app config LOG_LEVEL."""
  app.config["LOG_LEVEL"] = "WARNING"
  with patch('arb.portal.startup.flask.logger') as mock_logger:
    configure_flask_app(app)
    mock_logger.setLevel.assert_called_with("WARNING")


def test_logging_level_defaults_to_info(fresh_app):
  """Logger level defaults to INFO when LOG_LEVEL not in config."""
  with patch('arb.portal.startup.flask.logger') as mock_logger:
    configure_flask_app(fresh_app)
    mock_logger.setLevel.assert_called_with("INFO")


def test_werkzeug_logging_disabled():
  """Werkzeug color logging is disabled."""
  with patch('werkzeug.serving._log_add_style') as mock_log_add_style:
    app = Flask(__name__)
    configure_flask_app(app)
    # The function should be set to False
    assert werkzeug.serving._log_add_style is False


def test_werkzeug_logging_disabled_affects_global():
  """Werkzeug logging disable affects the global setting."""
  # Store original value
  original_value = werkzeug.serving._log_add_style
  try:
    app = Flask(__name__)
    configure_flask_app(app)
    assert werkzeug.serving._log_add_style is False
  finally:
    # Restore original value to avoid affecting other tests
    werkzeug.serving._log_add_style = original_value


def test_app_name_global_overwrites_existing(app):
  """App name global overwrites any existing value."""
  app.jinja_env.globals["app_name"] = "Old App Name"
  configure_flask_app(app)
  assert app.jinja_env.globals["app_name"] == "CARB Feedback Portal"


def test_california_tz_global_overwrites_existing(app):
  """California timezone global overwrites any existing value."""
  app.jinja_env.globals["california_tz"] = "old_tz"
  configure_flask_app(app)
  assert isinstance(app.jinja_env.globals["california_tz"], ZoneInfo)
  assert str(app.jinja_env.globals["california_tz"]) == "America/Los_Angeles"


def test_jinja_filters_overwrite_existing(app):
  """Jinja filters overwrite any existing filter functions."""
  # Set up existing filters
  app.jinja_env.filters['debug'] = lambda x: "old_debug"
  app.jinja_env.filters['args_to_string'] = lambda x: "old_args"
  app.jinja_env.filters['utc_iso_str_to_ca_str'] = lambda x: "old_utc"

  configure_flask_app(app)

  # Verify they were overwritten with correct functions
  assert app.jinja_env.filters['debug'] == diag_recursive
  assert app.jinja_env.filters['args_to_string'] == args_to_string
  assert app.jinja_env.filters['utc_iso_str_to_ca_str'] == utc_iso_str_to_ca_str


def test_configuration_is_idempotent(app):
  """Configuration can be applied multiple times without issues."""
  configure_flask_app(app)
  first_config = {
    'UPLOAD_FOLDER': app.config.get('UPLOAD_FOLDER'),
    'MAX_CONTENT_LENGTH': app.config.get('MAX_CONTENT_LENGTH'),
    'TEMPLATES_AUTO_RELOAD': app.config.get('TEMPLATES_AUTO_RELOAD'),
    'app_name': app.jinja_env.globals.get('app_name'),
    'california_tz': app.jinja_env.globals.get('california_tz')
  }

  configure_flask_app(app)
  second_config = {
    'UPLOAD_FOLDER': app.config.get('UPLOAD_FOLDER'),
    'MAX_CONTENT_LENGTH': app.config.get('MAX_CONTENT_LENGTH'),
    'TEMPLATES_AUTO_RELOAD': app.config.get('TEMPLATES_AUTO_RELOAD'),
    'app_name': app.jinja_env.globals.get('app_name'),
    'california_tz': app.jinja_env.globals.get('california_tz')
  }

  assert first_config == second_config


def test_all_jinja_settings_configured(app):
  """All documented Jinja settings are properly configured."""
  configure_flask_app(app)

  # Check all Jinja environment settings
  assert app.jinja_env.undefined == StrictUndefined
  assert app.jinja_env.trim_blocks is True
  assert app.jinja_env.lstrip_blocks is True
  assert app.jinja_env.auto_reload is True

  # Check all globals
  assert app.jinja_env.globals.get("app_name") == "CARB Feedback Portal"
  assert isinstance(app.jinja_env.globals.get("california_tz"), ZoneInfo)

  # Check all filters
  expected_filters = ['debug', 'args_to_string', 'utc_iso_str_to_ca_str']
  for filter_name in expected_filters:
    assert filter_name in app.jinja_env.filters


def test_all_app_config_settings_configured(app):
  """All documented app config settings are properly configured."""
  configure_flask_app(app)

  # Check all app config settings
  assert app.config.get('UPLOAD_FOLDER') is not None
  assert app.config.get('MAX_CONTENT_LENGTH') == 16 * 1024 * 1024
  assert app.config.get('TEMPLATES_AUTO_RELOAD') is True


def test_logging_debug_messages_emitted(app):
  """Debug logging messages are emitted during configuration."""
  with patch('arb.portal.startup.flask.logger') as mock_logger:
    configure_flask_app(app)
    # Should have called debug at least once for the function call
    assert mock_logger.debug.called


def test_upload_path_is_valid_directory(app):
  """Upload path is a valid directory path."""
  configure_flask_app(app)
  upload_path = app.config.get('UPLOAD_FOLDER')
  assert upload_path is not None
  # Should be a string path
  assert isinstance(upload_path, str)
  # Should not be empty
  assert upload_path.strip() != ""
  # Should match the expected path string
  from arb.portal.startup.runtime_info import UPLOAD_PATH
  assert upload_path == str(UPLOAD_PATH)


def test_max_content_length_is_reasonable(app):
  """Max content length is a reasonable value (16MB)."""
  configure_flask_app(app)
  max_length = app.config.get('MAX_CONTENT_LENGTH')
  assert max_length == 16 * 1024 * 1024  # 16MB in bytes
  assert max_length > 0
  assert max_length < 100 * 1024 * 1024  # Less than 100MB


def test_function_accepts_flask_app_instance():
  """Function accepts a Flask app instance as documented."""
  app = Flask(__name__)
  # Should not raise any errors
  configure_flask_app(app)


def test_function_modifies_app_in_place(app):
  """Function modifies the app instance in place as documented."""
  # Set to a dummy value
  app.config['UPLOAD_FOLDER'] = '/dummy/path'
  app.jinja_env.globals['app_name'] = 'Dummy App'
  configure_flask_app(app)
  from arb.portal.startup.runtime_info import UPLOAD_PATH
  assert app.config.get('UPLOAD_FOLDER') == str(UPLOAD_PATH)
  assert app.jinja_env.globals.get('app_name') == 'CARB Feedback Portal'
