# Feedback Form File Testing Automation

## Overview

This document outlines the comprehensive approach to automating testing of feedback form Excel files through the web UI, covering both the current implementation and future expansion options.

## Current Implementation

### Phase 1: Backend Integration Testing

**File:** `tests/arb/portal/test_file_upload_suite.py`

**Features:**
- Uses actual Excel files from `feedback_forms/testing_versions/` folder
- Tests both `/upload` and `/upload_staged` endpoints
- Validates presence of key fields in rendered forms
- Checks for successful redirects and form loading
- Includes error handling tests for invalid and corrupted files
- Provides parameterized tests for each sector and file type

**Test Runner:** `scripts/run_upload_tests.py`
- Options for quick or full runs
- Verbosity control
- Sector filtering
- Output saving to files

**Coverage:**
- All major feedback form types (dairy digester, energy, landfill, oil & gas)
- Both .xlsx and .xlsm file formats
- Error scenarios (corrupted files, invalid formats)
- Form rendering validation

## Expansion Options

### 1. Field-Level Value Assertions

**Purpose:** Verify that specific field values are correctly extracted and displayed in forms.

**Implementation:**
- Parse Excel files to extract expected field values
- Compare form field values against expected values
- Validate data types and formatting
- Test conditional field visibility based on form logic

**Benefits:**
- Ensures data integrity through the upload process
- Catches field mapping errors
- Validates form logic and conditional displays

### 2. Database State Verification

**Purpose:** Verify that uploaded data is correctly stored in the database.

**Implementation:**
- Query database after upload to verify data persistence
- Compare database records against original Excel data
- Validate foreign key relationships
- Test data type conversions and constraints

**Benefits:**
- End-to-end data flow validation
- Database schema compliance verification
- Data integrity assurance

### 3. Direct Database State Verification

**Purpose:** Comprehensive database validation after file processing.

**Implementation:**
- Query uploaded_file table for file metadata
- Query portal_update table for form data
- Validate all field mappings and data types
- Test relationship integrity

### 4. Negative Tests for Validation Errors

**Purpose:** Ensure proper error handling for invalid inputs.

**Implementation:**
- Test files with missing required fields
- Test files with invalid data types
- Test files exceeding size limits
- Test files with malformed structures

### 5. Round-Trip Export/Import Consistency

**Purpose:** Verify data consistency through export and re-import cycles.

**Implementation:**
- Export processed data back to Excel
- Re-import exported data
- Compare original vs. re-imported data
- Validate no data loss or corruption

### 6. Cross-Field and Conditional Logic Tests

**Purpose:** Test complex form validation and business logic.

**Implementation:**
- Test contingent field visibility
- Test cross-field validation rules
- Test conditional dropdown population
- Test regulatory compliance logic

### 7. Full UI/UX E2E Automation

**Purpose:** Complete end-to-end testing including user interface.

**Implementation:**
- Selenium WebDriver for browser automation
- Simulate drag-and-drop file uploads
- Test form interactions and submissions
- Validate user experience flows

### 8. Performance and Stress Testing

**Purpose:** Ensure system performance under load.

**Implementation:**
- Test multiple concurrent uploads
- Test large file processing
- Measure upload and processing times
- Test memory usage and cleanup

### 9. Security and Permissions Testing

**Purpose:** Validate security measures and access controls.

**Implementation:**
- Test file type restrictions
- Test file size limits
- Test malicious file handling
- Test authentication requirements

### 10. Regression Tests for Known Bugs

**Purpose:** Prevent regression of previously fixed issues.

**Implementation:**
- Maintain test cases for historical bugs
- Include edge cases that caused problems
- Test workarounds and fixes
- Validate bug fixes remain effective

### 11. CI Integration and Coverage Reporting

**Purpose:** Automated testing in continuous integration.

**Implementation:**
- GitHub Actions or similar CI/CD integration
- Automated test execution on code changes
- Coverage reporting and trending
- Test result notifications

### 12. Automated Test Data Generation

**Purpose:** Generate diverse test data automatically.

**Implementation:**
- Create Excel files with various data combinations
- Generate edge case scenarios
- Create files with different formats and structures
- Maintain test data versioning

### 13. Accessibility and Internationalization Testing

**Purpose:** Ensure accessibility and i18n compliance.

**Implementation:**
- Test screen reader compatibility
- Test keyboard navigation
- Test different language settings
- Test cultural formatting requirements

### 14. Snapshot Testing

**Purpose:** Detect unexpected changes in form rendering.

**Implementation:**
- Capture form HTML snapshots
- Compare against baseline snapshots
- Detect visual and structural changes
- Maintain snapshot versioning

### 15. Documentation and Test Review

**Purpose:** Maintain comprehensive test documentation.

**Implementation:**
- Document test scenarios and expected outcomes
- Maintain test data inventory
- Review and update test coverage
- Track test execution metrics

## Implementation Priority

### High Priority (Immediate)
1. Field-Level Value Assertions
2. Database State Verification
3. Negative Tests for Validation Errors

### Medium Priority (Next Phase)
4. Cross-Field and Conditional Logic Tests
5. Round-Trip Export/Import Consistency
6. Performance and Stress Testing

### Lower Priority (Future)
7. Full UI/UX E2E Automation
8. Security and Permissions Testing
9. CI Integration and Coverage Reporting

## Technical Considerations

### Test Data Management
- Maintain separate test data repository
- Version control for test files
- Automated test data generation
- Cleanup procedures for test artifacts

### Environment Requirements
- Isolated test database
- File system permissions for uploads
- Network access for external dependencies
- Consistent test environment setup

### Performance Impact
- Test execution time optimization
- Parallel test execution
- Resource cleanup between tests
- Memory and disk usage monitoring

### Maintenance
- Regular test data updates
- Test case review and cleanup
- Documentation updates
- Test result analysis and reporting

## Success Metrics

### Coverage Metrics
- Percentage of form fields tested
- Percentage of business logic paths covered
- Percentage of error scenarios tested
- Database operation coverage

### Quality Metrics
- Test execution time
- Test reliability (flaky test rate)
- Bug detection rate
- False positive rate

### Process Metrics
- Time to detect regressions
- Time to validate fixes
- Test maintenance effort
- Documentation completeness 