"""
Unit tests for route upload helper functions.

This module tests the shared helper functions used by upload routes to ensure
they work correctly and provide consistent behavior.
"""

import pytest
from unittest.mock import MagicMock, patch
from werkzeug.datastructures import FileStorage

from arb.portal.utils.route_upload_helpers import (
    validate_upload_request,
    get_error_message_for_type,
    get_success_message_for_upload,
    render_upload_form,
    render_upload_error,
    handle_upload_error,
    handle_upload_exception,
    handle_upload_success
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


class TestHandleUploadError:
    """Test the handle_upload_error helper function."""

    def test_handle_upload_error_function_signature(self):
        """handle_upload_error has correct function signature."""
        import inspect
        sig = inspect.signature(handle_upload_error)
        params = list(sig.parameters.keys())
        
        assert 'result' in params
        assert 'form' in params
        assert 'template_name' in params
        assert 'request_file' in params

    def test_handle_upload_error_docstring(self):
        """handle_upload_error has proper documentation."""
        assert handle_upload_error.__doc__ is not None
        assert "Handle upload errors" in handle_upload_error.__doc__

    def test_handle_upload_error_with_missing_id(self):
        """handle_upload_error handles missing_id error type."""
        mock_result = MagicMock()
        mock_result.error_type = "missing_id"
        mock_result.error_message = "No valid id_incidence found"
        mock_form = MagicMock()

        # Test that the function calls get_error_message_for_type correctly
        with patch('arb.portal.utils.route_upload_helpers.get_error_message_for_type') as mock_get_error:
            mock_get_error.return_value = "User-friendly error message"
            with patch('arb.portal.utils.route_upload_helpers.render_upload_error') as mock_render:
                mock_render.return_value = "Rendered HTML"
                
                result = handle_upload_error(mock_result, mock_form, 'upload.html')

                # Verify the function calls the expected helpers
                mock_get_error.assert_called_once_with("missing_id", mock_result)
                mock_render.assert_called_once_with(mock_form, "User-friendly error message", 'upload.html')
                assert result == "Rendered HTML"

    def test_handle_upload_error_with_conversion_failed(self):
        """handle_upload_error handles conversion_failed error type."""
        mock_result = MagicMock()
        mock_result.error_type = "conversion_failed"
        mock_result.error_message = "File format not supported"
        mock_result.file_path = "test.xlsx"
        mock_form = MagicMock()

        # Test that the function handles conversion_failed specially
        with patch('arb.portal.utils.route_upload_helpers.render_upload_error') as mock_render:
            mock_render.return_value = "Rendered HTML"
            
            result = handle_upload_error(mock_result, mock_form, 'upload.html')

            # Verify the function calls render_upload_error directly for conversion_failed
            mock_render.assert_called_once()
            assert result == "Rendered HTML"

    def test_handle_upload_error_with_file_error(self):
        """handle_upload_error handles file_error error type."""
        mock_result = MagicMock()
        mock_result.error_type = "file_error"
        mock_result.error_message = "Permission denied"
        mock_form = MagicMock()

        # Test that the function calls get_error_message_for_type correctly
        with patch('arb.portal.utils.route_upload_helpers.get_error_message_for_type') as mock_get_error:
            mock_get_error.return_value = "User-friendly error message"
            with patch('arb.portal.utils.route_upload_helpers.render_upload_error') as mock_render:
                mock_render.return_value = "Rendered HTML"
                
                result = handle_upload_error(mock_result, mock_form, 'upload.html')

                # Verify the function calls the expected helpers
                mock_get_error.assert_called_once_with("file_error", mock_result)
                mock_render.assert_called_once_with(mock_form, "User-friendly error message", 'upload.html')
                assert result == "Rendered HTML"


class TestHandleUploadException:
    """Test the handle_upload_exception helper function."""

    def test_handle_upload_exception_function_signature(self):
        """handle_upload_exception has correct function signature."""
        import inspect
        sig = inspect.signature(handle_upload_exception)
        params = list(sig.parameters.keys())
        
        assert 'e' in params
        assert 'form' in params
        assert 'template_name' in params
        assert 'request_file' in params
        assert 'result' in params
        assert 'diagnostic_func' in params

    def test_handle_upload_exception_docstring(self):
        """handle_upload_exception has proper documentation."""
        assert handle_upload_exception.__doc__ is not None
        assert "Handle exceptions" in handle_upload_exception.__doc__

    def test_handle_upload_exception_with_diagnostic_func(self):
        """handle_upload_exception uses diagnostic function when provided."""
        mock_exception = Exception("Test exception")
        mock_form = MagicMock()
        mock_request_file = MagicMock()
        mock_result = MagicMock()
        mock_result.file_path = "test.xlsx"
        
        # Mock diagnostic function
        def mock_diagnostic_func(req_file, file_path):
            return {"error": "Test diagnostic"}
        
        with patch('arb.portal.utils.route_upload_helpers.format_diagnostic_message') as mock_format:
            mock_format.return_value = "Formatted diagnostic message"
            with patch('arb.portal.utils.route_upload_helpers.render_upload_error') as mock_render:
                mock_render.return_value = "Rendered HTML"
                
                result = handle_upload_exception(mock_exception, mock_form, 'upload.html',
                                               mock_request_file, mock_result, mock_diagnostic_func)

                # Verify the function calls the expected helpers
                mock_format.assert_called_once_with({"error": "Test diagnostic"})
                mock_render.assert_called_once_with(mock_form, "Formatted diagnostic message", 'upload.html')
                assert result == "Rendered HTML"

    def test_handle_upload_exception_without_diagnostic_func(self):
        """handle_upload_exception handles case without diagnostic function."""
        mock_exception = Exception("Test exception")
        mock_form = MagicMock()

        with patch('arb.portal.utils.route_upload_helpers.render_upload_error') as mock_render:
            mock_render.return_value = "Rendered HTML"
            
            result = handle_upload_exception(mock_exception, mock_form, 'upload.html')

            # Verify the function calls render_upload_error with generic message
            mock_render.assert_called_once_with(mock_form, 
                "An unexpected error occurred during upload processing. Please try again.", 
                'upload.html')
            assert result == "Rendered HTML"

    def test_handle_upload_exception_with_diagnostic_error(self):
        """handle_upload_exception handles diagnostic function errors gracefully."""
        mock_exception = Exception("Test exception")
        mock_form = MagicMock()
        mock_request_file = MagicMock()
        
        # Mock diagnostic function that raises an exception
        def mock_diagnostic_func(req_file, file_path):
            raise Exception("Diagnostic error")
        
        with patch('arb.portal.utils.route_upload_helpers.render_upload_error') as mock_render:
            mock_render.return_value = "Rendered HTML"
            
            result = handle_upload_exception(mock_exception, mock_form, 'upload.html',
                                           mock_request_file, None, mock_diagnostic_func)

            # Verify the function falls back to generic message when diagnostic fails
            mock_render.assert_called_once_with(mock_form, 
                "An unexpected error occurred during upload processing. Please try again.", 
                'upload.html')
            assert result == "Rendered HTML"


class TestHandleUploadSuccess:
    """Test the handle_upload_success helper function."""

    def test_handle_upload_success_function_signature(self):
        """handle_upload_success has correct function signature."""
        import inspect
        sig = inspect.signature(handle_upload_success)
        params = list(sig.parameters.keys())
        
        assert 'result' in params
        assert 'request_file' in params
        assert 'upload_type' in params

    def test_handle_upload_success_docstring(self):
        """handle_upload_success has proper documentation."""
        assert handle_upload_success.__doc__ is not None
        assert "Handle successful upload" in handle_upload_success.__doc__

    def test_handle_upload_success_with_direct_upload(self):
        """handle_upload_success handles direct upload correctly."""
        mock_result = MagicMock()
        mock_result.id_ = 123
        mock_result.sector = "Test Sector"
        mock_request_file = MagicMock()
        mock_request_file.filename = "test.xlsx"
        
        with patch('arb.portal.utils.route_upload_helpers.get_success_message_for_upload') as mock_get_message:
            mock_get_message.return_value = "✅ File 'test.xlsx' uploaded successfully!"
            with patch('arb.portal.utils.route_upload_helpers.url_for') as mock_url_for:
                mock_url_for.return_value = "/incidence_update/123"
                
                success_message, redirect_url = handle_upload_success(mock_result, mock_request_file, "direct")

                # Verify the function calls the expected helpers
                mock_get_message.assert_called_once_with(mock_result, "test.xlsx", "direct")
                mock_url_for.assert_called_once_with('main.incidence_update', id_=123)
                assert success_message == "✅ File 'test.xlsx' uploaded successfully!"
                assert redirect_url == "/incidence_update/123"

    def test_handle_upload_success_with_staged_upload(self):
        """handle_upload_success handles staged upload correctly."""
        mock_result = MagicMock()
        mock_result.id_ = 456
        mock_result.sector = "Test Sector"
        mock_result.staged_filename = "staged_456.json"
        mock_request_file = MagicMock()
        mock_request_file.filename = "test.xlsx"
        
        with patch('arb.portal.utils.route_upload_helpers.get_success_message_for_upload') as mock_get_message:
            mock_get_message.return_value = "✅ File 'test.xlsx' staged successfully!"
            with patch('arb.portal.utils.route_upload_helpers.url_for') as mock_url_for:
                mock_url_for.return_value = "/review_staged/456/staged_456.json"
                
                success_message, redirect_url = handle_upload_success(mock_result, mock_request_file, "staged")

                # Verify the function calls the expected helpers
                mock_get_message.assert_called_once_with(mock_result, "test.xlsx", "staged")
                mock_url_for.assert_called_once_with('main.review_staged', id_=456, filename="staged_456.json")
                assert success_message == "✅ File 'test.xlsx' staged successfully!"
                assert redirect_url == "/review_staged/456/staged_456.json"

    def test_handle_upload_success_with_default_upload_type(self):
        """handle_upload_success uses 'direct' as default upload type."""
        mock_result = MagicMock()
        mock_result.id_ = 789
        mock_result.sector = "Test Sector"
        mock_request_file = MagicMock()
        mock_request_file.filename = "test.xlsx"
        
        with patch('arb.portal.utils.route_upload_helpers.get_success_message_for_upload') as mock_get_message:
            mock_get_message.return_value = "✅ File 'test.xlsx' uploaded successfully!"
            with patch('arb.portal.utils.route_upload_helpers.url_for') as mock_url_for:
                mock_url_for.return_value = "/incidence_update/789"
                
                success_message, redirect_url = handle_upload_success(mock_result, mock_request_file)

                # Verify the function uses 'direct' as default
                mock_get_message.assert_called_once_with(mock_result, "test.xlsx", "direct")
                mock_url_for.assert_called_once_with('main.incidence_update', id_=789)
                assert success_message == "✅ File 'test.xlsx' uploaded successfully!"
                assert redirect_url == "/incidence_update/789"
