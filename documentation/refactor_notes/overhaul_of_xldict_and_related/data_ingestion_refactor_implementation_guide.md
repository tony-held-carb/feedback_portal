# Data Ingestion Refactor - Implementation Guide

## Overview

This document provides technical implementation guidance for developers working on the ARB Feedback Portal's data
ingestion refactor. It includes code patterns, standards, and practical examples based on the successful staging
implementation.

**Last Updated:** August 2025
**Target Audience:** Developers working on the refactor

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

### 2. **Helper Function Pattern**

Break complex operations into focused helper functions with single responsibilities.

#### Pattern Template

```python
def _helper_function_name(param1, param2) -> tuple[ResultType, str | None]:
    """
    Brief description of what this helper does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        tuple[ResultType, str | None]: (result, error_message)
        - result: The operation result (None if failed)
        - error_message: Error message if operation failed (None if successful)

    Examples:
        result, error = _helper_function_name(value1, value2)
        if result:
            # Use result
        else:
            # Handle error
    """
    try:
        # Perform the specific operation
        result = perform_operation(param1, param2)

        if result:
            return result, None
        else:
            return None, "Operation failed"

    except Exception as e:
        logger.error(f"Error in _helper_function_name: {e}")
        return None, f"Unexpected error: {e}"
```

### 3. **Main Function Pattern**

Main functions should orchestrate helper functions and return rich result objects.

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
    try:
        file_path = _save_uploaded_file(upload_dir, request_file, db, description="Operation description")
    except ValueError as e:
        return MainResult(
            # ... result fields ...
            success=False,
            error_message=str(e),
            error_type="file_error"
        )

    # Step 2: Convert file to JSON
    json_path, sector, json_data, error = _convert_file_to_json(file_path)
    if not json_path:
        return MainResult(
            # ... result fields ...
            success=False,
            error_message="Unsupported file format. Please upload Excel (.xlsx) file.",
            error_type="conversion_failed"
        )

    # Step 3: Validate data
    id_, error = _validate_id_from_json(json_data)
    if not id_:
        return MainResult(
            # ... result fields ...
            success=False,
            error_message=error,
            error_type="missing_id"
        )

    # Step 4: Perform main operation
    result, error = _perform_main_operation(id_, json_data, db, base)
    if error:
        return MainResult(
            # ... result fields ...
            success=False,
            error_message=error,
            error_type="operation_error"
        )

    # Success case
    return MainResult(
        # ... result fields ...
        success=True,
        error_message=None,
        error_type=None
    )
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

## Conclusion

This implementation guide provides the patterns and standards needed to complete the data ingestion refactor
successfully. The key principles are:

1. **Consistency**: Follow established patterns from the staging implementation
2. **Quality**: Comprehensive testing and documentation
3. **Safety**: Maintain backward compatibility throughout
4. **Performance**: Monitor and optimize as needed

**Next Steps**: Use these patterns to complete the `upload_and_process_file()` implementation and any additional helper
functions needed for the direct upload workflow.
