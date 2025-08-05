"""
Tests for ARB Portal routes.

This module contains tests for the Flask routes in the ARB Feedback Portal,
including the new refactored staging route.
"""

import io
from pathlib import Path
from unittest.mock import patch

import pytest

from arb.portal.app import create_app
from arb.portal.utils.result_types import StagingResult, UploadResult


@pytest.fixture(scope="module")
def app():
  """Create a test Flask app."""
  app = create_app()
  yield app


@pytest.fixture(scope="module")
def client(app):
  """Create a test client for the Flask app."""
  return app.test_client()


def test_upload_file_staged_refactored_route_function_signature():
  """upload_file_staged_refactored route has correct signature."""
  from arb.portal.routes import upload_file_staged_refactored
  assert callable(upload_file_staged_refactored)


def test_upload_file_staged_refactored_get_request(client):
  """upload_file_staged_refactored GET request returns upload form."""
  response = client.get('/upload_staged_refactored')
  assert response.status_code == 200
  html = response.get_data(as_text=True)
  assert "Staged Upload Process" in html or "Upload & Review (Staged Workflow)" in html


def test_upload_file_staged_refactored_success(client):
  """upload_file_staged_refactored handles successful staging."""
  # Mock the staging function to return success
  with patch('arb.portal.routes.stage_uploaded_file_for_review') as mock_stage:
    mock_stage.return_value = StagingResult(
      file_path=Path("uploads/test.xlsx"),
      id_=123,
      sector="Dairy Digester",
      json_data={"id_incidence": 123},
      staged_filename="id_123_ts_20250101_120000.json",
      success=True,
      error_message=None,
      error_type=None
    )

    # Create a mock file upload
    data = {'file': (io.BytesIO(b'test file content'), 'test.xlsx')}
    response = client.post('/upload_staged_refactored', data=data, content_type='multipart/form-data')

    # Should redirect to review page
    assert response.status_code == 302
    assert b'list_staged' in response.data or b'review_staged' in response.data


def test_upload_file_staged_refactored_missing_id_error(client):
  """upload_file_staged_refactored handles missing ID error."""
  # Mock the staging function to return missing ID error
  with patch('arb.portal.routes.stage_uploaded_file_for_review') as mock_stage:
    mock_stage.return_value = StagingResult(
      file_path=Path("uploads/test.xlsx"),
      id_=None,
      sector="Dairy Digester",
      json_data={"sector": "Dairy Digester"},
      staged_filename=None,
      success=False,
      error_message="No valid 'Incidence/Emission ID' found in spreadsheet",
      error_type="missing_id"
    )

    # Create a mock file upload
    data = {'file': (io.BytesIO(b'test file content'), 'test.xlsx')}
    response = client.post('/upload_staged_refactored', data=data, content_type='multipart/form-data')

    # Should return error page with specific message
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "No valid" in html
    assert "Incidence/Emission ID" in html


def test_upload_file_staged_refactored_conversion_error(client):
  """upload_file_staged_refactored handles conversion error."""
  # Mock the staging function to return conversion error
  with patch('arb.portal.routes.stage_uploaded_file_for_review') as mock_stage:
    mock_stage.return_value = StagingResult(
      file_path=Path("uploads/test.txt"),
      id_=None,
      sector=None,
      json_data={},
      staged_filename=None,
      success=False,
      error_message="Unsupported file format. Please upload Excel (.xlsx) file.",
      error_type="conversion_failed"
    )

    # Create a mock file upload
    data = {'file': (io.BytesIO(b'test file content'), 'test.txt')}
    response = client.post('/upload_staged_refactored', data=data, content_type='multipart/form-data')

    # Should return error page with specific message
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Unsupported file format" in html
    assert "Excel" in html


def test_upload_file_staged_refactored_file_error(client):
  """upload_file_staged_refactored handles file error."""
  # Mock the staging function to return file error
  with patch('arb.portal.routes.stage_uploaded_file_for_review') as mock_stage:
    mock_stage.return_value = StagingResult(
      file_path=Path("uploads/test.xlsx"),
      id_=None,
      sector=None,
      json_data={},
      staged_filename=None,
      success=False,
      error_message="Failed to save uploaded file",
      error_type="file_error"
    )

    # Create a mock file upload
    data = {'file': (io.BytesIO(b'test file content'), 'test.xlsx')}
    response = client.post('/upload_staged_refactored', data=data, content_type='multipart/form-data')

    # Should return error page with specific message
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Failed to save uploaded file" in html


def test_upload_file_staged_refactored_database_error(client):
  """upload_file_staged_refactored handles database error."""
  # Mock the staging function to return database error
  with patch('arb.portal.routes.stage_uploaded_file_for_review') as mock_stage:
    mock_stage.return_value = StagingResult(
      file_path=Path("uploads/test.xlsx"),
      id_=123,
      sector="Dairy Digester",
      json_data={"id_incidence": 123},
      staged_filename=None,
      success=False,
      error_message="Database connection failed",
      error_type="database_error"
    )

    # Create a mock file upload
    data = {'file': (io.BytesIO(b'test file content'), 'test.xlsx')}
    response = client.post('/upload_staged_refactored', data=data, content_type='multipart/form-data')

    # Should return error page with specific message
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Database connection failed" in html


def test_upload_file_staged_refactored_unknown_error(client):
  """upload_file_staged_refactored handles unknown error."""
  # Mock the staging function to return unknown error
  with patch('arb.portal.routes.stage_uploaded_file_for_review') as mock_stage:
    mock_stage.return_value = StagingResult(
      file_path=Path("uploads/test.xlsx"),
      id_=None,
      sector=None,
      json_data={},
      staged_filename=None,
      success=False,
      error_message="An unexpected error occurred",
      error_type="unknown_error"
    )

    # Create a mock file upload
    data = {'file': (io.BytesIO(b'test file content'), 'test.xlsx')}
    response = client.post('/upload_staged_refactored', data=data, content_type='multipart/form-data')

    # Should return error page with specific message
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "An unexpected error occurred" in html


def test_upload_file_staged_refactored_no_file_selected(client):
  """upload_file_staged_refactored handles no file selected."""
  response = client.post('/upload_staged_refactored')
  assert response.status_code == 200
  html = response.get_data(as_text=True)
  assert "No file selected" in html


def test_upload_file_staged_refactored_with_message_parameter(client):
  """upload_file_staged_refactored GET with message parameter returns form."""
  test_message = "Test%20staged%20message"
  response = client.get(f'/upload_staged_refactored/{test_message}')
  assert response.status_code == 200
  html = response.get_data(as_text=True)
  assert "Staged Upload Process" in html or "Upload & Review (Staged Workflow)" in html


def test_upload_file_staged_refactored_exception_handling(client):
  """upload_file_staged_refactored handles exceptions gracefully."""
  # Mock the staging function to raise an exception
  with patch('arb.portal.routes.stage_uploaded_file_for_review') as mock_stage:
    mock_stage.side_effect = Exception("Test exception")

    # Create a mock file upload
    data = {'file': (io.BytesIO(b'test file content'), 'test.xlsx')}
    response = client.post('/upload_staged_refactored', data=data, content_type='multipart/form-data')

    # Should return error page
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "error" in html.lower() or "failed" in html.lower()


def test_upload_file_refactored_route_function_signature():
  """upload_file_refactored route has correct function signature."""
  from arb.portal.routes import upload_file_refactored
  import inspect

  sig = inspect.signature(upload_file_refactored)
  params = list(sig.parameters.keys())

  assert 'message' in params
  assert sig.parameters['message'].default is None
  # Check for Union type annotation (can be string or actual type)
  return_annotation = str(sig.return_annotation)
  assert 'Union' in return_annotation and 'str' in return_annotation and 'Response' in return_annotation


def test_upload_file_refactored_get_request(client):
  """upload_file_refactored handles GET request correctly."""
  response = client.get('/upload_refactored')
  assert response.status_code == 200
  html = response.get_data(as_text=True)
  assert "Upload Feedback Spreadsheet" in html


def test_upload_file_refactored_success(client):
  """upload_file_refactored handles successful upload."""
  # Mock the upload function to return success
  with patch('arb.portal.routes.upload_and_process_file') as mock_upload:
    mock_upload.return_value = UploadResult(
      file_path=Path("uploads/test.xlsx"),
      id_=123,
      sector="Dairy Digester",
      success=True,
      error_message=None,
      error_type=None
    )

    # Create a mock file upload
    data = {'file': (io.BytesIO(b'test file content'), 'test.xlsx')}
    response = client.post('/upload_refactored', data=data, content_type='multipart/form-data')

    # Should redirect to incidence_update page
    assert response.status_code == 302
    assert b'incidence_update' in response.data


def test_upload_file_refactored_missing_id_error(client):
  """upload_file_refactored handles missing ID error."""
  with patch('arb.portal.routes.upload_and_process_file') as mock_upload:
    mock_upload.return_value = UploadResult(
      file_path=Path("uploads/test.xlsx"),
      id_=None,
      sector="Dairy Digester",
      success=False,
      error_message="No valid id_incidence found in spreadsheet",
      error_type="missing_id"
    )

    data = {'file': (io.BytesIO(b'test file content'), 'test.xlsx')}
    response = client.post('/upload_refactored', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    # The error message is HTML-encoded, so check for the encoded version
    assert "missing a valid &#39;Incidence/Emission ID&#39;" in html or "missing a valid 'Incidence/Emission ID'" in html


def test_upload_file_refactored_conversion_error(client):
  """upload_file_refactored handles file conversion error."""
  with patch('arb.portal.routes.upload_and_process_file') as mock_upload:
    mock_upload.return_value = UploadResult(
      file_path=Path("uploads/test.txt"),
      id_=None,
      sector=None,
      success=False,
      error_message="File could not be converted to JSON format",
      error_type="conversion_failed"
    )

    data = {'file': (io.BytesIO(b'invalid content'), 'test.txt')}
    response = client.post('/upload_refactored', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Uploaded file format not recognized" in html


def test_upload_file_refactored_file_error(client):
  """upload_file_refactored handles file processing error."""
  with patch('arb.portal.routes.upload_and_process_file') as mock_upload:
    mock_upload.return_value = UploadResult(
      file_path=Path("unknown"),
      id_=None,
      sector=None,
      success=False,
      error_message="File upload failed",
      error_type="file_error"
    )

    data = {'file': (io.BytesIO(b'test content'), 'test.xlsx')}
    response = client.post('/upload_refactored', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Error processing uploaded file" in html


def test_upload_file_refactored_database_error(client):
  """upload_file_refactored handles database error."""
  with patch('arb.portal.routes.upload_and_process_file') as mock_upload:
    mock_upload.return_value = UploadResult(
      file_path=Path("uploads/test.xlsx"),
      id_=None,
      sector="Dairy Digester",
      success=False,
      error_message="Database connection failed",
      error_type="database_error"
    )

    data = {'file': (io.BytesIO(b'test content'), 'test.xlsx')}
    response = client.post('/upload_refactored', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Database error occurred" in html


def test_upload_file_refactored_unknown_error(client):
  """upload_file_refactored handles unknown error types."""
  with patch('arb.portal.routes.upload_and_process_file') as mock_upload:
    mock_upload.return_value = UploadResult(
      file_path=Path("uploads/test.xlsx"),
      id_=None,
      sector=None,
      success=False,
      error_message="Unexpected error occurred",
      error_type="unknown_error"
    )

    data = {'file': (io.BytesIO(b'test content'), 'test.xlsx')}
    response = client.post('/upload_refactored', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "An unexpected error occurred" in html


def test_upload_file_refactored_no_file_selected(client):
  """upload_file_refactored handles no file selected."""
  response = client.post('/upload_refactored')
  assert response.status_code == 200
  html = response.get_data(as_text=True)
  assert "No file selected" in html


def test_upload_file_refactored_with_message_parameter(client):
  """upload_file_refactored handles message parameter correctly."""
  test_message = "Test%20refactored%20message"
  response = client.get(f'/upload_refactored/{test_message}')
  assert response.status_code == 200
  html = response.get_data(as_text=True)
  assert "Test refactored message" in html


def test_upload_file_refactored_exception_handling(client):
  """upload_file_refactored handles exceptions gracefully."""
  with patch('arb.portal.routes.upload_and_process_file') as mock_upload:
    mock_upload.side_effect = Exception("Unexpected exception")

    data = {'file': (io.BytesIO(b'test content'), 'test.xlsx')}
    response = client.post('/upload_refactored', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    # Should show some form of error message
    assert "error" in html.lower() or "failed" in html.lower() or "not recognized" in html.lower()
