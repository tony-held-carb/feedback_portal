"""
Tests for the core upload logic functions extracted from Flask routes.

This module tests the business logic functions in upload_logic.py to ensure
they correctly orchestrate the backend functions without modifying them.
"""

import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
from werkzeug.datastructures import FileStorage

from arb.portal.upload_logic import (
    upload_file_logic,
    upload_file_refactored_logic,
    upload_file_staged_logic,
    upload_file_staged_refactored_logic,
    get_upload_folder_logic,
    UploadLogicResult
)


class TestUploadLogicFunctions:
    """Test the core upload logic functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.mock_base = Mock()
        self.mock_request_file = Mock(spec=FileStorage)
        self.mock_request_file.filename = "test_file.xlsx"
        self.upload_folder = Path("/tmp/test_upload")
    
    def test_upload_file_logic_success(self):
        """Test successful upload logic."""
        # Mock the backend function to return success
        with pytest.MonkeyPatch().context() as m:
            m.setattr('arb.portal.upload_logic.upload_and_update_db', 
                     lambda db, folder, file, base: (Path("/tmp/test.xlsx"), 123, "test_sector"))
            
            result = upload_file_logic(self.mock_db, self.upload_folder, self.mock_request_file, self.mock_base)
            
            assert result.success is True
            assert result.status_code == 200
            assert result.redirect_url == "/incidence_update/123"
            assert result.processed_data["id_incidence"] == 123
            assert result.processed_data["sector"] == "test_sector"
    
    def test_upload_file_logic_missing_id(self):
        """Test upload logic with missing ID."""
        # Mock the backend function to return missing ID
        with pytest.MonkeyPatch().context() as m:
            m.setattr('arb.portal.upload_logic.upload_and_update_db', 
                     lambda db, folder, file, base: (Path("/tmp/test.xlsx"), None, None))
            
            result = upload_file_logic(self.mock_db, self.upload_folder, self.mock_request_file, self.mock_base)
            
            assert result.success is False
            assert result.status_code == 400
            assert result.error_type == "missing_id"
            assert "id_incidence" in result.error_message
    
    def test_upload_file_refactored_logic_success(self):
        """Test successful refactored upload logic."""
        # Mock the backend function to return success
        mock_result = Mock()
        mock_result.success = True
        mock_result.id_ = 456
        mock_result.sector = "refactored_sector"
        mock_result.file_path = Path("/tmp/refactored.xlsx")
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr('arb.portal.upload_logic.upload_and_process_file', 
                     lambda db, folder, file, base: mock_result)
            
            result = upload_file_refactored_logic(self.mock_db, self.upload_folder, self.mock_request_file, self.mock_base)
            
            assert result.success is True
            assert result.status_code == 200
            assert result.redirect_url == "/incidence_update/456"
            assert result.processed_data["id_incidence"] == 456
            assert result.processed_data["sector"] == "refactored_sector"
    
    def test_upload_file_refactored_logic_error(self):
        """Test refactored upload logic with error."""
        # Mock the backend function to return error
        mock_result = Mock()
        mock_result.success = False
        mock_result.error_type = "conversion_failed"
        mock_result.error_message = "File conversion failed"
        mock_result.file_path = Path("/tmp/failed.xlsx")
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr('arb.portal.upload_logic.upload_and_process_file', 
                     lambda db, folder, file, base: mock_result)
            
            result = upload_file_refactored_logic(self.mock_db, self.upload_folder, self.mock_request_file, self.mock_base)
            
            assert result.success is False
            assert result.status_code == 400
            assert result.error_type == "conversion_failed"
            assert result.error_message == "File conversion failed"
    
    def test_upload_file_staged_logic_success(self):
        """Test successful staged upload logic."""
        # Mock the backend function to return success
        with pytest.MonkeyPatch().context() as m:
            m.setattr('arb.portal.upload_logic.upload_and_stage_only', 
                     lambda db, folder, file, base: (Path("/tmp/staged.xlsx"), 789, "staged_sector", {}, "staged_file.json"))
            
            result = upload_file_staged_logic(self.mock_db, self.upload_folder, self.mock_request_file, self.mock_base)
            
            assert result.success is True
            assert result.status_code == 200
            assert result.redirect_url == "/review_staged/789/staged_file.json"
            assert result.processed_data["id_incidence"] == 789
            assert result.processed_data["sector"] == "staged_sector"
            assert result.processed_data["staged_filename"] == "staged_file.json"
    
    def test_upload_file_staged_logic_missing_id(self):
        """Test staged upload logic with missing ID."""
        # Mock the backend function to return missing ID
        with pytest.MonkeyPatch().context() as m:
            m.setattr('arb.portal.upload_logic.upload_and_stage_only', 
                     lambda db, folder, file, base: (Path("/tmp/staged.xlsx"), None, None, {}, ""))
            
            result = upload_file_staged_logic(self.mock_db, self.upload_folder, self.mock_request_file, self.mock_base)
            
            assert result.success is False
            assert result.status_code == 400
            assert result.error_type == "missing_id"
            assert "id_incidence" in result.error_message
    
    def test_upload_file_staged_refactored_logic_success(self):
        """Test successful refactored staged upload logic."""
        # Mock the backend function to return success
        mock_result = Mock()
        mock_result.success = True
        mock_result.id_ = 101
        mock_result.sector = "refactored_staged_sector"
        mock_result.file_path = Path("/tmp/refactored_staged.xlsx")
        mock_result.staged_filename = "refactored_staged.json"
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr('arb.portal.upload_logic.stage_uploaded_file_for_review', 
                     lambda db, folder, file, base: mock_result)
            
            result = upload_file_staged_refactored_logic(self.mock_db, self.upload_folder, self.mock_request_file, self.mock_base)
            
            assert result.success is True
            assert result.status_code == 200
            assert result.redirect_url == "/review_staged/101/refactored_staged.json"
            assert result.processed_data["id_incidence"] == 101
            assert result.processed_data["sector"] == "refactored_staged_sector"
            assert result.processed_data["staged_filename"] == "refactored_staged.json"
    
    def test_upload_file_staged_refactored_logic_error(self):
        """Test refactored staged upload logic with error."""
        # Mock the backend function to return error
        mock_result = Mock()
        mock_result.success = False
        mock_result.error_type = "file_error"
        mock_result.error_message = "File processing failed"
        mock_result.file_path = Path("/tmp/failed_staged.xlsx")
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr('arb.portal.upload_logic.stage_uploaded_file_for_review', 
                     lambda db, folder, file, base: mock_result)
            
            result = upload_file_staged_refactored_logic(self.mock_db, self.upload_folder, self.mock_request_file, self.mock_base)
            
            assert result.success is False
            assert result.status_code == 400
            assert result.error_type == "file_error"
            assert result.error_message == "File processing failed"
    
    def test_exception_handling(self):
        """Test exception handling in all logic functions."""
        # Mock the backend functions to raise exceptions
        with pytest.MonkeyPatch().context() as m:
            m.setattr('arb.portal.upload_logic.upload_and_update_db', 
                     lambda db, folder, file, base: (_ for _ in ()).throw(Exception("Test error")))
            
            result = upload_file_logic(self.mock_db, self.upload_folder, self.mock_request_file, self.mock_base)
            
            assert result.success is False
            assert result.status_code == 500
            assert result.error_type == "processing_error"
            assert "Test error" in result.error_message
    
    def test_get_upload_folder_logic(self):
        """Test the upload folder logic function."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr('arb.portal.upload_logic.get_upload_folder', lambda: Path("/tmp/config_upload"))
            
            result = get_upload_folder_logic()
            
            assert result == Path("/tmp/config_upload")


class TestUploadLogicResult:
    """Test the UploadLogicResult dataclass."""
    
    def test_upload_logic_result_creation(self):
        """Test creating UploadLogicResult instances."""
        result = UploadLogicResult(
            success=True,
            status_code=200,
            flash_messages=["Success"],
            redirect_url="/success",
            validation_errors=None,
            processed_data={"key": "value"},
            error_message=None,
            error_type=None
        )
        
        assert result.success is True
        assert result.status_code == 200
        assert result.flash_messages == ["Success"]
        assert result.redirect_url == "/success"
        assert result.validation_errors is None
        assert result.processed_data == {"key": "value"}
        assert result.error_message is None
        assert result.error_type is None
    
    def test_upload_logic_result_with_errors(self):
        """Test creating UploadLogicResult instances with errors."""
        result = UploadLogicResult(
            success=False,
            status_code=400,
            flash_messages=["Error"],
            redirect_url=None,
            validation_errors={"field": "error"},
            processed_data=None,
            error_message="Something went wrong",
            error_type="validation_error"
        )
        
        assert result.success is False
        assert result.status_code == 400
        assert result.flash_messages == ["Error"]
        assert result.redirect_url is None
        assert result.validation_errors == {"field": "error"}
        assert result.processed_data is None
        assert result.error_message == "Something went wrong"
        assert result.error_type == "validation_error"
