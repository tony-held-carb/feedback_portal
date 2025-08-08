# Documentation Protocol: Enabling Automation and Better Testing

## Overview

This protocol establishes comprehensive documentation standards that directly support two critical goals:

1. **Automated Documentation Generation** via mkdocs/mkdocstrings
2. **Enhanced Unit Testing** through clear understanding of intended behavior and edge cases

Following this protocol ensures that documentation serves as both human-readable guidance and machine-readable metadata
for automation tools.

---

## 1. Core Documentation Principles

### 1.1 Documentation as Contract

- **Purpose**: Every function, class, and module docstring serves as a contract between the code and its users
- **Benefit**: Enables automated testing by clearly defining expected inputs, outputs, and behaviors
- **Automation Impact**: mkdocstrings can parse these contracts to generate comprehensive API documentation

### 1.2 Complete Parameter Documentation

```python
def process_upload(file_path: str, validate_schema: bool = True) -> UploadResult:
  """Process an uploaded file and return validation results.

  Args:
    file_path (str): Path to the uploaded file. Must be a valid Excel (.xlsx) file.
    validate_schema (bool): Whether to validate against known schemas. Defaults to True.
      If False, only basic file format validation is performed.

  Returns:
    UploadResult: Object containing validation status and any errors found.
      - success: True if file processed successfully
      - errors: List of validation error messages
      - warnings: List of non-critical warnings

  Raises:
    FileNotFoundError: If file_path doesn't exist
    ValueError: If file is not a valid Excel format
    SchemaValidationError: If validate_schema=True and file doesn't match expected schema

  Notes:
    This function is the main entry point for file processing. It handles both
    basic file validation and optional schema validation. The function is designed
    to be robust and provide detailed error information for debugging.

  Supplemental Notes:
    [PERSONAL NOTES - DO NOT MODIFY] This function was refactored from the original
    upload_and_update_db function to separate concerns. The original function was
    doing too much - file processing, validation, and database updates all in one
    place. This separation makes it much easier to test and maintain.
  """
```

**Testing Benefits**:

- Clear input validation requirements
- Explicit error conditions to test
- Return type structure for assertions
- Edge cases (e.g., `validate_schema=False`) identified

### 1.3 Edge Case Documentation

```python
def resolve_sector(json_sector: str | None, fk_sector: str | None) -> str:
  """Resolve sector from multiple sources with priority rules.

  Args:
    json_sector (str | None): Sector from JSON data, may be None
    fk_sector (str | None): Sector from foreign key lookup, may be None

  Returns:
    str: Resolved sector value

  Raises:
    ValueError: If both sources are None or contain conflicting non-None values

  Edge Cases:
    - Both None: Raises ValueError
    - One None, one valid: Returns the valid value
    - Both valid, same value: Returns the value
    - Both valid, different values: JSON sector takes priority, logs warning

  Notes:
    This function implements a priority system where JSON data takes precedence
    over foreign key data. This design choice was made because JSON data is
    typically more current and user-provided.

  Supplemental Notes:
    [PERSONAL NOTES - DO NOT MODIFY] The original implementation was inconsistent
    about which source to trust. This priority system was implemented after
    discovering that some records had conflicting sector information between
    JSON and foreign key sources. The logging of warnings helps track when
    conflicts occur without breaking the application.
  """
```

**Testing Benefits**:

- All edge cases explicitly documented
- Clear test scenarios for each combination
- Error conditions clearly defined

---

## 2. Module-Level Documentation

### 2.1 Module Purpose and Scope

```python
"""Excel file processing and validation utilities.

This module provides functions for processing uploaded Excel files, validating
their structure against known schemas, and converting data to JSON format
for database storage.

Key Functions:
- process_upload(): Main entry point for file processing
- validate_schema(): Check file structure against known schemas
- convert_to_json(): Transform Excel data to JSON format

Dependencies:
- openpyxl: Excel file reading
- pandas: Data manipulation
- jsonschema: Schema validation

Usage Example:
    result = process_upload("data.xlsx", validate_schema=True)
    if result.success:
        print(f"Processed {len(result.data)} rows")
    else:
        print(f"Errors: {result.errors}")

Notes:
    This module was designed to handle the specific requirements of the ARB
    feedback portal, including support for multiple feedback form types and
    strict validation requirements.

Supplemental Notes:
    [PERSONAL NOTES - DO NOT MODIFY] This module was created during the major
    refactor of 2025 to replace the monolithic upload_and_update_db function.
    The separation of concerns here has made the codebase much more maintainable
    and testable. The original approach was causing issues with testing and
    debugging because everything was tightly coupled.
"""
```

**Automation Benefits**:

- mkdocs can generate module overview pages
- Dependencies clearly listed for automation tools
- Usage examples provide immediate context

### 2.2 Class Documentation

```python
class UploadResult:
  """Result object for file upload processing operations.

  This class encapsulates the outcome of file processing operations,
  including success status, validation results, and any errors or warnings
  encountered during processing.

  Attributes:
    success: True if processing completed without critical errors
    data: Processed data (dict or list) if successful
    errors: List of error messages for critical failures
    warnings: List of warning messages for non-critical issues
    processing_time: Time taken for processing in seconds
    file_size: Size of processed file in bytes

  Example:
    result = UploadResult(
      success=True,
      data={"rows": 150, "columns": 10},
      warnings=["Column 'notes' contains empty values"]
    )

  Notes:
    This class follows the Result pattern to provide a consistent interface
    for handling both successful and failed operations. It includes timing
    information to help with performance monitoring.

  Supplemental Notes:
    [PERSONAL NOTES - DO NOT MODIFY] I chose to use a simple class instead of
    a dataclass or TypedDict because I wanted to maintain control over the
    attribute structure and add methods later if needed. The timing information
    was added after discovering that some file processing was taking longer
    than expected, and this helps with debugging performance issues.
  """
```

**Testing Benefits**:

- Clear attribute structure for test assertions
- Expected data types and formats
- Example usage for test case design

---

## 3. Type Hints and Documentation Alignment

### 3.1 Dual Type Documentation Strategy

**Best Practice**: Include type hints in both function signatures and docstrings.

**Rationale**:

- **Function signatures**: For automated tools (mkdocs, IDEs, static analyzers)
- **Docstrings**: For human readability and detailed type descriptions

This approach provides the best of both worlds - machine-readable metadata and human-friendly documentation.

### 3.2 Notes and Supplemental Notes Sections

**Best Practice**: Include both "Notes" and "Supplemental Notes" sections in docstrings.

**Rationale**:

- **Notes**: Standard documentation that can be updated during refactoring
- **Supplemental Notes**: Personal insights marked with "[PERSONAL NOTES - DO NOT MODIFY]" that should not be changed by
  AI

This separation allows for both maintainable documentation and preservation of personal insights and historical context.

### 3.3 Example Documentation Format

**Best Practice**: Use "Input/Output" format for examples to avoid IDE issues with `>>>` syntax.

**Standard Format**:

```
Examples:
    Input: function_call(arg1, arg2)
    Output: expected_result

    Input: function_call(edge_case)
    Output: expected_result (with explanation if needed)
```

**Rationale**:

- **IDE-friendly**: No `>>>` syntax that confuses IDE syntax checkers
- **Clear separation**: Input and output are clearly distinguished
- **Copy-paste friendly**: Easy to use in actual code
- **Flexible**: Can include explanatory text in output descriptions

**Alternative approaches** (consider case-by-case):

- **Inline comments**: `function_call(arg)  # Returns: result`
- **Table format**: For complex examples with multiple parameters
- **Code blocks with comments**: For multi-step examples

### 3.4 Consistent Type Documentation

```python
from typing import TypedDict, Literal

class ValidationError(TypedDict):
  """Structure for validation error messages.

  Attributes:
    field: Name of the field with the error
    message: Human-readable error description
    severity: Error severity level
  """
  field: str
  message: str
  severity: Literal["error", "warning", "info"]

def validate_excel_file(file_path: str) -> list[ValidationError]:
  """Validate Excel file structure and content.

  Args:
    file_path (str): Path to Excel file to validate

  Returns:
    list[ValidationError]: List of validation errors found. Empty list means file is valid.

  Notes:
    This function performs comprehensive validation including file format,
    required columns, data types, and business rule validation.

  Supplemental Notes:
    [PERSONAL NOTES - DO NOT MODIFY] The ValidationError TypedDict was chosen
    over a dataclass because it's more lightweight and works better with
    JSON serialization. The severity levels were added after realizing that
    not all validation issues should be treated equally - some are warnings
    that don't prevent processing.
  """
```

**Automation Benefits**:

- mkdocstrings can generate type documentation from function signatures
- IDE autocomplete and type checking from signatures
- Human-readable type descriptions in docstrings
- Clear return type structure for testing

### 3.5 Union Types and Optional Values

```python
def get_user_preferences(user_id: int | None = None) -> dict[str, str] | None:
  """Retrieve user preferences from database or cache.

  Args:
    user_id (int | None): User ID to look up. If None, uses current session user.

  Returns:
    dict[str, str] | None: Dictionary of user preferences, or None if user not found.
    Common keys: 'theme', 'language', 'notifications_enabled'

  Edge Cases:
    - user_id=None, no active session: Returns None
    - user_id provided but user doesn't exist: Returns None
    - user_id provided, user exists but no preferences: Returns empty dict

  Notes:
    This function implements a fallback strategy where it first checks the cache,
    then the database, and finally returns default preferences if nothing is found.

  Supplemental Notes:
    [PERSONAL NOTES - DO NOT MODIFY] The caching layer was added after performance
    testing showed that user preferences were being queried frequently. The
    fallback to default preferences instead of None was a design decision to
    ensure the UI always has sensible defaults, even for new users.
  """
```

**Testing Benefits**:

- All possible return types documented
- Edge cases for None values identified
- Clear test scenarios for each path

---

## 4. Error Handling Documentation

### 4.1 Comprehensive Exception Documentation

```python
class SchemaValidationError(ValueError):
  """Raised when uploaded file doesn't match expected schema.

  This exception is raised when an Excel file's structure doesn't match
  the expected schema for the given feedback form type.

  Attributes:
    schema_name: Name of the expected schema
    actual_columns: List of columns found in the file
    expected_columns: List of columns expected by the schema
    missing_columns: Columns that should be present but aren't
    extra_columns: Columns present but not expected
  """

  def __init__(self, schema_name: str, actual_columns: list[str],
               expected_columns: list[str]):
    self.schema_name = schema_name
    self.actual_columns = actual_columns
    self.expected_columns = expected_columns
    self.missing_columns = [col for col in expected_columns if col not in actual_columns]
    self.extra_columns = [col for col in actual_columns if col not in expected_columns]

    message = f"File doesn't match schema '{schema_name}'. "
    if self.missing_columns:
      message += f"Missing columns: {self.missing_columns}. "
    if self.extra_columns:
      message += f"Unexpected columns: {self.extra_columns}."

    super().__init__(message)

  Notes:
    This exception provides detailed information about schema mismatches to
    help users understand exactly what's wrong with their uploaded files.

  Supplemental Notes:
    [PERSONAL NOTES - DO NOT MODIFY] The detailed attribute structure was
    added after users complained that generic "schema validation failed"
    messages weren't helpful. The computed missing_columns and extra_columns
    attributes make it much easier to provide specific guidance to users
    about how to fix their files.
  """
```

**Testing Benefits**:

- Clear exception structure for test assertions
- Specific error conditions to test
- Attribute access for detailed error checking

### 4.2 Error Recovery Documentation

```python
def safe_json_parse(json_string: str, default: dict = None) -> dict:
  """Safely parse JSON string with fallback behavior.

  Args:
    json_string (str): JSON string to parse
    default (dict): Default value to return on parse failure. Defaults to empty dict.

  Returns:
    dict: Parsed JSON as dictionary, or default value if parsing fails.

  Edge Cases:
    - Empty string: Returns default value
    - Malformed JSON: Returns default value, logs warning
    - Valid JSON but not dict: Returns default value, logs warning
    - None input: Returns default value

  Notes:
    This function is designed to handle gracefully any JSON parsing errors
    that might occur when reading data from the database or external sources.

  Supplemental Notes:
    [PERSONAL NOTES - DO NOT MODIFY] This function was created after discovering
    that some JSON data in the database was malformed, causing crashes when
    trying to parse it. The logging of warnings helps track down the source
    of malformed data without breaking the application. The default to empty
    dict instead of None was chosen to prevent downstream None checks.
  """
```

**Testing Benefits**:

- All failure modes documented
- Clear fallback behavior
- Logging expectations for test verification

---

## 5. Examples and Usage Patterns

### 5.1 Comprehensive Examples

```python
def process_feedback_form(file_path: str, form_type: str) -> ProcessingResult:
  """Process a feedback form Excel file.

  Args:
    file_path (str): Path to Excel file
    form_type (str): Type of feedback form ('energy', 'dairy', 'landfill')

  Returns:
    ProcessingResult: ProcessingResult with validation status and processed data

  Raises:
    FileNotFoundError: If file doesn't exist
    SchemaValidationError: If file doesn't match expected schema
    DataValidationError: If data fails business rule validation

  Examples:
    Input: result = process_feedback_form("data.xlsx", "energy")
    Output: ProcessingResult object with success=True and processed data

    Input: if result.success:
              print(f"Processed {len(result.data)} records")
           else:
              print(f"Errors: {result.errors}")
    Output: "Processed 150 records" (if successful)
            "Errors: ['Column missing: contact_email']" (if failed)

    Input: try:
              result = process_feedback_form("invalid.xlsx", "energy")
           except SchemaValidationError as e:
              print(f"Schema mismatch: {e.missing_columns}")
    Output: "Schema mismatch: ['contact_email', 'facility_name']"

  Notes:
    This function orchestrates the complete feedback form processing pipeline,
    including validation, data transformation, and result compilation.

  Supplemental Notes:
    [PERSONAL NOTES - DO NOT MODIFY] The form_type parameter was added to support
    multiple feedback form types after the initial implementation only handled
    energy forms. The examples section was expanded to show both success and
    error handling patterns that are commonly used in the codebase.
  """
```

**Testing Benefits**:

- Clear usage patterns for test design
- Error handling examples
- Expected output formats

### 5.2 Edge Case Examples

```python
def validate_phone_number(phone: str | None) -> bool:
  """Validate phone number format.

  Args:
    phone (str | None): Phone number string to validate

  Returns:
    bool: True if valid format, False otherwise

  Examples:
    Input: validate_phone_number("(555) 123-4567")
    Output: True

    Input: validate_phone_number("555-123-4567")
    Output: True

    Input: validate_phone_number("5551234567")
    Output: True

    Input: validate_phone_number("123")
    Output: False (too short)

    Input: validate_phone_number("abc-def-ghij")
    Output: False (non-numeric)

    Input: validate_phone_number(None)
    Output: False (None not allowed)

    Input: validate_phone_number("")
    Output: False (empty string)

  Notes:
    This function uses regex patterns to validate common US phone number formats.
    It's designed to be flexible enough to handle various input formats while
    still ensuring the number is valid.

  Supplemental Notes:
    [PERSONAL NOTES - DO NOT MODIFY] The phone validation was originally much
    stricter, but was relaxed after users complained about valid phone numbers
    being rejected. The current regex patterns were chosen based on the most
    common formats found in the actual data. The explicit examples were added
    after several support tickets about phone validation issues.
  """
```

**Testing Benefits**:

- Specific test cases provided
- Edge cases clearly identified
- Expected behavior for each case

---

## 6. Automation Integration

### 6.1 mkdocs Configuration Alignment

```yaml
# mkdocs.yml
plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google  # Matches our protocol
            show_source: true        # Shows source code
            show_signature: true     # Shows function signatures
            separate_signature: true # Better formatting
            heading_level: 2         # Proper heading hierarchy
            merge_init_into_class: true  # Better class docs
```

**Benefits**:

- Consistent documentation generation
- Type hints automatically included
- Source code visibility for developers

### 6.2 Test Generation Hints

```python
def calculate_emissions(fuel_consumption: float, emission_factor: float) -> float:
  """Calculate emissions from fuel consumption.

  Args:
    fuel_consumption (float): Fuel consumption in gallons
    emission_factor (float): Emission factor in kg CO2/gallon

  Returns:
    float: Total emissions in kg CO2

  Test Cases:
    Input: calculate_emissions(100, 8.9)
    Output: 890.0

    Input: calculate_emissions(0, 8.9)
    Output: 0.0

    Input: calculate_emissions(10000, 8.9)
    Output: 89000.0

    Input: calculate_emissions(-100, 8.9)
    Output: ValueError (negative values not allowed)

    Input: calculate_emissions(None, 8.9)
    Output: TypeError (None values not allowed)

  Notes:
    This function performs a simple multiplication but includes validation
    to ensure inputs are positive numbers. The emission factors are based
    on EPA standards for different fuel types.

  Supplemental Notes:
    [PERSONAL NOTES - DO NOT MODIFY] The Test Cases section was added to this
    protocol specifically because I found that having explicit test scenarios
    in the docstring makes it much easier to write comprehensive unit tests.
    The edge cases (negative values, None) were discovered during testing and
    added to prevent runtime errors. The specific emission factor of 8.9 is
    the EPA standard for gasoline.
  """
```

**Benefits**:

- Clear test scenarios
- Expected outputs for assertions
- Edge cases identified

---

## 7. Quality Assurance Checklist

### 7.1 Documentation Completeness

- [ ] All functions have docstrings
- [ ] All parameters documented with types
- [ ] Return values documented with types
- [ ] Exceptions documented
- [ ] Edge cases identified
- [ ] Examples provided for complex functions
- [ ] Module-level documentation present
- [ ] Notes section included for additional context
- [ ] Supplemental Notes section included for personal insights (marked as DO NOT MODIFY)

### 7.2 Automation Readiness

- [ ] Type hints present in both function signatures and docstrings
- [ ] Google-style docstrings used consistently
- [ ] No `Args: None` or `Returns: None` boilerplate
- [ ] Examples use Input/Output format (avoid `>>>` syntax)
- [ ] Complex types use TypedDict or dataclasses
- [ ] Type hints in docstrings match function signature types

### 7.3 Testing Support

- [ ] Edge cases documented
- [ ] Error conditions clearly specified
- [ ] Return value structure documented
- [ ] Example inputs/outputs provided
- [ ] Exception types and messages documented

---

## 8. Benefits Realization

### 8.1 Automated Documentation

- **mkdocs Integration**: All docstrings automatically appear in generated documentation
- **Type Safety**: Type hints in signatures enable better IDE support and static analysis
- **Human Readability**: Type hints in docstrings provide clear, readable type descriptions
- **Consistency**: Standardized format ensures uniform documentation
- **Dual Purpose**: Signatures for tools, docstrings for humans

### 8.2 Enhanced Testing

- **Clear Contracts**: Function behavior is explicitly documented
- **Edge Case Coverage**: All edge cases identified for comprehensive testing
- **Error Testing**: Exception conditions clearly defined
- **Assertion Design**: Return types and structures enable precise assertions

### 8.3 Maintenance Benefits

- **Self-Documenting Code**: Documentation stays current with code changes
- **Onboarding**: New developers can understand system quickly
- **Debugging**: Clear error messages and expected behaviors
- **Refactoring**: Contracts help ensure changes don't break expectations

---

## 9. Implementation Strategy

### 9.1 Immediate Actions

1. **Audit Existing Code**: Review current docstrings against this protocol
2. **Update Critical Functions**: Focus on public APIs and complex logic
3. **Add Type Hints**: Gradually add type hints to existing functions
4. **Document Edge Cases**: Identify and document edge cases in existing code

### 9.2 Long-term Maintenance

1. **Code Review Integration**: Include documentation checks in review process
2. **Automated Validation**: Consider tools to validate documentation completeness
3. **Regular Audits**: Periodic reviews to ensure documentation stays current
4. **Team Training**: Ensure all team members understand and follow the protocol

---

*This protocol ensures that documentation serves both human readers and automated tools, enabling better testing,
clearer APIs, and more maintainable codebases.*
