# Result Types Module Creation

## Overview

The `StagingResult` and `UploadResult` named tuples have been moved from `db_ingest_util.py` to their own dedicated module `arb.portal.utils.result_types` for better organization and maintainability.

## Motivation

As the refactoring process continues, we anticipate creating many more result classes. Having them in a separate, well-documented module will:

1. **Improve Organization**: Keep related result types together
2. **Enhance Maintainability**: Centralized location for all result types
3. **Provide Better Documentation**: Dedicated module with comprehensive examples
4. **Enable Reusability**: Easy to import and use across different modules
5. **Support Future Growth**: Scalable structure for additional result types

## Changes Made

### 1. Created New Module: `source/production/arb/portal/utils/result_types.py`

- **Comprehensive Documentation**: Module-level docstring explaining purpose and usage patterns
- **StagingResult**: Moved from `db_ingest_util.py` with full documentation and examples
- **UploadResult**: Moved from `db_ingest_util.py` with full documentation and examples
- **Standardized Pattern**: All result types follow consistent structure:
  - Always include `success` indicator (bool)
  - Always include error information (`error_message`, `error_type`)
  - Include operation-specific data fields
  - Provide clear examples and error type documentation

### 2. Updated `source/production/arb/portal/utils/db_ingest_util.py`

- **Added Import**: `from arb.portal.utils.result_types import StagingResult, UploadResult`
- **Removed Class Definitions**: Deleted the original `StagingResult` and `UploadResult` class definitions
- **Removed NamedTuple Import**: No longer needed since classes are imported

### 3. Updated Test Files

- **tests/arb/portal/test_utils_db_ingest_util.py**: Updated import to use new module
- **tests/arb/portal/test_route_equivalence.py**: Updated import to use new module
- **tests/arb/portal/test_routes.py**: Updated import to use new module

### 4. Created New Test File: `tests/arb/portal/test_result_types.py`

- **Comprehensive Testing**: Tests for both `StagingResult` and `UploadResult`
- **Creation Tests**: Verify proper instantiation with all fields
- **Error Case Tests**: Verify error scenarios are handled correctly
- **Immutability Tests**: Verify NamedTuple immutability
- **Module Tests**: Verify module import and documentation

## Result Type Patterns

### Common Structure

All result types follow this pattern:

```python
class SomeResult(NamedTuple):
    """
    Result of some operation.
    
    Attributes:
        # Operation-specific fields
        success (bool): True if operation completed successfully
        error_message (str | None): Human-readable error message (None on success)
        error_type (str | None): Type of error for programmatic handling (None on success)
    
    Examples:
        # Success case
        result = SomeResult(
            # ... operation-specific fields ...
            success=True,
            error_message=None,
            error_type=None
        )
        
        # Error case
        result = SomeResult(
            # ... operation-specific fields ...
            success=False,
            error_message="Descriptive error message",
            error_type="specific_error_type"
        )
    
    Error Types:
        - "error_type_1": Description of this error type
        - "error_type_2": Description of this error type
    """
    # Operation-specific fields
    success: bool
    error_message: str | None
    error_type: str | None
```

### Standardized Error Types

Common error types used across result classes:

- **"missing_id"**: No valid id_incidence found in the file
- **"conversion_failed"**: File could not be converted to JSON
- **"file_error"**: Error uploading or saving the file
- **"validation_failed"**: Other validation errors
- **"database_error"**: Error during database operations

## Testing Results

All tests pass after the refactoring:

- ✅ `test_result_types.py`: 8/8 tests passed
- ✅ `test_utils_db_ingest_util.py` staging tests: 3/3 tests passed
- ✅ `test_utils_db_ingest_util.py` stage_uploaded_file tests: 6/6 tests passed
- ✅ `test_utils_db_ingest_util.py` refactored tests: 4/4 tests passed
- ✅ `test_routes.py` upload_file_staged_refactored tests: 11/11 tests passed
- ✅ `test_route_equivalence.py`: 13/13 tests passed

## Benefits Achieved

1. **Better Organization**: Result types are now in a dedicated, well-documented module
2. **Improved Maintainability**: Centralized location makes it easier to find and modify result types
3. **Enhanced Documentation**: Comprehensive examples and error type documentation
4. **Future-Proof Structure**: Ready for additional result types as refactoring continues
5. **Zero Breaking Changes**: All existing functionality continues to work unchanged

## Usage Examples

### Importing Result Types

```python
from arb.portal.utils.result_types import StagingResult, UploadResult
```

### Creating Success Results

```python
# Staging success
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

# Upload success
result = UploadResult(
    file_path=Path("upload.xlsx"),
    id_=123,
    sector="Dairy Digester",
    success=True,
    error_message=None,
    error_type=None
)
```

### Creating Error Results

```python
# Missing ID error
result = StagingResult(
    file_path=Path("upload.xlsx"),
    id_=None,
    sector="Dairy Digester",
    json_data={"sector": "Dairy Digester"},
    staged_filename=None,
    success=False,
    error_message="No valid id_incidence found in spreadsheet",
    error_type="missing_id"
)

# Database error
result = UploadResult(
    file_path=Path("upload.xlsx"),
    id_=None,
    sector="Dairy Digester",
    success=False,
    error_message="Database error occurred during insertion",
    error_type="database_error"
)
```

## Future Considerations

1. **Additional Result Types**: As refactoring continues, new result types can be added to this module
2. **Common Base Class**: Consider creating a base class or mixin for common result type functionality
3. **Validation**: Consider adding validation for error types to ensure consistency
4. **Serialization**: Consider adding JSON serialization methods for result types
5. **Type Hints**: Consider using more specific type hints for error types (e.g., Literal types)

## Migration Notes

- All existing code continues to work without changes
- Import statements have been updated in test files
- No breaking changes to the public API
- All functionality preserved exactly as before 