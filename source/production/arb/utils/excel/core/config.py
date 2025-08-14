"""
Configuration classes for Excel processing behavior.

This module defines configuration dataclasses that control the behavior of
Excel processing functions. These configurations allow users to customize
validation, processing, error handling, and logging behavior without
modifying the source code.

Classes:
    ExcelParseConfig: Configuration for Excel parsing behavior
    KeyValueExtractConfig: Configuration for key-value extraction
    TabExtractConfig: Configuration for tab extraction

Author: AI Assistant
Created: 2025-01-27
Version: 1.0
"""

from dataclasses import dataclass, field
from typing import Any, Tuple


@dataclass
class ExcelParseConfig:
    """
    Configuration for Excel parsing behavior.
    
    This class provides comprehensive configuration options for the Excel parsing
    process, including file validation, processing behavior, and logging settings.
    
    Attributes:
        validate_file_exists: Whether to validate that the file exists before processing
        validate_file_format: Whether to validate the file has a supported Excel format
        max_file_size_mb: Maximum allowed file size in megabytes
        allowed_extensions: Tuple of allowed file extensions (e.g., '.xlsx', '.xls')
        strict_mode: Whether to use strict validation (fail fast on any error)
        skip_invalid_tabs: Whether to skip tabs that fail validation
        max_tabs: Maximum number of tabs to process
        log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        enable_metrics: Whether to collect and report performance metrics
        detailed_logging: Whether to enable detailed logging for debugging
        
    Example:
        config = ExcelParseConfig(
            max_file_size_mb=50,
            strict_mode=True,
            log_level='DEBUG'
        )
    """
    
    # File validation settings
    validate_file_exists: bool = True
    validate_file_format: bool = True
    max_file_size_mb: int = 100
    allowed_extensions: Tuple[str, ...] = ('.xlsx', '.xls')
    
    # Processing settings
    strict_mode: bool = False
    skip_invalid_tabs: bool = True
    max_tabs: int = 50
    
    # Logging and debugging
    log_level: str = 'INFO'
    enable_metrics: bool = True
    detailed_logging: bool = False
    
    def __post_init__(self):
        """Validate configuration values after initialization."""
        # Validate log level
        valid_log_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(
                f"Invalid log_level: {self.log_level}. "
                f"Must be one of {valid_log_levels}"
            )
        
        # Validate file size
        if self.max_file_size_mb <= 0:
            raise ValueError(
                f"max_file_size_mb must be positive, got {self.max_file_size_mb}"
            )
        
        # Validate max tabs
        if self.max_tabs <= 0:
            raise ValueError(
                f"max_tabs must be positive, got {self.max_tabs}"
            )
        
        # Validate extensions
        if not self.allowed_extensions:
            raise ValueError("allowed_extensions cannot be empty")
        
        # Convert log level to uppercase for consistency
        self.log_level = self.log_level.upper()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return {
            'validate_file_exists': self.validate_file_exists,
            'validate_file_format': self.validate_file_format,
            'max_file_size_mb': self.max_file_size_mb,
            'allowed_extensions': self.allowed_extensions,
            'strict_mode': self.strict_mode,
            'skip_invalid_tabs': self.skip_invalid_tabs,
            'max_tabs': self.max_tabs,
            'log_level': self.log_level,
            'enable_metrics': self.enable_metrics,
            'detailed_logging': self.detailed_logging
        }
    
    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> 'ExcelParseConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)
    
    def get_validation_summary(self) -> str:
        """Get a human-readable summary of validation settings."""
        return (
            f"File validation: {'enabled' if self.validate_file_exists else 'disabled'}, "
            f"Format validation: {'enabled' if self.validate_file_format else 'disabled'}, "
            f"Max file size: {self.max_file_size_mb}MB, "
            f"Strict mode: {'enabled' if self.strict_mode else 'disabled'}"
        )


@dataclass
class KeyValueExtractConfig:
    """
    Configuration for key-value extraction behavior.
    
    This class provides configuration options for extracting key-value pairs
    from Excel worksheets, including limits, validation settings, and
    error handling behavior.
    
    Attributes:
        max_rows: Maximum number of rows to process during extraction
        max_columns: Maximum number of columns to process (A-Z = 26)
        validate_cell_references: Whether to validate cell references
        skip_empty_keys: Whether to skip rows with empty key values
        trim_whitespace: Whether to trim whitespace from extracted values
        stop_on_first_error: Whether to stop processing on the first error
        log_validation_warnings: Whether to log validation warnings
        
    Example:
        config = KeyValueExtractConfig(
            max_rows=500,
            validate_cell_references=True,
            stop_on_first_error=False
        )
    """
    
    # Extraction limits
    max_rows: int = 1000
    max_columns: int = 26  # A-Z
    
    # Validation settings
    validate_cell_references: bool = True
    skip_empty_keys: bool = True
    trim_whitespace: bool = True
    
    # Error handling
    stop_on_first_error: bool = False
    log_validation_warnings: bool = True
    
    def __post_init__(self):
        """Validate configuration values after initialization."""
        # Validate max rows
        if self.max_rows <= 0:
            raise ValueError(
                f"max_rows must be positive, got {self.max_rows}"
            )
        
        # Validate max columns
        if self.max_columns <= 0 or self.max_columns > 26:
            raise ValueError(
                f"max_columns must be between 1 and 26, got {self.max_columns}"
            )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return {
            'max_rows': self.max_rows,
            'max_columns': self.max_columns,
            'validate_cell_references': self.validate_cell_references,
            'skip_empty_keys': self.skip_empty_keys,
            'trim_whitespace': self.trim_whitespace,
            'stop_on_first_error': self.stop_on_first_error,
            'log_validation_warnings': self.log_validation_warnings
        }
    
    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> 'KeyValueExtractConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)
    
    def get_extraction_summary(self) -> str:
        """Get a human-readable summary of extraction settings."""
        return (
            f"Max rows: {self.max_rows}, "
            f"Max columns: {self.max_columns}, "
            f"Cell validation: {'enabled' if self.validate_cell_references else 'disabled'}, "
            f"Stop on error: {'enabled' if self.stop_on_first_error else 'disabled'}"
        )


@dataclass
class TabExtractConfig:
    """
    Configuration for tab extraction behavior.
    
    This class provides configuration options for extracting data from
    individual Excel tabs, including schema validation, data processing,
    and performance settings.
    
    Attributes:
        validate_schemas: Whether to validate schemas before processing
        skip_invalid_tabs: Whether to skip tabs that fail validation
        max_field_count: Maximum number of fields to process per tab
        type_conversion_strict: Whether to use strict type conversion
        trim_strings: Whether to trim whitespace from string values
        handle_missing_values: How to handle missing values ('skip', 'null', 'error')
        batch_size: Number of rows to process in each batch
        enable_parallel_processing: Whether to enable parallel processing
        
    Example:
        config = TabExtractConfig(
            validate_schemas=True,
            type_conversion_strict=False,
            handle_missing_values='null'
        )
    """
    
    # Schema validation
    validate_schemas: bool = True
    skip_invalid_tabs: bool = True
    max_field_count: int = 1000
    
    # Data processing
    type_conversion_strict: bool = False
    trim_strings: bool = True
    handle_missing_values: str = 'skip'  # 'skip', 'null', 'error'
    
    # Performance
    batch_size: int = 100
    enable_parallel_processing: bool = False
    
    def __post_init__(self):
        """Validate configuration values after initialization."""
        # Validate max field count
        if self.max_field_count <= 0:
            raise ValueError(
                f"max_field_count must be positive, got {self.max_field_count}"
            )
        
        # Validate batch size
        if self.batch_size <= 0:
            raise ValueError(
                f"batch_size must be positive, got {self.batch_size}"
            )
        
        # Validate missing value handling
        valid_missing_handlers = {'skip', 'null', 'error'}
        if self.handle_missing_values not in valid_missing_handlers:
            raise ValueError(
                f"handle_missing_values must be one of {valid_missing_handlers}, "
                f"got {self.handle_missing_values}"
            )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return {
            'validate_schemas': self.validate_schemas,
            'skip_invalid_tabs': self.skip_invalid_tabs,
            'max_field_count': self.max_field_count,
            'type_conversion_strict': self.type_conversion_strict,
            'trim_strings': self.trim_strings,
            'handle_missing_values': self.handle_missing_values,
            'batch_size': self.batch_size,
            'enable_parallel_processing': self.enable_parallel_processing
        }
    
    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> 'TabExtractConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)
    
    def get_processing_summary(self) -> str:
        """Get a human-readable summary of processing settings."""
        return (
            f"Schema validation: {'enabled' if self.validate_schemas else 'disabled'}, "
            f"Type conversion: {'strict' if self.type_conversion_strict else 'lenient'}, "
            f"Missing values: {self.handle_missing_values}, "
            f"Batch size: {self.batch_size}"
        )


# Default configurations for common use cases
DEFAULT_EXCEL_PARSE_CONFIG = ExcelParseConfig()
DEFAULT_KEY_VALUE_EXTRACT_CONFIG = KeyValueExtractConfig()
DEFAULT_TAB_EXTRACT_CONFIG = TabExtractConfig()

# Strict configurations for high-quality requirements
STRICT_EXCEL_PARSE_CONFIG = ExcelParseConfig(
    strict_mode=True,
    detailed_logging=True,
    log_level='DEBUG'
)

STRICT_KEY_VALUE_EXTRACT_CONFIG = KeyValueExtractConfig(
    validate_cell_references=True,
    stop_on_first_error=True,
    log_validation_warnings=True
)

STRICT_TAB_EXTRACT_CONFIG = TabExtractConfig(
    validate_schemas=True,
    type_conversion_strict=True,
    handle_missing_values='error'
)

# Performance configurations for large files
PERFORMANCE_EXCEL_PARSE_CONFIG = ExcelParseConfig(
    max_file_size_mb=500,
    max_tabs=100,
    enable_metrics=True,
    detailed_logging=False
)

PERFORMANCE_TAB_EXTRACT_CONFIG = TabExtractConfig(
    batch_size=500,
    enable_parallel_processing=True,
    validate_schemas=False  # Skip validation for performance
)
