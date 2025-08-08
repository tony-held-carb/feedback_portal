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
    FileSaveResult: Result of saving an uploaded file
    FileConversionResult: Result of converting a file to JSON format
    IdValidationResult: Result of validating and extracting an ID from JSON data
    StagedFileResult: Result of creating a staged file
    DatabaseInsertResult: Result of inserting data into the database

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


class FileSaveResult(NamedTuple):
    """
    Result of saving an uploaded file.

    This named tuple provides a consistent, type-safe way to return file save results
    with rich error information and clear success/failure indicators.

    Attributes:
        file_path (Path): Path to the saved file (None if save failed)
        success (bool): True if file was saved successfully
        error_message (str | None): Human-readable error message (None on success)
        error_type (str | None): Type of error for programmatic handling (None on success)

    Examples:
        # Success case
        result = FileSaveResult(
            file_path=Path("uploads/file.xlsx"),
            success=True,
            error_message=None,
            error_type=None
        )

        # Error case
        result = FileSaveResult(
            file_path=None,
            success=False,
            error_message="Failed to save uploaded file: Permission denied",
            error_type="file_error"
        )

    Error Types:
        - "file_error": Error uploading or saving the file
        - "permission_error": Insufficient permissions to save file
        - "disk_error": Disk space or I/O error
    """
    file_path: Path | None
    success: bool
    error_message: str | None
    error_type: str | None


class FileConversionResult(NamedTuple):
    """
    Result of converting a file to JSON format.

    This named tuple provides a consistent, type-safe way to return file conversion results
    with rich error information and clear success/failure indicators.

    Attributes:
        json_path (Path | None): Path to converted JSON file (None if conversion failed)
        sector (str | None): Extracted sector name (None if conversion failed)
        json_data (dict): Parsed JSON data (empty dict if conversion failed)
        success (bool): True if conversion completed successfully
        error_message (str | None): Human-readable error message (None on success)
        error_type (str | None): Type of error for programmatic handling (None on success)

    Examples:
        # Success case
        result = FileConversionResult(
            json_path=Path("uploads/file.json"),
            sector="Dairy Digester",
            json_data={"id_incidence": 123, "sector": "Dairy Digester"},
            success=True,
            error_message=None,
            error_type=None
        )

        # Conversion failed case
        result = FileConversionResult(
            json_path=None,
            sector=None,
            json_data={},
            success=False,
            error_message="Unsupported file format. Please upload Excel (.xlsx) file.",
            error_type="conversion_failed"
        )

    Error Types:
        - "conversion_failed": File could not be converted to JSON
        - "file_error": Error reading or processing the file
        - "format_error": File format not recognized
    """
    json_path: Path | None
    sector: str | None
    json_data: dict
    success: bool
    error_message: str | None
    error_type: str | None


class IdValidationResult(NamedTuple):
    """
    Result of validating and extracting an ID from JSON data.

    This named tuple provides a consistent, type-safe way to return ID validation results
    with rich error information and clear success/failure indicators.

    Attributes:
        id_ (int | None): Extracted incidence ID (None if missing/invalid)
        success (bool): True if valid ID was found
        error_message (str | None): Human-readable error message (None on success)
        error_type (str | None): Type of error for programmatic handling (None on success)

    Examples:
        # Success case
        result = IdValidationResult(
            id_=123,
            success=True,
            error_message=None,
            error_type=None
        )

        # Missing ID case
        result = IdValidationResult(
            id_=None,
            success=False,
            error_message="No valid id_incidence found in spreadsheet",
            error_type="missing_id"
        )

    Error Types:
        - "missing_id": No valid id_incidence found in the file
        - "invalid_id": ID found but is not a positive integer
        - "validation_error": Other validation errors
    """
    id_: int | None
    success: bool
    error_message: str | None
    error_type: str | None


class StagedFileResult(NamedTuple):
    """
    Result of creating a staged file.

    This named tuple provides a consistent, type-safe way to return staged file creation results
    with rich error information and clear success/failure indicators.

    Attributes:
        staged_filename (str | None): Name of staged file (None if staging failed)
        success (bool): True if staged file was created successfully
        error_message (str | None): Human-readable error message (None on success)
        error_type (str | None): Type of error for programmatic handling (None on success)

    Examples:
        # Success case
        result = StagedFileResult(
            staged_filename="id_123_ts_20250101_120000.json",
            success=True,
            error_message=None,
            error_type=None
        )

        # Staging failed case
        result = StagedFileResult(
            staged_filename=None,
            success=False,
            error_message="Failed to create staged file. Please try again.",
            error_type="database_error"
        )

    Error Types:
        - "database_error": Error accessing database for base_misc_json
        - "file_error": Error creating or writing the staged file
        - "permission_error": Insufficient permissions to create file
    """
    staged_filename: str | None
    success: bool
    error_message: str | None
    error_type: str | None


class DatabaseInsertResult(NamedTuple):
    """
    Result of inserting data into the database.

    This named tuple provides a consistent, type-safe way to return database insertion results
    with rich error information and clear success/failure indicators.

    Attributes:
        id_ (int | None): Inserted incidence ID (None if insertion failed)
        success (bool): True if data was inserted successfully
        error_message (str | None): Human-readable error message (None on success)
        error_type (str | None): Type of error for programmatic handling (None on success)

    Examples:
        # Success case
        result = DatabaseInsertResult(
            id_=123,
            success=True,
            error_message=None,
            error_type=None
        )

        # Insertion failed case
        result = DatabaseInsertResult(
            id_=None,
            success=False,
            error_message="Database error occurred during insertion",
            error_type="database_error"
        )

    Error Types:
        - "database_error": Error during database insertion
        - "validation_error": Data validation failed
        - "constraint_error": Database constraint violation
    """
    id_: int | None
    success: bool
    error_message: str | None
    error_type: str | None


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
