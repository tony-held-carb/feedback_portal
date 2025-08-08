# Data Ingestion Refactor - Implementation Guide

## Overview

This document provides technical implementation guidance for developers working on the ARB Feedback Portal's data
ingestion refactor. It includes code patterns, standards, and practical examples based on the successful staging
implementation.

**Last Updated:** August 2025
**Target Audience:** Developers working on the refactor
**Status:** ✅ **PHASE 2 COMPLETED** - Error handling logic extracted into shared helper functions

---

## Code Patterns and Standards

### 1. **Result Type Pattern**

All refactored functions should return rich result objects instead of tuples.

#### Pattern Template

```python
from arb.portal.utils.result_types import SomeResult

def some_function(param1, param2) -> SomeResult:
    """
    Brief description of what the function does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        SomeResult: Rich result object with success/failure information

    Examples:
        result = some_function(value1, value2)
        if result.success:
            # Handle success case
        else:
            # Handle error case based on result.error_type
    """
    try:
        # Step 1: Validate inputs
        if not param1:
            return SomeResult(
                # ... result fields ...
                success=False,
                error_message="Invalid parameter",
                error_type="validation_error"
            )

        # Step 2: Perform operation
        # ... operation logic ...

        # Step 3: Return success result
        return SomeResult(
            # ... result fields ...
            success=True,
            error_message=None,
            error_type=None
        )

    except Exception as e:
        logger.error(f"Error in some_function: {e}")
        return SomeResult(
            # ... result fields ...
            success=False,
            error_message=str(e),
            error_type="unexpected_error"
        )
```

#### Error Type Standards

- **`missing_id`**: No valid id_incidence found in the file
- **`conversion_failed`**: File could not be converted to JSON
- **`file_error`**: Error uploading or saving the file
- **`validation_failed`**: Other validation errors
- **`database_error`**: Error during database operations
- **`unexpected_error`**: Unexpected exceptions

### 2. **Helper Function Pattern with Result Types** ✅ **COMPLETED**

### 3. **Route Helper Function Pattern** ✅ **PHASE 1 COMPLETED**

### 4. **Error Handling Helper Function Pattern** ✅ **PHASE 2 COMPLETED**

Extract error handling logic into shared helper functions to eliminate duplication and ensure consistent error behavior.

#### Pattern Template

```python
def handle_upload_error(result, form, template_name, request_file=None) -> str:
    """
    Handle upload errors with appropriate error messages and logging.

    Args:
        result: Result object containing error information
        form: UploadForm instance
        template_name: Name of the template to render
        request_file: Optional uploaded file for diagnostic information

    Returns:
        str: Rendered HTML with error message

    Examples:
        return handle_upload_error(result, form, 'upload.html', request_file)
    """
    # Get user-friendly error message
    error_message = get_error_message_for_type(result.error_type, result)
    
    # Handle specific error types with special logic
    if result.error_type == "conversion_failed":
        logger.warning(f"Upload failed file conversion: {result.file_path=}")
        return render_upload_error(form, error_message, template_name)
    
    # Log the error for debugging
    logger.error(f"Upload error - Type: {result.error_type}, Message: {result.error_message}")
    
    return render_upload_error(form, error_message, template_name)


def handle_upload_exception(e: Exception, form, template_name, 
                          request_file=None, result=None, diagnostic_func=None) -> str:
    """
    Handle exceptions during upload processing with enhanced error handling.

    Args:
        e: The exception that occurred
        form: UploadForm instance
        template_name: Name of the template to render
        request_file: Optional uploaded file for diagnostic information
        result: Optional result object if available
        diagnostic_func: Optional function to generate detailed diagnostics

    Returns:
        str: Rendered HTML with detailed error message

    Examples:
        return handle_upload_exception(e, form, 'upload.html', request_file, result)
    """
    logger.exception("Exception occurred during upload processing.")
    
    # Generate detailed diagnostic information if diagnostic function is provided
    if diagnostic_func and request_file:
        try:
            file_path = result.file_path if result else None
            error_details = diagnostic_func(request_file, file_path)
            detailed_message = format_diagnostic_message(error_details)
            return render_upload_error(form, detailed_message, template_name)
        except Exception as diagnostic_error:
            logger.error(f"Error generating diagnostics: {diagnostic_error}")
    
    # Fallback to generic error message
    generic_message = "An unexpected error occurred during upload processing. Please try again."
    return render_upload_error(form, generic_message, template_name)
```

#### Implemented Error Handling Helper Functions

```python
# Error Handling
def handle_upload_error(result, form, template_name, request_file=None) -> str:
    """Handle upload errors with appropriate error messages and logging."""

def handle_upload_exception(e: Exception, form, template_name, 
                          request_file=None, result=None, diagnostic_func=None) -> str:
    """Handle exceptions during upload processing with enhanced error handling."""
```

#### Pattern Template

```python
def route_helper_function(param1, param2) -> tuple[bool, str | None]:
    """
    Brief description of what this route helper does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        tuple[bool, str | None]: (is_valid, error_message)
        - is_valid: True if operation is valid, False otherwise
        - error_message: Error message if validation failed, None if successful

    Examples:
        is_valid, error = route_helper_function(value1, value2)
        if not is_valid:
            return render_template('template.html', form=form, upload_message=error)
    """
    try:
        # Perform the specific validation/operation
        if not param1 or not param1.filename:
            return False, "No file selected. Please choose a file."
        
        # Additional validation logic...
        
        return True, None

    except Exception as e:
        logger.error(f"Error in route_helper_function: {e}")
        return False, f"An unexpected error occurred: {str(e)}"
```

#### Implemented Route Helper Functions

```python
# File Validation
def validate_upload_request(request_file) -> tuple[bool, str | None]:
    """Validate that a file was uploaded in the request."""

# Error Message Generation
def get_error_message_for_type(error_type: str, result) -> str:
    """Get user-friendly error message for specific error types."""

# Success Message Generation
def get_success_message_for_upload(result, filename: str, upload_type: str) -> str:
    """Get success message for upload (direct vs staged)."""

# Template Rendering
def render_upload_form(form, message: str | None, template_name: str) -> str:
    """Render upload form with consistent message handling."""

def render_upload_error(form, message: str, template_name: str) -> str:
    """Render upload error with consistent error display."""
```

#### Pattern Template

```python
def helper_function_with_result(param1, param2) -> HelperResult:
    """
    Brief description of what this helper does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        HelperResult: Rich result object with operation-specific data

    Examples:
        result = helper_function_with_result(value1, value2)
        if result.success:
            # Use result.data
        else:
            # Handle error based on result.error_type
    """
    try:
        # Perform the specific operation
        data = perform_operation(param1, param2)

        if data:
            return HelperResult(
                data=data,
                success=True,
                error_message=None,
                error_type=None
            )
        else:
            return HelperResult(
                data=None,
                success=False,
                error_message="Operation failed",
                error_type="operation_failed"
            )

    except Exception as e:
        logger.error(f"Error in helper_function_with_result: {e}")
        return HelperResult(
            data=None,
            success=False,
            error_message=str(e),
            error_type="unexpected_error"
        )
```

#### Implemented Helper Functions

```python
# File Operations
def save_uploaded_file_with_result(upload_dir, request_file, db, description) -> FileSaveResult:
    """Save uploaded file and return result with file path or error."""

def convert_file_to_json_with_result(file_path) -> FileConversionResult:
    """Convert file to JSON and return result with JSON data or error."""

# Data Validation
def validate_id_from_json_with_result(json_data) -> IdValidationResult:
    """Validate ID from JSON data and return result with ID or error."""

# Database Operations
def create_staged_file_with_result(id_, json_data, db, base, upload_dir) -> StagedFileResult:
    """Create staged file and return result with filename or error."""

def insert_json_into_database_with_result(json_path, base, db) -> DatabaseInsertResult:
    """Insert JSON into database and return result with ID or error."""
```

### 5. **Main Function Pattern** ✅ **UPDATED**

Main functions should orchestrate helper functions with result types and return rich result objects.

#### Pattern Template

```python
def main_function(db, upload_dir, request_file, base) -> MainResult:
    """
    Main function that orchestrates the complete workflow.

    Args:
        db: Database instance
        upload_dir: Upload directory
        request_file: Uploaded file
        base: SQLAlchemy base

    Returns:
        MainResult: Rich result object with complete operation information
    """
    logger.debug(f"main_function() called with {request_file.filename}")

    # Step 1: Save uploaded file
    save_result = save_uploaded_file_with_result(upload_dir, request_file, db, description="Operation description")
    if not save_result.success:
        return MainResult(
            # ... result fields ...
            success=False,
            error_message=save_result.error_message,
            error_type=save_result.error_type
        )

    # Step 2: Convert file to JSON
    convert_result = convert_file_to_json_with_result(save_result.file_path)
    if not convert_result.success:
        return MainResult(
            # ... result fields ...
            success=False,
            error_message="Unsupported file format. Please upload Excel (.xlsx) file.",
            error_type="conversion_failed"
        )

    # Step 3: Validate data
    validate_result = validate_id_from_json_with_result(convert_result.json_data)
    if not validate_result.success:
        return MainResult(
            # ... result fields ...
            success=False,
            error_message=validate_result.error_message,
            error_type="missing_id"
        )

    # Step 4: Perform main operation
    operation_result = perform_main_operation_with_result(validate_result.id_, convert_result.json_data, db, base)
    if not operation_result.success:
        return MainResult(
            # ... result fields ...
            success=False,
            error_message=operation_result.error_message,
            error_type=operation_result.error_type
        )

    # Success case
    return MainResult(
        # ... result fields ...
        success=True,
        error_message=None,
        error_type=None
    )
```

#### Implemented Main Functions

```python
def stage_uploaded_file_for_review(db, upload_dir, request_file, base) -> StagingResult:
    """Stage uploaded file for review with comprehensive error handling."""

def upload_and_process_file(db, upload_dir, request_file, base) -> UploadResult:
    """Upload and process file directly to database with comprehensive error handling."""
```

---

## Error Handling Standards

### 1. **Error Type Hierarchy**

```python
# Standard error types (in order of specificity)
ERROR_TYPES = {
    "missing_id": "No valid id_incidence found in the file",
    "conversion_failed": "File could not be converted to JSON",
    "file_error": "Error uploading or saving the file",
    "validation_failed": "Other validation errors",
    "database_error": "Error during database operations",
    "unexpected_error": "Unexpected exceptions"
}
```

### 2. **Error Message Standards**

#### User-Friendly Messages

- **Clear and actionable**: Tell users what they can do to fix the issue
- **Specific**: Don't use generic "something went wrong" messages
- **Helpful**: Provide guidance on how to resolve the issue

#### Examples

```python
# Good error messages
"Please add a valid 'Incidence/Emission ID' to your spreadsheet before uploading."
"Please upload an Excel (.xlsx) file instead of the current format."
"File upload failed. Please check your internet connection and try again."

# Bad error messages
"Error occurred during processing."
"Something went wrong."
"Upload failed."
```

### 3. **Error Handling Pattern**

```python
def handle_error(error_type: str, error_message: str, context: dict) -> str:
    """
    Standard error handling pattern.

    Args:
        error_type: Type of error that occurred
        error_message: Technical error message
        context: Additional context for logging

    Returns:
        str: User-friendly error message
    """
    logger.error(f"Error type: {error_type}, Message: {error_message}, Context: {context}")

    if error_type == "missing_id":
        return "Please add a valid 'Incidence/Emission ID' to your spreadsheet before uploading."
    elif error_type == "conversion_failed":
        return "Please upload an Excel (.xlsx) file instead of the current format."
    elif error_type == "file_error":
        return "File upload failed. Please check your internet connection and try again."
    elif error_type == "database_error":
        return "Database error occurred. Please try again or contact support if the problem persists."
    else:
        return f"An unexpected error occurred: {error_message}"
```

---

## Testing Guidelines

### 1. **Unit Test Pattern**

```python
def test_function_name_success():
    """Function successfully processes valid input."""
    # Arrange
    valid_input = create_valid_input()

    # Act
    result = function_under_test(valid_input)

    # Assert
    assert result.success is True
    assert result.error_message is None
    assert result.error_type is None
    # ... other assertions ...

def test_function_name_error_case():
    """Function handles error case correctly."""
    # Arrange
    invalid_input = create_invalid_input()

    # Act
    result = function_under_test(invalid_input)

    # Assert
    assert result.success is False
    assert result.error_message is not None
    assert result.error_type == "expected_error_type"
```

### 2. **Integration Test Pattern**

```python
def test_end_to_end_workflow():
    """Complete workflow from upload to result."""
    # Arrange
    test_file = create_test_file()

    # Act
    result = complete_workflow(test_file)

    # Assert
    assert result.success is True
    # ... verify all expected outcomes ...
```

### 3. **Error Testing Pattern**

```python
def test_all_error_scenarios():
    """Test all possible error scenarios."""
    error_scenarios = [
        ("missing_id", create_file_without_id),
        ("conversion_failed", create_invalid_file),
        ("file_error", create_corrupted_file),
        ("database_error", create_database_error),
    ]

    for error_type, file_creator in error_scenarios:
        with subtests(error_type=error_type):
            # Arrange
            test_file = file_creator()

            # Act
            result = function_under_test(test_file)

            # Assert
            assert result.success is False
            assert result.error_type == error_type
            assert result.error_message is not None
```

### 4. **Helper Function Test Pattern** ✅ **COMPLETED**

```python
def test_helper_function_with_result_success():
    """Helper function returns success result for valid input."""
    # Arrange
    valid_input = create_valid_input()

    # Act
    result = helper_function_with_result(valid_input)

    # Assert
    assert result.success is True
    assert result.data is not None
    assert result.error_message is None
    assert result.error_type is None

def test_helper_function_with_result_failure():
    """Helper function returns failure result for invalid input."""
    # Arrange
    invalid_input = create_invalid_input()

    # Act
    result = helper_function_with_result(invalid_input)

    # Assert
    assert result.success is False
    assert result.data is None
    assert result.error_message is not None
    assert result.error_type == "expected_error_type"
```

---

## Documentation Standards

### 1. **Function Documentation Template**

```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """
    Brief description of what the function does.

    This function provides a detailed explanation of its purpose, behavior,
    and any important implementation details.

    Args:
        param1 (Type1): Description of param1 and its expected format
        param2 (Type2): Description of param2 and its constraints

    Returns:
        ReturnType: Description of the return value and its structure

    Raises:
        ValueError: When param1 is invalid
        DatabaseError: When database operation fails

    Examples:
        # Success case
        result = function_name(valid_param1, valid_param2)
        if result.success:
            print(f"Operation successful: {result.data}")

        # Error case
        result = function_name(invalid_param1, valid_param2)
        if not result.success:
            print(f"Error: {result.error_message}")

    Notes:
        - Important implementation details
        - Performance considerations
        - Side effects

    Error Types:
        - "error_type_1": Description of this error type
        - "error_type_2": Description of this error type
    """
```

### 2. **Result Type Documentation**

```python
class SomeResult(NamedTuple):
    """
    Result of some operation.

    This named tuple provides a consistent, type-safe way to return operation
    results with rich error information and clear success/failure indicators.

    Attributes:
        field1 (Type1): Description of field1
        field2 (Type2): Description of field2
        success (bool): True if operation completed successfully
        error_message (str | None): Human-readable error message (None on success)
        error_type (str | None): Type of error for programmatic handling (None on success)

    Examples:
        # Success case
        result = SomeResult(
            field1=value1,
            field2=value2,
            success=True,
            error_message=None,
            error_type=None
        )

        # Error case
        result = SomeResult(
            field1=None,
            field2=None,
            success=False,
            error_message="Descriptive error message",
            error_type="specific_error_type"
        )

    Error Types:
        - "error_type_1": Description of this error type
        - "error_type_2": Description of this error type
    """
```

---

## Migration Strategies

### 1. **Parallel Implementation Pattern**

```python
# Original function (maintained for compatibility)
def original_function(param1, param2):
    """Original implementation."""
    # ... original logic ...
    return result

# Refactored function (new implementation)
def refactored_function(param1, param2) -> RefactoredResult:
    """Refactored implementation with improved error handling."""
    # ... refactored logic ...
    return RefactoredResult(...)

# Route that can use either implementation
@app.route('/endpoint', methods=['POST'])
def endpoint():
    """Endpoint that can use either original or refactored implementation."""
    if use_refactored_implementation():
        result = refactored_function(param1, param2)
        return handle_refactored_result(result)
    else:
        result = original_function(param1, param2)
        return handle_original_result(result)
```

### 2. **Feature Flag Pattern**

```python
def use_refactored_implementation() -> bool:
    """Determine whether to use refactored implementation."""
    # Can be controlled by environment variable, database setting, etc.
    return os.getenv('USE_REFACTORED_IMPLEMENTATION', 'false').lower() == 'true'

def handle_refactored_result(result: RefactoredResult):
    """Handle result from refactored implementation."""
    if result.success:
        return redirect(url_for('success_page'))
    else:
        return render_template('error.html', message=result.error_message)

def handle_original_result(result):
    """Handle result from original implementation."""
    # ... original result handling ...
```

---

## Performance Considerations

### 1. **Benchmarking Pattern**

```python
import time
from functools import wraps

def benchmark_function(func):
    """Decorator to benchmark function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        logger.info(f"{func.__name__} took {end_time - start_time:.3f} seconds")
        return result
    return wrapper

@benchmark_function
def function_to_benchmark(param1, param2):
    """Function that will be benchmarked."""
    # ... function implementation ...
```

### 2. **Performance Testing Pattern**

```python
def test_performance_comparison():
    """Compare performance of original vs refactored implementation."""
    test_data = create_large_test_dataset()

    # Benchmark original implementation
    start_time = time.time()
    original_result = original_function(test_data)
    original_time = time.time() - start_time

    # Benchmark refactored implementation
    start_time = time.time()
    refactored_result = refactored_function(test_data)
    refactored_time = time.time() - start_time

    # Assert performance is within acceptable bounds
    performance_ratio = refactored_time / original_time
    assert performance_ratio <= 1.1, f"Refactored implementation is {performance_ratio:.2f}x slower"
```

---

## Implementation Status ✅ **PHASE 2 COMPLETED**

### Completed Components

1. ✅ **Result Types**: All 7 result types implemented
2. ✅ **Helper Functions**: All 5 helper functions with result types implemented
3. ✅ **Route Helper Functions**: All 5 route helper functions implemented (Phase 1)
4. ✅ **Error Handling Helper Functions**: All 2 error handling helper functions implemented (Phase 2)
5. ✅ **Main Functions**: Both main functions updated to use new helpers
6. ✅ **Testing**: 53 tests passing (16 helper + 12 main function + 25 route helper tests)
7. ✅ **Backward Compatibility**: All original functions maintained

### Test Results

- **Helper Function Tests**: 16/16 passed (100%)
- **Main Function Tests**: 12/12 passed (100%)
- **Route Helper Tests**: 25/25 passed (100%)
- **Total Tests**: 53/53 passed (100%)

---

## Conclusion

This implementation guide provides the patterns and standards needed to complete the data ingestion refactor
successfully. The key principles are:

1. **Consistency**: Follow established patterns from the staging implementation
2. **Quality**: Comprehensive testing and documentation
3. **Safety**: Maintain backward compatibility throughout
4. **Performance**: Monitor and optimize as needed

**✅ COMPLETED**: The error handling helper functions have been successfully implemented, providing a major
architectural improvement that eliminates error handling duplication while maintaining full backward compatibility.

**Next Steps**: Phase 3 - Extract success handling logic into shared helper functions to complete the route refactoring.
