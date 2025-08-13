# Excel Test Data Directory

This directory contains test Excel files and data for comprehensive testing of the Excel parsing functionality.

## Test Files Structure

### Sample Excel Files (to be created)
- `sample_metadata.xlsx` - Excel file with metadata tab
- `sample_schema.xlsx` - Excel file with schema tab  
- `sample_data.xlsx` - Excel file with data tab
- `sample_complete.xlsx` - Complete Excel file with all tabs
- `sample_invalid.xlsx` - Excel file with invalid data for error testing

### Test Data Files
- `sample_schema_map.json` - Sample schema mapping for testing
- `sample_expected_output.json` - Expected output for validation tests

## Usage

These test files are used by the comprehensive test suite to verify:
- Normal Excel parsing functionality
- Edge cases and error conditions
- Function equivalence between original and _2 versions
- Input validation and error handling

## Note

Currently, this directory contains placeholder files. In a production testing environment,
you would populate this with actual Excel files that represent real-world scenarios
and edge cases for comprehensive testing.
