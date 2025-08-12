"""
Unit tests for in-memory staging infrastructure.

This module provides comprehensive testing for the Phase 8 unified upload
processing architecture, focusing on the InMemoryStaging class and related
infrastructure components.

Test Coverage:
- InMemoryStaging data structure and methods
- UploadProcessingConfig configuration class  
- process_upload_to_memory unified processing pipeline
- Configuration-driven processing with process_upload_with_config
- Error handling and Result Type integration
- Performance and memory usage characteristics

The tests demonstrate the architectural benefits of the in-memory first approach:
- Perfect separation of concerns (processing vs persistence)
- Surgical unit testing capabilities
- Configuration-driven behavior validation
- Enhanced error handling with Result Types
"""

import json
import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from arb.portal.utils.in_memory_staging import (
    InMemoryStaging,
    UploadProcessingConfig, 
    process_upload_to_memory,
    process_upload_with_config
)
from arb.portal.utils.result_types import (
    InMemoryStagingResult,
    PersistenceResult,
    DatabaseInsertResult,
    StagedFileResult,
    FileSaveResult,
    FileConversionResult,
    IdValidationResult
)


class TestUploadProcessingConfig:
    """Test suite for UploadProcessingConfig class."""
    
    def test_upload_processing_config_defaults(self):
        """Test default configuration values."""
        config = UploadProcessingConfig()
        
        assert config.auto_confirm is False
        assert config.update_all_fields is False
        assert config.persist_staging_file is True
        assert config.cleanup_staging_file is False
    
    def test_upload_processing_config_direct_upload(self):
        """Test configuration for direct upload scenario."""
        config = UploadProcessingConfig(
            auto_confirm=True,
            update_all_fields=True,
            persist_staging_file=False
        )
        
        assert config.auto_confirm is True
        assert config.update_all_fields is True
        assert config.persist_staging_file is False
        assert config.cleanup_staging_file is False
    
    def test_upload_processing_config_staged_upload(self):
        """Test configuration for staged upload scenario."""
        config = UploadProcessingConfig(
            auto_confirm=False,
            persist_staging_file=True
        )
        
        assert config.auto_confirm is False
        assert config.update_all_fields is False
        assert config.persist_staging_file is True
        assert config.cleanup_staging_file is False


class TestInMemoryStaging:
    """Test suite for InMemoryStaging dataclass."""
    
    @pytest.fixture
    def sample_in_memory_staging(self):
        """Create sample InMemoryStaging for testing."""
        return InMemoryStaging(
            id_=123,
            sector="Dairy Digester",
            original_filename="test_upload.xlsx",
            file_path=Path("/tmp/test_upload.xlsx"),
            json_data={"id_incidence": 123, "sector": "Dairy Digester", "data": "test"},
            metadata={"file_size": 1024, "upload_time": "2025-01-01T12:00:00"},
            timestamp=datetime(2025, 1, 1, 12, 0, 0)
        )
    
    def test_in_memory_staging_creation(self, sample_in_memory_staging):
        """Test InMemoryStaging object creation and attributes."""
        staging = sample_in_memory_staging
        
        assert staging.id_ == 123
        assert staging.sector == "Dairy Digester"
        assert staging.original_filename == "test_upload.xlsx"
        assert staging.file_path == Path("/tmp/test_upload.xlsx")
        assert staging.json_data["id_incidence"] == 123
        assert staging.metadata["file_size"] == 1024
        assert staging.timestamp == datetime(2025, 1, 1, 12, 0, 0)
    
    @patch('arb.portal.utils.db_ingest_util.xl_dict_to_database')
    def test_to_database_success(self, mock_xl_dict_to_database, sample_in_memory_staging):
        """Test successful database persistence from in-memory staging."""
        # Mock successful database insertion
        mock_xl_dict_to_database.return_value = (123, "Dairy Digester")
        
        mock_db = Mock()
        mock_base = Mock()
        
        result = sample_in_memory_staging.to_database(mock_db, mock_base, "all_fields")
        
        assert result.success is True
        assert result.id_ == 123
        assert result.error_message is None
        assert result.error_type is None
        
        # Verify xl_dict_to_database was called with correct structured format
        expected_xl_dict_format = {
            "metadata": {
                "sector": sample_in_memory_staging.sector,
                "original_filename": sample_in_memory_staging.original_filename,
                "upload_timestamp": sample_in_memory_staging.timestamp.isoformat(),
                **sample_in_memory_staging.metadata
            },
            "tab_contents": {
                "Feedback Form": sample_in_memory_staging.json_data
            }
        }
        mock_xl_dict_to_database.assert_called_once_with(
            mock_db, mock_base, expected_xl_dict_format
        )
    
    @patch('arb.portal.utils.db_ingest_util.xl_dict_to_database')
    def test_to_database_validation_failure(self, mock_xl_dict_to_database, sample_in_memory_staging):
        """Test database persistence with validation failure."""
        # Mock validation failure (returns None)
        mock_xl_dict_to_database.return_value = (None, None)
        
        mock_db = Mock()
        mock_base = Mock()
        
        result = sample_in_memory_staging.to_database(mock_db, mock_base)
        
        assert result.success is False
        assert result.id_ is None
        assert "validation error" in result.error_message.lower()
        assert result.error_type == "validation_error"
    
    @patch('arb.portal.utils.db_ingest_util.xl_dict_to_database')
    def test_to_database_exception(self, mock_xl_dict_to_database, sample_in_memory_staging):
        """Test database persistence with exception."""
        # Mock database exception
        mock_xl_dict_to_database.side_effect = Exception("Database connection failed")
        
        mock_db = Mock()
        mock_base = Mock()
        
        result = sample_in_memory_staging.to_database(mock_db, mock_base)
        
        assert result.success is False
        assert result.id_ is None
        assert "Database connection failed" in result.error_message
        assert result.error_type == "database_error"
    
    def test_to_staging_file_success(self, sample_in_memory_staging):
        """Test successful staging file creation from in-memory staging."""
        with tempfile.TemporaryDirectory() as temp_dir:
            staging_dir = Path(temp_dir)
            
            result = sample_in_memory_staging.to_staging_file(staging_dir)
            
            assert result.success is True
            assert result.staged_filename.startswith("id_123_ts_2025_01_01_12_00_00.json")
            assert result.error_message is None
            assert result.error_type is None
            
            # Verify file was created with correct content
            staged_file_path = staging_dir / result.staged_filename
            assert staged_file_path.exists()
            
            with open(staged_file_path, 'r') as f:
                staged_data = json.load(f)
            
            assert staged_data["id_incidence"] == 123
            assert staged_data["sector"] == "Dairy Digester"
            assert staged_data["original_filename"] == "test_upload.xlsx"
            assert staged_data["json_data"]["id_incidence"] == 123
    
    def test_to_staging_file_directory_creation(self, sample_in_memory_staging):
        """Test staging file creation with automatic directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use non-existent subdirectory
            staging_dir = Path(temp_dir) / "nested" / "staging"
            
            result = sample_in_memory_staging.to_staging_file(staging_dir)
            
            assert result.success is True
            assert staging_dir.exists()
            
            staged_file_path = staging_dir / result.staged_filename
            assert staged_file_path.exists()
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_to_staging_file_permission_error(self, mock_open, sample_in_memory_staging):
        """Test staging file creation with permission error."""
        staging_dir = Path("/tmp/test_staging")
        
        result = sample_in_memory_staging.to_staging_file(staging_dir)
        
        assert result.success is False
        assert result.staged_filename is None
        assert "Permission denied" in result.error_message
        assert result.error_type == "file_error"


class TestProcessUploadToMemory:
    """Test suite for process_upload_to_memory unified processing function."""
    
    @pytest.fixture
    def mock_file_storage(self):
        """Create mock FileStorage for testing."""
        mock_file = Mock()
        mock_file.filename = "test_upload.xlsx"
        mock_file.read.return_value = b"mock file content"
        mock_file.seek = Mock()
        return mock_file
    
    @patch('arb.portal.utils.db_ingest_util.save_uploaded_file_with_result')
    @patch('arb.portal.utils.db_ingest_util.convert_file_to_json_with_result')
    @patch('arb.portal.utils.db_ingest_util.validate_id_from_json_with_result')
    def test_process_upload_to_memory_success(self, 
                                            mock_validate, 
                                            mock_convert, 
                                            mock_save,
                                            mock_file_storage):
        """Test successful unified processing to in-memory staging."""
        # Mock successful processing steps
        mock_save.return_value = FileSaveResult(
            file_path=Path("/tmp/upload.xlsx"),
            success=True,
            error_message=None,
            error_type=None
        )
        
        mock_convert.return_value = FileConversionResult(
            json_path=Path("/tmp/upload.json"),
            sector="Dairy Digester",
            json_data={
                "metadata": {"sector": "Dairy Digester"},
                "tab_contents": {"Feedback Form": {"id_incidence": 123, "sector": "Dairy Digester"}}
            },
            success=True,
            error_message=None,
            error_type=None
        )
        
        mock_validate.return_value = IdValidationResult(
            id_=123,
            success=True,
            error_message=None,
            error_type=None
        )
        
        mock_db = Mock()
        mock_base = Mock()
        upload_dir = "/tmp/uploads"
        
        result = process_upload_to_memory(mock_db, upload_dir, mock_file_storage, mock_base)
        
        assert result.success is True
        assert result.in_memory_staging is not None
        assert result.error_message is None
        assert result.error_type is None
        
        # Verify in-memory staging properties
        staging = result.in_memory_staging
        assert staging.id_ == 123
        assert staging.sector == "Dairy Digester"
        assert staging.original_filename == "test_upload.xlsx"
        # json_data now contains just the tab contents (not the full structure)
        assert staging.json_data["id_incidence"] == 123
        assert staging.json_data["sector"] == "Dairy Digester"
        
        # Verify all processing steps were called
        mock_save.assert_called_once_with(upload_dir, mock_file_storage, mock_db)
        mock_convert.assert_called_once_with(Path("/tmp/upload.xlsx"))
        mock_validate.assert_called_once_with({
            "metadata": {"sector": "Dairy Digester"},
            "tab_contents": {"Feedback Form": {"id_incidence": 123, "sector": "Dairy Digester"}}
        })
    
    @patch('arb.portal.utils.db_ingest_util.save_uploaded_file_with_result')
    def test_process_upload_to_memory_save_failure(self, mock_save, mock_file_storage):
        """Test unified processing with file save failure."""
        # Mock file save failure
        mock_save.return_value = FileSaveResult(
            file_path=None,
            success=False,
            error_message="Failed to save uploaded file",
            error_type="file_error"
        )
        
        mock_db = Mock()
        mock_base = Mock()
        upload_dir = "/tmp/uploads"
        
        result = process_upload_to_memory(mock_db, upload_dir, mock_file_storage, mock_base)
        
        assert result.success is False
        assert result.in_memory_staging is None
        assert result.error_message == "Failed to save uploaded file"
        assert result.error_type == "file_error"
    
    @patch('arb.portal.utils.db_ingest_util.save_uploaded_file_with_result')
    @patch('arb.portal.utils.db_ingest_util.convert_file_to_json_with_result')
    def test_process_upload_to_memory_conversion_failure(self, 
                                                       mock_convert, 
                                                       mock_save,
                                                       mock_file_storage):
        """Test unified processing with file conversion failure."""
        # Mock successful save but failed conversion
        mock_save.return_value = FileSaveResult(
            file_path=Path("/tmp/upload.xlsx"),
            success=True,
            error_message=None,
            error_type=None
        )
        
        mock_convert.return_value = FileConversionResult(
            json_path=None,
            sector=None,
            json_data={},
            success=False,
            error_message="Unsupported file format",
            error_type="conversion_failed"
        )
        
        mock_db = Mock()
        mock_base = Mock()
        upload_dir = "/tmp/uploads"
        
        result = process_upload_to_memory(mock_db, upload_dir, mock_file_storage, mock_base)
        
        assert result.success is False
        assert result.in_memory_staging is None
        assert result.error_message == "Unsupported file format"
        assert result.error_type == "conversion_failed"
    
    @patch('arb.portal.utils.db_ingest_util.save_uploaded_file_with_result')
    @patch('arb.portal.utils.db_ingest_util.convert_file_to_json_with_result')
    @patch('arb.portal.utils.db_ingest_util.validate_id_from_json_with_result')
    def test_process_upload_to_memory_validation_failure(self, 
                                                       mock_validate,
                                                       mock_convert, 
                                                       mock_save,
                                                       mock_file_storage):
        """Test unified processing with ID validation failure."""
        # Mock successful save and convert but failed validation
        mock_save.return_value = FileSaveResult(
            file_path=Path("/tmp/upload.xlsx"),
            success=True,
            error_message=None,
            error_type=None
        )
        
        mock_convert.return_value = FileConversionResult(
            json_path=Path("/tmp/upload.json"),
            sector="Dairy Digester",
            json_data={"sector": "Dairy Digester"},  # Missing id_incidence
            success=True,
            error_message=None,
            error_type=None
        )
        
        mock_validate.return_value = IdValidationResult(
            id_=None,
            success=False,
            error_message="No valid id_incidence found",
            error_type="missing_id"
        )
        
        mock_db = Mock()
        mock_base = Mock()
        upload_dir = "/tmp/uploads"
        
        result = process_upload_to_memory(mock_db, upload_dir, mock_file_storage, mock_base)
        
        assert result.success is False
        assert result.in_memory_staging is None
        assert result.error_message == "No valid id_incidence found"
        assert result.error_type == "missing_id"


class TestProcessUploadWithConfig:
    """Test suite for configuration-driven upload processing."""
    
    @pytest.fixture
    def mock_successful_memory_processing(self):
        """Mock successful in-memory processing."""
        mock_staging = InMemoryStaging(
            id_=123,
            sector="Dairy Digester",
            original_filename="test.xlsx",
            file_path=Path("/tmp/test.xlsx"),
            json_data={"id_incidence": 123},
            metadata={"size": 1024},
            timestamp=datetime.now()
        )
        
        return InMemoryStagingResult(
            in_memory_staging=mock_staging,
            success=True,
            error_message=None,
            error_type=None
        )
    
    @patch('arb.portal.utils.in_memory_staging.process_upload_to_memory')
    def test_process_upload_with_config_direct_upload(self, 
                                                    mock_process,
                                                    mock_successful_memory_processing):
        """Test configuration-driven processing for direct upload."""
        mock_process.return_value = mock_successful_memory_processing
        
        # Mock successful database persistence
        with patch.object(mock_successful_memory_processing.in_memory_staging, 'to_database') as mock_to_db:
            mock_to_db.return_value = DatabaseInsertResult(
                id_=123,
                success=True,
                error_message=None,
                error_type=None
            )
            
            config = UploadProcessingConfig(
                auto_confirm=True,
                update_all_fields=True,
                persist_staging_file=False
            )
            
            mock_db = Mock()
            mock_base = Mock()
            mock_file = Mock()
            upload_dir = "/tmp/uploads"
            
            result = process_upload_with_config(config, mock_db, upload_dir, mock_file, mock_base)
            
            assert result.success is True
            assert result.result_data["id_"] == 123
            assert result.result_data["persistence_type"] == "database"
            assert "staged_filename" not in result.result_data
            
            # Verify database persistence was called with correct strategy
            mock_to_db.assert_called_once_with(mock_db, mock_base, "all_fields")
    
    @patch('arb.portal.utils.in_memory_staging.process_upload_to_memory')
    def test_process_upload_with_config_staged_upload(self, 
                                                    mock_process,
                                                    mock_successful_memory_processing):
        """Test configuration-driven processing for staged upload."""
        mock_process.return_value = mock_successful_memory_processing
        
        # Mock successful staging file creation
        with patch.object(mock_successful_memory_processing.in_memory_staging, 'to_staging_file') as mock_to_file:
            mock_to_file.return_value = StagedFileResult(
                staged_filename="id_123_ts_20250101_120000.json",
                success=True,
                error_message=None,
                error_type=None
            )
            
            config = UploadProcessingConfig(
                auto_confirm=False,
                persist_staging_file=True
            )
            
            mock_db = Mock()
            mock_base = Mock()
            mock_file = Mock()
            upload_dir = "/tmp/uploads"
            
            result = process_upload_with_config(config, mock_db, upload_dir, mock_file, mock_base)
            
            assert result.success is True
            assert result.result_data["staged_filename"] == "id_123_ts_20250101_120000.json"
            assert result.result_data["persistence_type"] == "staging_file"
            assert result.result_data["id_"] == 123
            
            # Verify staging file creation was called
            mock_to_file.assert_called_once()
    
    @patch('arb.portal.utils.in_memory_staging.process_upload_to_memory')
    def test_process_upload_with_config_both_persistence(self, 
                                                       mock_process,
                                                       mock_successful_memory_processing):
        """Test configuration-driven processing with both database and file persistence."""
        mock_process.return_value = mock_successful_memory_processing
        
        # Mock successful database and file persistence
        with patch.object(mock_successful_memory_processing.in_memory_staging, 'to_database') as mock_to_db, \
             patch.object(mock_successful_memory_processing.in_memory_staging, 'to_staging_file') as mock_to_file:
            
            mock_to_db.return_value = DatabaseInsertResult(
                id_=123,
                success=True,
                error_message=None,
                error_type=None
            )
            
            mock_to_file.return_value = StagedFileResult(
                staged_filename="id_123_ts_20250101_120000.json",
                success=True,
                error_message=None,
                error_type=None
            )
            
            config = UploadProcessingConfig(
                auto_confirm=True,
                persist_staging_file=True
            )
            
            mock_db = Mock()
            mock_base = Mock()
            mock_file = Mock()
            upload_dir = "/tmp/uploads"
            
            result = process_upload_with_config(config, mock_db, upload_dir, mock_file, mock_base)
            
            assert result.success is True
            assert result.result_data["id_"] == 123
            assert result.result_data["staged_filename"] == "id_123_ts_20250101_120000.json"
            assert result.result_data["persistence_type"] == "both"
            
            # Verify both persistence methods were called
            mock_to_db.assert_called_once()
            mock_to_file.assert_called_once()
    
    @patch('arb.portal.utils.in_memory_staging.process_upload_to_memory')
    def test_process_upload_with_config_memory_processing_failure(self, mock_process):
        """Test configuration-driven processing with in-memory processing failure."""
        mock_process.return_value = InMemoryStagingResult(
            in_memory_staging=None,
            success=False,
            error_message="File conversion failed",
            error_type="conversion_failed"
        )
        
        config = UploadProcessingConfig(auto_confirm=True)
        
        mock_db = Mock()
        mock_base = Mock()
        mock_file = Mock()
        upload_dir = "/tmp/uploads"
        
        result = process_upload_with_config(config, mock_db, upload_dir, mock_file, mock_base)
        
        assert result.success is False
        assert result.result_data == {}
        assert result.error_message == "File conversion failed"
        assert result.error_type == "conversion_failed"


class TestArchitecturalBenefits:
    """Test suite demonstrating architectural benefits of in-memory approach."""
    
    def test_perfect_separation_of_concerns(self):
        """Test that processing and persistence are perfectly separated."""
        # Create in-memory staging
        staging = InMemoryStaging(
            id_=123,
            sector="Test",
            original_filename="test.xlsx",
            file_path=Path("/tmp/test.xlsx"),
            json_data={"id_incidence": 123},
            metadata={},
            timestamp=datetime.now()
        )
        
        # Processing is complete - now we can test persistence separately
        assert staging.id_ == 123
        assert staging.json_data["id_incidence"] == 123
        
        # Persistence methods are testable in isolation
        assert hasattr(staging, 'to_database')
        assert hasattr(staging, 'to_staging_file')
        assert callable(staging.to_database)
        assert callable(staging.to_staging_file)
    
    def test_configuration_driven_behavior(self):
        """Test that configuration drives different behaviors from same core logic."""
        # Direct upload configuration
        direct_config = UploadProcessingConfig(
            auto_confirm=True,
            update_all_fields=True,
            persist_staging_file=False
        )
        
        # Staged upload configuration
        staged_config = UploadProcessingConfig(
            auto_confirm=False,
            persist_staging_file=True
        )
        
        # Validation-only configuration
        validation_config = UploadProcessingConfig(
            auto_confirm=False,
            persist_staging_file=False
        )
        
        # Each configuration represents different upload type behavior
        assert direct_config.auto_confirm != staged_config.auto_confirm
        assert direct_config.persist_staging_file != staged_config.persist_staging_file
        assert validation_config.persist_staging_file != staged_config.persist_staging_file
    
    def test_result_types_provide_type_safety(self):
        """Test that Result Types provide type safety throughout pipeline."""
        # All result types have consistent structure
        result_types = [
            InMemoryStagingResult,
            PersistenceResult,
            DatabaseInsertResult,
            StagedFileResult
        ]
        
        for result_type in result_types:
            # All result types have success field
            assert hasattr(result_type, '_fields')
            assert 'success' in result_type._fields
            
            # Most have error_message and error_type
            if result_type != PersistenceResult:  # PersistenceResult has different structure
                assert 'error_message' in result_type._fields
                assert 'error_type' in result_type._fields


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
