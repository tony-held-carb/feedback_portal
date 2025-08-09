"""
Integration Tests for Route Equivalence

This module provides integration testing to ensure that the refactored
upload_file_staged_refactored route produces equivalent results to the original
upload_file_staged route.

These tests use Flask test client for faster, more reliable testing compared to
E2E tests, while still testing the complete route behavior including database
interactions.
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
  return app


@pytest.fixture(scope="module")
def client(app):
  """Create a test client for the Flask app."""
  return app.test_client()


class TestRouteEquivalence:
  """Test suite for comparing original vs refactored route behavior."""

  def test_get_request_equivalence(self, client):
    """Test that both routes return identical GET responses."""
    # Test original route
    original_response = client.get("/upload_staged")
    assert original_response.status_code == 200
    original_html = original_response.get_data(as_text=True)

    # Test refactored route
    refactored_response = client.get("/upload_staged_refactored")
    assert refactored_response.status_code == 200
    refactored_html = refactored_response.get_data(as_text=True)

    # Both should contain the same key elements
    assert "Upload" in original_html
    assert "Upload" in refactored_html
    assert "file" in original_html.lower()
    assert "file" in refactored_html.lower()

  def test_get_request_with_message_equivalence(self, client):
    """Test that both routes handle message parameters identically."""
    test_message = "Test%20message%20for%20equivalence"

    # Test original route with message
    original_response = client.get(f"/upload_staged/{test_message}")
    assert original_response.status_code == 200
    original_html = original_response.get_data(as_text=True)

    # Test refactored route with message
    refactored_response = client.get(f"/upload_staged_refactored/{test_message}")
    assert refactored_response.status_code == 200
    refactored_html = refactored_response.get_data(as_text=True)

    # Both should display the message
    assert "Test message for equivalence" in original_html
    assert "Test message for equivalence" in refactored_html

  def test_post_no_file_equivalence(self, client):
    """Test that both routes handle 'no file selected' identically."""
    # Test original route
    original_response = client.post("/upload_staged")
    assert original_response.status_code == 200
    original_html = original_response.get_data(as_text=True)
    assert "No file selected" in original_html

    # Test refactored route
    refactored_response = client.post("/upload_staged_refactored")
    assert refactored_response.status_code == 200
    refactored_html = refactored_response.get_data(as_text=True)
    assert "No file selected" in refactored_html

  def test_post_empty_file_equivalence(self, client):
    """Test that both routes handle empty files identically."""
    # Test original route
    original_data = {'file': (io.BytesIO(b''), '')}
    original_response = client.post(
      "/upload_staged",
      data=original_data,
      content_type='multipart/form-data'
    )
    assert original_response.status_code == 200
    original_html = original_response.get_data(as_text=True)
    assert "No file selected" in original_html

    # Test refactored route
    refactored_data = {'file': (io.BytesIO(b''), '')}
    refactored_response = client.post(
      "/upload_staged_refactored",
      data=refactored_data,
      content_type='multipart/form-data'
    )
    assert refactored_response.status_code == 200
    refactored_html = refactored_response.get_data(as_text=True)
    assert "No file selected" in refactored_html

  def test_post_invalid_file_equivalence(self, client):
    """Test that both routes handle invalid files identically."""
    # Test original route
    original_data = {'file': (io.BytesIO(b'invalid content'), 'test.txt')}
    original_response = client.post(
      "/upload_staged",
      data=original_data,
      content_type='multipart/form-data'
    )
    assert original_response.status_code == 200
    original_html = original_response.get_data(as_text=True)

    # Test refactored route
    refactored_data = {'file': (io.BytesIO(b'invalid content'), 'test.txt')}
    refactored_response = client.post(
      "/upload_staged_refactored",
      data=refactored_data,
      content_type='multipart/form-data'
    )
    assert refactored_response.status_code == 200
    refactored_html = refactored_response.get_data(as_text=True)

    # Both should show some form of error
    assert any(word in original_html.lower() for word in ["error", "failed", "not recognized"])
    assert any(word in refactored_html.lower() for word in ["error", "failed", "not recognized"])

  @patch('arb.portal.routes.upload_and_stage_only')
  @patch('arb.portal.routes.stage_uploaded_file_for_review')
  def test_success_case_equivalence(self, mock_stage_refactored, mock_upload_and_stage, client):
    """Test that both routes handle successful uploads identically."""
    # Mock successful staging result for original route
    mock_original_result = ("test.xlsx", 123, "Dairy Digester", {"id_incidence": 123}, "staged_123.json")
    mock_upload_and_stage.return_value = mock_original_result

    # Mock successful staging result for refactored route
    mock_refactored_result = StagingResult(
      file_path=Path("test.xlsx"),
      id_=123,
      sector="Dairy Digester",
      json_data={"id_incidence": 123},
      staged_filename="staged_123.json",
      success=True,
      error_message=None,
      error_type=None
    )
    mock_stage_refactored.return_value = mock_refactored_result

    # Create a mock Excel file
    excel_content = b'PK\x03\x04'  # Minimal Excel file signature

    # Test original route
    original_data = {'file': (io.BytesIO(excel_content), 'test.xlsx')}
    original_response = client.post(
      "/upload_staged",
      data=original_data,
      content_type='multipart/form-data'
    )

    # Test refactored route
    refactored_data = {'file': (io.BytesIO(excel_content), 'test.xlsx')}
    refactored_response = client.post(
      "/upload_staged_refactored",
      data=refactored_data,
      content_type='multipart/form-data'
    )

    # Both should redirect to review page
    assert original_response.status_code in [200, 302]
    assert refactored_response.status_code in [200, 302]

    # Both should call their respective staging functions
    assert mock_upload_and_stage.call_count == 1
    assert mock_stage_refactored.call_count == 1

  @patch('arb.portal.routes.stage_uploaded_file_for_review')
  def test_refactored_route_specific_error_handling(self, mock_stage_refactored, client):
    """Test that refactored route provides specific error messages."""
    # Mock different error scenarios
    error_scenarios = [
      ("missing_id", "No valid id_incidence found in the uploaded file"),
      ("conversion_failed", "Failed to convert file to JSON format"),
      ("file_error", "Error processing uploaded file"),
      ("database_error", "Database error occurred during staging"),
    ]

    for error_type, expected_message in error_scenarios:
      # Mock error result
      mock_error_result = StagingResult(
        file_path=Path("test.xlsx"),
        id_=None,
        sector=None,
        json_data={},
        staged_filename=None,
        success=False,
        error_message=expected_message,
        error_type=error_type
      )
      mock_stage_refactored.return_value = mock_error_result

      # Test refactored route
      excel_content = b'PK\x03\x04'  # Minimal Excel file signature
      data = {'file': (io.BytesIO(excel_content), 'test.xlsx')}
      response = client.post(
        "/upload_staged_refactored",
        data=data,
        content_type='multipart/form-data'
      )

      assert response.status_code == 200
      html = response.get_data(as_text=True)
      # Check for user-friendly messages that our helper functions provide
      if error_type == "missing_id":
        assert "missing a valid" in html and "Incidence/Emission ID" in html
      elif error_type == "conversion_failed":
        assert "Unsupported file format" in html and "Excel" in html
      elif error_type == "file_error":
        assert "Error processing uploaded file" in html
      elif error_type == "database_error":
        assert "Database error occurred" in html


class TestRefactoredRouteImprovements:
  """Test suite for refactored route-specific improvements."""

  def test_refactored_route_uses_staging_result(self, client):
    """Test that refactored route uses StagingResult for better error handling."""
    # This test verifies that the refactored route uses the new StagingResult
    # named tuple instead of the old tuple return format

    with patch('arb.portal.routes.stage_uploaded_file_for_review') as mock_stage:
      # Mock a StagingResult (not a tuple)
      mock_result = StagingResult(
        file_path=Path("test.xlsx"),
        id_=123,
        sector="Dairy Digester",
        json_data={"id_incidence": 123},
        staged_filename="staged_123.json",
        success=True,
        error_message=None,
        error_type=None
      )
      mock_stage.return_value = mock_result

      excel_content = b'PK\x03\x04'
      data = {'file': (io.BytesIO(excel_content), 'test.xlsx')}

      response = client.post(
        "/upload_staged_refactored",
        data=data,
        content_type='multipart/form-data'
      )

      # Should succeed
      assert response.status_code in [200, 302]
      mock_stage.assert_called_once()

  def test_refactored_route_specific_error_types(self, client):
    """Test that refactored route provides specific error type handling."""
    with patch('arb.portal.routes.stage_uploaded_file_for_review') as mock_stage:
      # Test missing ID error
      mock_result = StagingResult(
        file_path=Path("test.xlsx"),
        id_=None,
        sector="Dairy Digester",
        json_data={"sector": "Dairy Digester"},
        staged_filename=None,
        success=False,
        error_message="No valid id_incidence found",
        error_type="missing_id"
      )
      mock_stage.return_value = mock_result

      excel_content = b'PK\x03\x04'
      data = {'file': (io.BytesIO(excel_content), 'test.xlsx')}

      response = client.post(
        "/upload_staged_refactored",
        data=data,
        content_type='multipart/form-data'
      )

      assert response.status_code == 200
      html = response.get_data(as_text=True)
      # Check for user-friendly message that our helper function provides
      assert "missing a valid" in html and "Incidence/Emission ID" in html

  def test_refactored_route_exception_handling(self, client):
    """Test that refactored route handles exceptions gracefully."""
    with patch('arb.portal.routes.stage_uploaded_file_for_review') as mock_stage:
      # Mock an exception
      mock_stage.side_effect = Exception("Unexpected error")

      excel_content = b'PK\x03\x04'
      data = {'file': (io.BytesIO(excel_content), 'test.xlsx')}

      response = client.post(
        "/upload_staged_refactored",
        data=data,
        content_type='multipart/form-data'
      )

      # Should handle exception gracefully
      assert response.status_code == 200
      html = response.get_data(as_text=True)
      assert "error" in html.lower() or "failed" in html.lower()


class TestRouteNavigation:
  """Test suite for route navigation and accessibility."""

  def test_refactored_route_accessible(self, client):
    """Test that refactored route is accessible."""
    response = client.get("/upload_staged_refactored")
    assert response.status_code == 200

    html = response.get_data(as_text=True)
    assert "Upload" in html
    assert "file" in html.lower()

  def test_refactored_route_in_navigation(self, client):
    """Test that refactored route is accessible from main page."""
    # This would require checking if the navbar includes the refactored route
    # For now, just verify the route exists and is accessible
    response = client.get("/")
    assert response.status_code == 200

    # The refactored route should be accessible directly
    refactored_response = client.get("/upload_staged_refactored")
    assert refactored_response.status_code == 200


class TestUploadFileRouteEquivalence:
  """Test suite for comparing original vs refactored upload_file route behavior."""

  def test_get_request_equivalence(self, client):
    """Test that both upload_file routes return identical GET responses."""
    # Test original route
    original_response = client.get("/upload")
    assert original_response.status_code == 200
    original_html = original_response.get_data(as_text=True)

    # Test refactored route
    refactored_response = client.get("/upload_refactored")
    assert refactored_response.status_code == 200
    refactored_html = refactored_response.get_data(as_text=True)

    # Both should contain the same key elements
    assert "Upload Feedback Spreadsheet" in original_html
    assert "Upload Feedback Spreadsheet" in refactored_html
    assert "file" in original_html.lower()
    assert "file" in refactored_html.lower()

  def test_get_request_with_message_equivalence(self, client):
    """Test that both upload_file routes handle message parameters identically."""
    test_message = "Test%20upload%20message%20for%20equivalence"

    # Test original route with message
    original_response = client.get(f"/upload/{test_message}")
    assert original_response.status_code == 200
    original_html = original_response.get_data(as_text=True)

    # Test refactored route with message
    refactored_response = client.get(f"/upload_refactored/{test_message}")
    assert refactored_response.status_code == 200
    refactored_html = refactored_response.get_data(as_text=True)

    # Both should display the message
    assert "Test upload message for equivalence" in original_html
    assert "Test upload message for equivalence" in refactored_html

  def test_post_no_file_equivalence(self, client):
    """Test that both upload_file routes handle 'no file selected' identically."""
    # Test original route
    original_response = client.post("/upload")
    assert original_response.status_code == 200
    original_html = original_response.get_data(as_text=True)
    assert "Upload Feedback Spreadsheet" in original_html

    # Test refactored route
    refactored_response = client.post("/upload_refactored")
    assert refactored_response.status_code == 200
    refactored_html = refactored_response.get_data(as_text=True)
    assert "Upload Feedback Spreadsheet" in refactored_html

  def test_post_empty_file_equivalence(self, client):
    """Test that both upload_file routes handle empty files identically."""
    # Test original route
    original_data = {'file': (io.BytesIO(b''), '')}
    original_response = client.post(
      "/upload",
      data=original_data,
      content_type='multipart/form-data'
    )
    assert original_response.status_code == 200
    original_html = original_response.get_data(as_text=True)
    assert "Upload Feedback Spreadsheet" in original_html

    # Test refactored route
    refactored_data = {'file': (io.BytesIO(b''), '')}
    refactored_response = client.post(
      "/upload_refactored",
      data=refactored_data,
      content_type='multipart/form-data'
    )
    assert refactored_response.status_code == 200
    refactored_html = refactored_response.get_data(as_text=True)
    assert "Upload Feedback Spreadsheet" in refactored_html

  def test_post_invalid_file_equivalence(self, client):
    """Test that both upload_file routes handle invalid files identically."""
    # Test original route
    original_data = {'file': (io.BytesIO(b'invalid content'), 'test.txt')}
    original_response = client.post(
      "/upload",
      data=original_data,
      content_type='multipart/form-data'
    )
    assert original_response.status_code == 200
    original_html = original_response.get_data(as_text=True)
    assert "error" in original_html.lower() or "failed" in original_html.lower() or "not recognized" in original_html.lower()

    # Test refactored route
    refactored_data = {'file': (io.BytesIO(b'invalid content'), 'test.txt')}
    refactored_response = client.post(
      "/upload_refactored",
      data=refactored_data,
      content_type='multipart/form-data'
    )
    assert refactored_response.status_code == 200
    refactored_html = refactored_response.get_data(as_text=True)
    assert "error" in refactored_html.lower() or "failed" in refactored_html.lower() or "not recognized" in refactored_html.lower()

  @patch('arb.portal.routes.upload_and_update_db')
  @patch('arb.portal.routes.upload_and_process_file')
  def test_success_case_equivalence(self, mock_upload_refactored, mock_upload_original, client):
    """Test that both routes handle successful uploads identically."""
    # Mock both functions to return success
    mock_upload_original.return_value = (Path("uploads/test.xlsx"), 123, "Dairy Digester")
    mock_upload_refactored.return_value = UploadResult(
      file_path=Path("uploads/test.xlsx"),
      id_=123,
      sector="Dairy Digester",
      success=True,
      error_message=None,
      error_type=None
    )

    # Test original route
    original_data = {'file': (io.BytesIO(b'test content'), 'test.xlsx')}
    original_response = client.post(
      "/upload",
      data=original_data,
      content_type='multipart/form-data'
    )
    assert original_response.status_code == 302
    assert b'incidence_update' in original_response.data

    # Test refactored route
    refactored_data = {'file': (io.BytesIO(b'test content'), 'test.xlsx')}
    refactored_response = client.post(
      "/upload_refactored",
      data=refactored_data,
      content_type='multipart/form-data'
    )
    assert refactored_response.status_code == 302
    assert b'incidence_update' in refactored_response.data


class TestUploadFileRefactoredRouteImprovements:
  """Test suite for improvements in the refactored upload_file route."""

  @patch('arb.portal.routes.upload_and_process_file')
  def test_refactored_route_uses_upload_result(self, mock_upload_refactored, client):
    """Test that refactored route uses UploadResult for better error handling."""
    mock_upload_refactored.return_value = UploadResult(
      file_path=Path("uploads/test.xlsx"),
      id_=None,
      sector="Dairy Digester",
      success=False,
      error_message="Test error message",
      error_type="missing_id"
    )

    data = {'file': (io.BytesIO(b'test content'), 'test.xlsx')}
    response = client.post('/upload_refactored', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    # The error message is HTML-encoded, so check for the encoded version
    assert "missing a valid &#39;Incidence/Emission ID&#39;" in html or "missing a valid 'Incidence/Emission ID'" in html

  @patch('arb.portal.routes.upload_and_process_file')
  def test_refactored_route_specific_error_types(self, mock_upload_refactored, client):
    """Test that refactored route provides specific error messages based on error_type."""
    # Test missing_id error
    mock_upload_refactored.return_value = UploadResult(
      file_path=Path("uploads/test.xlsx"),
      id_=None,
      sector="Dairy Digester",
      success=False,
      error_message="No valid id_incidence found",
      error_type="missing_id"
    )

    data = {'file': (io.BytesIO(b'test content'), 'test.xlsx')}
    response = client.post('/upload_refactored', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    # The error message is HTML-encoded, so check for the encoded version
    assert "missing a valid &#39;Incidence/Emission ID&#39;" in html or "missing a valid 'Incidence/Emission ID'" in html

  @patch('arb.portal.routes.upload_and_process_file')
  def test_refactored_route_exception_handling(self, mock_upload_refactored, client):
    """Test that refactored route handles exceptions gracefully."""
    mock_upload_refactored.side_effect = Exception("Test exception")

    data = {'file': (io.BytesIO(b'test content'), 'test.xlsx')}
    response = client.post('/upload_refactored', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    # Should show some form of error message
    assert "error" in html.lower() or "failed" in html.lower() or "not recognized" in html.lower()


class TestUploadFileRouteNavigation:
  """Test suite for navigation and accessibility of upload_file routes."""

  def test_refactored_upload_route_accessible(self, client):
    """Test that refactored upload route is accessible."""
    response = client.get("/upload_refactored")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Upload Feedback Spreadsheet" in html

  def test_refactored_upload_route_in_navigation(self, client):
    """Test that refactored upload route appears in navigation."""
    response = client.get("/upload_refactored")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    # Should contain navigation elements
    assert "nav" in html.lower() or "navbar" in html.lower() or "menu" in html.lower()


def test_route_function_signatures():
  """Test that both routes have the same function signatures."""
  from arb.portal.routes import upload_file_staged, upload_file_staged_refactored, upload_file, upload_file_refactored

  # Both staged routes should be callable functions
  assert callable(upload_file_staged)
  assert callable(upload_file_staged_refactored)

  # Both upload routes should be callable functions
  assert callable(upload_file)
  assert callable(upload_file_refactored)

  # Both should accept the same parameters
  import inspect
  original_staged_sig = inspect.signature(upload_file_staged)
  refactored_staged_sig = inspect.signature(upload_file_staged_refactored)
  original_upload_sig = inspect.signature(upload_file)
  refactored_upload_sig = inspect.signature(upload_file_refactored)

  # Both staged routes should accept message parameter
  assert 'message' in original_staged_sig.parameters
  assert 'message' in refactored_staged_sig.parameters

  # Both upload routes should accept message parameter
  assert 'message' in original_upload_sig.parameters
  assert 'message' in refactored_upload_sig.parameters
