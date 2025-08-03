# Playwright Testing Companion

## Overview

This document provides a comprehensive guide to E2E testing with Playwright for the ARB Feedback Portal. It consolidates all proven strategies, best practices, and working patterns from our testing experience.

## Table of Contents

1. [Core Testing Strategy](#core-testing-strategy)
2. [E2E Readiness Marker System](#e2e-readiness-marker-system)
3. [Waiting Strategies](#waiting-strategies)
4. [Test Structure and Patterns](#test-structure-and-patterns)
5. [Setup and Configuration](#setup-and-configuration)
6. [Running Tests](#running-tests)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Core Testing Strategy

### Philosophy
- **Single-purpose tests**: Each test covers one workflow for clarity and reliability
- **Explicit synchronization**: Use Playwright's waiting tools to avoid flakiness
- **Robust patterns**: Replace arbitrary timeouts with element-specific assertions
- **Maintainable code**: Follow consistent patterns across all tests

### Test Types
1. **Unit Tests**: Individual functions and modules (`tests/arb/`)
2. **Integration Tests**: Complete workflows and database operations (`tests/arb/portal/`)
3. **E2E Tests**: Complete user workflows via browser automation (`tests/e2e/`)

---

## E2E Readiness Marker System

### Overview
Our project uses a custom E2E readiness marker system to ensure pages are fully loaded before interaction.

### Implementation
1. **JavaScript File**: `static/js/e2e_testing_related.js`
2. **Jinja Include**: `templates/includes/e2e_testing_related.jinja`
3. **Helper Functions**: `tests/e2e/e2e_helpers.py`

### Helper Functions
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

### Usage Pattern
```python
# Instead of:
page.goto(f"{BASE_URL}/upload_staged")
page.wait_for_load_state("networkidle")

# Use:
navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged")
```

### When NOT to Use E2E Readiness Marker
- **File upload scenarios**: Page navigation destroys execution context
- **Immediate redirects**: Page reloads before marker can be set
- **Dynamic content**: Content that loads after initial page render

---

## Waiting Strategies

### ✅ Recommended Patterns

#### 1. Element-Specific Waits (Preferred)
```python
# Wait for specific element to be visible
expect(page.locator("table tbody tr").first).to_be_visible()

# Wait for either data rows or empty state
expect(page.locator("table tbody tr td[colspan='7'], table tbody tr")).to_be_visible()

# Wait for checkbox state
expect(checkbox).to_be_checked()
expect(checkbox).not_to_be_checked()
```

#### 2. Navigation Waits
```python
# For actions that trigger page navigation
with page.expect_navigation():
    confirm_btn.click()

# For URL changes
page.wait_for_url("**/success", timeout=10000)
```

#### 3. Response Waits
```python
# For specific API calls
with page.expect_response("**/api/endpoint"):
    submit_btn.click()
```

### ❌ Avoid These Patterns

#### 1. Arbitrary Timeouts
```python
# DON'T: Use arbitrary timeouts
page.wait_for_timeout(1000)

# DO: Wait for specific elements
expect(page.locator("table tbody tr")).to_be_visible()
```

#### 2. Network Idle (Problematic)
```python
# DON'T: Use networkidle (can hang indefinitely)
page.wait_for_load_state("networkidle")

# DO: Use E2E readiness marker or element-specific waits
navigate_and_wait_for_ready(page, url)
```

#### 3. Count Assertions Without Waiting
```python
# DON'T: This doesn't wait at all
expect(page.locator("table tbody tr")).to_have_count_at_least(0)

# DO: Wait for visibility
expect(page.locator("table tbody tr")).to_be_visible()
```

#### 4. Multi-Element Locators in Strict Mode
```python
# DON'T: Use broad selectors that match multiple elements
expect(page.locator("table tbody tr td[colspan='7'], table tbody tr")).to_be_visible()

# DO: Use .first() or more specific targeting
expect(page.locator("table tbody tr").first).to_be_visible()
```

### Pattern by Use Case

#### Filter Operations
```python
# Apply filter and wait for results
apply_btn.click()
expect(page.locator("table tbody tr").first).to_be_visible()
```

#### File Uploads
```python
# For file uploads that trigger navigation
with page.expect_navigation():
    upload_page.set_input_files(file_path)

# For file uploads that show success/error messages
upload_page.set_input_files(file_path)
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

## Test Structure and Patterns

### Basic Test Template
```python
import pytest
from playwright.sync_api import Page, expect
from e2e_helpers import navigate_and_wait_for_ready

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

### Test File Organization
```
tests/e2e/
├── test_excel_upload_workflows.py    # Main upload workflows
├── test_feedback_updates.py          # Updates page functionality
├── test_review_staged.py             # Staged file review
├── test_javascript_logging.py        # JS diagnostics
├── test_homepage.py                  # Homepage functionality
├── test_list_uploads.py              # Upload listing
├── e2e_helpers.py                    # Shared helper functions
└── conftest.py                       # Pytest configuration
```

### Naming Conventions
- **Test functions**: `test_descriptive_name`
- **Test files**: `test_feature_name.py`
- **Helper functions**: `descriptive_verb_noun`
- **Selectors**: Use role-based selectors when possible

### Selector Best Practices
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

## Setup and Configuration

### Prerequisites
1. **Python Environment**: Python 3.8+
2. **Dependencies**: `pytest`, `playwright`
3. **Browsers**: Playwright browsers installed
4. **Flask App**: Running for E2E tests

### Installation
```bash
# Install dependencies
pip install pytest playwright

# Install browsers
playwright install

# Set PYTHONPATH (from project root)
set PYTHONPATH=D:\local\cursor\feedback_portal\source\production;%PYTHONPATH%
```

### Environment Variables
```bash
# Required for database tests
export DATABASE_URI=postgresql+psycopg2://user:pass@localhost:5432/db

# Optional: Override test base URL
export TEST_BASE_URL=http://localhost:5000
```

### Flask App Setup
```bash
# Start Flask app (required for E2E tests)
cd source/production
flask --app arb/wsgi run --debug --no-reload
```

---

## Running Tests

### Command Format
```bash
# Recommended format with verbose output and logging
pytest tests/e2e/test_file.py -v -k "test_name" | tee output.txt
```

### Common Commands

#### Run All E2E Tests
```bash
pytest tests/e2e/ -v | tee e2e_all.txt
```

#### Run Specific Test File
```bash
pytest tests/e2e/test_feedback_updates.py -v | tee feedback_updates.txt
```

#### Run Specific Test
```bash
pytest tests/e2e/test_feedback_updates.py -v -k "test_filter_functionality" | tee filter_test.txt
```

#### Run Tests by Pattern
```bash
# All upload-related tests
pytest tests/e2e/ -v -k "upload" | tee upload_tests.txt

# All filter-related tests
pytest tests/e2e/ -v -k "filter" | tee filter_tests.txt
```

#### Debug Mode
```bash
# Run with browser visible
pytest tests/e2e/test_file.py --headed -v

# Interactive debugging
pytest tests/e2e/test_file.py --headed --pause-on-failure
```

### Test Output Files
- `e2e_all.txt` - Complete test suite results
- `filter_tests.txt` - Filter-specific test results
- `upload_tests.txt` - Upload workflow test results
- `debug_output.txt` - Debug information

---

## Troubleshooting

### Common Issues

#### 1. E2E Readiness Marker Timeout
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

#### 2. Multi-Element Locator Issues
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

#### 3. Execution Context Destroyed
```python
# Problem: Page navigation during file upload
Execution context was destroyed, most likely because of a navigation

# Solution: Use expect_navigation for file uploads
with page.expect_navigation():
    upload_page.set_input_files(file_path)
```

#### 4. Flask App Not Running
```bash
# Problem: E2E tests fail with connection errors
# Solution: Start Flask app first
cd source/production
flask --app arb/wsgi run --debug --no-reload
```

#### 5. Browser Not Found
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
```

#### 4. Video Recording
```bash
# Enable video recording for failure analysis
pytest tests/e2e/ --headed --video=retain-on-failure
```

---

## Best Practices

### 1. Test Design
- **Single responsibility**: Each test covers one specific functionality
- **Descriptive names**: Test names should clearly indicate what they test
- **Proper setup/teardown**: Use pytest fixtures for common setup
- **Independent tests**: Tests should not depend on each other

### 2. Waiting Strategies
- **Prefer element-specific waits** over arbitrary timeouts
- **Use E2E readiness marker** for standard page navigation
- **Handle both success and failure states** in assertions
- **Provide clear error messages** in assertions

### 3. Selector Strategy
- **Role-based selectors first**: `page.get_by_role("button", name="Submit")`
- **Specific CSS selectors**: `page.locator("table tbody tr")`
- **Avoid generic selectors**: Don't use `page.locator("button")`
- **Test selectors manually**: Verify selectors work before using in tests

### 4. Error Handling
- **Graceful degradation**: Handle cases where elements might not exist
- **Meaningful assertions**: Provide clear error messages
- **Screenshots on failure**: Capture visual state for debugging
- **Logging**: Add debug information for troubleshooting

### 5. Performance
- **Minimize waits**: Use targeted waits instead of long timeouts
- **Parallel execution**: Run tests in parallel when possible
- **Resource cleanup**: Close browsers and clean up resources
- **Efficient selectors**: Use efficient CSS selectors

### 6. Maintenance
- **Consistent patterns**: Follow established patterns across all tests
- **Documentation**: Keep test documentation up to date
- **Regular review**: Periodically review and update test patterns
- **Version control**: Track changes to test infrastructure

---

## Success Metrics

### Test Reliability
- **100% pass rate** in stable environments
- **Consistent results** across multiple runs
- **Fast execution** with minimal arbitrary delays
- **Clear failure messages** for debugging

### Coverage Goals
- **Core workflows**: All main user journeys covered
- **Edge cases**: Error conditions and boundary cases
- **Accessibility**: Basic accessibility testing included
- **Cross-browser**: Works across different browsers

### Maintenance Goals
- **Easy to extend**: New tests follow established patterns
- **Clear documentation**: All patterns and strategies documented
- **Robust infrastructure**: Reliable test execution environment
- **Fast feedback**: Quick test execution for development workflow

---

## Lessons Learned: Real-World Fix Example

### The `test_feedback_updates.py` Strict Mode Violation

#### What Happened
When replacing `wait_for_timeout()` instances in `test_feedback_updates.py`, we used a generalized pattern:
```python
# Attempted replacement pattern
expect(page.locator("table tbody tr td[colspan='7'], table tbody tr")).to_be_visible()
```

#### Why It Failed
This locator failed with `StrictModeViolation: Multiple elements found` because:
- The selector `"table tbody tr td[colspan='7'], table tbody tr"` matched multiple elements
- In some cases, it matched 100+ table rows
- In other cases, it matched 2 elements (empty state + data rows)
- Playwright's strict mode requires exactly one element for `.to_be_visible()`

#### The Fix
We replaced the broad selector with a more specific approach:
```python
# Working replacement pattern
expect(page.locator("table tbody tr").first).to_be_visible()
```

#### Why This Works
- `.first` ensures we're targeting exactly one element
- We only need to verify that table content is visible, not specific content
- This handles both data rows and empty state rows
- The test logic after the wait handles the specific content validation

#### Key Lessons for Future Testing

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

---

## References

- [Playwright Documentation](https://playwright.dev/python/)
- [Pytest Documentation](https://docs.pytest.org/)
- [E2E Readiness Strategy](./e2e_playwright_readiness_strategy.md)
- [Wait for Timeout Analysis](./wait_for_timeout_analysis_summary.md) 