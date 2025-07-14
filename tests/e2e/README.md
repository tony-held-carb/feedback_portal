# E2E Testing with Playwright

This directory contains end-to-end tests for the ARB Feedback Portal using Playwright.

## Migration from Selenium

The E2E tests have been migrated from Selenium WebDriver to Playwright for better reliability, performance, and debugging capabilities.

### Benefits of Playwright Migration

- **Better reliability**: Auto-waiting for elements reduces flaky tests
- **Enhanced debugging**: Built-in video recording and trace viewer
- **Modern web support**: Better handling of dynamic content and JavaScript
- **Performance**: Faster execution and lower resource usage
- **Cross-browser**: Single API for Chrome, Firefox, and Safari

## Test Files

### `test_excel_upload_ui_playwright.py`
Standalone test suite that can be run independently. Includes:
- Complete file upload workflow testing
- Multiple file type validation
- Success/error message verification
- Comprehensive test reporting

### `test_excel_upload_playwright_pytest.py`
Pytest-compatible test suite with fixtures and parametrized tests. Includes:
- Individual test methods for specific scenarios
- Pytest fixtures for browser setup
- Parametrized tests for multiple file types
- Accessibility and page structure testing

### `debug_upload_page_playwright.py`
Debugging utility for examining page structure and elements.

## Setup

### Prerequisites
1. Install Playwright:
   ```bash
   pip install playwright
   ```

2. Install browsers:
   ```bash
   playwright install
   ```

3. Ensure Flask app is running:
   ```bash
   # Start the Flask application
   python -m flask run
   ```

## Running Tests

### Standalone Test Suite
```bash
python tests/e2e/test_excel_upload_ui_playwright.py
```

### Pytest Tests
```bash
# Run all E2E tests
pytest tests/e2e/test_excel_upload_playwright_pytest.py -v

# Run specific test class
pytest tests/e2e/test_excel_upload_playwright_pytest.py::TestExcelUpload -v

# Run with browser visible (for debugging)
pytest tests/e2e/test_excel_upload_playwright_pytest.py --headed -v
```

### Debug Script
```bash
python tests/e2e/debug_upload_page_playwright.py
```

## Test Configuration

### Environment Variables
- `BASE_URL`: Flask application URL (default: http://127.0.0.1:5000)
- `TEST_FILES_DIR`: Directory containing test Excel files
- `GENERATED_FILES_DIR`: Directory containing generated test files

### Browser Options
Tests use Chromium by default with the following options:
- Viewport: 1920x1080
- Headless mode: False (for debugging), True (for CI/CD)
- Additional args: --no-sandbox, --disable-dev-shm-usage, --disable-gpu

## Test Coverage

### File Upload Testing
- Basic file upload functionality
- Drag-and-drop file upload
- File validation and error handling
- Success/failure message verification
- Multiple file types (.xlsx, .xls)
- Large file handling
- Invalid file rejection

### Page Structure Testing
- Upload page loading
- Form element presence and functionality
- File input accessibility
- Drop zone functionality (if implemented)
- Navigation and layout

### Error Handling
- Invalid file type uploads
- Empty file uploads
- Network timeout handling
- Form validation errors

## Debugging

### Video Recording
Playwright automatically records videos of test runs when using the `--video` flag:
```bash
pytest tests/e2e/test_excel_upload_playwright_pytest.py --video=on
```

### Screenshots
Tests can take screenshots on failure or manually:
```python
page.screenshot(path="debug.png", full_page=True)
```

### Trace Viewer
Enable trace recording for step-by-step debugging:
```bash
pytest tests/e2e/test_excel_upload_playwright_pytest.py --tracing=on
```

## Migration Notes

### Removed Selenium Dependencies
- `selenium` package
- `webdriver-manager` package
- Chrome WebDriver setup and management
- Selenium-specific selectors and wait conditions

### Playwright Advantages
- **Auto-waiting**: No need for explicit `WebDriverWait`
- **Better selectors**: More reliable element location
- **Built-in assertions**: `expect()` for cleaner test code
- **Network handling**: Better handling of AJAX and dynamic content
- **Mobile testing**: Built-in mobile emulation

### Code Changes
- `webdriver.Chrome()` → `playwright.chromium.launch()`
- `driver.find_element()` → `page.locator()`
- `send_keys()` → `set_input_files()`
- `WebDriverWait` → `page.wait_for_*()`
- `assert` → `expect()`

## Troubleshooting

### Common Issues

1. **Browser not found**: Run `playwright install`
2. **Tests timing out**: Increase timeout values or check Flask app is running
3. **Element not found**: Use Playwright's auto-waiting or explicit waits
4. **File upload failures**: Check file paths and permissions

### Debug Tips

1. Run tests with `--headed` flag to see browser
2. Use `page.pause()` in tests for interactive debugging
3. Enable video recording for failure analysis
4. Use trace viewer for step-by-step debugging

## Future Enhancements

- Add mobile device testing
- Implement visual regression testing
- Add performance testing
- Integrate with CI/CD pipeline
- Add cross-browser testing (Firefox, Safari) 