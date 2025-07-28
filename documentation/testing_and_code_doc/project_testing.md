# Project Testing Overview

## Table of Contents
- [Testing Quick Start](./testing_quick_start.md)
- [Testing Infrastructure & CI](./testing_infrastructure.md)
- [Testing Feedback Form File](./testing_feedback_form_file.md)
- [Testing Protocols & Notes](./testing_protocols_and_notes.md)
- [E2E Testing with Playwright](../tests/e2e/README.md)

---

*This file provides the high-level philosophy, goals, and summary of testing for the project. For details on running tests, infrastructure, or protocols, see the linked docs above.*

## Testing Philosophy and Goals

Our approach to unit testing in this codebase is guided by the following principles:

1. **Comprehensive, Honest Coverage:**
   - Achieve the maximum meaningful unit test coverage for all production logic.
   - All functions/classes that can be robustly unit tested should have direct tests.
   - If a function/class cannot be unit tested (e.g., requires a real Flask app, database, or is pure integration glue), this is clearly documented in both the test file (with skip markers and reasons) and the source docstring.

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
   - The goal is not just to maximize coverage numbers, but to ensure that all critical business logic is protected by tests.
   - Uncovered or untestable code is clearly marked so that future changes are made with caution and awareness of risk.

5. **Testing Policy Consistency:**
   - The same standards and process are applied across all modules: portal, utils, and any new code.
   - Trivial files (e.g., `__init__.py`, constants-only modules) are marked as "Testing Complete - Not Needed" and do not require tests.

6. **Examples and Edge Cases:**
   - Where possible, tests should include edge cases and examples that match those in the docstrings.
   - Docstrings should be kept up to date with the actual test coverage and behavior.

**Summary Table of Testing Philosophy**

| Principle                         | Description                                                                 |
|-----------------------------------|-----------------------------------------------------------------------------|
| Maximize meaningful coverage      | Test all production logic that can be robustly unit tested.                 |
| No source changes for testability | Do not refactor production code just for testing.                           |
| Document all limitations          | Clearly mark and explain any untestable code in tests, docstrings, and docs.|
| Prioritize maintainability        | Focus on protecting business logic and managing risk, not just coverage %.  |
| Consistent policy                 | Apply the same standards across all modules and new code.                   |
| Edge cases/examples               | Include edge cases and docstring examples in tests where possible.          |

## No Changes in Source Code Policy for Unit Testing

**Policy Summary:**
- **No production code changes during test improvements:**  
  When adding or improving unit tests, do not modify production source code files (e.g., files in `source/production/arb/...`).
- **Test-only fixes and workarounds:**  
  All fixes, workarounds, and improvements should be implemented only in test files (e.g., `tests/arb/...`).
- **Document limitations, don’t patch source:**  
  If a robust test cannot be implemented without changing the source code, clearly document the limitation in this file. Do not change the source code as part of the testing process.
- **Track and review future source changes:**  
  Any required or recommended source code changes for improved testability should be listed here for future review, but not implemented automatically.

**Rationale:**
- **Protect production code integrity:**  
  This policy ensures the stability and reliability of production code during the testing process.
- **Prevent accidental bugs or regressions:**  
  By not changing production code while focusing on test coverage, we avoid introducing unintended issues.
- **Maintain clear separation:**  
  Keeping test improvements separate from production code changes allows for deliberate, well-reviewed updates to the source code in the future.

**Change Request Counter:**  
`number_of_times_you_ask_me_to_change_my_source_code = 1`
- This counter is incremented each time a source code change is requested or recommended as part of the unit testing update process.

## Ensuring Docstrings are Comprehensive and Suitable for Testing

Our docstring policy is fully aligned with **Testing Philosophy & Goals Item 1: Comprehensive, Honest Coverage**. Every function and class should have a clear, accurate, and up-to-date docstring that supports robust, maintainable unit testing. This ensures:
- All arguments, return values, and exceptions are explicitly documented.
- Edge cases, default values, and special behaviors (e.g., handling of `None` or empty values) are described.
- Examples are included where helpful, using a consistent, readable format (Input/Output style, no '>>>' prompts).
- Any limitations, ambiguous behaviors, or TODOs for risky argument handling are clearly noted.

**Process:**
- Review each function and class for docstring completeness and clarity.
- Update docstrings to use 2-space indentation, matching project style.
- Ensure every argument, return, and exception is described, including types and default values.
- Add examples for edge cases and typical usage, formatted for readability.
- If a function’s behavior is ambiguous or not robust, add a note or TODO for follow-up during unit testing or refactoring.
- If a function cannot be robustly tested, document the limitation in both the test file (with skip markers and reasons) and the source docstring.

This approach ensures that our documentation is not only comprehensive but also directly supports our testing strategy, making it easier for future maintainers to understand coverage, limitations, and risks.

## Types of Tests We Run

### 1. Unit Tests
- **Purpose:** Test individual functions and modules in isolation
- **Coverage:** Isolated logic with mocked dependencies
- **Location:** `tests/arb/`
- **Status:** Comprehensive coverage for utility functions and business logic

### 2. Integration Tests
- **Purpose:** Test complete workflows and database operations
- **Coverage:** End-to-end workflows, file uploads, database operations
- **Location:** `tests/arb/portal/`
- **Status:** Full coverage for upload workflows and data processing

### 3. E2E UI Automation
- **Purpose:** Test complete user workflows via browser automation
- **Coverage:** Full UI automation with Playwright
- **Location:** `tests/e2e/`
- **Status:** 100% success rate, enhanced reliability and debugging
- **Requirements:** Flask app running, Playwright installed with browsers
- **Benefits:** Auto-waiting, video recording, trace viewer, cross-browser support

### 4. Automated Test Data Generation
- **Purpose:** Generate comprehensive test data for all scenarios
- **Coverage:** Excel files for all schemas and validation cases
- **Location:** `scripts/generate_test_excel_files.py`
- **Status:** Comprehensive test data for all sectors and validation cases

### 5. Cross-Field Validation Tests
- **Purpose:** Test conditional field visibility and regulatory compliance
- **Coverage:** Conditional logic, cross-field validation, regulatory rules
- **Location:** `tests/arb/portal/test_cross_field_conditional_logic.py`
- **Status:** Full coverage for all major sectors

### 6. Round-Trip Export/Import Testing

### 7. Integration Test Suite

## E2E Testing Migration to Playwright

### Migration Completed ✅
The E2E testing framework has been successfully migrated from Selenium WebDriver to Playwright for improved reliability, performance, and debugging capabilities.

### Key Benefits Achieved
- **Better Reliability**: Auto-waiting for elements reduces flaky tests
- **Enhanced Debugging**: Built-in video recording and trace viewer
- **Modern Web Support**: Better handling of dynamic content and JavaScript
- **Performance**: Faster execution and lower resource usage
- **Cross-Browser**: Single API for Chrome, Firefox, and Safari

### New E2E Test Files
- `tests/e2e/test_excel_upload_ui_playwright.py` - Standalone test suite
- `tests/e2e/test_excel_upload_playwright_pytest.py` - Pytest-compatible tests
- `tests/e2e/debug_upload_page_playwright.py` - Debug utility
- `tests/e2e/test_playwright_setup.py` - Setup verification
- `tests/e2e/README.md` - Comprehensive documentation

### Removed Selenium Dependencies
- `selenium` package
- `webdriver-manager` package
- Chrome WebDriver setup and management
- Selenium-specific selectors and wait conditions

### Migration Impact
- **Low Migration Effort**: Only 2 files needed migration (~579 lines total)
- **High Impact**: Critical file upload functionality now more reliable
- **Future-Proof**: Better support for modern web features and debugging

## How We Measure Coverage
- **Unit Test Coverage:** Individual module testing with mocked dependencies
- **Integration Test Coverage:** End-to-end workflows, database operations, file uploads
- **E2E Test Coverage:** Complete user workflows via Playwright automation with enhanced debugging
- **Test Data Coverage:** Comprehensive scenarios for all sectors and validation cases


## Table 1. Testing Status Codes & Meanings

| Code    | Meaning                                                                                  |
|---------|------------------------------------------------------------------------------------------|
| TC      | Testing Complete: All meaningful logic is fully tested (unit and/or integration).        |
| TC-NT   | Testing Complete - Not Needed: File is trivial (e.g., __init__.py, constants-only) and does not require tests. |
| ITC     | Integration Testing Complete: All integration points are fully tested.                   |
| UTC     | Unit Testing Complete: All unit-testable logic is fully tested.                          |
| UTP     | Unit Testing Partial: Some unit tests exist, but coverage is incomplete.                 |
| ITP     | Integration Testing Partial: Some integration tests exist, but coverage is incomplete.   |
| FPC     | First Pass Complete: Basic structure tested; context-dependent or complex features skipped. |
| NR      | Not Required: Testing not required due to file purpose (e.g., data, config, or legacy).  |
| SKIP    | Skipped: Test intentionally skipped (with documented reason).                            |
| TODO    | Testing not yet implemented or planned for future.                                       |



## Testing Progress

### Table 2. Unit and Integration Testing Results

| # | File (arb/portal/util)                        | Testing Status             |
|---|-----------------------------------------------|:--------------------------:|
|  1| arb/__init__.py                               | TC-NT     |
|  2| arb/logging/arb_logging.py                    | UTC        |
|  3| arb/portal/__init__.py                        | TC-NT     |
|  4| arb/portal/app.py                             | ITC        |
|  5| arb/portal/constants.py                       | TC-NT     |
|  6| arb/portal/db_hardcoded.py                    | UTC        |
|  7| arb/portal/extensions.py                      | TC-NT     |
|  8| arb/portal/globals.py                         | UTC        |
|  9| arb/portal/json_update_util.py                | UTC        |
| 10| arb/portal/routes.py                          | TC         |
| 11| arb/portal/sqla_models.py                     | TC         |
| 12| arb/portal/wtf_landfill.py                    | UTC        |
| 13| arb/portal/wtf_oil_and_gas.py                 | UTC        |
| 14| arb/portal/wtf_upload.py                      | UTC        |
| 15| arb/portal/startup/__init__.py                | TC-NT     |
| 16| arb/portal/startup/db.py                      | ITC        |
| 17| arb/portal/startup/flask.py                   | UTC        |
| 18| arb/portal/startup/runtime_info.py            | UTC        |
| 19| arb/portal/utils/__init__.py                  | TC-NT     |
| 20| arb/portal/utils/db_ingest_util.py            | UTC        |
| 21| arb/portal/utils/db_introspection_util.py     | UTC        |
| 22| arb/portal/utils/file_upload_util.py          | UTC        |
| 23| arb/portal/utils/form_mapper.py               | UTC        |
| 24| arb/portal/utils/github_and_ai.py             | TC-NT     |
| 25| arb/portal/utils/route_util.py                | UTC        |
| 26| arb/portal/utils/sector_util.py               | FPC        |
| 27| arb/utils/__init__.py                         | TC-NT     |
| 28| arb/utils/constants.py                        | TC-NT     |
| 29| arb/utils/database.py                         | UTC        |
| 30| arb/utils/date_and_time.py                    | UTC        |
| 31| arb/utils/diagnostics.py                      | UTC        |
| 32| arb/utils/file_io.py                          | UTC        |
| 33| arb/utils/io_wrappers.py                      | UTC        |
| 34| arb/utils/json.py                             | UTC        |
| 35| arb/utils/log_util.py                         | UTC        |
| 36| arb/utils/misc.py                             | UTC        |
| 37| arb/utils/sql_alchemy.py                      | UTC        |
| 38| arb/utils/web_html.py                         | UTC        |
| 39| arb/utils/wtf_forms_util.py                   | TC         |
| 40| arb/wsgi.py                                   | TC-NT     |
| 41| arb/portal/config/__init__.py                 | UTC        |
| 42| arb/portal/config/accessors.py                | UTC        |
| 43| arb/portal/config/settings.py                 | UTC        |

### Table 3. Supplemental Progress Notes

| File                        | Status Code | Notes / Special Considerations                                 |
|-----------------------------|-------------|---------------------------------------------------------------|
| arb/portal/db_hardcoded.py  | UTC         | All tests pass. Range validation tested in form validation.    |
| arb/portal/globals.py       | UTC         | Integration tests require real DB. Some functions skipped.     |
| arb/portal/sqla_models.py   | TC          | run_diagnostics intentionally skipped (legacy, dev-only).      |
| arb/portal/routes.py        | TC          | 5 scenarios skipped for external dependencies.                 |
| arb/portal/utils/sector_util.py | FPC     | DB operations skipped; follow-up context testing required.     |
| arb/utils/wtf_forms_util.py | TC          | Integration-dependent functions skipped, documented in tests.  |

#### Integration Test Files Overview
- **tests/arb/portal/test_integration_app.py**: Covers all simple GET routes and basic integration points for app.py and routes.py.
- **tests/arb/portal/test_routes_integration.py**: Dedicated to complex POST/file upload routes and those requiring specific DB/file state in routes.py. Includes skip markers and docstrings for each.
- **tests/arb/portal/test_startup_db_integration.py**: Covers database reflection, model registration, table creation, and combined initialization for startup/db.py using a Flask app context and in-memory SQLite DB.

**Summary:**
- All integration points for app.py, routes.py, and startup/db.py are now covered by automated integration tests, with limitations and skipped tests clearly documented.
- Progress tables and documentation have been updated to reflect this expanded coverage.
