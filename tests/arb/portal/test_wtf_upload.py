"""
First pass tests for arb.portal.wtf_upload

Tests what can be tested with minimal context: form instantiation, basic validation, field defaults.
Skips complex context-dependent features for future follow-up testing.
"""
import io

import pytest
from flask import Flask
from werkzeug.datastructures import FileStorage

from arb.portal.wtf_upload import UploadForm


# Helper to create a FileStorage object for testing

def make_filestorage(filename, content=b"dummy", content_type="application/vnd.ms-excel"):
  return FileStorage(
    stream=io.BytesIO(content),
    filename=filename,
    content_type=content_type
  )


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


def test_form_instantiation(app_ctx):
  """UploadForm can be instantiated with no data."""
  form = UploadForm()
  assert form is not None
  assert hasattr(form, 'file')
  assert hasattr(form, 'submit')


def test_file_field_present(app_ctx):
  """File field is defined with appropriate validators."""
  form = UploadForm()
  assert hasattr(form, 'file')
  assert form.file.label.text == "Choose Excel File"
  # Check that validators are present (DataRequired and FileAllowed)
  assert len(form.file.validators) >= 1


def test_submit_field_present(app_ctx):
  """Submit field is defined."""
  form = UploadForm()
  assert hasattr(form, 'submit')
  assert form.submit.label.text == "Upload"


def test_form_validation_with_valid_excel_file(app):
  """Form validates with a valid .xlsx file upload."""
  with app.test_request_context(method="POST", data={}):
    form = UploadForm()
    file = make_filestorage("test.xlsx")
    form.file.data = file
    assert form.validate() is True


def test_form_validation_with_invalid_file_type(app):
  """Form fails validation with a .txt file upload (invalid type)."""
  with app.test_request_context(method="POST", data={}):
    form = UploadForm()
    file = make_filestorage("test.txt", content_type="text/plain")
    form.file.data = file
    assert form.validate() is False
    assert any("Excel files only" in str(e) for e in form.file.errors)


def test_form_validation_without_file(app):
  """Form fails validation when no file is provided."""
  with app.test_request_context(method="POST", data={}):
    form = UploadForm()
    form.file.data = None
    assert form.validate() is False
    assert any("This field is required" in str(e) for e in form.file.errors)


def test_form_validation_with_empty_filename(app):
  """Form fails validation when file has empty filename."""
  with app.test_request_context(method="POST", data={}):
    form = UploadForm()
    file = make_filestorage("")
    form.file.data = file
    assert form.validate() is False
    # Should fail DataRequired
    assert any("This field is required" in str(e) for e in form.file.errors)
