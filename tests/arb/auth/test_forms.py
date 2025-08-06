"""
First pass tests for arb.auth.forms

Tests what can be tested with minimal context: form instantiation, field presence.
Skips complex context-dependent features for future follow-up testing.
"""
import pytest
from flask import Flask

from arb.auth import forms


@pytest.fixture(scope="module")
def app():
  app = Flask(__name__)
  app.config["SECRET_KEY"] = "test-secret-key"
  app.config["WTF_CSRF_ENABLED"] = False
  return app


@pytest.fixture(scope="module")
def app_ctx(app):
  with app.app_context():
    yield


def test_registration_form_instantiation(app_ctx):
  """RegistrationForm can be instantiated with no data."""
  form = forms.RegistrationForm()
  assert form is not None
  assert hasattr(form, 'email')
  assert hasattr(form, 'password')
  assert hasattr(form, 'confirm_password')
  assert hasattr(form, 'submit')


def test_login_form_instantiation(app_ctx):
  """LoginForm can be instantiated with no data."""
  form = forms.LoginForm()
  assert form is not None
  assert hasattr(form, 'email')
  assert hasattr(form, 'password')
  assert hasattr(form, 'remember_me')
  assert hasattr(form, 'submit')


def test_password_reset_form_instantiation(app_ctx):
  """PasswordResetForm can be instantiated with no data."""
  form = forms.PasswordResetForm()
  assert form is not None
  assert hasattr(form, 'email')
  assert hasattr(form, 'submit')


def test_forgot_username_form_instantiation(app_ctx):
  """ForgotUsernameForm can be instantiated with no data."""
  form = forms.ForgotUsernameForm()
  assert form is not None
  assert hasattr(form, 'submit')


def test_change_password_form_instantiation(app_ctx):
  """ChangePasswordForm can be instantiated with no data."""
  form = forms.ChangePasswordForm()
  assert form is not None
  assert hasattr(form, 'current_password')
  assert hasattr(form, 'new_password')
  assert hasattr(form, 'confirm_new_password')
  assert hasattr(form, 'submit')


@pytest.mark.skip(
  reason="Requires complex Flask app context and database queries. Will be addressed in follow-up context testing.")
def test_registration_form_validation():
  """RegistrationForm validates correctly with valid data."""
  pass


@pytest.mark.skip(
  reason="Requires complex Flask app context and database queries. Will be addressed in follow-up context testing.")
def test_login_form_validation():
  """LoginForm validates correctly with valid data."""
  pass


@pytest.mark.skip(
  reason="Requires complex Flask app context and database queries. Will be addressed in follow-up context testing.")
def test_password_reset_form_validation():
  """PasswordResetForm validates correctly with valid data."""
  pass


@pytest.mark.skip(
  reason="Requires complex Flask app context and database queries. Will be addressed in follow-up context testing.")
def test_change_password_form_validation():
  """ChangePasswordForm validates correctly with valid data."""
  pass
