"""
Unit tests for route upload helper functions.

This module tests the shared helper functions used by upload routes to ensure
they work correctly and provide consistent behavior.
"""

import pytest
from unittest.mock import MagicMock
from werkzeug.datastructures import FileStorage

from arb.portal.utils.route_upload_helpers import (
    validate_upload_request,
    get_error_message_for_type,
    get_success_message_for_upload,
    render_upload_form,
    render_upload_error
)
from arb.portal.wtf_upload import UploadForm


class TestValidateUploadRequest:
    """Test the validate_upload_request helper function."""

    def test_validate_upload_request_with_valid_file(self):
        """validate_upload_request returns True for valid file."""
        mock_file = MagicMock(spec=FileStorage)
        mock_file.filename = "test.xlsx"

        is_valid, error_message = validate_upload_request(mock_file)

        assert is_valid is True
        assert error_message is None

    def test_validate_upload_request_with_no_file(self):
        """validate_upload_request returns False for no file."""
        is_valid, error_message = validate_upload_request(None)

        assert is_valid is False
        assert error_message == "No file selected. Please choose a file."

    def test_validate_upload_request_with_empty_filename(self):
        """validate_upload_request returns False for empty filename."""
        mock_file = MagicMock(spec=FileStorage)
        mock_file.filename = ""

        is_valid, error_message = validate_upload_request(mock_file)

        assert is_valid is False
        assert error_message == "No file selected. Please choose a file."

    def test_validate_upload_request_with_none_filename(self):
        """validate_upload_request returns False for None filename."""
        mock_file = MagicMock(spec=FileStorage)
        mock_file.filename = None

        is_valid, error_message = validate_upload_request(mock_file)

        assert is_valid is False
        assert error_message == "No file selected. Please choose a file."


class TestGetErrorMessageForType:
    """Test the get_error_message_for_type helper function."""

    def test_get_error_message_for_missing_id(self):
        """get_error_message_for_type returns correct message for missing_id."""
        mock_result = MagicMock()
        mock_result.error_message = "No valid id_incidence found"

        message = get_error_message_for_type("missing_id", mock_result)

        assert "missing a valid 'Incidence/Emission ID'" in message
        assert "Please add a positive integer id_incidence" in message

    def test_get_error_message_for_conversion_failed(self):
        """get_error_message_for_type returns correct message for conversion_failed."""
        mock_result = MagicMock()
        mock_result.error_message = "File format not supported"

        message = get_error_message_for_type("conversion_failed", mock_result)

        assert "Unsupported file format" in message
        assert "Please upload Excel (.xlsx) file" in message

    def test_get_error_message_for_file_error(self):
        """get_error_message_for_type returns correct message for file_error."""
        mock_result = MagicMock()
        mock_result.error_message = "Permission denied"

        message = get_error_message_for_type("file_error", mock_result)

        assert "Error processing uploaded file" in message
        assert "Permission denied" in message

    def test_get_error_message_for_database_error(self):
        """get_error_message_for_type returns correct message for database_error."""
        mock_result = MagicMock()
        mock_result.error_message = "Connection failed"

        message = get_error_message_for_type("database_error", mock_result)

        assert "Database error occurred" in message
        assert "Connection failed" in message

    def test_get_error_message_for_unknown_error(self):
        """get_error_message_for_type returns correct message for unknown error."""
        mock_result = MagicMock()
        mock_result.error_message = "Unknown error occurred"

        message = get_error_message_for_type("unknown_error", mock_result)

        assert "An unexpected error occurred" in message
        assert "Unknown error occurred" in message


class TestGetSuccessMessageForUpload:
    """Test the get_success_message_for_upload helper function."""

    def test_get_success_message_for_staged_upload(self):
        """get_success_message_for_upload returns correct message for staged upload."""
        mock_result = MagicMock()
        mock_result.id_ = 123
        mock_result.sector = "Dairy Digester"
        mock_result.staged_filename = "id_123_ts_20250101_120000.json"

        message = get_success_message_for_upload(mock_result, "test.xlsx", "staged")

        assert "✅ File 'test.xlsx' staged successfully!" in message
        assert "📋 ID: 123" in message
        assert "🏭 Sector: Dairy Digester" in message
        assert "📁 Staged as: id_123_ts_20250101_120000.json" in message
        assert "🔍 Ready for review and confirmation" in message

    def test_get_success_message_for_direct_upload(self):
        """get_success_message_for_upload returns correct message for direct upload."""
        mock_result = MagicMock()
        mock_result.id_ = 123
        mock_result.sector = "Dairy Digester"

        message = get_success_message_for_upload(mock_result, "test.xlsx", "direct")

        assert "✅ File 'test.xlsx' uploaded successfully!" in message
        assert "ID: 123" in message
        assert "Sector: Dairy Digester" in message


class TestRenderUploadForm:
    """Test the render_upload_form helper function."""

    def test_render_upload_form_function_signature(self):
        """render_upload_form has correct function signature."""
        # Test that the function exists and has the right signature
        import inspect
        sig = inspect.signature(render_upload_form)
        params = list(sig.parameters.keys())
        
        assert 'form' in params
        assert 'message' in params
        assert 'template_name' in params

    def test_render_upload_form_docstring(self):
        """render_upload_form has proper documentation."""
        assert render_upload_form.__doc__ is not None
        assert "Render upload form" in render_upload_form.__doc__


class TestRenderUploadError:
    """Test the render_upload_error helper function."""

    def test_render_upload_error_function_signature(self):
        """render_upload_error has correct function signature."""
        # Test that the function exists and has the right signature
        import inspect
        sig = inspect.signature(render_upload_error)
        params = list(sig.parameters.keys())
        
        assert 'form' in params
        assert 'message' in params
        assert 'template_name' in params

    def test_render_upload_error_docstring(self):
        """render_upload_error has proper documentation."""
        assert render_upload_error.__doc__ is not None
        assert "Render upload error" in render_upload_error.__doc__
