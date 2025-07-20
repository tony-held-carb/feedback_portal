# E2E Testing with Playwright

This directory contains robust, maintainable end-to-end (E2E) tests for the ARB Feedback Portal using Playwright and pytest.

## Overview

- All tests are written using Playwright's sync API and pytest.
- The suite focuses on **single-purpose, well-synchronized tests** for reliability and maintainability.
- All legacy/compound/console-output tests have been removed; only robust, maintainable tests remain.
- Diagnostics overlay and backend logging are tested as part of the core workflows.

## Test Files

### `test_excel_upload_playwright_pytest.py` (suggested: `test_excel_upload_workflows.py`)
- Main E2E suite for Excel upload, review, discard, error handling, and backend validation.
- Covers:
  - File upload (valid, invalid, empty, large)
  - Deep backend validation (DB vs. spreadsheet)
  - Staged file discard (single and multiple files)
  - Malformed file handling
  - Diagnostics overlay logging

### `test_list_staged_diagnostics.py`
- Focused E2E suite for verifying the JavaScript diagnostics overlay and diagnostics block on `/list_staged`.
- Covers:
  - Overlay presence and logging
  - Diagnostics block UI and button functionality
  - Modal confirmation for return home
  - Text input and custom message logging
  - UI structure and required elements

### `test_diagnostics.py`
- Standalone E2E tests for the JavaScript diagnostics overlay and discard modal.
- Used for isolated verification and regression testing of diagnostics features on both the dedicated diagnostics test page and `/list_staged`.
- Covers:
  - Overlay logging on both pages
  - Diagnostics button and modal interactions
  - Discard modal and overlay log timing

### `test_playwright_setup.py`
- Simple async test to verify Playwright installation and environment.
- Navigates to example.com and checks for expected content.
- Does **not** require the Flask app to be running.
- Useful for confirming Playwright is set up correctly before running full E2E tests.

### `debug_upload_page_playwright.py` (suggested: `debug_upload_page.py`)
- Utility for interactively examining the upload page structure and selectors.

## Test Configuration and Utilities

### `conftest.py`
- Custom pytest options for E2E test selection.
- Provides `--only-discard-tests` flag to run only discard-related tests for rapid debugging and development.
- Filters test collection to speed up iteration on discard modal and file deletion workflows.

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

- Run all E2E tests:
  ```bash
  pytest tests/e2e/test_excel_upload_playwright_pytest.py -v
  ```
- Run a specific test:
  ```bash
  pytest tests/e2e/test_excel_upload_playwright_pytest.py -v -k 'test_name'
  ```
- Run with browser visible (for debugging):
  ```bash
  pytest tests/e2e/test_excel_upload_playwright_pytest.py --headed -v
  ```
- Debug script:
  ```bash
  python tests/e2e/debug_upload_page_playwright.py
  ```

## Test Coverage

- **File Upload:** Valid, invalid, empty, and large files
- **Deep Backend Validation:** DB vs. spreadsheet field-by-field
- **Staged File Workflows:** Upload, discard, multiple files
- **Malformed File Handling:** Creation, listing, discard
- **Diagnostics Overlay:** Logging on test and staged list pages
- **Accessibility and Page Structure:** Upload page elements, labels, drop zone

## Philosophy

- **Single-purpose tests:** Each test covers one workflow for clarity and reliability.
- **Explicit synchronization:** All tests use Playwright's waiting tools (`expect_navigation`, `wait_for_load_state`, etc.) to avoid flakiness.
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

**Note:**
- All legacy/compound/console-output tests have been removed. The suite now only contains robust, maintainable, single-purpose tests.
- Consider renaming test files for clarity as the suite evolves (e.g., `test_excel_upload_workflows.py`, `test_diagnostics_overlay.py`). 
