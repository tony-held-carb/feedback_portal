# Quick Start Guide - Running Tests

## Prerequisites

1. **Set PYTHONPATH** (from project root):
   ```bash
   set PYTHONPATH=D:\local\cursor\feedback_portal\source\production;%PYTHONPATH%
   ```

2. **Install Dependencies**:
   ```bash
   pip install pytest selenium webdriver-manager
   ```

## Test Types & How to Run

### 1. Unit Tests
**Purpose:** Test individual functions and modules
```bash
# Run all unit tests
pytest tests/arb/

# Run specific test file
pytest tests/arb/utils/test_date_and_time.py

# Run with verbose output
pytest -v tests/arb/
```

### 2. Integration Tests
**Purpose:** Test complete workflows and database operations
```bash
# Run all integration tests
pytest tests/arb/portal/

# Run specific integration test
pytest tests/arb/portal/test_file_upload_suite.py

# Run with output redirection
pytest tests/arb/portal/ > integration_test_output.txt 2>&1
```

### 3. E2E UI Tests
**Purpose:** Test complete user workflows via browser automation
```bash
# Start Flask app first (in separate terminal)
cd source/production
python -m flask run

# Run E2E tests (in another terminal)
python tests/e2e/test_excel_upload_ui.py > e2e_test_output.txt 2>&1
```

### 4. Generate Test Data
**Purpose:** Create Excel files for testing
```bash
# Generate comprehensive test data
python scripts/generate_test_excel_files.py > generate_test_data_output.txt 2>&1

# Output location: feedback_forms/testing_versions/generated/
```

## Quick Test Commands

### Run All Tests (Recommended Order)
```bash
# 1. Unit tests
pytest tests/arb/ -v

# 2. Integration tests  
pytest tests/arb/portal/ -v

# 3. Generate test data
python scripts/generate_test_excel_files.py

# 4. E2E tests (requires Flask app running)
python tests/e2e/test_excel_upload_ui.py
```

### Debug E2E Tests
```bash
# Debug upload page structure
python tests/e2e/debug_upload_page.py > debug_output.txt 2>&1
```

## Expected Results

### Unit Tests
- ✅ All tests should pass
- Coverage: Individual module functionality

### Integration Tests  
- ✅ All tests should pass
- Coverage: File upload workflows, database operations

### E2E Tests
- ✅ 100% success rate (5/5 files)
- Coverage: Complete UI workflows
- Requires: Flask app running at http://127.0.0.1:5000

### Test Data Generation
- ✅ 36+ Excel files generated
- Location: `feedback_forms/testing_versions/generated/`
- Includes: Valid, invalid, and edge case scenarios

## Troubleshooting

### Import Errors
```bash
# Ensure PYTHONPATH is set correctly
echo %PYTHONPATH%
# Should include: D:\local\cursor\feedback_portal\source\production
```

### E2E Test Failures
1. **Flask app not running**: Start with `python -m flask run`
2. **Chrome not installed**: Install Chrome browser
3. **Selenium not installed**: `pip install selenium webdriver-manager`

### Test Data Generation Issues
1. **Missing directories**: Ensure `feedback_forms/testing_versions/` exists
2. **Permission errors**: Check write permissions to output directory

## Test Output Files

### Generated Files
- `integration_test_output.txt` - Integration test results
- `e2e_test_output.txt` - E2E test results  
- `generate_test_data_output.txt` - Test data generation results
- `debug_output.txt` - Debug information

### Test Data Location
- `feedback_forms/testing_versions/generated/` - Generated Excel files
- `feedback_forms/testing_versions/generated/manifest.json` - Test file descriptions

## Success Indicators

### ✅ All Tests Passing
- Unit tests: No failures
- Integration tests: All workflows successful
- E2E tests: 100% success rate
- Test data: 36+ files generated

### 📊 Coverage Summary
- **Unit Tests**: Individual module functionality
- **Integration Tests**: Complete workflows
- **E2E Tests**: Full UI automation
- **Test Data**: Comprehensive scenarios

---

*For detailed documentation, see `TEST_COVERAGE.md`* 