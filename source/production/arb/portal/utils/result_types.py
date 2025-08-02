"""
Result types for data ingestion and processing operations.

This module provides named tuples that represent the results of various
data processing operations in the ARB Feedback Portal. These result types
provide consistent, type-safe, and self-documenting return values with
rich error information.

The result types follow a common pattern:
- Always include a success indicator (bool)
- Always include error information (error_message, error_type)
- Include operation-specific data fields
- Provide clear examples and error type documentation

Attributes:
    StagingResult: Result of staging an uploaded file for review
    UploadResult: Result of processing an uploaded file for direct database insertion

Examples:
    from arb.portal.utils.result_types import StagingResult, UploadResult
    
    # Create a successful staging result
    result = StagingResult(
        file_path=Path("upload.xlsx"),
        id_=123,
        sector="Dairy Digester",
        json_data={"id_incidence": 123, "sector": "Dairy Digester"},
        staged_filename="id_123_ts_20250101_120000.json",
        success=True,
        error_message=None,
        error_type=None
    )

Notes:
    - All result types are immutable (NamedTuple)
    - Error types are standardized across result classes
    - Examples are provided for each result type
    - Comprehensive documentation includes all possible error scenarios
"""

from pathlib import Path
from typing import NamedTuple


class StagingResult(NamedTuple):
    """
    Result of staging an uploaded file for review.
    
    This named tuple provides a consistent, type-safe way to return staging results
    with rich error information and clear success/failure indicators.
    
    Attributes:
        file_path (Path): Path to the uploaded file (always present, even on failure)
        id_ (int | None): Extracted incidence ID (None if missing/invalid)
        sector (str | None): Extracted sector name (None if conversion failed)
        json_data (dict): Parsed JSON data (empty dict if conversion failed)
        staged_filename (str | None): Name of staged file (None if staging failed)
        success (bool): True if staging completed successfully
        error_message (str | None): Human-readable error message (None on success)
        error_type (str | None): Type of error for programmatic handling (None on success)
    
    Examples:
        # Success case
        result = StagingResult(
            file_path=Path("upload.xlsx"),
            id_=123,
            sector="Dairy Digester",
            json_data={"id_incidence": 123, "sector": "Dairy Digester"},
            staged_filename="id_123_ts_20250101_120000.json",
            success=True,
            error_message=None,
            error_type=None
        )
        
        # Missing ID case
        result = StagingResult(
            file_path=Path("upload.xlsx"),
            id_=None,
            sector="Dairy Digester",
            json_data={"sector": "Dairy Digester"},  # No id_incidence
            staged_filename=None,
            success=False,
            error_message="No valid id_incidence found in spreadsheet",
            error_type="missing_id"
        )
        
        # File format error case
        result = StagingResult(
            file_path=Path("upload.txt"),
            id_=None,
            sector=None,
            json_data={},
            staged_filename=None,
            success=False,
            error_message="Unsupported file format. Please upload Excel (.xlsx) file.",
            error_type="conversion_failed"
        )
    
    Error Types:
        - "missing_id": No valid id_incidence found in the file
        - "conversion_failed": File could not be converted to JSON
        - "file_error": Error uploading or saving the file
        - "validation_failed": Other validation errors
        - "database_error": Error accessing database for base_misc_json
    """
    file_path: Path
    id_: int | None
    sector: str | None
    json_data: dict
    staged_filename: str | None
    success: bool
    error_message: str | None
    error_type: str | None


class UploadResult(NamedTuple):
    """
    Result of processing an uploaded file for direct database insertion.
    
    This named tuple provides a consistent, type-safe way to return upload results
    with rich error information and clear success/failure indicators.
    
    Attributes:
        file_path (Path): Path to the uploaded file (always present, even on failure)
        id_ (int | None): Extracted incidence ID (None if missing/invalid or processing failed)
        sector (str | None): Extracted sector name (None if conversion failed)
        success (bool): True if upload and database insertion completed successfully
        error_message (str | None): Human-readable error message (None on success)
        error_type (str | None): Type of error for programmatic handling (None on success)
    
    Examples:
        # Success case
        result = UploadResult(
            file_path=Path("upload.xlsx"),
            id_=123,
            sector="Dairy Digester",
            success=True,
            error_message=None,
            error_type=None
        )
        
        # Missing ID case
        result = UploadResult(
            file_path=Path("upload.xlsx"),
            id_=None,
            sector="Dairy Digester",
            success=False,
            error_message="No valid id_incidence found in spreadsheet",
            error_type="missing_id"
        )
        
        # File format error case
        result = UploadResult(
            file_path=Path("upload.txt"),
            id_=None,
            sector=None,
            success=False,
            error_message="Unsupported file format. Please upload Excel (.xlsx) file.",
            error_type="conversion_failed"
        )
        
        # Database error case
        result = UploadResult(
            file_path=Path("upload.xlsx"),
            id_=None,
            sector="Dairy Digester",
            success=False,
            error_message="Database error occurred during insertion",
            error_type="database_error"
        )
    
    Error Types:
        - "missing_id": No valid id_incidence found in the file
        - "conversion_failed": File could not be converted to JSON
        - "file_error": Error uploading or saving the file
        - "validation_failed": Other validation errors
        - "database_error": Error during database insertion
    """
    file_path: Path
    id_: int | None
    sector: str | None
    success: bool
    error_message: str | None
    error_type: str | None 