# Testing Technical Guide: Comprehensive Reference for ARB Feedback Portal Testing

## Table of Contents

1. [E2E Testing with Playwright](#e2e-testing-with-playwright)
2. [Unit and Integration Testing](#unit-and-integration-testing)
3. [Testing Infrastructure](#testing-infrastructure)
4. [Specialty Testing Techniques](#specialty-testing-techniques)
5. [Best Practices and Patterns](#best-practices-and-patterns)
6. [Troubleshooting](#troubleshooting)

---

## E2E Testing with Playwright

### Core Testing Strategy

#### Philosophy

- **Single-purpose tests**: Each test covers one workflow for clarity and reliability
- **Explicit synchronization**: Use Playwright's waiting tools to avoid flakiness
- **Robust patterns**: Replace arbitrary timeouts with element-specific assertions
- **Maintainable code**: Follow consistent patterns across all tests
- **DOM marker synchronization**: Use custom markers for reliable file upload testing

#### Test Types

1. **Unit Tests**: Individual functions and modules (`tests/arb/`)
2. **Integration Tests**: Complete workflows and database operations (`tests/arb/portal/`)
3. **E2E Tests**: Complete user workflows via browser automation (`tests/e2e/`)

### E2E Readiness Marker System

#### Overview

Our project uses a custom E2E readiness marker system to ensure pages are fully loaded before interaction. This system
provides a unified readiness signal that layers multiple browser events.

#### Implementation

1. **JavaScript File**: `source/production/arb/portal/static/js/e2e_testing_related.js`
2. **Jinja Include**: `source/production/arb/portal/templates/includes/e2e_testing_related.jinja`
3. **Helper Functions**: `source/production/arb/portal/utils/e2e_testing_util.py`

#### How It Works

The E2E readiness system uses a layered approach:

```
window.onload
  ↳ requestAnimationFrame (wait for next paint frame)
    ↳ requestIdleCallback (wait for JS to finish initializing)
      ↳ SET ATTRIBUTE: <html data-e2e-ready="true">
```

#### Helper Functions

```python
def wait_for_e2e_readiness(page: Page, timeout: int = 7000) -> None:
    """Wait for the E2E readiness marker to be set."""
    try:
        page.wait_for_selector("html[data-e2e-ready='true']", timeout=timeout)
    except TimeoutError:
        print(f"❌ E2E readiness marker not found on {page.url}")
        page.screenshot(path="debug_e2e_timeout.png", full_page=True)
        raise

def navigate_and_wait_for_ready(page: Page, url: str, timeout: int = 7000) -> None:
    """Navigate to a URL and wait for the page to be ready for E2E testing."""
    page.goto(url, wait_until="load")
    wait_for_e2e_readiness(page, timeout)
```

#### Usage Pattern

```python
# Instead of:
page.goto(f"{BASE_URL}/upload_staged")
page.wait_for_load_state("networkidle")

# Use:
from source.production.arb.portal.utils.e2e_testing_util import navigate_and_wait_for_ready
navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged")
```

#### When NOT to Use E2E Readiness Marker

- **File upload scenarios**: Page navigation destroys execution context
- **Immediate redirects**: Page reloads before marker can be set
- **Dynamic content**: Content that loads after initial page render

### DOM Marker Synchronization System

#### Overview

Our custom DOM marker synchronization system provides reliable file upload testing by using hidden DOM elements as
synchronization points. This system eliminates the need for arbitrary `wait_for_timeout` calls.

#### Core Components

##### 1. Flask Backend Integration

```python
# In Flask routes (source/production/arb/portal/routes.py)
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # ... file processing logic ...
        flash("_upload_attempted", "internal-marker")  # Creates DOM marker
        return redirect(url_for('main.review_staged'))
```

##### 2. Jinja Template Rendering

```html
<!-- In flash_messaging.jinja -->
{% if category == "internal-marker" %}
  <div class="upload-marker" data-upload-attempted="true" style="display: none;"></div>
{% endif %}
```

##### 3. Helper Functions

```python
# In source/production/arb/portal/utils/playwright_testing_util.py

def wait_for_upload_attempt_marker(page: Page, timeout: int = 10000) -> None:
    """Wait for the upload attempt marker to appear in the DOM."""
    try:
        page.wait_for_selector(".upload-marker[data-upload-attempted='true']", timeout=timeout)
    except TimeoutError:
        print(f"❌ Upload attempt marker not found on {page.url}")
        page.screenshot(path="debug_upload_marker_timeout.png", full_page=True)
        raise

def clear_upload_attempt_marker(page: Page) -> None:
    """Remove any existing upload attempt markers from the DOM."""
    try:
        page.evaluate("""
            document.querySelectorAll('.upload-marker[data-upload-attempted="true"]')
                .forEach(el => el.remove());
        """)
    except Exception as e:
        print(f"⚠️ Could not clear upload markers: {e}")

def upload_file_and_wait_for_attempt_marker(page: Page, file_path: str) -> None:
    """Upload a file and wait for the upload attempt marker to appear."""
    clear_upload_attempt_marker(page)
    page.set_input_files("input[type='file']", file_path)
    wait_for_upload_attempt_marker(page)
```

#### Decision Framework: Which Helper to Use

##### Use `upload_file_and_wait_for_attempt_marker` when:

- You need to upload a file AND wait for the marker
- The page doesn't navigate immediately after upload
- You want a single function call for the complete operation

```python
# Example: Upload form that shows success/error messages
upload_file_and_wait_for_attempt_marker(page, file_path)
expect(page.locator(".alert-success, .alert-danger")).to_be_visible()
```

##### Use `wait_for_upload_attempt_marker` when:

- `page.set_input_files` causes immediate page navigation
- You need to handle the upload and wait separately
- The execution context might be destroyed by navigation

```python
# Example: Upload that triggers immediate redirect
clear_upload_attempt_marker(page)
file_input = page.locator("input[type='file']")
file_input.set_input_files(file_path)
# Page navigates here, destroying execution context
wait_for_upload_attempt_marker(page)  # Wait on new page
```

### Waiting Strategies

#### ✅ Recommended Patterns

##### 1. Element-Specific Waits (Preferred)

```python
# Wait for specific element to be visible
expect(page.locator("table tbody tr").first).to_be_visible()

# Wait for either data rows or empty state
expect(page.locator("table tbody tr td[colspan='7'], table tbody tr")).to_be_visible()

# Wait for checkbox state
expect(checkbox).to_be_checked()
expect(checkbox).not_to_be_checked()
```

##### 2. Navigation Waits

```python
# For actions that trigger page navigation
with page.expect_navigation():
    confirm_btn.click()

# For URL changes
page.wait_for_url("**/success", timeout=10000)
```

##### 3. Response Waits

```python
# For specific API calls
with page.expect_response("**/api/endpoint"):
    submit_btn.click()
```

##### 4. DOM Marker Waits

```python
# For file upload synchronization
wait_for_upload_attempt_marker(page)

# For E2E readiness
wait_for_e2e_readiness(page)
```

#### ❌ Avoid These Patterns

##### 1. Arbitrary Timeouts

```python
# DON'T: Use arbitrary timeouts
page.wait_for_timeout(1000)

# DO: Wait for specific elements or markers
wait_for_upload_attempt_marker(page)
```

##### 2. Network Idle (Problematic)

```python
# DON'T: Use networkidle (can hang indefinitely)
page.wait_for_load_state("networkidle")

# DO: Use E2E readiness marker or element-specific waits
navigate_and_wait_for_ready(page, url)
```

##### 3. Count Assertions Without Waiting

```python
# DON'T: This doesn't wait at all
expect(page.locator("table tbody tr")).to_have_count_at_least(0)

# DO: Wait for visibility
expect(page.locator("table tbody tr")).to_be_visible()
```

##### 4. Multi-Element Locators in Strict Mode

```python
# DON'T: Use broad selectors that match multiple elements
expect(page.locator("table tbody tr td[colspan='7'], table tbody tr")).to_be_visible()

# DO: Use .first() or more specific targeting
expect(page.locator("table tbody tr").first).to_be_visible()
```

### File Upload Testing

#### Overview

File upload testing requires special handling due to page navigation and execution context destruction. Our marker
system provides reliable synchronization for these scenarios.

#### Common Patterns

##### 1. Single File Upload (No Navigation)

```python
def test_upload_file_with_feedback(page: Page, file_path: str):
    """Upload file and wait for feedback message."""
    navigate_and_wait_for_ready(page, f"{BASE_URL}/upload")

    upload_file_and_wait_for_attempt_marker(page, file_path)
    expect(page.locator(".alert-success, .alert-danger")).to_be_visible()
```

##### 2. Single File Upload (With Navigation)

```python
def test_upload_file_with_redirect(page: Page, file_path: str):
    """Upload file and handle page redirect."""
    navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged")

    # Clear markers before upload
    clear_upload_attempt_marker(page)
    file_input = page.locator("input[type='file']")
    file_input.set_input_files(file_path)
    # Page navigates here, destroying execution context
    wait_for_upload_attempt_marker(page)  # Wait on new page
```

##### 3. Multiple File Upload

```python
def test_multiple_file_upload(page: Page, file_paths: List[str]):
    """Upload multiple files sequentially."""
    navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged")

    for file_path in file_paths:
        clear_upload_attempt_marker(page)
        file_input = page.locator("input[type='file']")
        file_input.set_input_files(file_path)
        wait_for_upload_attempt_marker(page)
```

### Test Structure and Patterns

#### Basic Test Template

```python
import pytest
from playwright.sync_api import Page, expect
from source.production.arb.portal.utils.e2e_testing_util import navigate_and_wait_for_ready
from source.production.arb.portal.utils.playwright_testing_util import (
    upload_file_and_wait_for_attempt_marker,
    wait_for_upload_attempt_marker,
    clear_upload_attempt_marker
)

@pytest.mark.e2e
def test_example_functionality(page: Page):
    """E2E: Brief description of what this test does."""

    # Navigate to page
    navigate_and_wait_for_ready(page, f"{BASE_URL}/page_url")

    # Perform actions
    element = page.locator("selector")
    element.click()

    # Wait for results
    expect(page.locator("result_selector")).to_be_visible()

    # Assert expected state
    assert expected_condition, "Clear error message"
```

#### Test File Organization

```
tests/e2e/
├── test_excel_upload_workflows.py    # Main upload workflows
├── test_feedback_updates.py          # Updates page functionality
├── test_review_staged.py             # Staged file review
├── test_javascript_logging.py        # JS diagnostics
├── test_homepage.py                  # Homepage functionality
├── test_list_uploads.py              # Upload listing
└── conftest.py                       # Pytest configuration

source/production/arb/portal/utils/
├── e2e_testing_util.py               # E2E readiness helpers
└── playwright_testing_util.py        # Playwright-specific helpers
```

#### Naming Conventions

- **Test functions**: `test_descriptive_name`
- **Test files**: `test_feature_name.py`
- **Helper functions**: `descriptive_verb_noun`
- **Selectors**: Use role-based selectors when possible

#### Selector Best Practices

```python
# Preferred: Role-based selectors
page.get_by_role("button", name="Apply Filters")
page.get_by_role("link", name="Download CSV")

# Good: Specific CSS selectors
page.locator("table tbody tr")
page.locator("input[type='file']")

# Avoid: Generic selectors
page.locator("button")  # Too generic
page.locator(".btn")    # Too generic
```

---

## Unit and Integration Testing

### Testing Philosophy and Goals

Our approach to unit testing in this codebase is guided by the following principles:

1. **Comprehensive, Honest Coverage:**
    - Achieve the maximum meaningful unit test coverage for all production logic.
    - All functions/classes that can be robustly unit tested should have direct tests.
    - If a function/class cannot be unit tested (e.g., requires a real Flask app, database, or is pure integration
      glue), this is clearly documented in both the test file (with skip markers and reasons) and the source docstring.

2. **No Source Changes for Testability:**
    - Do not refactor or alter production code solely to make it more testable.
    - All workarounds, mocks, and test-specific logic are implemented in the test files only.
    - If a function cannot be tested without changing the source, document the limitation and do not change the source.

3. **Transparency and Documentation:**
    - Every limitation in test coverage is explicitly documented in:
        - The test file (with `@pytest.mark.skip` and a reason)
        - The source code docstring (with a note about lack of coverage and why)
        - The central testing documentation (this file)
    - Documentation makes it clear to future maintainers which parts of the code are covered, which are not, and why.

4. **Maintainability and Risk Management:**
    - The goal is not just to maximize coverage numbers, but to ensure that all critical business logic is protected by
      tests.
    - Uncovered or untestable code is clearly marked so that future changes are made with caution and awareness of risk.

5. **Testing Policy Consistency:**
    - The same standards and process are applied across all modules: portal, utils, and any new code.
    - Trivial files (e.g., `__init__.py`, constants-only modules) are marked as "Testing Complete - Not Needed" and do
      not require tests.

6. **Examples and Edge Cases:**
    - Where possible, tests should include edge cases and examples that match those in the docstrings.
    - Docstrings should be kept up to date with the actual test coverage and behavior.

### Types of Tests We Run

#### 1. Unit Tests

- **Purpose:** Test individual functions and modules in isolation
- **Coverage:** Isolated logic with mocked dependencies
- **Location:** `tests/arb/`
- **Status:** Comprehensive coverage for utility functions and business logic

#### 2. Integration Tests

- **Purpose:** Test complete workflows and database operations
- **Coverage:** End-to-end workflows, file uploads, database operations
- **Location:** `tests/arb/portal/`
- **Status:** Full coverage for upload workflows and data processing

#### 3. E2E UI Automation

- **Purpose:** Test complete user workflows via browser automation
- **Coverage:** Full UI automation with Playwright
- **Location:** `tests/e2e/`
- **Status:** 100% success rate, enhanced reliability and debugging
- **Requirements:** Flask app running, Playwright installed with browsers
- **Benefits:** Auto-waiting, video recording, trace viewer, cross-browser support

#### 4. Automated Test Data Generation

- **Purpose:** Generate comprehensive test data for all scenarios
- **Coverage:** Excel files for all schemas and validation cases
- **Location:** `scripts/generate_test_excel_files.py`
- **Status:** Comprehensive test data for all sectors and validation cases

#### 5. Cross-Field Validation Tests

- **Purpose:** Test conditional field visibility and regulatory compliance
- **Coverage:** Conditional logic, cross-field validation, regulatory rules
- **Location:** `tests/arb/portal/test_cross_field_conditional_logic.py`
- **Status:** Full coverage for all major sectors

#### 6. Round-Trip Export/Import Testing

- **Purpose:** Test data integrity through export/import cycles
- **Coverage:** Data consistency, format preservation, schema compliance
- **Location:** `tests/arb/portal/test_round_trip_export_import.py`
- **Status:** Full coverage for data integrity validation

#### 7. Integration Test Suite

- **Purpose:** Test complete upload workflows using actual Excel files
- **Coverage:** File upload endpoints, field validation, error handling
- **Location:** `tests/arb/portal/test_file_upload_suite.py`
- **Status:** Full coverage for upload workflows

### Test Status Codes & Meanings

| Code  | Meaning                                                                                                        |
|-------|----------------------------------------------------------------------------------------------------------------|
| TC    | Testing Complete: All meaningful logic is fully tested (unit and/or integration).                              |
| TC-NT | Testing Complete - Not Needed: File is trivial (e.g., __init__.py, constants-only) and does not require tests. |
| ITC   | Integration Testing Complete: All integration points are fully tested.                                         |
| UTC   | Unit Testing Complete: All unit-testable logic is fully tested.                                                |
| UTP   | Unit Testing Partial: Some unit tests exist, but coverage is incomplete.                                       |
| ITP   | Integration Testing Partial: Some integration tests exist, but coverage is incomplete.                         |
| FPC   | First Pass Complete: Basic structure tested; context-dependent or complex features skipped.                    |
| NR    | Not Required: Testing not required due to file purpose (e.g., data, config, or legacy).                        |
| SKIP  | Skipped: Test intentionally skipped (with documented reason).                                                  |
| TODO  | Testing not yet implemented or planned for future.                                                             |

---

## Testing Infrastructure

### Setup and Configuration

#### Prerequisites

1. **Python Environment**: Python 3.8+
2. **Dependencies**: `pytest`, `playwright`
3. **Browsers**: Playwright browsers installed
4. **Flask App**: Running for E2E tests

#### Installation

```bash
# Install dependencies
pip install pytest playwright

# Install browsers
playwright install

# Set PYTHONPATH (from project root)
set PYTHONPATH=D:\local\cursor\feedback_portal\source\production;%PYTHONPATH%
```

#### Environment Variables

```bash
# Required for database tests
export DATABASE_URI=postgresql+psycopg2://user:pass@localhost:5432/db

# Optional: Override test base URL
export TEST_BASE_URL=http://localhost:5000
```

#### Flask App Setup

```bash
# Start Flask app (required for E2E tests)
cd source/production
flask --app arb/wsgi run --debug --no-reload
```

### Running Tests

#### Command Format

```bash
# Recommended format with verbose output and logging
pytest tests/e2e/test_file.py -v -k "test_name" | tee output.txt
```

#### Common Commands

##### Run All E2E Tests

```bash
pytest tests/e2e/ -v | tee e2e_all.txt
```

##### Run Specific Test File

```bash
pytest tests/e2e/test_feedback_updates.py -v | tee feedback_updates.txt
```

##### Run Specific Test

```bash
pytest tests/e2e/test_feedback_updates.py -v -k "test_filter_functionality" | tee filter_test.txt
```

##### Run Tests by Pattern

```bash
# All upload-related tests
pytest tests/e2e/ -v -k "upload" | tee upload_tests.txt

# All filter-related tests
pytest tests/e2e/ -v -k "filter" | tee filter_tests.txt
```

##### Debug Mode

```bash
# Run with browser visible
pytest tests/e2e/test_file.py --headed -v

# Interactive debugging
pytest tests/e2e/test_file.py --headed --pause-on-failure
```

### File Structure

```
tests/
├── arb/
│   ├── portal/
│   │   ├── test_file_upload_suite.py
│   │   ├── test_round_trip_export_import.py
│   │   └── test_cross_field_conditional_logic.py
│   └── utils/
│       └── [existing unit tests]
└── e2e/
    ├── test_excel_upload_workflows.py
    └── debug_upload_page.py

scripts/
└── generate_test_excel_files.py
```

### Key Components

#### E2E Test Class: `ExcelUploadE2ETest`

- **Automatic WebDriver management** with ChromeDriver
- **Robust page navigation** and element detection
- **Auto-submit form handling** for drag-and-drop interfaces
- **Comprehensive success/error detection**
- **Configurable test parameters** and file selection

#### Test Data Generator: `generate_test_excel_files.py`

- **Schema-aware file generation** for all sectors
- **Multiple test scenarios** with realistic data
- **Validation testing** with controlled errors
- **Performance testing** with large datasets
- **Comprehensive manifest** generation for test tracking

#### Cross-Field Validator: `test_cross_field_conditional_logic.py`

- **Sector-specific validation** logic
- **Conditional field testing** for complex forms
- **Regulatory compliance** verification
- **Cross-field dependency** validation
- **Form submission** with various field combinations

---

## Specialty Testing Techniques

### Custom Modal Diagnostics System

#### Overview

This system replaces browser confirm dialogs on the `/list_staged` page with custom Bootstrap modals that provide
consistent, testable, and well-logged confirmation dialogs for discard actions.

#### Problem Statement

The original `/list_staged` page used browser's native `window.confirm()` dialogs for discard confirmations, which
caused E2E test failures due to:

- **Browser-Specific Behavior**: Different browsers handle `window.confirm()` differently
- **Timing Issues**: Browser confirms have unpredictable timing in automated tests
- **No Logging**: Browser confirms don't integrate with our diagnostics system
- **Playwright Inconsistency**: `page.on("dialog", lambda dialog: dialog.accept())` doesn't always work reliably
- **No Visibility**: Test failures were hard to debug due to lack of logging

#### Solution: Custom Bootstrap Modals

##### Key Benefits

1. **Consistent Behavior**: Bootstrap modals work identically across all browsers
2. **Full Diagnostics Logging**: Every modal interaction is logged to both overlay and backend
3. **Predictable Timing**: Modals have consistent show/hide timing
4. **Easy Testing**: Playwright can reliably interact with Bootstrap modal elements
5. **Better UX**: Styled, professional-looking confirmation dialogs

##### Implementation Architecture

###### 1. HTML Structure

```html
<!-- Discard button with data attributes for file identification -->
<button type="submit" class="btn btn-outline-danger js-log-btn"
        data-js-logging-context="discard-staged"
        data-filename="{{ file.filename }}"
        data-file-id="{{ file.id_incidence }}">
  🗑️ Discard
</button>
```

###### 2. JavaScript Modal Management

```javascript
// Find all discard buttons and attach custom modal handlers
const discardButtons = document.querySelectorAll(
  'button[data-js-logging-context="discard-staged"], ' +
  'button[data-js-logging-context="discard-malformed"]'
);

discardButtons.forEach(function(button) {
  button.addEventListener('click', function(e) {
    e.preventDefault(); // Prevent immediate form submission
    // Show custom modal instead
    showDiscardModal(button);
  });
});
```

###### 3. Dynamic Modal Creation

```javascript
function createDiscardModal() {
  const modal = document.createElement('div');
  modal.id = 'discardConfirmModal';
  modal.className = 'modal fade';
  // ... modal HTML structure
  return modal;
}
```

###### 4. File-Specific Content

```javascript
function updateDiscardModalContent(modal, filename, fileId, form) {
  // Update modal with specific file information
  modal.querySelector('#discard-filename').textContent = filename;
  modal.querySelector('#discard-file-id').textContent = fileId;

  // Set up form submission on confirm
  const confirmBtn = modal.querySelector('#discard-confirm-btn');
  confirmBtn.addEventListener('click', function() {
    modal.hide();
    setTimeout(() => form.submit(), 100);
  });
}
```

#### Diagnostics Integration

##### Automatic Logging

All modal interactions are automatically logged via the diagnostics system:

1. **Button Click**: `Button clicked: discard-staged`
2. **Modal Show**: (handled by Bootstrap modal events)
3. **Modal Confirm**: `Button clicked: discard-modal-confirm`
4. **Modal Cancel**: `Button clicked: discard-modal-cancel`
5. **Form Submission**: (handled by form submit event)

##### Log Examples

```
[JS_DIAG] Page loaded: list_staged
Button clicked: discard-staged
Button clicked: discard-modal-confirm
[Backend] Discarded staged upload file: filename.json
```

#### E2E Testing Improvements

##### Before (Browser Confirm)

```python
# Unreliable browser confirm handling
page.on("dialog", lambda dialog: dialog.accept())
discard_btn.click()
# Sometimes fails, hard to debug
```

##### After (Custom Modal)

```python
# Reliable Bootstrap modal handling
discard_btn = page.locator('[data-js-logging-context="discard-staged"]').first
discard_btn.click()
# Modal appears
confirm_btn = page.locator('[data-js-logging-context="discard-modal-confirm"]')
confirm_btn.click()
# Form submits reliably
```

##### Test Selectors

```python
# Easy to find and interact with modal elements
page.locator('#discardConfirmModal')  # Modal container
page.locator('[data-js-logging-context="discard-modal-confirm"]')  # Confirm button
page.locator('[data-js-logging-context="discard-modal-cancel"]')   # Cancel button
page.locator('#discard-filename')  # File information display
```

### Wait for Timeout Replacement Strategy

#### The Problem with `page.wait_for_timeout()`

##### What it Does:

```python
page.wait_for_timeout(1000)
```

Pauses test execution for 1000 milliseconds, unconditionally.

##### Why It's Problematic:

| Issue             | Description                                                                  |
|-------------------|------------------------------------------------------------------------------|
| ❌ Blind Wait      | Waits even if the page is already ready, wasting time.                       |
| ❌ Race Conditions | Waits might not be long enough if slow systems or network delays occur.      |
| ❌ Fragile Tests   | The tests may pass or fail unpredictably depending on machine or CI speed.   |
| ❌ Hard to Debug   | Failures from timing mismatches are not obvious and often non-deterministic. |

#### ✅ Recommended Solutions

Each replacement depends on **what the test is waiting for**. Below are general patterns and their specific applications
in this test suite.

##### 1. 🔄 File Upload Processing

**Old:**

```python
page.set_input_files("input[type='file']", file_path)
page.wait_for_timeout(1000)
```

**New:**

```python
page.set_input_files("input[type='file']", file_path)
expect(page.locator(".alert-success, .alert-danger, .alert-warning, .success-message, .error-message")).to_have_count_greater_than(0, timeout=10000)
```

**Why it works:**

- Waits for a visible result (success or error message) that confirms upload processing is complete.
- Covers all known message types used in your app.

##### 2. 🧭 General Post-Action Stabilization

**Old:**

```python
page.wait_for_timeout(1000)
```

**New:**

```python
expect(page.locator("body")).to_be_visible(timeout=2000)
```

**Why it works:**

- Ensures that the body of the page is rendered and visible.
- Acts as a minimal safeguard when no specific dynamic event can be targeted.

##### 3. 🪟 Modal and Overlay Activation

**Old:**

```python
discard_btn.click()
page.wait_for_timeout(500)
```

**New:**

```python
discard_btn.click()
expect(page.locator("#discardConfirmModal")).to_be_visible(timeout=2000)
```

**Why it works:**

- Targets the actual UI effect (modal appearing) instead of an arbitrary pause.
- Avoids race conditions in modal tests.

#### 🔄 When Not to Use General Replacements

| Situation                    | Don't blindly replace with... | Use this instead                                     |
|------------------------------|-------------------------------|------------------------------------------------------|
| Waiting for network events   | `wait_for_timeout()`          | `page.wait_for_function(...)`, `expect_navigation()` |
| Waiting for text update      | `wait_for_timeout()`          | `expect(locator).to_contain_text(...)`               |
| Waiting for row count change | `wait_for_timeout()`          | `expect(locator).to_have_count(...)`                 |

#### 🧪 Limitations of `expect().to_be_visible()` as a General Strategy

| Limitation                                 | Mitigation                                                                   |
|--------------------------------------------|------------------------------------------------------------------------------|
| Doesn't guarantee backend completion       | Combine with log/database check (which your test already does)               |
| Requires predictable DOM elements          | Ensure UI consistently renders success/error markers                         |
| Can fail if elements are hidden but in DOM | Use `expect(locator).to_have_count(...)` or `wait_for_function(...)` instead |

---

## Best Practices and Patterns

### 1. Test Design

- **Single responsibility**: Each test covers one specific functionality
- **Descriptive names**: Test names should clearly indicate what they test
- **Proper setup/teardown**: Use pytest fixtures for common setup
- **Independent tests**: Tests should not depend on each other

### 2. Waiting Strategies

- **Prefer element-specific waits** over arbitrary timeouts
- **Use E2E readiness marker** for standard page navigation
- **Use DOM markers** for file upload synchronization
- **Handle both success and failure states** in assertions
- **Provide clear error messages** in assertions

### 3. File Upload Testing

- **Clear markers before uploads** to prevent stale state
- **Handle page navigation** when execution context is destroyed
- **Use appropriate helper functions** based on upload behavior
- **Test both success and error scenarios**

### 4. Selector Strategy

- **Role-based selectors first**: `page.get_by_role("button", name="Submit")`
- **Specific CSS selectors**: `page.locator("table tbody tr")`
- **Avoid generic selectors**: Don't use `page.locator("button")`
- **Test selectors manually**: Verify selectors work before using in tests

### 5. Error Handling

- **Graceful degradation**: Handle cases where elements might not exist
- **Meaningful assertions**: Provide clear error messages
- **Screenshots on failure**: Capture visual state for debugging
- **Logging**: Add debug information for troubleshooting

### 6. Performance

- **Minimize waits**: Use targeted waits instead of long timeouts
- **Parallel execution**: Run tests in parallel when possible
- **Resource cleanup**: Close browsers and clean up resources
- **Efficient selectors**: Use efficient CSS selectors
- **Browser process management**: Monitor and clean up Chrome processes to prevent resource exhaustion

### 7. Maintenance

- **Consistent patterns**: Follow established patterns across all tests
- **Documentation**: Keep test documentation up to date
- **Regular review**: Periodically review and update test patterns
- **Version control**: Track changes to test infrastructure

### Pattern by Use Case

#### Filter Operations

```python
# Apply filter and wait for results
apply_btn.click()
expect(page.locator("table tbody tr").first).to_be_visible()
```

#### File Uploads with Navigation

```python
# For file uploads that trigger immediate navigation
clear_upload_attempt_marker(page)
file_input = page.locator("input[type='file']")
file_input.set_input_files(file_path)
wait_for_upload_attempt_marker(page)  # Wait on redirected page
```

#### File Uploads with Messages

```python
# For file uploads that show success/error messages
upload_file_and_wait_for_attempt_marker(page, file_path)
expect(page.locator(".alert-success, .alert-danger")).to_be_visible()
```

#### UI Interactions

```python
# Checkbox interactions
checkbox.check()
expect(checkbox).to_be_checked()

# Form submissions
submit_btn.click()
expect(page.locator(".success-message")).to_be_visible()
```

---

## Troubleshooting

### Common Issues

#### 1. Intermittent Test Failures and Browser Resource Exhaustion

**Problem**: Tests pass individually but fail intermittently during full test suite runs, often with
`TimeoutError: Page.goto: Timeout 30000ms exceeded.`

**Root Cause**: Browser resource exhaustion from accumulated Chrome processes:

- 50+ Chrome processes running simultaneously
- ~2GB+ RAM consumption
- Network bottlenecks from too many simultaneous connections
- Browser instability causing navigation timeouts

**Symptoms**:

- Tests pass when run individually
- Intermittent failures during full suite runs
- Increasing failure frequency as test suite progresses
- `TimeoutError` during page navigation
- Whack-a-mole pattern: fixing one timeout causes another to appear

**Immediate Solution**:

```bash
# Kill all Chrome processes before test runs
taskkill //f //im chrome.exe

# On Linux/Mac:
pkill -f chrome
```

**Long-term Prevention**:

- Implement proper browser cleanup in test configuration
- Monitor browser process count during test runs
- Consider browser pool management for parallel test execution

**Detection**:

```bash
# Check for excessive Chrome processes
tasklist | findstr -i chrome  # Windows
ps aux | grep chrome          # Linux/Mac

# If you see 20+ Chrome processes, clean up before running tests
```

#### 2. E2E Readiness Marker Timeout

```python
# Problem: Marker not set within timeout
TimeoutError: page.wait_for_selector: Timeout 7000ms exceeded.

# Solution: Use fallback approach
page.goto(url, wait_until="domcontentloaded")
expect(page.locator("table, .table")).to_be_visible(timeout=30000)
try:
    page.wait_for_selector("html[data-e2e-ready='true']", timeout=5000)
except:
    pass  # Continue if marker doesn't appear
```

#### 3. Upload Marker Timeout

```python
# Problem: Upload marker not found
TimeoutError: page.wait_for_selector: Timeout 10000ms exceeded.

# Solution: Check if page navigated and marker is on new page
try:
    wait_for_upload_attempt_marker(page, timeout=5000)
except TimeoutError:
    # Page may have navigated, check current URL
    if "/review_staged" in page.url:
        wait_for_upload_attempt_marker(page, timeout=5000)
    else:
        raise
```

#### 4. Execution Context Destroyed

```python
# Problem: Page navigation during file upload
Execution context was destroyed, most likely because of a navigation

# Solution: Clear markers before navigation
clear_upload_attempt_marker(page)
file_input.set_input_files(file_path)
wait_for_upload_attempt_marker(page)  # Wait on new page
```

#### 5. Multi-Element Locator Issues

```python
# Problem: Multiple elements match selector
StrictModeViolation: Multiple elements found

# Solution: Use .first or specific targeting
expect(page.locator(".confirm-checkbox").first).to_be_visible()

# Real-world example: Table row waiting
# Problem: expect(page.locator("table tbody tr td[colspan='7'], table tbody tr")).to_be_visible()
# Error: StrictModeViolation: locator resolved to 100 elements
# Solution: expect(page.locator("table tbody tr").first).to_be_visible()
```

#### 6. Flask App Not Running

```bash
# Problem: E2E tests fail with connection errors
# Solution: Start Flask app first
cd source/production
flask --app arb/wsgi run --debug --no-reload
```

#### 7. Browser Not Found

```bash
# Problem: Playwright can't find browsers
# Solution: Install browsers
playwright install
```

### Debugging Techniques

#### 1. Screenshots on Failure

```python
# Automatic screenshots in helper functions
page.screenshot(path="debug_failure.png", full_page=True)
```

#### 2. Interactive Debugging

```python
# Add to test for interactive debugging
page.pause()
```

#### 3. Console Logging

```python
# Add debug information
print(f"[DEBUG] Current URL: {page.url}")
print(f"[DEBUG] Element count: {page.locator('table tr').count()}")
print(f"[DEBUG] Upload markers: {page.locator('.upload-marker').count()}")
```

#### 4. Video Recording

```bash
# Enable video recording for failure analysis
pytest tests/e2e/ --headed --video=retain-on-failure
```

### Lessons Learned: Real-World Fix Examples

#### The Intermittent Test Failure Pattern

##### What Happened

We encountered a pattern where tests would pass individually but fail intermittently during full test suite runs:

- Individual test runs: ✅ PASS
- Full suite runs: ❌ Intermittent failures
- Error: `TimeoutError: Page.goto: Timeout 30000ms exceeded.`
- Pattern: Fixing one timeout would cause another to appear elsewhere

##### Root Cause Analysis

The issue was **browser resource exhaustion**:

- 50+ Chrome processes running simultaneously
- ~2GB+ RAM consumption
- Network bottlenecks from too many simultaneous connections
- Browser instability causing navigation timeouts

##### The Solution

**Immediate Fix**: Kill all Chrome processes before test runs:

```bash
# Windows
taskkill //f //im chrome.exe

# Linux/Mac
pkill -f chrome
```

**Result**:

- Test execution time improved from 120s to 81s (32% faster)
- 100% pass rate restored
- Consistent, reliable test results

##### Key Lessons

1. **Infrastructure Hygiene**: Sometimes the issue isn't with test logic but with underlying resource management
2. **Whack-a-Mole Pattern**: Intermittent failures that move around often indicate resource exhaustion
3. **Individual vs. Batch Testing**: Tests passing individually but failing in batches is a red flag
4. **Browser Process Monitoring**: Regular cleanup of browser processes is essential for E2E testing

#### The `test_feedback_updates.py` Strict Mode Violation

##### What Happened

When replacing `wait_for_timeout()` instances in `test_feedback_updates.py`, we used a generalized pattern:

```python
# Attempted replacement pattern
expect(page.locator("table tbody tr td[colspan='7'], table tbody tr")).to_be_visible()
```

##### Why It Failed

This locator failed with `StrictModeViolation: Multiple elements found` because:

- The selector `"table tbody tr td[colspan='7'], table tbody tr"` matched multiple elements
- In some cases, it matched 100+ table rows
- In other cases, it matched 2 elements (empty state + data rows)
- Playwright's strict mode requires exactly one element for `.to_be_visible()`

##### The Fix

We replaced the broad selector with a more specific approach:

```python
# Working replacement pattern
expect(page.locator("table tbody tr").first).to_be_visible()
```

#### The File Upload Execution Context Issue

##### What Happened

In file upload tests, we encountered "Execution context was destroyed" errors:

```python
# Problematic pattern
file_input.set_input_files(file_path)
clear_upload_attempt_marker(page)  # Page already navigated!
```

##### Why It Failed

- `page.set_input_files` triggered immediate page navigation
- The navigation destroyed the JavaScript execution context
- `clear_upload_attempt_marker` tried to run JavaScript on a destroyed context

##### The Fix

We moved marker clearing before the upload:

```python
# Working pattern
clear_upload_attempt_marker(page)  # Clear before navigation
file_input.set_input_files(file_path)
wait_for_upload_attempt_marker(page)  # Wait on new page
```

##### Key Lessons for Future Testing

1. **Avoid Compound Selectors for Visibility Checks**
    - Don't use `selector1, selector2` patterns for `.to_be_visible()`
    - Use `.first`, `.nth(0)`, or more specific targeting

2. **Test Locators Manually First**
    - Always verify locators work before using in tests
    - Check element counts: `page.locator("selector").count()`

3. **Separate Waiting from Validation**
    - Use simple waits for synchronization: `expect(element).to_be_visible()`
    - Use specific assertions for validation: `assert element.inner_text() == "expected"`

4. **Handle Both Success and Empty States**
    - Design waits that work for both data and empty states
    - Use `.first` when you only need to verify presence, not specific content

5. **Strict Mode is Your Friend**
    - Strict mode violations catch selector problems early
    - They prevent flaky tests from passing with wrong elements
    - Always fix strict mode violations rather than disabling strict mode

6. **File Uploads Require Special Handling**
    - Clear markers before uploads to prevent stale state
    - Handle page navigation that destroys execution context
    - Use appropriate helper functions based on upload behavior

#### Pattern for Future Filter Operations

```python
# ✅ Recommended pattern for filter operations
apply_btn.click()
expect(page.locator("table tbody tr").first).to_be_visible()

# Then validate specific content
if page.locator("table tbody tr td[colspan='7']").count() > 0:
    # Handle empty state
    assert "No updates found" in page.locator("table tbody tr td[colspan='7']").first.inner_text()
else:
    # Handle data rows
    assert page.locator("table tbody tr").count() > 0
```

#### Pattern for Future File Upload Operations

```python
# ✅ Recommended pattern for file uploads with navigation
clear_upload_attempt_marker(page)
file_input = page.locator("input[type='file']")
file_input.set_input_files(file_path)
wait_for_upload_attempt_marker(page)  # Wait on redirected page

# ✅ Recommended pattern for file uploads with feedback
upload_file_and_wait_for_attempt_marker(page, file_path)
expect(page.locator(".alert-success, .alert-danger")).to_be_visible()
```

### Lessons Learned from Marker System Implementation

#### 1. Marker System Benefits

- **Eliminates arbitrary timeouts**: Provides explicit synchronization points
- **Provides reliable synchronization**: Consistent behavior across different environments
- **Reduces test flakiness**: Predictable waiting patterns
- **Improves test performance**: Faster execution with targeted waits

#### 2. Navigation Pattern Consistency

- **Standard navigation approach prevents hanging**: Use `navigate_and_wait_for_ready` consistently
- **Avoid mixing different navigation strategies**: Stick to established patterns
- **Handle page navigation properly**: Account for execution context destruction

#### 3. Test Isolation

- **Excluding problematic tests allows suite to run**: Don't let one bad test block everything
- **Marking tests for investigation maintains visibility**: Keep track of known issues
- **Gradual improvement approach is effective**: Fix issues systematically

#### 4. Documentation Importance

- **Comprehensive documentation prevents confusion**: Clear patterns help future development
- **Decision frameworks help with future development**: Document when to use which helper
- **Migration guides ease transition to new patterns**: Provide clear upgrade paths

---

## Success Metrics

### Test Reliability

- **100% pass rate** in stable environments
- **Consistent results** across multiple runs
- **Fast execution** with minimal arbitrary delays
- **Clear failure messages** for debugging
- **Resource management**: Proper browser process cleanup to prevent intermittent failures

### Coverage Goals

- **Core workflows**: All main user journeys covered
- **Edge cases**: Error conditions and boundary cases
- **File upload scenarios**: All upload workflows tested
- **Accessibility**: Basic accessibility testing included
- **Cross-browser**: Works across different browsers

### Maintenance Goals

- **Easy to extend**: New tests follow established patterns
- **Clear documentation**: All patterns and strategies documented
- **Robust infrastructure**: Reliable test execution environment
- **Fast feedback**: Quick test execution for development workflow
- **Resource monitoring**: Regular cleanup and monitoring of browser processes

---

*This technical guide provides comprehensive information about all testing approaches. For a beginner-friendly overview,
see `testing_overview.md`. For current status and coverage, see `testing_status.md`.*
