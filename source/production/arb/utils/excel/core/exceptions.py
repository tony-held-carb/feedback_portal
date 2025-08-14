"""
Custom exception classes for Excel processing operations.

This module defines a hierarchy of custom exceptions used throughout
the Excel processing system to provide meaningful error information
and enable proper error handling and reporting.

Classes:
    ExcelProcessingError: Base exception for Excel processing errors
    ValidationError: Raised when validation fails
    ProcessingError: Raised when data processing fails
    SchemaError: Raised when schema-related errors occur
    FileError: Raised when file operations fail
    ConfigurationError: Raised when configuration is invalid
    DataError: Raised when data is malformed or invalid

Author: AI Assistant
Created: 2025-01-27
Version: 1.0
"""

from typing import Any, Dict, Optional


class ExcelProcessingError(Exception):
    """
    Base exception for Excel processing errors.
    
    This is the root exception class for all Excel processing errors.
    It provides a structured way to capture error information including
    error codes, context, and additional metadata.
    
    Attributes:
        message: Human-readable error message
        error_code: Unique error code for categorization
        context: Additional context information for debugging
        original_exception: The original exception that caused this error
        
    Example:
        raise ExcelProcessingError(
            message="Failed to parse Excel file",
            error_code="EXCEL_PARSE_FAILED",
            context={"file_path": "sample.xlsx", "line": 42}
        )
    """
    
    def __init__(self, message: str, error_code: str, 
                 context: Optional[Dict[str, Any]] = None,
                 original_exception: Optional[Exception] = None):
        """
        Initialize the Excel processing error.
        
        Args:
            message: Human-readable error message
            error_code: Unique error code for categorization
            context: Additional context information for debugging
            original_exception: The original exception that caused this error
        """
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.original_exception = original_exception
        
        # Build the full error message
        full_message = f"[{error_code}] {message}"
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            full_message += f" (Context: {context_str})"
        
        super().__init__(full_message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the error to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the error
        """
        return {
            'error_code': self.error_code,
            'message': self.message,
            'context': self.context,
            'exception_type': self.__class__.__name__,
            'original_exception_type': (
                self.original_exception.__class__.__name__ 
                if self.original_exception else None
            ),
            'original_exception_message': (
                str(self.original_exception) 
                if self.original_exception else None
            )
        }
    
    def get_error_summary(self) -> str:
        """
        Get a concise summary of the error.
        
        Returns:
            Concise error summary
        """
        return f"{self.error_code}: {self.message}"
    
    def add_context(self, additional_context: Dict[str, Any]) -> None:
        """
        Add additional context information to the error.
        
        Args:
            additional_context: Additional context to merge
        """
        self.context.update(additional_context)


class ValidationError(ExcelProcessingError):
    """
    Raised when validation fails.
    
    This exception is raised when data validation fails during
    Excel processing operations. It provides specific information
    about what validation failed and why.
    
    Attributes:
        field_name: Name of the field that failed validation
        validation_type: Type of validation that failed
        expected_value: Expected value or format
        actual_value: Actual value that failed validation
        
    Example:
        raise ValidationError(
            message="File size exceeds maximum allowed",
            error_code="FILE_SIZE_TOO_LARGE",
            context={"max_size_mb": 100, "actual_size_mb": 150},
            field_name="file_size",
            validation_type="size_limit"
        )
    """
    
    def __init__(self, message: str, error_code: str,
                 field_name: Optional[str] = None,
                 validation_type: Optional[str] = None,
                 expected_value: Optional[Any] = None,
                 actual_value: Optional[Any] = None,
                 context: Optional[Dict[str, Any]] = None,
                 original_exception: Optional[Exception] = None):
        """
        Initialize the validation error.
        
        Args:
            message: Human-readable error message
            error_code: Unique error code for categorization
            field_name: Name of the field that failed validation
            validation_type: Type of validation that failed
            expected_value: Expected value or format
            actual_value: Actual value that failed validation
            context: Additional context information for debugging
            original_exception: The original exception that caused this error
        """
        # Add validation-specific context
        validation_context = context or {}
        if field_name:
            validation_context['field_name'] = field_name
        if validation_type:
            validation_context['validation_type'] = validation_type
        if expected_value is not None:
            validation_context['expected_value'] = expected_value
        if actual_value is not None:
            validation_context['actual_value'] = actual_value
        
        super().__init__(message, error_code, validation_context, original_exception)
        
        self.field_name = field_name
        self.validation_type = validation_type
        self.expected_value = expected_value
        self.actual_value = actual_value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the validation error to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the validation error
        """
        base_dict = super().to_dict()
        base_dict.update({
            'field_name': self.field_name,
            'validation_type': self.validation_type,
            'expected_value': self.expected_value,
            'actual_value': self.actual_value
        })
        return base_dict


class ProcessingError(ExcelProcessingError):
    """
    Raised when data processing fails.
    
    This exception is raised when data processing operations fail
    during Excel processing. It provides information about what
    processing step failed and the context in which it occurred.
    
    Attributes:
        processing_step: Name of the processing step that failed
        data_location: Location of the data being processed
        processing_context: Additional processing context information
        
    Example:
        raise ProcessingError(
            message="Failed to convert cell value to datetime",
            error_code="TYPE_CONVERSION_FAILED",
            context={"cell_reference": "B15", "value": "invalid_date"},
            processing_step="datetime_conversion",
            data_location="Sheet1!B15"
        )
    """
    
    def __init__(self, message: str, error_code: str,
                 processing_step: Optional[str] = None,
                 data_location: Optional[str] = None,
                 processing_context: Optional[Dict[str, Any]] = None,
                 context: Optional[Dict[str, Any]] = None,
                 original_exception: Optional[Exception] = None):
        """
        Initialize the processing error.
        
        Args:
            message: Human-readable error message
            error_code: Unique error code for categorization
            processing_step: Name of the processing step that failed
            data_location: Location of the data being processed
            processing_context: Additional processing context information
            context: Additional context information for debugging
            original_exception: The original exception that caused this error
        """
        # Merge processing context with general context
        merged_context = context or {}
        if processing_context:
            merged_context.update(processing_context)
        if processing_step:
            merged_context['processing_step'] = processing_step
        if data_location:
            merged_context['data_location'] = data_location
        
        super().__init__(message, error_code, merged_context, original_exception)
        
        self.processing_step = processing_step
        self.data_location = data_location
        self.processing_context = processing_context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the processing error to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the processing error
        """
        base_dict = super().to_dict()
        base_dict.update({
            'processing_step': self.processing_step,
            'data_location': self.data_location,
            'processing_context': self.processing_context
        })
        return base_dict


class SchemaError(ExcelProcessingError):
    """
    Raised when schema-related errors occur.
    
    This exception is raised when there are issues with schema
    definitions, validation, or resolution during Excel processing.
    
    Attributes:
        schema_name: Name of the schema that caused the error
        schema_location: Location of the schema definition
        schema_issue: Description of the specific schema issue
        
    Example:
        raise SchemaError(
            message="Schema definition is missing required fields",
            error_code="SCHEMA_INVALID",
            context={"schema_name": "oil_and_gas_v03"},
            schema_name="oil_and_gas_v03",
            schema_issue="missing_required_fields"
        )
    """
    
    def __init__(self, message: str, error_code: str,
                 schema_name: Optional[str] = None,
                 schema_location: Optional[str] = None,
                 schema_issue: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None,
                 original_exception: Optional[Exception] = None):
        """
        Initialize the schema error.
        
        Args:
            message: Human-readable error message
            error_code: Unique error code for categorization
            schema_name: Name of the schema that caused the error
            schema_location: Location of the schema definition
            schema_issue: Description of the specific schema issue
            context: Additional context information for debugging
            original_exception: The original exception that caused this error
        """
        # Add schema-specific context
        schema_context = context or {}
        if schema_name:
            schema_context['schema_name'] = schema_name
        if schema_location:
            schema_context['schema_location'] = schema_location
        if schema_issue:
            schema_context['schema_issue'] = schema_issue
        
        super().__init__(message, error_code, schema_context, original_exception)
        
        self.schema_name = schema_name
        self.schema_location = schema_location
        self.schema_issue = schema_issue
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the schema error to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the schema error
        """
        base_dict = super().to_dict()
        base_dict.update({
            'schema_name': self.schema_name,
            'schema_location': self.schema_location,
            'schema_issue': self.schema_issue
        })
        return base_dict


class FileError(ExcelProcessingError):
    """
    Raised when file operations fail.
    
    This exception is raised when there are issues with file
    operations such as reading, writing, or accessing Excel files.
    
    Attributes:
        file_path: Path to the file that caused the error
        operation: File operation that failed
        file_context: Additional file context information
        
    Example:
        raise FileError(
            message="File not found",
            error_code="FILE_NOT_FOUND",
            context={"operation": "read"},
            file_path="/path/to/file.xlsx",
            operation="read"
        )
    """
    
    def __init__(self, message: str, error_code: str,
                 file_path: Optional[str] = None,
                 operation: Optional[str] = None,
                 file_context: Optional[Dict[str, Any]] = None,
                 context: Optional[Dict[str, Any]] = None,
                 original_exception: Optional[Exception] = None):
        """
        Initialize the file error.
        
        Args:
            message: Human-readable error message
            error_code: Unique error code for categorization
            file_path: Path to the file that caused the error
            operation: File operation that failed
            file_context: Additional file context information
            context: Additional context information for debugging
            original_exception: The original exception that caused this error
        """
        # Add file-specific context
        file_error_context = context or {}
        if file_context:
            file_error_context.update(file_context)
        if file_path:
            file_error_context['file_path'] = file_path
        if operation:
            file_error_context['operation'] = operation
        
        super().__init__(message, error_code, file_error_context, original_exception)
        
        self.file_path = file_path
        self.operation = operation
        self.file_context = file_context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the file error to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the file error
        """
        base_dict = super().to_dict()
        base_dict.update({
            'file_path': self.file_path,
            'operation': self.operation,
            'file_context': self.file_context
        })
        return base_dict


class ConfigurationError(ExcelProcessingError):
    """
    Raised when configuration is invalid.
    
    This exception is raised when there are issues with configuration
    settings, such as invalid values, missing required settings,
    or configuration conflicts.
    
    Attributes:
        config_key: Configuration key that caused the error
        config_value: Invalid configuration value
        config_issue: Description of the specific configuration issue
        
    Example:
        raise ConfigurationError(
            message="Invalid log level specified",
            error_code="INVALID_LOG_LEVEL",
            context={"allowed_values": ["DEBUG", "INFO", "WARNING"]},
            config_key="log_level",
            config_value="INVALID",
            config_issue="value_not_allowed"
        )
    """
    
    def __init__(self, message: str, error_code: str,
                 config_key: Optional[str] = None,
                 config_value: Optional[Any] = None,
                 config_issue: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None,
                 original_exception: Optional[Exception] = None):
        """
        Initialize the configuration error.
        
        Args:
            message: Human-readable error message
            error_code: Unique error code for categorization
            config_key: Configuration key that caused the error
            config_value: Invalid configuration value
            config_issue: Description of the specific configuration issue
            context: Additional context information for debugging
            original_exception: The original exception that caused this error
        """
        # Add configuration-specific context
        config_context = context or {}
        if config_key:
            config_context['config_key'] = config_key
        if config_value is not None:
            config_context['config_value'] = config_value
        if config_issue:
            config_context['config_issue'] = config_issue
        
        super().__init__(message, error_code, config_context, original_exception)
        
        self.config_key = config_key
        self.config_value = config_value
        self.config_issue = config_issue
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration error to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the configuration error
        """
        base_dict = super().to_dict()
        base_dict.update({
            'config_key': self.config_key,
            'config_value': self.config_value,
            'config_issue': self.config_issue
        })
        return base_dict


class DataError(ExcelProcessingError):
    """
    Raised when data is malformed or invalid.
    
    This exception is raised when there are issues with the data
    itself, such as malformed content, unexpected formats, or
    data integrity problems.
    
    Attributes:
        data_location: Location of the problematic data
        data_type: Expected data type
        data_value: Problematic data value
        data_issue: Description of the specific data issue
        
    Example:
        raise DataError(
            message="Cell contains invalid date format",
            error_code="INVALID_DATE_FORMAT",
            context={"expected_format": "YYYY-MM-DD"},
            data_location="Sheet1!B15",
            data_type="datetime",
            data_value="invalid_date_string",
            data_issue="format_mismatch"
        )
    """
    
    def __init__(self, message: str, error_code: str,
                 data_location: Optional[str] = None,
                 data_type: Optional[str] = None,
                 data_value: Optional[Any] = None,
                 data_issue: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None,
                 original_exception: Optional[Exception] = None):
        """
        Initialize the data error.
        
        Args:
            message: Human-readable error message
            error_code: Unique error code for categorization
            data_location: Location of the problematic data
            data_type: Expected data type
            data_value: Problematic data value
            data_issue: Description of the specific data issue
            context: Additional context information for debugging
            original_exception: The original exception that caused this error
        """
        # Add data-specific context
        data_error_context = context or {}
        if data_location:
            data_error_context['data_location'] = data_location
        if data_type:
            data_error_context['data_type'] = data_type
        if data_value is not None:
            data_error_context['data_value'] = data_value
        if data_issue:
            data_error_context['data_issue'] = data_issue
        
        super().__init__(message, error_code, data_error_context, original_exception)
        
        self.data_location = data_location
        self.data_type = data_type
        self.data_value = data_value
        self.data_issue = data_issue
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the data error to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the data error
        """
        base_dict = super().to_dict()
        base_dict.update({
            'data_location': self.data_location,
            'data_type': self.data_type,
            'data_value': self.data_value,
            'data_issue': self.data_issue
        })
        return base_dict


# Common error codes for consistent error handling
class ErrorCodes:
    """Common error codes used throughout the Excel processing system."""
    
    # File-related errors
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_ACCESS_DENIED = "FILE_ACCESS_DENIED"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    FILE_FORMAT_INVALID = "FILE_FORMAT_INVALID"
    FILE_CORRUPTED = "FILE_CORRUPTED"
    
    # Validation errors
    VALIDATION_FAILED = "VALIDATION_FAILED"
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
    FIELD_TYPE_MISMATCH = "FIELD_TYPE_MISMATCH"
    FIELD_VALUE_INVALID = "FIELD_VALUE_INVALID"
    FIELD_CONSTRAINT_VIOLATION = "FIELD_CONSTRAINT_VIOLATION"
    
    # Processing errors
    PROCESSING_FAILED = "PROCESSING_FAILED"
    TYPE_CONVERSION_FAILED = "TYPE_CONVERSION_FAILED"
    DATA_EXTRACTION_FAILED = "DATA_EXTRACTION_FAILED"
    SCHEMA_PROCESSING_FAILED = "SCHEMA_PROCESSING_FAILED"
    
    # Schema errors
    SCHEMA_INVALID = "SCHEMA_INVALID"
    SCHEMA_NOT_FOUND = "SCHEMA_NOT_FOUND"
    SCHEMA_VERSION_MISMATCH = "SCHEMA_VERSION_MISMATCH"
    SCHEMA_FIELD_MISSING = "SCHEMA_FIELD_MISSING"
    
    # Configuration errors
    CONFIG_INVALID = "CONFIG_INVALID"
    CONFIG_MISSING = "CONFIG_MISSING"
    CONFIG_VALUE_INVALID = "CONFIG_VALUE_INVALID"
    CONFIG_CONFLICT = "CONFIG_CONFLICT"
    
    # Data errors
    DATA_MALFORMED = "DATA_MALFORMED"
    DATA_TYPE_INVALID = "DATA_TYPE_INVALID"
    DATA_VALUE_INVALID = "DATA_VALUE_INVALID"
    DATA_INTEGRITY_ERROR = "DATA_INTEGRITY_ERROR"
    
    # System errors
    SYSTEM_ERROR = "SYSTEM_ERROR"
    MEMORY_ERROR = "MEMORY_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
