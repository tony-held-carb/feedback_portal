"""
First pass tests for arb.portal.startup.flask

Tests what can be tested with minimal context: function can be called, basic configuration is applied.
Skips complex context-dependent features for future follow-up testing.
"""
import pytest
from flask import Flask
from arb.portal.startup.flask import configure_flask_app

@pytest.fixture(scope="module")
def app():
  app = Flask(__name__)
  app.config["SECRET_KEY"] = "test-secret-key"
  app.config["LOG_LEVEL"] = "DEBUG"
  return app

def test_configure_flask_app_can_be_called(app):
  """configure_flask_app() can be called without error."""
  configure_flask_app(app)
  # Should not raise

def test_upload_configuration_applied(app):
  """Upload configuration is applied to the app."""
  configure_flask_app(app)
  assert app.config.get('UPLOAD_FOLDER') is not None
  assert app.config.get('MAX_CONTENT_LENGTH') == 16 * 1024 * 1024  # 16MB

def test_jinja_configuration_applied(app):
  """Jinja configuration is applied to the app."""
  configure_flask_app(app)
  assert app.config.get("TEMPLATES_AUTO_RELOAD") is True
  assert app.jinja_env.auto_reload is True
  assert app.jinja_env.trim_blocks is True
  assert app.jinja_env.lstrip_blocks is True

def test_jinja_globals_applied(app):
  """Jinja globals are applied to the app."""
  configure_flask_app(app)
  assert app.jinja_env.globals.get("app_name") == "CARB Feedback Portal"
  assert app.jinja_env.globals.get("california_tz") is not None

def test_jinja_filters_applied(app):
  """Jinja filters are applied to the app."""
  configure_flask_app(app)
  assert 'debug' in app.jinja_env.filters
  assert 'args_to_string' in app.jinja_env.filters
  assert 'utc_iso_str_to_ca_str' in app.jinja_env.filters

@pytest.mark.skip(reason="Requires complex Flask app context and runtime conditions. Will be addressed in follow-up context testing.")
def test_logging_configuration_works_in_runtime(app):
  """Logging configuration works correctly in runtime context."""
  pass

@pytest.mark.skip(reason="Requires complex Flask app context and runtime conditions. Will be addressed in follow-up context testing.")
def test_werkzeug_logging_disabled_in_runtime(app):
  """Werkzeug color logging is disabled in runtime context."""
  pass 