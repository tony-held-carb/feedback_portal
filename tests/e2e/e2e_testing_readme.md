# E2E Testing with Playwright

This directory contains robust, maintainable end-to-end (E2E) tests for the ARB Feedback Portal using Playwright and pytest.

## Overview

- All tests are written using Playwright's sync API and pytest.
- The suite focuses on **single-purpose, well-synchronized tests** for reliability and maintainability.
- Diagnostics overlay and backend logging are tested as part of the core workflows.
- All legacy/compound/console-output tests have been removed; only robust, maintainable tests remain.

## Test Files

### `test_excel_upload_workflows.py`
- Main E2E suite for Excel upload, review, discard, error handling, and backend validation.
- Covers:
  - File upload (valid, invalid, empty, large)
  - Deep backend validation (DB vs. spreadsheet)
  - Staged file discard (single and multiple files)
  - Malformed file handling
  - Diagnostics overlay logging on workflow pages (e.g., `/list_staged`)

### `test_javascript_logging.py`
- Dedicated E2E test for the JavaScript diagnostics overlay and logging system.
- Focuses on the `/java_script_diagnostic_test` route, which is a development/debugging page.
- Covers:
  - Overlay presence and correct logging on page load
  - Logging of button clicks (including send-diagnostic with input value)
  - Robust Playwright waiting strategies to avoid race conditions
  - Demonstrates integration of `java_script_diagnostics.js` and `java_script_diagnostic_test.html`

### `test_playwright_setup.py`
- Simple async test to verify Playwright installation and environment.
- Navigates to example.com and checks for expected content.
- Does **not** require the Flask app to be running.
- Useful for confirming Playwright is set up correctly before running full E2E tests.


## Test Configuration and Utilities


### `pytest.ini`
- Pytest configuration to suppress openpyxl UserWarnings about unsupported Excel features (e.g., Data Validation, Conditional Formatting).
- Keeps test output clean and focused on actionable issues.
- See: https://foss.heptapod.net/openpyxl/openpyxl/-/issues/1604

## Setup

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
   python -m flask run
   ```

## Running Tests

**Run all test commands from the project root directory:**

```bash
cd /path/to/your/feedback_portal  # (e.g., D:\local\cursor\feedback_portal)
```

### Recommended Command Format

Use the following format to run tests and capture output both to the terminal and a file:

```bash
pytest tests/e2e/test_excel_upload_workflows.py -v -k "test_name" | tee pytest_output.txt
```

- `-v` (**verbose**): Shows each test name and status, making it easier to see which tests ran and which failed.
- `-k "pattern"`: Runs only tests whose names match the given pattern (substring or expression). This is useful for running a subset of tests quickly.
- `| tee pytest_output.txt`: Writes output to both the terminal (so you see progress live) and to a file for later review or sharing.

### Common Examples

- **Run all E2E tests (with verbose output, log to file):**
  ```bash
  pytest tests/e2e/test_excel_upload_workflows.py -v | tee pytest_all.txt
  ```
- **Run a specific test by name:**
  ```bash
  pytest tests/e2e/test_excel_upload_workflows.py -v -k "test_diagnostics_overlay_on_diagnostic_test_page" | tee pytest_diag_01.txt
  ```
- **Run all discard-related tests:**
  ```bash
  pytest tests/e2e/test_excel_upload_workflows.py -v -k "discard" | tee pytest_discard.txt
  ```
- **Run all diagnostics overlay tests:**
  ```bash
  pytest tests/e2e/test_excel_upload_workflows.py -v -k "diagnostics_overlay" | tee pytest_overlay.txt
  ```
- **Run diagnostics overlay/logging test for the JS system:**
  ```bash
  pytest tests/e2e/test_javascript_logging.py -v | tee pytest_js_diag.txt
  ```
- **Run with browser visible (for debugging):**
  ```bash
  pytest tests/e2e/test_excel_upload_workflows.py --headed -v | tee pytest_headed.txt
  ```
- **Debug script (not a test, just prints to terminal):**
  ```bash
  python tests/e2e/debug_upload_page_playwright.py
  ```

### Why Use These Options?
- `-v` makes it easy to see which tests ran and their results, especially in large suites.
- `-k` lets you quickly run only the tests you care about (by substring or pattern), saving time during development.
- `| tee` lets you monitor progress live and keeps a log for later review, which is especially helpful for long or flaky tests.

## Test Coverage

- **File Upload:** Valid, invalid, empty, and large files
- **Deep Backend Validation:** DB vs. spreadsheet field-by-field
- **Staged File Workflows:** Upload, discard, multiple files
- **Malformed File Handling:** Creation, listing, discard
- **Diagnostics Overlay:** Logging on workflow and diagnostics test pages
- **Accessibility and Page Structure:** Upload page elements, labels, drop zone

## Philosophy

- **Single-purpose tests:** Each test covers one workflow for clarity and reliability.
- **Explicit synchronization:** All tests use Playwright's waiting tools (`expect_navigation`, `wait_for_load_state`, `expect(locator)`, etc.) to avoid flakiness.
- **No legacy/compound/console-output tests:** All such tests have been removed for maintainability.
- **Easy to extend:** Add new workflows or edge cases by following the current patterns.

## Troubleshooting

- **Browser not found:** Run `playwright install`
- **Tests timing out:** Increase timeout values or check Flask app is running
- **Element not found:** Use Playwright's auto-waiting or explicit waits
- **File upload failures:** Check file paths and permissions
- **Debugging:**
  - Run with `--headed` to see browser
  - Use `page.pause()` for interactive debugging
  - Enable video/trace recording for failure analysis

## Future Enhancements

- Add mobile device and cross-browser testing
- Implement visual regression testing
- Add performance and concurrency tests
- Integrate with CI/CD pipeline

---

