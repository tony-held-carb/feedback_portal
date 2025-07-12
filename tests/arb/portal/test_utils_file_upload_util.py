"""
Comprehensive tests for arb.portal.utils.file_upload_util

Tests all file upload utility logic including database operations, error handling,
and edge cases. Covers audit trail functionality with proper mocking.
"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from arb.portal.utils import file_upload_util
from arb.portal.utils.file_upload_util import add_file_to_upload_table

@pytest.fixture
def mock_db():
    """Create a mock SQLAlchemy database instance."""
    mock_db = MagicMock()
    mock_db.session = MagicMock()
    return mock_db

@pytest.fixture
def mock_uploaded_file():
    """Create a mock UploadedFile model instance."""
    mock_model = MagicMock()
    mock_model.path = "uploads/test.xlsx"
    mock_model.status = "success"
    mock_model.description = "Test upload"
    return mock_model

def test_add_file_to_upload_table_function_signature():
    """add_file_to_upload_table function has correct signature."""
    assert hasattr(file_upload_util, 'add_file_to_upload_table')
    assert callable(file_upload_util.add_file_to_upload_table)

def test_add_file_to_upload_table_with_valid_data(mock_db, mock_uploaded_file):
    """add_file_to_upload_table works with valid data."""
    with patch('arb.portal.sqla_models.UploadedFile') as mock_uploaded_file_class:
        with patch('arb.portal.utils.file_upload_util.logger') as mock_logger:
            mock_uploaded_file_class.return_value = mock_uploaded_file
            
            add_file_to_upload_table(mock_db, "uploads/test.xlsx", "success", "Test upload")
            
            # Check that UploadedFile was created with correct parameters
            mock_uploaded_file_class.assert_called_once_with(
                path="uploads/test.xlsx",
                status="success",
                description="Test upload"
            )
            # Check that model was added to session and committed
            mock_db.session.add.assert_called_once_with(mock_uploaded_file)
            mock_db.session.commit.assert_called_once()

def test_add_file_to_upload_table_with_path_object(mock_db, mock_uploaded_file):
    """add_file_to_upload_table works with Path objects."""
    with patch('arb.portal.sqla_models.UploadedFile') as mock_uploaded_file_class:
        with patch('arb.portal.utils.file_upload_util.logger') as mock_logger:
            mock_uploaded_file_class.return_value = mock_uploaded_file
            
            file_path = Path("uploads/test.xlsx")
            add_file_to_upload_table(mock_db, file_path, "success", "Test upload")
            
            # Check that Path was converted to string (handle platform-specific separators)
            actual_call = mock_uploaded_file_class.call_args
            assert actual_call is not None
            assert actual_call[1]['path'] == str(file_path)  # Use actual Path conversion
            assert actual_call[1]['status'] == "success"
            assert actual_call[1]['description'] == "Test upload"

def test_add_file_to_upload_table_with_none_status_and_description(mock_db, mock_uploaded_file):
    """add_file_to_upload_table handles None status and description."""
    with patch('arb.portal.sqla_models.UploadedFile') as mock_uploaded_file_class:
        with patch('arb.portal.utils.file_upload_util.logger') as mock_logger:
            mock_uploaded_file_class.return_value = mock_uploaded_file
            
            add_file_to_upload_table(mock_db, "uploads/test.xlsx", None, None)
            
            # Check that None values are passed through
            mock_uploaded_file_class.assert_called_once_with(
                path="uploads/test.xlsx",
                status=None,
                description=None
            )

def test_add_file_to_upload_table_with_default_parameters(mock_db, mock_uploaded_file):
    """add_file_to_upload_table works with default parameters."""
    with patch('arb.portal.sqla_models.UploadedFile') as mock_uploaded_file_class:
        with patch('arb.portal.utils.file_upload_util.logger') as mock_logger:
            mock_uploaded_file_class.return_value = mock_uploaded_file
            
            add_file_to_upload_table(mock_db, "uploads/test.xlsx")
            
            # Check that default None values are used
            mock_uploaded_file_class.assert_called_once_with(
                path="uploads/test.xlsx",
                status=None,
                description=None
            )

def test_add_file_to_upload_table_raises_error_for_none_filename(mock_db):
    """add_file_to_upload_table raises ValueError for None filename."""
    with pytest.raises(ValueError, match="file_name cannot be None"):
        add_file_to_upload_table(mock_db, None)  # type: ignore

def test_add_file_to_upload_table_handles_commit_failure(mock_db, mock_uploaded_file):
    """add_file_to_upload_table handles commit failure."""
    from sqlalchemy.exc import SQLAlchemyError
    
    with patch('arb.portal.sqla_models.UploadedFile') as mock_uploaded_file_class:
        with patch('arb.portal.utils.file_upload_util.logger') as mock_logger:
            mock_uploaded_file_class.return_value = mock_uploaded_file
            mock_db.session.commit.side_effect = SQLAlchemyError("Database error")
            
            with pytest.raises(SQLAlchemyError, match="Database error"):
                add_file_to_upload_table(mock_db, "uploads/test.xlsx")

def test_add_file_to_upload_table_logs_debug_messages(mock_db, mock_uploaded_file):
    """add_file_to_upload_table logs debug messages."""
    with patch('arb.portal.sqla_models.UploadedFile') as mock_uploaded_file_class:
        with patch('arb.portal.utils.file_upload_util.logger') as mock_logger:
            mock_uploaded_file_class.return_value = mock_uploaded_file
            
            add_file_to_upload_table(mock_db, "uploads/test.xlsx", "success", "Test upload")
            
            # Check that debug messages were logged
            assert mock_logger.debug.call_count >= 2

def test_add_file_to_upload_table_with_empty_strings(mock_db, mock_uploaded_file):
    """add_file_to_upload_table handles empty strings for status and description."""
    with patch('arb.portal.sqla_models.UploadedFile') as mock_uploaded_file_class:
        with patch('arb.portal.utils.file_upload_util.logger') as mock_logger:
            mock_uploaded_file_class.return_value = mock_uploaded_file
            
            add_file_to_upload_table(mock_db, "uploads/test.xlsx", "", "")
            
            # Check that empty strings are passed through
            mock_uploaded_file_class.assert_called_once_with(
                path="uploads/test.xlsx",
                status="",
                description=""
            )

def test_add_file_to_upload_table_with_unicode_filename(mock_db, mock_uploaded_file):
    """add_file_to_upload_table handles unicode filenames."""
    with patch('arb.portal.sqla_models.UploadedFile') as mock_uploaded_file_class:
        with patch('arb.portal.utils.file_upload_util.logger') as mock_logger:
            mock_uploaded_file_class.return_value = mock_uploaded_file
            
            unicode_filename = "uploads/测试文件.xlsx"
            add_file_to_upload_table(mock_db, unicode_filename, "success", "Unicode test")
            
            # Check that unicode filename is handled correctly
            mock_uploaded_file_class.assert_called_once_with(
                path=unicode_filename,
                status="success",
                description="Unicode test"
            )

def test_add_file_to_upload_table_with_long_description(mock_db, mock_uploaded_file):
    """add_file_to_upload_table handles long descriptions."""
    with patch('arb.portal.sqla_models.UploadedFile') as mock_uploaded_file_class:
        with patch('arb.portal.utils.file_upload_util.logger') as mock_logger:
            mock_uploaded_file_class.return_value = mock_uploaded_file
            
            long_description = "This is a very long description that might contain a lot of text for debugging purposes and should be handled correctly by the database"
            add_file_to_upload_table(mock_db, "uploads/test.xlsx", "success", long_description)
            
            # Check that long description is handled correctly
            mock_uploaded_file_class.assert_called_once_with(
                path="uploads/test.xlsx",
                status="success",
                description=long_description
            )

def test_add_file_to_upload_table_returns_none(mock_db, mock_uploaded_file):
    """add_file_to_upload_table returns None as documented."""
    with patch('arb.portal.sqla_models.UploadedFile') as mock_uploaded_file_class:
        with patch('arb.portal.utils.file_upload_util.logger') as mock_logger:
            mock_uploaded_file_class.return_value = mock_uploaded_file
            
            result = add_file_to_upload_table(mock_db, "uploads/test.xlsx")
            
            assert result is None

def test_add_file_to_upload_table_creates_audit_record(mock_db, mock_uploaded_file):
    """add_file_to_upload_table creates proper audit record."""
    with patch('arb.portal.sqla_models.UploadedFile') as mock_uploaded_file_class:
        with patch('arb.portal.utils.file_upload_util.logger') as mock_logger:
            mock_uploaded_file_class.return_value = mock_uploaded_file
            
            add_file_to_upload_table(mock_db, "uploads/audit_test.xlsx", "audit", "Audit trail test")
            
            # Verify the audit record was created with correct data
            mock_uploaded_file_class.assert_called_once_with(
                path="uploads/audit_test.xlsx",
                status="audit",
                description="Audit trail test"
            )
            # Verify it was committed to database
            mock_db.session.commit.assert_called_once()

def test_add_file_to_upload_table_with_special_characters(mock_db, mock_uploaded_file):
    """add_file_to_upload_table handles special characters in filename."""
    with patch('arb.portal.sqla_models.UploadedFile') as mock_uploaded_file_class:
        with patch('arb.portal.utils.file_upload_util.logger') as mock_logger:
            mock_uploaded_file_class.return_value = mock_uploaded_file
            
            special_filename = "uploads/file with spaces & symbols (2024).xlsx"
            add_file_to_upload_table(mock_db, special_filename, "success", "Special chars test")
            
            # Check that special characters are handled correctly
            mock_uploaded_file_class.assert_called_once_with(
                path=special_filename,
                status="success",
                description="Special chars test"
            ) 