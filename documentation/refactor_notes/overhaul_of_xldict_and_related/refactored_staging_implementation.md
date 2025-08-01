# Refactored Staging Implementation - January 2025

## Overview

This document describes the new refactored staging implementation that provides a more robust, maintainable, and user-friendly approach to file staging in the ARB Feedback Portal.

## Key Improvements

### 1. **Named Tuple Results**
- **Problem Solved**: Inconsistent return patterns and unclear error handling
- **Solution**: `StagingResult` named tuple with rich error information
- **Benefits**: Type-safe, self-documenting, extensible

### 2. **Modular Function Design**
- **Problem Solved**: Monolithic `upload_and_stage_only` function doing too much
- **Solution**: Broken into focused helper functions with single responsibilities
- **Benefits**: Easier to test, debug, and maintain

### 3. **Specific Error Handling**
- **Problem Solved**: Generic error messages that don't help users
- **Solution**: Specific error types and messages for different failure scenarios
- **Benefits**: Better user experience, easier debugging

## Implementation Details

### StagingResult Named Tuple

```python
class StagingResult(NamedTuple):
    file_path: Path
    id_: int | None
    sector: str | None
    json_data: dict
    staged_filename: str | None
    success: bool
    error_message: str | None
    error_type: str | None
```

**Error Types:**
- `"missing_id"`: No valid id_incidence found in the file
- `"conversion_failed"`: File could not be converted to JSON
- `"file_error"`: Error uploading or saving the file
- `"validation_failed"`: Other validation errors
- `"database_error"`: Error accessing database for base_misc_json

### Main Function: `stage_uploaded_file_for_review`

```python
def stage_uploaded_file_for_review(db: SQLAlchemy,
                                 upload_dir: str | Path,
                                 request_file: FileStorage,
                                 base: AutomapBase) -> StagingResult:
```

**Workflow:**
1. **Save uploaded file** - `_save_uploaded_file()`
2. **Convert to JSON** - `_convert_file_to_json()`
3. **Validate and extract ID** - `_validate_and_extract_id()`
4. **Create staged file** - `_create_staged_file()`

### Helper Functions

#### `_save_uploaded_file()`
- Saves uploaded file to upload directory
- Adds file to upload table for tracking
- Returns file path or raises ValueError on failure

#### `_convert_file_to_json()`
- Converts Excel/JSON files to standardized JSON format
- Extracts sector information
- Returns (json_path, sector) or (None, None) on failure

#### `_validate_and_extract_id()`
- Loads JSON data and extracts id_incidence
- Validates ID is positive integer
- Returns (id_, json_data) or (None, json_data) on failure

#### `_create_staged_file()`
- Gets current database state for comparison
- Creates timestamped staged file with metadata
- Returns staged filename or None on failure

## New Route: `upload_file_staged_refactored`

### URL
- `GET /upload_staged_refactored` - Display upload form
- `POST /upload_staged_refactored` - Process file upload

### Error Handling

```python
result = stage_uploaded_file_for_review(db, upload_folder, request_file, base)

if result.success:
    # Success case - redirect to review page
    flash(f"File staged successfully: {result.staged_filename}")
    return redirect(url_for('main.review_staged', id_=result.id_, filename=result.staged_filename))
else:
    # Handle specific error types
    if result.error_type == "missing_id":
        flash("Please add a valid ID to your spreadsheet")
    elif result.error_type == "conversion_failed":
        flash("Please upload an Excel file")
    elif result.error_type == "file_error":
        flash(f"File upload error: {result.error_message}")
    elif result.error_type == "database_error":
        flash(f"Database error during staging: {result.error_message}")
    else:
        flash(f"Unexpected error: {result.error_message}")
```

## Comparison with Original Implementation

### Original Approach
```python
# Inconsistent return patterns
file_path, id_, sector, json_data, staged_filename = upload_and_stage_only(...)

if id_ and staged_filename:
    # Success
else:
    # Failure - but WHAT failed?
    # Route has to guess based on return values
```

### Refactored Approach
```python
# Consistent, rich return information
result = stage_uploaded_file_for_review(...)

if result.success:
    # Success - clear and explicit
else:
    # Specific error handling based on error_type
    # Clear error messages for users
```

## Benefits

### 1. **Better User Experience**
- **Specific error messages** instead of generic ones
- **Clear guidance** on what went wrong and how to fix it
- **Consistent behavior** across different error scenarios

### 2. **Improved Maintainability**
- **Modular functions** with single responsibilities
- **Clear separation of concerns** between steps
- **Easy to test** individual components
- **Self-documenting code** with named tuple fields

### 3. **Enhanced Debugging**
- **Rich error information** with specific error types
- **Detailed logging** at each step
- **Easy to trace** where failures occur
- **Better diagnostic information** for support

### 4. **Type Safety**
- **Named tuple** provides type hints and validation
- **Clear interfaces** between functions
- **IDE support** for autocomplete and error detection

## Testing Strategy

### Unit Tests
- **Individual helper functions** tested in isolation
- **Mock dependencies** to test specific failure scenarios
- **Edge cases** covered (missing files, invalid data, etc.)

### Integration Tests
- **End-to-end workflow** testing
- **Route behavior** with different error conditions
- **User experience** validation

### Test Coverage
- **Success scenarios** - valid files with proper data
- **Error scenarios** - missing ID, conversion failures, file errors
- **Edge cases** - empty files, invalid formats, database errors

## Migration Strategy

### Phase 1: Parallel Implementation ✅
- ✅ Created new functions alongside existing ones
- ✅ No changes to existing code
- ✅ Comprehensive tests added

### Phase 2: Testing and Validation
- [ ] Run tests to ensure functionality
- [ ] Manual testing with real files
- [ ] Compare behavior with original implementation

### Phase 3: Gradual Migration
- [ ] Start using new route in development
- [ ] Monitor for any issues
- [ ] Gradually migrate users to new route

### Phase 4: Cleanup
- [ ] Remove old implementation once confident
- [ ] Update documentation
- [ ] Archive old code

## Usage Examples

### Basic Usage
```python
from arb.portal.utils.db_ingest_util import stage_uploaded_file_for_review

# Stage a file for review
result = stage_uploaded_file_for_review(db, upload_dir, request_file, base)

if result.success:
    print(f"File staged successfully: {result.staged_filename}")
    print(f"ID: {result.id_}, Sector: {result.sector}")
else:
    print(f"Staging failed: {result.error_message}")
    print(f"Error type: {result.error_type}")
```

### Error Handling
```python
# Handle specific error types
if result.error_type == "missing_id":
    # Guide user to add ID to spreadsheet
    user_message = "Please add a valid 'Incidence/Emission ID' to your spreadsheet"
elif result.error_type == "conversion_failed":
    # Guide user to upload correct file format
    user_message = "Please upload an Excel (.xlsx) file"
elif result.error_type == "file_error":
    # Technical error - log for debugging
    logger.error(f"File upload error: {result.error_message}")
    user_message = "File upload failed. Please try again."
else:
    # Generic error handling
    user_message = f"Error: {result.error_message}"
```

### Route Integration
```python
@app.route('/upload_staged_refactored', methods=['POST'])
def upload_file_staged_refactored():
    request_file = request.files.get('file')
    
    if not request_file:
        return render_template('upload.html', message="No file selected")
    
    result = stage_uploaded_file_for_review(db, upload_dir, request_file, base)
    
    if result.success:
        flash(f"File staged successfully: {result.staged_filename}")
        return redirect(url_for('review_staged', id_=result.id_, filename=result.staged_filename))
    else:
        return render_template('upload.html', message=result.error_message)
```

## Future Enhancements

### 1. **Additional Error Types**
- `"validation_failed"` - for other validation errors
- `"permission_denied"` - for file permission issues
- `"quota_exceeded"` - for storage quota issues

### 2. **Enhanced Metadata**
- File size and type validation
- Virus scanning results
- Processing time metrics

### 3. **Async Processing**
- Background file processing for large files
- Progress tracking and status updates
- Cancellation support

### 4. **Validation Extensions**
- Custom validation rules
- Sector-specific validation
- Data quality checks

## Conclusion

The refactored staging implementation provides a significant improvement over the original approach:

- **Better user experience** with specific error messages
- **Improved maintainability** with modular design
- **Enhanced debugging** with rich error information
- **Type safety** with named tuples
- **Comprehensive testing** strategy

This implementation serves as a model for future refactoring efforts in the ARB Feedback Portal, demonstrating how to improve code quality while maintaining backward compatibility and user experience. 