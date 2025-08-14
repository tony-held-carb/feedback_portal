"""
Test suite for enhanced Excel processing foundation components.

This module tests the foundation components created in Phase 1 of the refactoring,
including configuration classes, data models, and custom exceptions.

Test Classes:
    TestConfigurationClasses: Tests for configuration dataclasses
    TestDataModels: Tests for data model classes
    TestCustomExceptions: Tests for custom exception hierarchy

Author: AI Assistant
Created: 2025-01-27
Version: 1.0
"""

import pytest
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Import the enhanced components
from arb.utils.excel.core import (
    ExcelParseConfig,
    KeyValueExtractConfig,
    TabExtractConfig,
    ExcelParseResult,
    ValidationResult,
    ProcessingStats,
    ExcelProcessingError,
    ValidationError,
    ProcessingError,
    SchemaError,
    FileError,
    ConfigurationError,
    DataError
)


class TestConfigurationClasses:
    """Test configuration classes for Excel processing."""
    
    def test_excel_parse_config_defaults(self):
        """Test ExcelParseConfig with default values."""
        config = ExcelParseConfig()
        
        assert config.validate_file_exists is True
        assert config.validate_file_format is True
        assert config.max_file_size_mb == 100
        assert config.allowed_extensions == ('.xlsx', '.xls')
        assert config.strict_mode is False
        assert config.skip_invalid_tabs is True
        assert config.max_tabs == 50
        assert config.log_level == 'INFO'
        assert config.enable_metrics is True
        assert config.detailed_logging is False
    
    def test_excel_parse_config_custom_values(self):
        """Test ExcelParseConfig with custom values."""
        config = ExcelParseConfig(
            max_file_size_mb=50,
            strict_mode=True,
            log_level='DEBUG',
            detailed_logging=True
        )
        
        assert config.max_file_size_mb == 50
        assert config.strict_mode is True
        assert config.log_level == 'DEBUG'
        assert config.detailed_logging is True
    
    def test_excel_parse_config_validation(self):
        """Test ExcelParseConfig validation."""
        # Test invalid log level
        with pytest.raises(ValueError, match="Invalid log_level"):
            ExcelParseConfig(log_level='INVALID')
        
        # Test invalid file size
        with pytest.raises(ValueError, match="max_file_size_mb must be positive"):
            ExcelParseConfig(max_file_size_mb=0)
        
        # Test invalid max tabs
        with pytest.raises(ValueError, match="max_tabs must be positive"):
            ExcelParseConfig(max_tabs=0)
    
    def test_key_value_extract_config_defaults(self):
        """Test KeyValueExtractConfig with default values."""
        config = KeyValueExtractConfig()
        
        assert config.max_rows == 1000
        assert config.max_columns == 26
        assert config.validate_cell_references is True
        assert config.skip_empty_keys is True
        assert config.trim_whitespace is True
        assert config.stop_on_first_error is False
        assert config.log_validation_warnings is True
    
    def test_key_value_extract_config_validation(self):
        """Test KeyValueExtractConfig validation."""
        # Test invalid max rows
        with pytest.raises(ValueError, match="max_rows must be positive"):
            KeyValueExtractConfig(max_rows=0)
        
        # Test invalid max columns
        with pytest.raises(ValueError, match="max_columns must be between 1 and 26"):
            KeyValueExtractConfig(max_columns=30)
    
    def test_tab_extract_config_defaults(self):
        """Test TabExtractConfig with default values."""
        config = TabExtractConfig()
        
        assert config.validate_schemas is True
        assert config.skip_invalid_tabs is True
        assert config.max_field_count == 1000
        assert config.type_conversion_strict is False
        assert config.trim_strings is True
        assert config.handle_missing_values == 'skip'
        assert config.batch_size == 100
        assert config.enable_parallel_processing is False
    
    def test_tab_extract_config_validation(self):
        """Test TabExtractConfig validation."""
        # Test invalid max field count
        with pytest.raises(ValueError, match="max_field_count must be positive"):
            TabExtractConfig(max_field_count=0)
        
        # Test invalid batch size
        with pytest.raises(ValueError, match="batch_size must be positive"):
            TabExtractConfig(batch_size=0)
        
        # Test invalid missing value handler
        with pytest.raises(ValueError, match="handle_missing_values must be one of"):
            TabExtractConfig(handle_missing_values='invalid')
    
    def test_config_serialization(self):
        """Test configuration serialization to/from dictionaries."""
        config = ExcelParseConfig(
            max_file_size_mb=75,
            strict_mode=True,
            log_level='WARNING'
        )
        
        # Test to_dict
        config_dict = config.to_dict()
        assert config_dict['max_file_size_mb'] == 75
        assert config_dict['strict_mode'] is True
        assert config_dict['log_level'] == 'WARNING'
        
        # Test from_dict
        new_config = ExcelParseConfig.from_dict(config_dict)
        assert new_config.max_file_size_mb == 75
        assert new_config.strict_mode is True
        assert new_config.log_level == 'WARNING'
    
    def test_config_summary_methods(self):
        """Test configuration summary methods."""
        config = ExcelParseConfig(
            max_file_size_mb=50,
            strict_mode=True
        )
        
        summary = config.get_validation_summary()
        assert "File validation: enabled" in summary
        assert "Format validation: enabled" in summary
        assert "Max file size: 50MB" in summary
        assert "Strict mode: enabled" in summary


class TestDataModels:
    """Test data model classes for Excel processing results."""
    
    def test_validation_result_creation(self):
        """Test ValidationResult creation and properties."""
        result = ValidationResult(
            field_name="file_size",
            is_valid=False,
            message="File size exceeds maximum allowed",
            severity="ERROR",
            location="B15"
        )
        
        assert result.field_name == "file_size"
        assert result.is_valid is False
        assert result.message == "File size exceeds maximum allowed"
        assert result.severity == "ERROR"
        assert result.location == "B15"
        assert result.is_error() is True
        assert result.is_warning() is False
        assert result.is_info() is False
    
    def test_validation_result_severity_validation(self):
        """Test ValidationResult severity validation."""
        # Test invalid severity
        with pytest.raises(ValueError, match="Invalid severity"):
            ValidationResult(
                field_name="test",
                is_valid=True,
                message="test",
                severity="INVALID",
                location="A1"
            )
    
    def test_processing_stats_timing(self):
        """Test ProcessingStats timing functionality."""
        stats = ProcessingStats()
        
        # Test timing
        stats.start_timing()
        stats.end_timing()
        
        assert stats.total_time >= 0
        assert stats.start_time > 0
        assert stats.end_time > 0
    
    def test_processing_stats_increment(self):
        """Test ProcessingStats increment methods."""
        stats = ProcessingStats()
        
        stats.increment_processed(rows=10, cells=100, tabs=2, fields=50)
        
        assert stats.rows_processed == 10
        assert stats.cells_processed == 100
        assert stats.tabs_processed == 2
        assert stats.fields_processed == 50
    
    def test_processing_stats_error_recording(self):
        """Test ProcessingStats error recording."""
        stats = ProcessingStats()
        
        stats.record_error('validation')
        stats.record_error('processing')
        stats.record_error('warning')
        
        assert stats.validation_errors == 1
        assert stats.processing_errors == 1
        assert stats.warnings == 1
        assert stats.total_errors == 2
    
    def test_processing_stats_properties(self):
        """Test ProcessingStats computed properties."""
        stats = ProcessingStats()
        stats.start_timing()
        
        # Simulate some processing
        stats.increment_processed(rows=100, cells=1000)
        
        stats.end_timing()
        
        assert stats.total_time >= 0
        assert stats.success_rate == 1.0  # No errors
        assert stats.cells_per_second >= 0
        assert stats.rows_per_second >= 0
    
    def test_excel_parse_result_creation(self):
        """Test ExcelParseResult creation."""
        stats = ProcessingStats()
        validation_results = [
            ValidationResult(
                field_name="test",
                is_valid=True,
                message="test",
                severity="INFO",
                location="A1"
            )
        ]
        
        result = ExcelParseResult(
            success=True,
            metadata={"filename": "test.xlsx"},
            schemas={"schema1": {}},
            tab_contents={"Sheet1": {}},
            validation_results=validation_results,
            processing_stats=stats,
            errors=[],
            warnings=[],
            file_path=Path("test.xlsx"),
            processing_time=1.5
        )
        
        assert result.success is True
        assert result.is_valid() is True
        assert result.file_path == Path("test.xlsx")
        assert result.processing_time == 1.5
        assert len(result.validation_results) == 1
        assert result.get_error_summary() == "No errors"
        assert result.get_warning_summary() == "No warnings"


class TestCustomExceptions:
    """Test custom exception hierarchy for Excel processing."""
    
    def test_excel_processing_error_base(self):
        """Test base ExcelProcessingError functionality."""
        error = ExcelProcessingError(
            message="Test error message",
            error_code="TEST_ERROR",
            context={"key": "value"}
        )
        
        assert error.message == "Test error message"
        assert error.error_code == "TEST_ERROR"
        assert error.context == {"key": "value"}
        assert "TEST_ERROR" in str(error)
        assert "key=value" in str(error)
    
    def test_validation_error(self):
        """Test ValidationError creation and properties."""
        error = ValidationError(
            message="Validation failed",
            error_code="VALIDATION_FAILED",
            field_name="test_field",
            validation_type="size_limit",
            expected_value=100,
            actual_value=150
        )
        
        assert error.field_name == "test_field"
        assert error.validation_type == "size_limit"
        assert error.expected_value == 100
        assert error.actual_value == 150
        assert "VALIDATION_FAILED" in str(error)
    
    def test_processing_error(self):
        """Test ProcessingError creation and properties."""
        error = ProcessingError(
            message="Processing failed",
            error_code="PROCESSING_FAILED",
            processing_step="data_extraction",
            data_location="Sheet1!A1"
        )
        
        assert error.processing_step == "data_extraction"
        assert error.data_location == "Sheet1!A1"
        assert "PROCESSING_FAILED" in str(error)
    
    def test_schema_error(self):
        """Test SchemaError creation and properties."""
        error = SchemaError(
            message="Schema invalid",
            error_code="SCHEMA_INVALID",
            schema_name="test_schema",
            schema_issue="missing_fields"
        )
        
        assert error.schema_name == "test_schema"
        assert error.schema_issue == "missing_fields"
        assert "SCHEMA_INVALID" in str(error)
    
    def test_file_error(self):
        """Test FileError creation and properties."""
        error = FileError(
            message="File not found",
            error_code="FILE_NOT_FOUND",
            file_path="/path/to/file.xlsx",
            operation="read"
        )
        
        assert error.file_path == "/path/to/file.xlsx"
        assert error.operation == "read"
        assert "FILE_NOT_FOUND" in str(error)
    
    def test_configuration_error(self):
        """Test ConfigurationError creation and properties."""
        error = ConfigurationError(
            message="Invalid configuration",
            error_code="CONFIG_INVALID",
            config_key="log_level",
            config_value="INVALID",
            config_issue="invalid_value"
        )
        
        assert error.config_key == "log_level"
        assert error.config_value == "INVALID"
        assert error.config_issue == "invalid_value"
        assert "CONFIG_INVALID" in str(error)
    
    def test_data_error(self):
        """Test DataError creation and properties."""
        error = DataError(
            message="Data invalid",
            error_code="DATA_INVALID",
            data_location="Sheet1!B15",
            data_type="datetime",
            data_value="invalid_date",
            data_issue="format_error"
        )
        
        assert error.data_location == "Sheet1!B15"
        assert error.data_type == "datetime"
        assert error.data_value == "invalid_date"
        assert error.data_issue == "format_error"
        assert "DATA_INVALID" in str(error)
    
    def test_exception_serialization(self):
        """Test exception serialization to dictionaries."""
        error = ValidationError(
            message="Test error",
            error_code="TEST_ERROR",
            field_name="test_field",
            context={"context_key": "context_value"}
        )
        
        error_dict = error.to_dict()
        assert error_dict['error_code'] == "TEST_ERROR"
        assert error_dict['message'] == "Test error"
        assert error_dict['field_name'] == "test_field"
        assert error_dict['context']['context_key'] == "context_value"
        assert error_dict['exception_type'] == "ValidationError"
    
    def test_exception_context_management(self):
        """Test exception context management."""
        error = ExcelProcessingError(
            message="Test error",
            error_code="TEST_ERROR"
        )
        
        # Test adding context
        error.add_context({"additional_key": "additional_value"})
        assert error.context["additional_key"] == "additional_value"
        
        # Test context merging
        error.add_context({"existing_key": "new_value"})
        assert error.context["existing_key"] == "new_value"


class TestIntegration:
    """Test integration between foundation components."""
    
    def test_config_with_validation_result(self):
        """Test configuration with validation results."""
        config = ExcelParseConfig(strict_mode=True)
        validation_result = ValidationResult(
            field_name="file_size",
            is_valid=False,
            message="File too large",
            severity="ERROR",
            location="B15"
        )
        
        # Test that both work together
        assert config.strict_mode is True
        assert validation_result.is_error() is True
        assert validation_result.field_name == "file_size"
    
    def test_processing_stats_with_validation(self):
        """Test processing stats with validation results."""
        stats = ProcessingStats()
        validation_result = ValidationResult(
            field_name="test",
            is_valid=False,
            message="test",
            severity="ERROR",
            location="A1"
        )
        
        # Record validation error
        stats.record_error('validation')
        
        # Test integration
        assert stats.validation_errors == 1
        assert validation_result.is_error() is True
        assert stats.total_errors == 1
    
    def test_exception_with_validation_result(self):
        """Test exception with validation result."""
        validation_result = ValidationResult(
            field_name="file_size",
            is_valid=False,
            message="File too large",
            severity="ERROR",
            location="B15"
        )
        
        error = ValidationError(
            message="File size validation failed",
            error_code="FILE_SIZE_INVALID",
            field_name=validation_result.field_name,
            context={"validation_result": validation_result.to_dict()}
        )
        
        # Test integration
        assert error.field_name == validation_result.field_name
        assert error.context["validation_result"]["field_name"] == "file_size"
        assert error.context["validation_result"]["is_valid"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
