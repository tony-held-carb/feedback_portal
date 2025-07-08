# Upload Error Handling Improvements

## Overview

Enhanced error handling in the `upload_file` and `upload_file_staged` routes to provide more specific diagnostic information when uploads fail. The diagnostic logic has been extracted into reusable helper functions.

## Problem Analysis

### Original Issue
The upload routes had generic error handling that provided minimal information:
```
"Error: Could not process the uploaded file. Make sure it is closed and try again."
```

This generic message didn't help users understand:
- Whether the file was uploaded successfully
- Whether JSON conversion succeeded
- What sector/schema was detected
- Where exactly the failure occurred

### Failure Scenarios Identified

1. **File Upload Success, JSON Conversion Fails**
   - File is saved successfully
   - Excel parsing fails (schema issues, format problems, missing required tabs)
   - `convert_excel_to_json_if_valid()` returns `(None, None)`
   - User gets "format not recognized" message with enhanced diagnostics

2. **File Upload Success, JSON Conversion Success, Database Insertion Fails**
   - File is saved successfully
   - JSON is created successfully
   - Database insertion fails (constraint violations, data type issues)
   - Exception is thrown and caught in route's try/catch block
   - User gets enhanced error message with diagnostic info

**Note**: There is no scenario where JSON conversion succeeds but schema is not recognized. Schema recognition happens during Excel parsing, and if it fails, JSON conversion fails entirely.

## Solution Implemented

### Helper Functions Created

#### `generate_upload_diagnostics()`
Located in `arb.portal.utils.route_util`, this function analyzes what succeeded and what failed in the upload process:

**Parameters:**
- `request_file`: The uploaded file object from Flask request
- `file_path`: Optional path to the saved file
- `include_id_extraction`: Whether to include ID extraction diagnostics (for staged uploads)

**Returns:**
- `List[str]`: List of diagnostic messages with ✅/❌ indicators

#### `format_diagnostic_message()`
Formats diagnostic information into a user-friendly error message:

**Parameters:**
- `error_details`: List of diagnostic messages from `generate_upload_diagnostics()`
- `base_message`: Optional base error message to prepend

**Returns:**
- `str`: Formatted error message with diagnostic information

### Enhanced Error Handling

Both `upload_file` and `upload_file_staged` routes now provide detailed diagnostic information:

#### Diagnostic Information Provided

1. **File Upload Status**
   - ✅ Confirms if file was uploaded successfully
   - Shows original filename

2. **JSON Conversion Status**
   - ✅ Confirms if JSON file was created
   - Shows JSON filename

3. **Schema/Sector Detection**
   - ✅ Shows detected sector (e.g., "Landfill", "Oil and Gas")
   - ✅ Shows detected schema version (e.g., "landfill_v01_00")

4. **ID Extraction Status** (for staged uploads)
   - ✅ Shows extracted incidence ID
   - ❌ Indicates if ID extraction failed

5. **Failure Point Identification**
   - ❌ Database insertion failed - check data validity
   - ❌ Excel to JSON conversion failed - check file format and schema
   - ❌ Staging failed - check file structure and permissions

### Example Enhanced Error Messages

#### Scenario 1: JSON Conversion Fails (Schema Recognition Failure)
```
Uploaded file format not recognized. Diagnostic information:
✅ File 'my_upload.xlsx' was uploaded successfully
❌ Excel to JSON conversion failed - check file format and schema
```

#### Scenario 2: Database Insertion Fails
```
Error: Could not process the uploaded file. Diagnostic information:
✅ File 'my_upload.xlsx' was uploaded successfully
✅ JSON file was created: my_upload.json
✅ Detected sector: Landfill, schema: landfill_v01_00
❌ Database insertion failed - check data validity
```

#### Scenario 3: Staging Failure
```
Error: Could not process the uploaded file. Diagnostic information:
✅ File 'my_upload.xlsx' was uploaded successfully
✅ JSON file was created: my_upload.json
✅ Detected sector: Oil and Gas, schema: oil_and_gas_v01_00
✅ Extracted ID: 12345
❌ Staging failed - check file structure and permissions
```

## Benefits

1. **Better User Experience**
   - Users know exactly what succeeded and what failed
   - Clear guidance on what to check/fix
   - Enhanced diagnostics for schema recognition failures (previously minimal info)

2. **Easier Troubleshooting**
   - Developers can quickly identify failure points
   - Sector and schema information helps with debugging
   - Reusable diagnostic functions reduce code duplication

3. **Reduced Support Burden**
   - Users can self-diagnose many issues
   - More specific error messages reduce back-and-forth
   - Schema recognition failures now provide detailed diagnostics

## Technical Implementation

### Error Handling Strategy

1. **Progressive Diagnostics**
   - Check each step in the upload pipeline
   - Build diagnostic information incrementally
   - Gracefully handle partial failures

2. **Safe Information Extraction**
   - Use try/catch blocks around diagnostic code
   - Don't let diagnostic failures mask original errors
   - Provide fallback messages when diagnostics fail

3. **Consistent Format**
   - Use ✅/❌ symbols for visual clarity
   - Structured diagnostic information
   - Clear separation between success and failure indicators

4. **Reusable Helper Functions**
   - Extract common diagnostic logic into helper functions
   - Support both regular and staged uploads
   - Configurable diagnostic depth (with/without ID extraction)

### Code Changes

- **New helper functions** in `arb.portal.utils.route_util`:
  - `generate_upload_diagnostics()`
  - `format_diagnostic_message()`
- **Enhanced exception handling** in `upload_file()` route
- **Enhanced exception handling** in `upload_file_staged()` route
- **Enhanced schema recognition failure handling** in `upload_file()` route
- **Added diagnostic information extraction** from JSON files
- **Improved error message formatting**

## Future Enhancements

1. **Database Error Details**
   - Extract specific database constraint violation messages
   - Show which fields failed validation

2. **Schema Validation Details**
   - Show which schema fields are missing or invalid
   - Provide guidance on required vs optional fields

3. **File Format Validation**
   - Check Excel file structure before processing
   - Validate required tabs and metadata

4. **User-Friendly Suggestions**
   - Provide specific action items based on error type
   - Link to relevant documentation or examples 