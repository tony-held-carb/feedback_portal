# Excel Testing Suite

This directory contains comprehensive testing for Excel parsing functionality using real test files and expected results.

## Overview

The Excel testing suite provides two levels of testing:

1. **Basic Unit Tests** (`test_xl_parse.py`) - Tests individual functions with mocked data
2. **Functional Equivalence Tests** (`test_excel_functional_equivalence.py`) - Tests with real Excel files and validates against expected results

## Test Files

### `test_xl_parse.py`
- **Purpose**: Basic unit testing of Excel functions
- **Coverage**: All Excel parsing functions with mocked data
- **Status**: ✅ Complete and passing (32 tests)

### `test_excel_functional_equivalence.py`
- **Purpose**: Real-world testing using actual feedback form files
- **Coverage**: Function equivalence between original and `_2` versions
- **Data Source**: `feedback_forms/testing_versions/standard/`
- **Expected Results**: `feedback_forms/testing_versions/standard/expected_results/`

### `excel_content_validator.py`
- **Purpose**: Utilities for comparing Excel parsing results against expected results
- **Features**: Timestamp normalization, structure validation, content comparison

## Test Data

### Input Files
Located in `feedback_forms/testing_versions/standard/`:
- **Good Data Files**: `*_test_01_good_data.xlsx`
- **Bad Data Files**: `*_test_02_bad_data.xlsx`
- **Blank Files**: `*_test_03_blank.xlsx`

### Feedback Form Types
- `landfill_operator` - Landfill operator feedback forms
- `oil_and_gas_operator` - Oil and gas operator feedback forms
- `dairy_digester` - Dairy digester operator feedback forms
- `energy_operator` - Energy operator feedback forms
- `generic_operator` - Generic operator feedback forms

### Expected Results
Located in `feedback_forms/testing_versions/standard/expected_results/`:
- **JSON Files**: Expected output from working upload routes
- **Excel Files**: Timestamped versions of input files

## Running Tests

### Basic Unit Tests
```bash
cd tests/arb/utils/excel
python -m pytest test_xl_parse.py -v
```

### Functional Equivalence Tests
```bash
cd tests/arb/utils/excel
python -m pytest test_excel_functional_equivalence.py -v
```

### All Excel Tests
```bash
cd tests/arb/utils/excel
python -m pytest . -v
```

### With Content Validation
```bash
cd tests/arb/utils/excel
python -m pytest test_excel_functional_equivalence.py --test-content-validation -v
```

## Test Coverage

### Function Testing
- ✅ `parse_xl_file` vs `parse_xl_file_2`
- ✅ `extract_tabs` vs `extract_tabs_2`
- ✅ `get_spreadsheet_key_value_pairs` vs `get_spreadsheet_key_value_pairs_2`
- ✅ `ensure_schema`
- ✅ `split_compound_keys`
- ✅ `convert_upload_to_json`
- ✅ `get_json_file_name_old`

### Validation Types
- **Structure Validation**: Ensures parsed results have expected keys and types
- **Content Validation**: Compares actual data against expected results
- **Function Equivalence**: Verifies `_2` functions produce identical output
- **Error Handling**: Tests with bad data and blank files
- **Cross-Form Testing**: Validates all feedback form types

## Content Validation

### Timestamp Normalization
The testing suite automatically normalizes timestamps in filenames and content to enable consistent comparison:
- `ts_2025_08_11_16_00_57.xlsx` → `ts_TIMESTAMP.xlsx`
- `ts_2025_08_11_16_00_57.json` → `ts_TIMESTAMP.json`

### Comparison Logic
1. **Structure Validation**: Ensures parsed results have expected keys
2. **Metadata Comparison**: Compares metadata fields between results
3. **Schema Validation**: Validates schema definitions
4. **Content Validation**: Compares actual field values (with timestamp normalization)

## Expected Results

The expected results were created by:
1. Running each test Excel file through the working `/upload` route
2. Saving the generated JSON output
3. Using these as the "known-good" reference for validation

This ensures that our Excel parsing functions produce output identical to the working production system.

## Test Results

### Current Status
- **Basic Unit Tests**: 32/32 passing ✅
- **Functional Tests**: Ready for execution with real data
- **Content Validation**: Implemented and ready for use

### Success Criteria
- All Excel functions are callable and have correct signatures
- `_2` functions produce identical output to original functions
- Parsed results match expected results exactly
- All feedback form types can be processed successfully
- Error handling works consistently across function versions

## Future Enhancements

### Planned Improvements
1. **Performance Testing**: Measure parsing speed improvements
2. **Memory Usage**: Monitor memory consumption during parsing
3. **Edge Case Coverage**: Add more boundary condition tests
4. **Schema Evolution**: Test with different schema versions

### Integration Testing
1. **Route Integration**: Test Excel functions within actual routes
2. **Database Integration**: Validate parsed data against database
3. **End-to-End Workflows**: Test complete upload and processing flows

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure `source/production` is in Python path
2. **Missing Test Data**: Verify `feedback_forms/testing_versions/standard/` exists
3. **Expected Results Missing**: Check `expected_results/` subdirectory
4. **Function Not Found**: Ensure all `_2` functions are implemented

### Debug Mode
Enable verbose output to see detailed comparison reports:
```bash
python -m pytest test_excel_functional_equivalence.py -v -s
```

## Contributing

When adding new tests:
1. Follow the existing test structure and naming conventions
2. Include both positive and negative test cases
3. Add appropriate assertions and error messages
4. Update this README with new test coverage information
5. Ensure tests pass before committing changes
