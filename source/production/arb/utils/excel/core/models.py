"""
Data models and result classes for Excel processing.

This module defines the data structures used to represent the results of
Excel processing operations, including validation results, processing
statistics, and comprehensive result objects.

Classes:
    ExcelParseResult: Structured result from Excel parsing
    ValidationResult: Result of a validation check
    ProcessingStats: Processing performance and statistics
    ProcessedValue: Result of processing a single cell value
    ProcessedField: Result of processing a single field
    TabExtractResult: Result of extracting data from a single tab
    KeyValueExtractResult: Result of extracting key-value pairs
    ErrorReport: Comprehensive error reporting structure

Author: AI Assistant
Created: 2025-01-27
Version: 1.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class ValidationResult:
    """
    Result of a validation check.
    
    This class represents the outcome of a single validation operation,
    including whether it passed, any error messages, and contextual
    information about the validation.
    
    Attributes:
        field_name: Name of the field or element being validated
        is_valid: Whether the validation passed
        message: Human-readable message about the validation result
        severity: Severity level ('ERROR', 'WARNING', 'INFO')
        location: Location identifier (cell reference, tab name, etc.)
        context: Additional context information for debugging
        timestamp: When the validation was performed
        
    Example:
        result = ValidationResult(
            field_name="file_size",
            is_valid=False,
            message="File size exceeds maximum allowed",
            severity="ERROR",
            location="B15"
        )
    """
    
    field_name: str
    is_valid: bool
    message: str
    severity: str  # 'ERROR', 'WARNING', 'INFO'
    location: str  # Cell reference or tab name
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate severity values after initialization."""
        valid_severities = {'ERROR', 'WARNING', 'INFO'}
        if self.severity.upper() not in valid_severities:
            raise ValueError(
                f"Invalid severity: {self.severity}. "
                f"Must be one of {valid_severities}"
            )
        
        # Convert severity to uppercase for consistency
        self.severity = self.severity.upper()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary for serialization."""
        return {
            'field_name': self.field_name,
            'is_valid': self.is_valid,
            'message': self.message,
            'severity': self.severity,
            'location': self.location,
            'context': self.context,
            'timestamp': self.timestamp.isoformat()
        }
    
    def is_error(self) -> bool:
        """Check if this is an error-level validation result."""
        return self.severity == 'ERROR'
    
    def is_warning(self) -> bool:
        """Check if this is a warning-level validation result."""
        return self.severity == 'WARNING'
    
    def is_info(self) -> bool:
        """Check if this is an info-level validation result."""
        return self.severity == 'INFO'
    
    def get_summary(self) -> str:
        """Get a concise summary of the validation result."""
        status = "✓ PASS" if self.is_valid else "✗ FAIL"
        return f"{status} {self.field_name} at {self.location}: {self.message}"


@dataclass
class ProcessingStats:
    """
    Processing performance and statistics.
    
    This class tracks various metrics during Excel processing operations,
    including timing, volume metrics, quality metrics, and performance
    indicators.
    
    Attributes:
        start_time: When processing started (timestamp)
        end_time: When processing ended (timestamp)
        rows_processed: Number of rows processed
        cells_processed: Number of cells processed
        tabs_processed: Number of tabs processed
        fields_processed: Number of fields processed
        validation_errors: Number of validation errors encountered
        processing_errors: Number of processing errors encountered
        warnings: Number of warnings generated
        memory_usage_mb: Memory usage in megabytes
        
    Example:
        stats = ProcessingStats()
        stats.start_timing()
        # ... process data ...
        stats.end_timing()
        print(f"Processed {stats.cells_per_second:.2f} cells/second")
    """
    
    # Timing
    start_time: float = 0.0
    end_time: float = 0.0
    
    # Volume metrics
    rows_processed: int = 0
    cells_processed: int = 0
    tabs_processed: int = 0
    fields_processed: int = 0
    
    # Quality metrics
    validation_errors: int = 0
    processing_errors: int = 0
    warnings: int = 0
    
    # Performance metrics
    memory_usage_mb: float = 0.0
    
    def start_timing(self) -> None:
        """Start timing the processing."""
        self.start_time = datetime.now().timestamp()
    
    def end_timing(self) -> None:
        """End timing the processing."""
        self.end_time = datetime.now().timestamp()
    
    def increment_processed(self, rows: int = 0, cells: int = 0, 
                          tabs: int = 0, fields: int = 0) -> None:
        """Increment processed counts."""
        self.rows_processed += rows
        self.cells_processed += cells
        self.tabs_processed += tabs
        self.fields_processed += fields
    
    def record_error(self, error_type: str) -> None:
        """Record an error occurrence."""
        if error_type == 'validation':
            self.validation_errors += 1
        elif error_type == 'processing':
            self.processing_errors += 1
        elif error_type == 'warning':
            self.warnings += 1
    
    def set_memory_usage(self, memory_mb: float) -> None:
        """Set the current memory usage."""
        self.memory_usage_mb = memory_mb
    
    @property
    def total_time(self) -> float:
        """Total processing time in seconds."""
        return self.end_time - self.start_time if self.end_time > self.start_time else 0.0
    
    @property
    def cells_per_second(self) -> float:
        """Processing rate in cells per second."""
        return self.cells_processed / self.total_time if self.total_time > 0 else 0.0
    
    @property
    def rows_per_second(self) -> float:
        """Processing rate in rows per second."""
        return self.rows_processed / self.total_time if self.total_time > 0 else 0.0
    
    @property
    def total_errors(self) -> int:
        """Total number of errors (validation + processing)."""
        return self.validation_errors + self.processing_errors
    
    @property
    def success_rate(self) -> float:
        """Success rate as a percentage (0.0 to 1.0)."""
        total_operations = self.cells_processed + self.fields_processed
        if total_operations == 0:
            return 1.0
        return (total_operations - self.total_errors) / total_operations
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of all metrics."""
        return {
            'total_time_seconds': self.total_time,
            'rows_processed': self.rows_processed,
            'cells_processed': self.cells_processed,
            'tabs_processed': self.tabs_processed,
            'fields_processed': self.fields_processed,
            'validation_errors': self.validation_errors,
            'processing_errors': self.processing_errors,
            'warnings': self.warnings,
            'total_errors': self.total_errors,
            'success_rate': self.success_rate,
            'cells_per_second': self.cells_per_second,
            'rows_per_second': self.rows_per_second,
            'memory_usage_mb': self.memory_usage_mb
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert processing stats to dictionary for serialization."""
        return {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'rows_processed': self.rows_processed,
            'cells_processed': self.cells_processed,
            'tabs_processed': self.tabs_processed,
            'fields_processed': self.fields_processed,
            'validation_errors': self.validation_errors,
            'processing_errors': self.processing_errors,
            'warnings': self.warnings,
            'memory_usage_mb': self.memory_usage_mb,
            'total_time': self.total_time,
            'success_rate': self.success_rate
        }


@dataclass
class ProcessedValue:
    """
    Result of processing a single cell value.
    
    This class represents the outcome of processing a single cell value,
    including the original value, processed value, type information,
    and any processing metadata.
    
    Attributes:
        original_value: The original value from the cell
        processed_value: The processed/converted value
        expected_type: The expected data type
        actual_type: The actual data type of the processed value
        is_valid: Whether the value was processed successfully
        error_message: Error message if processing failed
        location: Cell location (e.g., 'A1', 'B15')
        processing_metadata: Additional processing information
        
    Example:
        value = ProcessedValue(
            original_value="2023-01-15",
            processed_value=datetime(2023, 1, 15),
            expected_type=datetime,
            actual_type=datetime,
            is_valid=True,
            location="B15"
        )
    """
    
    original_value: Any
    processed_value: Any
    expected_type: type
    actual_type: type
    is_valid: bool
    error_message: Optional[str] = None
    location: str = ""
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert processed value to dictionary for serialization."""
        return {
            'original_value': str(self.original_value),
            'processed_value': str(self.processed_value),
            'expected_type': self.expected_type.__name__,
            'actual_type': self.actual_type.__name__,
            'is_valid': self.is_valid,
            'error_message': self.error_message,
            'location': self.location,
            'processing_metadata': self.processing_metadata
        }


@dataclass
class ProcessedField:
    """
    Result of processing a single field.
    
    This class represents the outcome of processing a single field from
    an Excel tab, including the field name, processed value, validation
    results, and processing metadata.
    
    Attributes:
        field_name: Name of the field being processed
        processed_value: The processed value for the field
        validation_result: Validation result for the field
        processing_metadata: Additional processing information
        location: Location information (tab name, cell reference)
        
    Example:
        field = ProcessedField(
            field_name="project_name",
            processed_value="Sample Project",
            validation_result=ValidationResult(...),
            location="Sheet1!A1"
        )
    """
    
    field_name: str
    processed_value: Any
    validation_result: ValidationResult
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    location: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert processed field to dictionary for serialization."""
        return {
            'field_name': self.field_name,
            'processed_value': str(self.processed_value),
            'validation_result': self.validation_result.to_dict(),
            'processing_metadata': self.processing_metadata,
            'location': self.location
        }


@dataclass
class TabExtractResult:
    """
    Result of extracting data from a single tab.
    
    This class represents the outcome of extracting data from a single
    Excel tab, including the extracted data, validation results,
    processing statistics, and any errors encountered.
    
    Attributes:
        tab_name: Name of the tab that was processed
        success: Whether the extraction was successful
        extracted_data: The extracted data from the tab
        validation_results: List of validation results
        processing_stats: Processing statistics for this tab
        errors: List of processing errors
        warnings: List of processing warnings
        processing_metadata: Additional processing information
        
    Example:
        result = TabExtractResult(
            tab_name="Sheet1",
            success=True,
            extracted_data={"field1": "value1", "field2": "value2"},
            validation_results=[...],
            processing_stats=ProcessingStats()
        )
    """
    
    tab_name: str
    success: bool
    extracted_data: Dict[str, Any]
    validation_results: List[ValidationResult]
    processing_stats: ProcessingStats
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """Check if the tab extraction result is valid."""
        return self.success and not self.errors
    
    def get_error_summary(self) -> str:
        """Get a summary of all errors for this tab."""
        if not self.errors:
            return "No errors"
        return f"{len(self.errors)} errors: " + "; ".join(self.errors)
    
    def get_validation_summary(self) -> str:
        """Get a summary of validation results."""
        total_validations = len(self.validation_results)
        passed_validations = sum(1 for r in self.validation_results if r.is_valid)
        return f"{passed_validations}/{total_validations} validations passed"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tab extract result to dictionary for serialization."""
        return {
            'tab_name': self.tab_name,
            'success': self.success,
            'extracted_data': self.extracted_data,
            'validation_results': [r.to_dict() for r in self.validation_results],
            'processing_stats': self.processing_stats.to_dict(),
            'errors': self.errors,
            'warnings': self.warnings,
            'processing_metadata': self.processing_metadata
        }


@dataclass
class KeyValueExtractResult:
    """
    Result of extracting key-value pairs from a worksheet.
    
    This class represents the outcome of extracting key-value pairs from
    an Excel worksheet, including the extracted pairs, validation results,
    and processing metadata.
    
    Attributes:
        success: Whether the extraction was successful
        extracted_pairs: Dictionary of extracted key-value pairs
        validation_results: List of validation results
        processing_stats: Processing statistics
        errors: List of processing errors
        warnings: List of processing warnings
        metadata: Additional metadata about the extraction
        
    Example:
        result = KeyValueExtractResult(
            success=True,
            extracted_pairs={"project_name": "Sample Project", "version": "1.0"},
            validation_results=[...],
            processing_stats=ProcessingStats()
        )
    """
    
    success: bool
    extracted_pairs: Dict[str, Any]
    validation_results: List[ValidationResult]
    processing_stats: ProcessingStats
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """Check if the key-value extraction result is valid."""
        return self.success and not self.errors
    
    def get_error_summary(self) -> str:
        """Get a summary of all errors."""
        if not self.errors:
            return "No errors"
        return f"{len(self.errors)} errors: " + "; ".join(self.errors)
    
    def get_pairs_count(self) -> int:
        """Get the number of extracted key-value pairs."""
        return len(self.extracted_pairs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert key-value extract result to dictionary for serialization."""
        return {
            'success': self.success,
            'extracted_pairs': self.extracted_pairs,
            'validation_results': [r.to_dict() for r in self.validation_results],
            'processing_stats': self.processing_stats.to_dict(),
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': self.metadata,
            'pairs_count': self.get_pairs_count()
        }


@dataclass
class ExcelParseResult:
    """
    Structured result from Excel parsing.
    
    This class represents the comprehensive result of parsing an Excel file,
    including all extracted data, validation results, processing statistics,
    and error information. This is the main result object returned by
    the enhanced Excel parsing functions.
    
    Attributes:
        success: Whether the overall parsing operation was successful
        metadata: File metadata (name, size, creation date, etc.)
        schemas: Extracted schema information
        tab_contents: Extracted content from all tabs
        validation_results: List of all validation results
        processing_stats: Overall processing statistics
        errors: List of all processing errors
        warnings: List of all processing warnings
        file_path: Path to the processed file
        processing_time: Total processing time in seconds
        timestamp: When the parsing was completed
        
    Example:
        result = ExcelParseResult(
            success=True,
            metadata={"filename": "sample.xlsx", "size_mb": 2.5},
            schemas={"schema1": {...}},
            tab_contents={"Sheet1": {...}},
            validation_results=[...],
            processing_stats=ProcessingStats(),
            file_path=Path("sample.xlsx")
        )
    """
    
    # Core data
    success: bool
    metadata: Dict[str, Any]
    schemas: Dict[str, Any]
    tab_contents: Dict[str, Any]
    
    # Validation and processing results
    validation_results: List[ValidationResult]
    processing_stats: ProcessingStats
    errors: List[str]
    warnings: List[str]
    
    # Metadata
    file_path: Path
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def is_valid(self) -> bool:
        """Check if the result is valid (no errors)."""
        return self.success and not self.errors
    
    def get_error_summary(self) -> str:
        """Get a summary of all errors."""
        if not self.errors:
            return "No errors"
        return f"{len(self.errors)} errors: " + "; ".join(self.errors)
    
    def get_warning_summary(self) -> str:
        """Get a summary of all warnings."""
        if not self.warnings:
            return "No warnings"
        return f"{len(self.warnings)} warnings: " + "; ".join(self.warnings)
    
    def get_validation_summary(self) -> str:
        """Get a summary of validation results."""
        total_validations = len(self.validation_results)
        passed_validations = sum(1 for r in self.validation_results if r.is_valid)
        return f"{passed_validations}/{total_validations} validations passed"
    
    def get_file_info(self) -> str:
        """Get file information summary."""
        return (
            f"File: {self.file_path.name}, "
            f"Size: {self.metadata.get('size_mb', 'unknown')}MB, "
            f"Processing time: {self.processing_time:.2f}s"
        )
    
    def get_processing_summary(self) -> str:
        """Get processing performance summary."""
        stats = self.processing_stats
        return (
            f"Processed {stats.tabs_processed} tabs, "
            f"{stats.rows_processed} rows, "
            f"{stats.cells_processed} cells in {stats.total_time:.2f}s "
            f"({stats.cells_per_second:.1f} cells/s)"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Excel parse result to dictionary for serialization."""
        return {
            'success': self.success,
            'metadata': self.metadata,
            'schemas': self.schemas,
            'tab_contents': self.tab_contents,
            'validation_results': [r.to_dict() for r in self.validation_results],
            'processing_stats': self.processing_stats.to_dict(),
            'errors': self.errors,
            'warnings': self.warnings,
            'file_path': str(self.file_path),
            'processing_time': self.processing_time,
            'timestamp': self.timestamp.isoformat(),
            'is_valid': self.is_valid(),
            'error_summary': self.get_error_summary(),
            'warning_summary': self.get_warning_summary(),
            'validation_summary': self.get_validation_summary(),
            'file_info': self.get_file_info(),
            'processing_summary': self.get_processing_summary()
        }


@dataclass
class ErrorReport:
    """
    Comprehensive error reporting structure.
    
    This class provides a structured way to report and analyze errors
    that occur during Excel processing operations.
    
    Attributes:
        total_errors: Total number of errors encountered
        error_categories: Errors grouped by category
        error_summary: Human-readable error summary
        recommendations: Suggested actions to resolve errors
        timestamp: When the error report was generated
        
    Example:
        report = ErrorReport(
            total_errors=5,
            error_categories={"validation": 3, "processing": 2},
            error_summary="3 validation errors, 2 processing errors",
            recommendations=["Check file format", "Verify schema definitions"]
        )
    """
    
    total_errors: int
    error_categories: Dict[str, int]
    error_summary: str
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error report to dictionary for serialization."""
        return {
            'total_errors': self.total_errors,
            'error_categories': self.error_categories,
            'error_summary': self.error_summary,
            'recommendations': self.recommendations,
            'timestamp': self.timestamp.isoformat()
        }
    
    def get_severity_level(self) -> str:
        """Get the overall severity level of the errors."""
        if self.total_errors == 0:
            return "NONE"
        elif self.total_errors <= 2:
            return "LOW"
        elif self.total_errors <= 5:
            return "MEDIUM"
        else:
            return "HIGH"
