"""
Core module for Excel processing configuration and data structures.

This module contains the foundational classes and data structures used throughout
the enhanced Excel processing system, including configuration classes, result
classes, and custom exceptions.

Classes:
    ExcelParseConfig: Configuration for Excel parsing behavior
    KeyValueExtractConfig: Configuration for key-value extraction
    TabExtractConfig: Configuration for tab extraction
    ExcelParseResult: Structured result from Excel parsing
    ValidationResult: Result of a validation check
    ProcessingStats: Processing performance and statistics
    ExcelProcessingError: Base exception for Excel processing errors
    ValidationError: Raised when validation fails
    ProcessingError: Raised when data processing fails
    SchemaError: Raised when schema-related errors occur

Author: AI Assistant
Created: 2025-01-27
Version: 1.0
"""

from .config import (
    ExcelParseConfig,
    KeyValueExtractConfig,
    TabExtractConfig
)

from .models import (
    ExcelParseResult,
    ValidationResult,
    ProcessingStats
)

from .exceptions import (
    ExcelProcessingError,
    ValidationError,
    ProcessingError,
    SchemaError,
    FileError,
    ConfigurationError,
    DataError,
    ErrorCodes
)

__all__ = [
    # Configuration classes
    'ExcelParseConfig',
    'KeyValueExtractConfig', 
    'TabExtractConfig',
    
    # Result classes
    'ExcelParseResult',
    'ValidationResult',
    'ProcessingStats',
    
    # Exception classes
    'ExcelProcessingError',
    'ValidationError',
    'ProcessingError',
    'SchemaError',
    'FileError',
    'ConfigurationError',
    'DataError',
    'ErrorCodes'
]

__version__ = "1.0.0"
__author__ = "AI Assistant"
__created__ = "2025-01-27"
