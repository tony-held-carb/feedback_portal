# Quick Start Guide - Running Tests

This file provides minimal steps to get up and running with tests. 

For addtionial details see
- [Project Testing](./project_testing.md)


## Setup

1. Set directory to project root: `D:\local\cursor\feedback_portal`
   cd /d "D:\local\cursor\feedback_portal"

2. Set PYTHONPATH (from project root):
   set PYTHONPATH=D:\local\cursor\feedback_portal\source\production;%PYTHONPATH%
   echo %PYTHONPATH%

3. Install Dependencies
   pip install pytest playwright
   playwright install

## Test Options

1. Use the -v flag for verbose diagnostics
2. Redirect output and errors to diagnostic file rather than terminal
   - this will stop cursor from hanging
   - pytest tests/arb/ -v > test_output.txt 2>&1
3. If you want to run the test in Pycharm
   - Right-click the test file or function and select "Run pytest…"

## Test Types & How to Run

### 1. Unit Tests
**Purpose:** Test individual functions and modules

#### Run all unit tests
pytest tests/arb/ -v > test_units.txt 2>&1

#### Run specific test file
pytest tests/arb/utils/test_date_and_time.py -v > test_unit_date_and_time.txt 2>&1

### 2. Integration Tests
**Purpose:** Test complete workflows and database operations

#### Run all integration tests
pytest tests/arb/portal/ -v > test_integration.txt 2>&1

#### Run specific integration test
pytest tests/arb/portal/test_file_upload_suite.py -v > test_output.txt 2>&1

### 3. Generate Test Data
**Purpose:** Create Excel files for testing

#### Generate comprehensive test data
python scripts/generate_test_excel_files.py > generate_test_data_output.txt 2>&1

#### Output location: feedback_forms/testing_versions/generated/

### 4. E2E UI Tests
**Purpose:** Test complete user workflows via browser automation

#### Start Flask app first (in separate terminal)
cd /d D:\local\cursor\feedback_portal\source\production
flask --app arb/wsgi run --debug --no-reload

#### Run E2E tests (in another terminal)
# Standalone test suite
python tests/e2e/test_excel_upload_ui_playwright.py > e2e_test_output.txt 2>&1

# Pytest-compatible tests (recommended)
pytest tests/e2e/test_excel_upload_playwright_pytest.py -v > e2e_test_output.txt 2>&1

### 5. Run All Tests (Recommended Order)

#### 1. Unit tests
pytest tests/arb/ -v > test_unit.txt 2>&1

#### 2. Integration tests  
pytest tests/arb/portal/ -v > test_integration.txt 2>&1

#### 3. Generate test data
python scripts/generate_test_excel_files.py

#### 4. E2E tests (requires Flask app running)
# Standalone test suite
python tests/e2e/test_excel_upload_ui_playwright.py

# Pytest-compatible tests (recommended)
pytest tests/e2e/test_excel_upload_playwright_pytest.py -v

#### Debug E2E Tests
python tests/e2e/debug_upload_page_playwright.py > debug_output.txt 2>&1

## Expected Results

### Unit Tests
- ✅ All tests should pass
- Coverage: Individual module functionality

### Integration Tests  
- ✅ Integration tests now use PostgreSQL database
- Uses your configured `DATABASE_URI` environment variable
- Tests real database operations and schema interactions
- Coverage: File upload workflows, database operations, model interactions

### Test Data Generation
- ✅ 36+ Excel files generated
- Location: `feedback_forms/testing_versions/generated/`
- Includes: Valid, invalid, and edge case scenarios

### E2E Tests
- ✅ 100% success rate with Playwright
- Coverage: Complete UI workflows with enhanced reliability
- Requires: Flask app running at http://127.0.0.1:5000
- Benefits: Auto-waiting, video recording, better debugging


## Troubleshooting

### Database Configuration
The tests use your PostgreSQL database configuration securely:

1. **Environment Variable Required**: Set `DATABASE_URI` to your PostgreSQL connection string
   ```bash
   export DATABASE_URI=postgresql+psycopg2://postgres:password@localhost:5432/your_db
   ```

2. **Security**: No hardcoded credentials in test files - only environment variables are used

3. **Schema**: Tests work with the `satellite_tracker_new` schema and PostgreSQL-specific features

### Common Issues

**Database Connection Errors**
- Ensure PostgreSQL is running
- Verify `DATABASE_URI` environment variable is set correctly
- Check database permissions

**Missing Environment Variable**
- Tests will fail if `DATABASE_URI` is not set
- No fallback credentials are provided for security reasons

### Import Errors
```bash
# Ensure PYTHONPATH is set correctly
echo %PYTHONPATH%
# Should include: D:\local\cursor\feedback_portal\source\production
```

### E2E Test Failures
1. **Flask app not running**: Start with `python -m flask run`
2. **Playwright not installed**: `pip install playwright && playwright install`
3. **Browser not found**: Run `playwright install` to download browsers
4. **Tests timing out**: Increase timeout values or check Flask app is running

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
- Integration tests: Core functionality tested (some skipped for database compatibility)
- E2E tests: 100% success rate with Playwright
- Test data: 36+ files generated

### 📊 Coverage Summary
- **Unit Tests**: Individual module functionality
- **Integration Tests**: Core workflows (partial due to database compatibility)
- **E2E Tests**: Full UI automation with Playwright (enhanced reliability)
- **Test Data**: Comprehensive scenarios

### 🔧 Known Issues
- **Database Compatibility**: Some integration tests skipped due to PostgreSQL vs SQLite differences
- **SQLAlchemy Warnings**: Legacy Query.get() usage (non-critical)
- **Relationship Warnings**: SQLAlchemy relationship conflicts (non-critical)
