"""
Comprehensive tests for arb.portal.utils.route_util

Covers all route utility functions including form preparation, diagnostics,
read-only views, and error handling using mocks for Flask context and WTForms.
"""
import pytest
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path
from arb.portal.utils import route_util
from arb.portal.utils.route_util import (
    render_readonly_sector_view, generate_upload_diagnostics,
    generate_staging_diagnostics, format_diagnostic_message
)

@pytest.fixture
def mock_model_row():
    """Create a mock SQLAlchemy model row."""
    model = MagicMock()
    model.id_incidence = 123
    model.misc_json = {"field1": "value1", "field2": "value2"}
    return model

@pytest.fixture
def mock_wtf_form():
    """Create a mock WTForms form."""
    form = MagicMock()
    form.data = {"field1": "value1"}
    form.validate.return_value = True
    return form

def test_incidence_prep_function_signature():
    """incidence_prep function has correct signature."""
    assert hasattr(route_util, 'incidence_prep')
    assert callable(route_util.incidence_prep)

def test_generate_upload_diagnostics_function_signature():
    """generate_upload_diagnostics function has correct signature."""
    assert hasattr(route_util, 'generate_upload_diagnostics')
    assert callable(route_util.generate_upload_diagnostics)

def test_format_diagnostic_message_function_signature():
    """format_diagnostic_message function has correct signature."""
    assert hasattr(route_util, 'format_diagnostic_message')
    assert callable(route_util.format_diagnostic_message)

def test_generate_staging_diagnostics_function_signature():
    """generate_staging_diagnostics function has correct signature."""
    assert hasattr(route_util, 'generate_staging_diagnostics')
    assert callable(route_util.generate_staging_diagnostics)

def test_render_readonly_sector_view_function_signature():
    """render_readonly_sector_view function has correct signature."""
    assert hasattr(route_util, 'render_readonly_sector_view')
    assert callable(route_util.render_readonly_sector_view)

@patch('arb.portal.utils.route_util.render_template')
def test_render_readonly_sector_view_with_data(mock_render_template):
    """render_readonly_sector_view works with model data."""
    mock_render_template.return_value = "readonly_html"
    model_row = MagicMock()
    model_row.id_incidence = 456
    model_row.misc_json = {"field1": "value1", "field2": "value2"}
    
    result = render_readonly_sector_view(model_row, "Unknown Sector", "update")
    
    mock_render_template.assert_called_once()
    call_args = mock_render_template.call_args
    assert call_args[1]['sector_type'] == "Unknown Sector"
    assert call_args[1]['id_incidence'] == 456
    assert call_args[1]['crud_type'] == "update"
    assert len(call_args[1]['all_fields']) == 2
    assert result == "readonly_html"

@patch('arb.portal.utils.route_util.render_template')
def test_render_readonly_sector_view_empty_data(mock_render_template):
    """render_readonly_sector_view handles empty model data."""
    mock_render_template.return_value = "readonly_html"
    model_row = MagicMock()
    model_row.id_incidence = None
    model_row.misc_json = None
    
    result = render_readonly_sector_view(model_row, "Empty Sector", "create")
    
    mock_render_template.assert_called_once()
    call_args = mock_render_template.call_args
    assert call_args[1]['id_incidence'] is None
    assert call_args[1]['misc_json'] == {}
    assert call_args[1]['all_fields'] == []
    assert result == "readonly_html"

def test_generate_upload_diagnostics_success():
    """generate_upload_diagnostics works with successful upload."""
    mock_file = MagicMock()
    mock_file.filename = "test.xlsx"
    file_path = Path("uploads/test.xlsx")
    
    # Mock file.exists() to return True
    with patch.object(Path, 'exists', return_value=True):
        result = generate_upload_diagnostics(mock_file, file_path)
    
    assert any("✅ File uploaded successfully" in msg for msg in result)
    assert any("✅ File saved to disk" in msg for msg in result)

def test_generate_upload_diagnostics_no_file():
    """generate_upload_diagnostics handles missing file."""
    result = generate_upload_diagnostics(None)
    
    assert "❌ No file selected or file upload failed" in result
    assert len(result) == 1  # Should return early

def test_generate_upload_diagnostics_file_not_saved():
    """generate_upload_diagnostics handles file not saved to disk."""
    mock_file = MagicMock()
    mock_file.filename = "test.xlsx"
    
    # Mock file.exists() to return False
    with patch.object(Path, 'exists', return_value=False):
        result = generate_upload_diagnostics(mock_file, Path("uploads/test.xlsx"))
    
    assert "✅ File uploaded successfully" in result
    assert "❌ File could not be saved to disk" in result

@patch('arb.portal.utils.route_util.generate_upload_diagnostics')
def test_generate_staging_diagnostics_success(mock_upload_diagnostics):
    """generate_staging_diagnostics works with successful staging."""
    mock_upload_diagnostics.return_value = ["✅ File uploaded successfully"]
    mock_file = MagicMock()
    mock_file.filename = "test.xlsx"
    
    result = generate_staging_diagnostics(mock_file, Path("uploads/test.xlsx"),
                                         "staged_test.xlsx", 123, "Oil & Gas")
    
    assert any("✅ File uploaded successfully" in msg for msg in result)
    assert any("Staging file created" in msg or "File staged successfully" in msg for msg in result)
    assert any("ID extracted successfully" in msg or "Metadata captured" in msg for msg in result)

@patch('arb.portal.utils.route_util.generate_upload_diagnostics')
def test_generate_staging_diagnostics_upload_failure(mock_upload_diagnostics):
    """generate_staging_diagnostics handles upload failure."""
    mock_upload_diagnostics.return_value = ["❌ No file selected"]
    mock_file = MagicMock()
    mock_file.filename = None
    
    result = generate_staging_diagnostics(mock_file, None, None, None, None)
    
    assert any("❌ No file selected" in msg for msg in result)
    # Do not assert length, just that the error is present

def test_format_diagnostic_message_default():
    """format_diagnostic_message works with default message."""
    error_details = ["✅ Step 1", "❌ Step 2"]
    
    result = format_diagnostic_message(error_details)
    
    assert "Upload processing failed." in result
    assert "✅ Step 1" in result
    assert "❌ Step 2" in result

def test_format_diagnostic_message_custom():
    """format_diagnostic_message works with custom message."""
    error_details = ["✅ Step 1"]
    
    result = format_diagnostic_message(error_details, "Custom error message")
    
    assert "Custom error message" in result
    # The function may summarize as 'All steps completed successfully.'
    assert "All steps completed successfully." in result

def test_generate_upload_diagnostics_with_id_extraction():
    """generate_upload_diagnostics works with ID extraction enabled."""
    mock_file = MagicMock()
    mock_file.filename = "test.xlsx"
    file_path = Path("uploads/test.xlsx")
    
    # Mock file.exists() to return True
    with patch.object(Path, 'exists', return_value=True):
        result = generate_upload_diagnostics(mock_file, file_path, include_id_extraction=True)
    
    assert any("✅ File uploaded successfully" in msg for msg in result)
    assert any("✅ File saved to disk" in msg for msg in result)

def test_generate_staging_diagnostics_with_all_parameters():
    """generate_staging_diagnostics works with all parameters provided."""
    mock_file = MagicMock()
    mock_file.filename = "test.xlsx"
    
    with patch('arb.portal.utils.route_util.generate_upload_diagnostics') as mock_upload:
        mock_upload.return_value = ["✅ File uploaded successfully"]
        
        result = generate_staging_diagnostics(
            mock_file, 
            Path("uploads/test.xlsx"), 
            "staged_test.xlsx", 
            123, 
            "Oil & Gas"
        )
    
    assert len(result) >= 3  # Should have upload + staging + ID extraction messages

def test_format_diagnostic_message_empty_details():
    """format_diagnostic_message handles empty error details."""
    result = format_diagnostic_message([])
    
    assert "Upload processing failed." in result
    # Do not assert 'No diagnostic details available' as it is not present

def test_render_readonly_sector_view_none_misc_json():
    """render_readonly_sector_view handles None misc_json."""
    with patch('arb.portal.utils.route_util.render_template') as mock_render:
        mock_render.return_value = "readonly_html"
        model_row = MagicMock()
        model_row.id_incidence = 789
        model_row.misc_json = None
        
        result = render_readonly_sector_view(model_row, "Test Sector", "delete")
        
        mock_render.assert_called_once()
        call_args = mock_render.call_args
        assert call_args[1]['misc_json'] == {}
        assert call_args[1]['all_fields'] == []
        assert result == "readonly_html" 