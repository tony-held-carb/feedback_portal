"""
Tests for the unified upload processing pipeline - Phase 9 Implementation.

This module tests the unified processing pipeline to ensure it correctly
handles all upload types with configuration-driven behavior.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from werkzeug.datastructures import FileStorage

from arb.portal.utils.unified_upload_pipeline import (
    UnifiedUploadConfig,
    get_core_logic_function,
    process_upload_unified,
    get_standard_configurations,
    create_custom_configuration,
    validate_configuration,
    get_configuration_summary
)
from arb.portal.upload_logic import (
    upload_file_logic,
    upload_file_refactored_logic,
    upload_file_staged_logic,
    upload_file_staged_refactored_logic,
    UploadLogicResult
)


class TestUnifiedUploadConfig:
    """Test the UnifiedUploadConfig dataclass."""
    
    def test_valid_direct_original_config(self):
        """Test creating valid direct upload with original logic configuration."""
        config = UnifiedUploadConfig(
            upload_type="direct",
            template_name="upload.html",
            core_logic_function="original",
            description="Direct upload with original logic",
            is_refactored=False
        )
        
        assert config.upload_type == "direct"
        assert config.template_name == "upload.html"
        assert config.core_logic_function == "original"
        assert config.description == "Direct upload with original logic"
        assert config.is_refactored is False
    
    def test_valid_staged_refactored_config(self):
        """Test creating valid staged upload with refactored logic configuration."""
        config = UnifiedUploadConfig(
            upload_type="staged",
            template_name="upload_staged.html",
            core_logic_function="refactored",
            description="Staged upload with refactored logic",
            is_refactored=True
        )
        
        assert config.upload_type == "staged"
        assert config.template_name == "upload_staged.html"
        assert config.core_logic_function == "refactored"
        assert config.description == "Staged upload with refactored logic"
        assert config.is_refactored is True
    
    def test_invalid_upload_type(self):
        """Test that invalid upload type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid upload_type: invalid_type"):
            UnifiedUploadConfig(
                upload_type="invalid_type",
                template_name="upload.html",
                core_logic_function="original",
                description="Invalid config",
                is_refactored=False
            )
    
    def test_invalid_core_logic_function(self):
        """Test that invalid core logic function raises ValueError."""
        with pytest.raises(ValueError, match="Invalid core_logic_function: invalid_logic"):
            UnifiedUploadConfig(
                upload_type="direct",
                template_name="upload.html",
                core_logic_function="invalid_logic",
                description="Invalid config",
                is_refactored=False
            )
    
    def test_staged_original_warning(self):
        """Test that staged original logic generates a warning."""
        # This should trigger the warning in __post_init__ but not raise an exception
        config = UnifiedUploadConfig(
            upload_type="staged",
            template_name="upload_staged.html",
            core_logic_function="original",
            description="Staged upload with original logic",
            is_refactored=False
        )
        # The warning should be logged but the config should still be created
        assert config.upload_type == "staged"
        assert config.core_logic_function == "original"


class TestGetCoreLogicFunction:
    """Test the get_core_logic_function function."""
    
    def test_direct_original_logic(self):
        """Test getting direct upload with original logic function."""
        config = UnifiedUploadConfig(
            upload_type="direct",
            template_name="upload.html",
            core_logic_function="original",
            description="Direct upload with original logic",
            is_refactored=False
        )
        
        func = get_core_logic_function(config)
        assert func == upload_file_logic
    
    def test_direct_refactored_logic(self):
        """Test getting direct upload with refactored logic function."""
        config = UnifiedUploadConfig(
            upload_type="direct",
            template_name="upload.html",
            core_logic_function="refactored",
            description="Direct upload with refactored logic",
            is_refactored=True
        )
        
        func = get_core_logic_function(config)
        assert func == upload_file_refactored_logic
    
    def test_staged_original_logic(self):
        """Test getting staged upload with original logic function."""
        config = UnifiedUploadConfig(
            upload_type="staged",
            template_name="upload_staged.html",
            core_logic_function="original",
            description="Staged upload with original logic",
            is_refactored=False
        )
        
        func = get_core_logic_function(config)
        assert func == upload_file_staged_logic
    
    def test_staged_refactored_logic(self):
        """Test getting staged upload with refactored logic function."""
        config = UnifiedUploadConfig(
            upload_type="staged",
            template_name="upload_staged.html",
            core_logic_function="refactored",
            description="Staged upload with refactored logic",
            is_refactored=True
        )
        
        func = get_core_logic_function(config)
        assert func == upload_file_staged_refactored_logic
    
    def test_invalid_upload_type(self):
        """Test that invalid upload type raises ValueError."""
        config = Mock()
        config.upload_type = "invalid_type"
        
        with pytest.raises(ValueError, match="Invalid upload_type: invalid_type"):
            get_core_logic_function(config)
    
    def test_invalid_core_logic_function(self):
        """Test that invalid core logic function raises ValueError."""
        config = Mock()
        config.upload_type = "direct"
        config.core_logic_function = "invalid_logic"
        
        with pytest.raises(ValueError, match="Invalid core_logic_function for direct upload: invalid_logic"):
            get_core_logic_function(config)


class TestProcessUploadUnified:
    """Test the process_upload_unified function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.mock_base = Mock()
        self.mock_request_file = Mock(spec=FileStorage)
        self.mock_request_file.filename = "test_file.xlsx"
        self.upload_folder = Path("/tmp/test_upload")
        
        # Standard configuration for testing
        self.config = UnifiedUploadConfig(
            upload_type="direct",
            template_name="upload.html",
            core_logic_function="refactored",
            description="Test configuration",
            is_refactored=True
        )
    
    @patch('arb.portal.utils.unified_upload_pipeline.get_core_logic_function')
    def test_successful_upload(self, mock_get_func):
        """Test successful upload processing."""
        # Mock the core logic function to return success
        mock_core_func = Mock()
        mock_core_func.return_value = UploadLogicResult(
            success=True,
            status_code=200,
            flash_messages=["Upload successful"],
            redirect_url="/incidence_update/123",
            validation_errors=None,
            processed_data={"id_incidence": 123, "sector": "test_sector"}
        )
        mock_get_func.return_value = mock_core_func
        
        result = process_upload_unified(
            self.mock_db, self.upload_folder, self.mock_request_file, self.mock_base, self.config
        )
        
        assert result.success is True
        assert result.status_code == 200
        assert result.redirect_url == "/incidence_update/123"
        assert result.processed_data["id_incidence"] == 123
        assert result.processed_data["sector"] == "test_sector"
        
        # Verify the core logic function was called correctly
        mock_core_func.assert_called_once_with(
            self.mock_db, self.upload_folder, self.mock_request_file, self.mock_base
        )
    
    @patch('arb.portal.utils.unified_upload_pipeline.get_core_logic_function')
    def test_failed_upload(self, mock_get_func):
        """Test failed upload processing."""
        # Mock the core logic function to return failure
        mock_core_func = Mock()
        mock_core_func.return_value = UploadLogicResult(
            success=False,
            status_code=400,
            flash_messages=["Upload failed"],
            redirect_url=None,
            validation_errors={"missing_id": "Missing ID"},
            processed_data=None,
            error_message="Missing valid ID",
            error_type="missing_id"
        )
        mock_get_func.return_value = mock_core_func
        
        result = process_upload_unified(
            self.mock_db, self.upload_folder, self.mock_request_file, self.mock_base, self.config
        )
        
        assert result.success is False
        assert result.status_code == 400
        assert result.error_type == "missing_id"
        assert result.error_message == "Missing valid ID"
    
    @patch('arb.portal.utils.unified_upload_pipeline.get_core_logic_function')
    def test_exception_handling(self, mock_get_func):
        """Test exception handling in unified processing."""
        # Mock the core logic function to raise an exception
        mock_core_func = Mock()
        mock_core_func.side_effect = Exception("Test error")
        mock_get_func.return_value = mock_core_func
        
        result = process_upload_unified(
            self.mock_db, self.upload_folder, self.mock_request_file, self.mock_base, self.config
        )
        
        assert result.success is False
        assert result.status_code == 500
        assert result.error_type == "processing_error"
        assert "Test error" in result.error_message
    
    def test_logging(self):
        """Test that logging is performed correctly."""
        with patch('arb.portal.utils.unified_upload_pipeline.logger') as mock_logger:
            with patch('arb.portal.utils.unified_upload_pipeline.get_core_logic_function') as mock_get_func:
                # Mock successful result
                mock_core_func = Mock()
                mock_core_func.return_value = UploadLogicResult(
                    success=True,
                    status_code=200,
                    flash_messages=["Success"],
                    redirect_url="/success",
                    validation_errors=None,
                    processed_data={"id_incidence": 123}
                )
                mock_get_func.return_value = mock_core_func
                
                process_upload_unified(
                    self.mock_db, self.upload_folder, self.mock_request_file, self.mock_base, self.config
                )
                
                # Verify logging calls - check that info was called at least once
                mock_logger.info.assert_called()
                # The first call should be the processing start message
                first_call_args = mock_logger.info.call_args_list[0][0]
                assert "Unified upload processing for direct upload using refactored logic" in first_call_args[0]


class TestStandardConfigurations:
    """Test the standard configuration functions."""
    
    def test_get_standard_configurations(self):
        """Test getting standard configurations."""
        configs = get_standard_configurations()
        
        # Verify all expected configurations exist
        assert "direct_original" in configs
        assert "direct_refactored" in configs
        assert "staged_original" in configs
        assert "staged_refactored" in configs
        
        # Verify direct_original configuration
        direct_original = configs["direct_original"]
        assert direct_original.upload_type == "direct"
        assert direct_original.template_name == "upload.html"
        assert direct_original.core_logic_function == "original"
        assert direct_original.is_refactored is False
        
        # Verify staged_refactored configuration
        staged_refactored = configs["staged_refactored"]
        assert staged_refactored.upload_type == "staged"
        assert staged_refactored.template_name == "upload_staged.html"
        assert staged_refactored.core_logic_function == "refactored"
        assert staged_refactored.is_refactored is True
    
    def test_create_custom_configuration(self):
        """Test creating custom configurations."""
        config = create_custom_configuration(
            upload_type="direct",
            template_name="custom_upload.html",
            core_logic_function="refactored",
            description="Custom direct upload",
            is_refactored=True
        )
        
        assert config.upload_type == "direct"
        assert config.template_name == "custom_upload.html"
        assert config.core_logic_function == "refactored"
        assert config.description == "Custom direct upload"
        assert config.is_refactored is True


class TestConfigurationValidation:
    """Test configuration validation functions."""
    
    def test_valid_configuration(self):
        """Test validation of valid configuration."""
        config = UnifiedUploadConfig(
            upload_type="direct",
            template_name="upload.html",
            core_logic_function="refactored",
            description="Valid config",
            is_refactored=True
        )
        
        is_valid, error_message = validate_configuration(config)
        assert is_valid is True
        assert error_message is None
    
    def test_invalid_configuration(self):
        """Test validation of invalid configuration."""
        # Create a mock config that will fail validation
        config = Mock()
        config.template_name = ""
        config.description = ""
        
        # Mock the get_core_logic_function to raise an error
        with patch('arb.portal.utils.unified_upload_pipeline.get_core_logic_function') as mock_get_func:
            mock_get_func.side_effect = ValueError("Invalid config")
            
            is_valid, error_message = validate_configuration(config)
            assert is_valid is False
            assert "Configuration validation error" in error_message
    
    def test_get_configuration_summary(self):
        """Test getting configuration summary."""
        summary = get_configuration_summary()
        
        # Verify summary contains all configurations
        assert "direct_original" in summary
        assert "direct_refactored" in summary
        assert "staged_original" in summary
        assert "staged_refactored" in summary
        
        # Verify summary format
        assert "Available Unified Upload Configurations:" in summary
        assert "Upload Type:" in summary
        assert "Template:" in summary
        assert "Logic:" in summary
        assert "Refactored:" in summary
        assert "Description:" in summary


class TestIntegration:
    """Integration tests for the unified processing pipeline."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db = Mock()
        self.mock_base = Mock()
        self.mock_request_file = Mock(spec=FileStorage)
        self.mock_request_file.filename = "test_file.xlsx"
        self.upload_folder = Path("/tmp/test_upload")
    
    def test_direct_upload_workflow(self):
        """Test complete direct upload workflow."""
        config = UnifiedUploadConfig(
            upload_type="direct",
            template_name="upload.html",
            core_logic_function="refactored",
            description="Direct upload test",
            is_refactored=True
        )
        
        # Mock the core logic function
        with patch('arb.portal.utils.unified_upload_pipeline.get_core_logic_function') as mock_get_func:
            mock_core_func = Mock()
            mock_core_func.return_value = UploadLogicResult(
                success=True,
                status_code=200,
                flash_messages=["Success"],
                redirect_url="/incidence_update/456",
                validation_errors=None,
                processed_data={"id_incidence": 456, "sector": "test_sector"}
            )
            mock_get_func.return_value = mock_core_func
            
            result = process_upload_unified(
                self.mock_db, self.upload_folder, self.mock_request_file, self.mock_base, config
            )
            
            assert result.success is True
            assert result.redirect_url == "/incidence_update/456"
    
    def test_staged_upload_workflow(self):
        """Test complete staged upload workflow."""
        config = UnifiedUploadConfig(
            upload_type="staged",
            template_name="upload_staged.html",
            core_logic_function="refactored",
            description="Staged upload test",
            is_refactored=True
        )
        
        # Mock the core logic function
        with patch('arb.portal.utils.unified_upload_pipeline.get_core_logic_function') as mock_get_func:
            mock_core_func = Mock()
            mock_core_func.return_value = UploadLogicResult(
                success=True,
                status_code=200,
                flash_messages=["Success"],
                redirect_url="/review_staged/789/staged_file.json",
                validation_errors=None,
                processed_data={
                    "id_incidence": 789,
                    "sector": "test_sector",
                    "staged_filename": "staged_file.json"
                }
            )
            mock_get_func.return_value = mock_core_func
            
            result = process_upload_unified(
                self.mock_db, self.upload_folder, self.mock_request_file, self.mock_base, config
            )
            
            assert result.success is True
            assert result.redirect_url == "/review_staged/789/staged_file.json"
            assert result.processed_data["staged_filename"] == "staged_file.json"
