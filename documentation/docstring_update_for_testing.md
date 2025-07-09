# Docstring Update for Testing Tracker

## Purpose
This document tracks the progress and methodology of enhancing docstrings in the `portal` and `utils` directories to support robust, maintainable unit testing. It also serves as a checklist for argument analysis and edge case documentation.

## Docstring Enhancement and Argument Analysis Process
- All function and class docstrings are updated to use 2-space indentation, matching project style.
- Each docstring includes:
  - A clear, concise summary line.
  - Explicit documentation of all arguments, including types, default values, and edge case handling (e.g., `None`, empty strings).
  - Returns and Raises sections, with details on output and exceptions.
  - Examples where helpful, always using a clear and consistent format:
      Examples:
        Input : ...
        Output: ...
    These examples are retained wherever they clarify usage or edge cases, and are formatted for readability and consistency.
  - **Policy:** As of this point, all docstring enhancements will retain clear and consistently formatted examples wherever they clarify usage or edge cases. Examples will use the Input/Output style, and the '>>>' prompt will not be used.
  - Notes or TODOs for ambiguous or risky argument handling, especially for `None` or empty values.
- During this process, functions are reviewed for how they handle edge cases. If behavior is ambiguous or not robust, a note or TODO is added to the docstring for follow-up during unit testing or refactoring.

## Source Code Change Policy for Unit Testing (2025-07-04)

**Policy Summary:**
- During the process of adding or improving unit tests, no changes will be made to production source code files (e.g., files in source/production/arb/...).
- All fixes, workarounds, and improvements will be made only in the test files (e.g., tests/arb/...).
- If a comprehensive or robust test cannot be implemented without a change to the source code, the limitation will be clearly documented in this file, but the source code will not be changed as part of the testing process.
- Any required or recommended source code changes for improved testability will be listed here for future review, but not implemented automatically.

**Rationale:**
- This policy ensures the integrity and stability of production code during the testing process.
- It prevents accidental introduction of bugs or regressions while focusing on test coverage.
- It maintains a clear separation between test improvements and production code changes, allowing for deliberate review of any future source code updates.

**Counter: number_of_times_you_ask_me_to_change_my_source_code = 1**
- This counter will be incremented each time a source code change is requested or recommended as part of the unit testing update process.

---

## Test Coverage Status for Current Batch (as of 2025-07-04)

| File                                      | Test Status         | Notes / Pending Source Change |
|-------------------------------------------|---------------------|-------------------------------|
| arb/logging/arb_logging.py                | Complete            | All tests pass                |
| arb/portal/db_hardcoded.py                | Complete            | All tests pass                |
| arb/portal/globals.py                     | Partial (Skipped)   | 2 tests skipped: cannot robustly mock methods due to imports inside methods. See below. |
| arb/portal/json_update_util.py            | Complete            | All tests pass                |
| arb/portal/sqla_models.py                 | Partial (Skipped)   | Only __repr__ methods tested; run_diagnostics skipped as legacy/dev code. |
| arb/portal/wtf_landfill.py                | Skipped (all tests) | WTForm requires Flask app context; see test file. |
| arb/portal/wtf_oil_and_gas.py             | Skipped (all tests) | WTForm requires Flask app context; see test file. |
| arb/portal/wtf_upload.py                  | Skipped (all tests) | WTForm requires Flask app context; see test file. |
| arb/portal/startup/flask.py               | Skipped (all tests) | configure_flask_app requires Flask app context.   |
| arb/portal/startup/runtime_info.py        | Skipped (partial)   | print_runtime_diagnostics skipped; others testable.|
| arb/portal/utils/db_ingest_util.py        | Skipped (all tests) | Requires DB/SQLAlchemy context; see test file.    |
| arb/portal/utils/db_introspection_util.py | Skipped (all tests) | Requires DB/SQLAlchemy context; see test file.    |
| arb/portal/utils/file_upload_util.py      | Skipped (all tests) | Requires Flask/file I/O context; see test file.   |
| arb/portal/utils/form_mapper.py           | Skipped (all tests) | Requires Flask/WTForms context; see test file.    |
| arb/portal/utils/route_util.py            | Skipped (all tests) | Requires Flask/request context; see test file.    |
| arb/portal/utils/sector_util.py           | Skipped (all tests) | Requires integration context; see test file.      |

**Batch status:**
- All test files for this batch were created and discovered by pytest.
- All tests were skipped as intended, with clear skip reasons matching source code and context limitations.
- No source code changes were made for testability in this batch.
- The source code change counter remains at 1.

## Progress Table

| # | File (arb/portal/util)                        | Enhanced Documentation| Testing Status             | Unit Testing Order |
|---|-----------------------------------------------|:---------------------:|:--------------------------:|:------------------:|
|  1| arb/__init__.py                               | Yes                   | Not Needed - Trivial       |                    |
|  2| arb/logging/arb_logging.py                    | Yes                   | Unit Testing Recommended   |  5                 |
|  3| arb/portal/__init__.py                        | Yes                   | Not Needed - Trivial       |                    |
|  4| arb/portal/app.py                             | Yes                   | Integration Testing Recommended |                |
|  5| arb/portal/constants.py                       | Yes                   | Not Needed - Trivial       |                    |
|  6| arb/portal/db_hardcoded.py                    | Yes                   | Unit Testing Recommended   | 13                 |
|  7| arb/portal/extensions.py                      | Yes                   | Not Needed - Trivial       |                    |
|  8| arb/portal/globals.py                         | Yes                   | Unit Testing Recommended   | 12                 |
|  9| arb/portal/json_update_util.py                | Yes                   | Unit Testing Recommended   | 10                 |
| 10| arb/portal/routes.py                          | Yes                   | Integration Testing Recommended |                |
| 11| arb/portal/sqla_models.py                     | Yes                   | Unit Testing Recommended   | 14                 |
| 12| arb/portal/wtf_landfill.py                    | Yes                   | Skipped (all tests)        | 18                 |
| 13| arb/portal/wtf_oil_and_gas.py                 | Yes                   | Skipped (all tests)        | 19                 |
| 14| arb/portal/wtf_upload.py                      | Yes                   | Skipped (all tests)        | 20                 |
| 15| arb/portal/startup/__init__.py                | Yes                   | Not Needed - Trivial       |                    |
| 16| arb/portal/startup/db.py                      | Yes                   | Integration Testing Recommended |                |
| 17| arb/portal/startup/flask.py                   | Yes                   | Skipped (all tests)        | 16                 |
| 18| arb/portal/startup/runtime_info.py            | Yes                   | Skipped (partial)          | 17                 |
| 19| arb/portal/utils/__init__.py                  | Yes                   | Not Needed - Trivial       |                    |
| 20| arb/portal/utils/db_ingest_util.py            | Yes                   | Skipped (all tests)        |  2                 |
| 21| arb/portal/utils/db_introspection_util.py     | Yes                   | Skipped (all tests)        |  8                 |
| 22| arb/portal/utils/file_upload_util.py          | Yes                   | Skipped (all tests)        | 15                 |
| 23| arb/portal/utils/form_mapper.py               | Yes                   | Skipped (all tests)        |  3                 |
| 24| arb/portal/utils/github_and_ai.py             | Yes                   | Not Needed - Trivial       |                    |
| 25| arb/portal/utils/route_util.py                | Yes                   | Skipped (all tests)        | 11                 |
| 26| arb/portal/utils/sector_util.py               | Yes                   | Skipped (all tests)        |  9                 |
| 27| arb/utils/__init__.py                         | Yes                   | Not Needed - Trivial       |                    |
| 28| arb/utils/constants.py                        | Yes                   | Not Needed - Trivial       |                    |
| 29| arb/utils/database.py                         | Yes                   | Unit Testing Complete      |  7                 |
| 30| arb/utils/date_and_time.py                    | Yes                   | Unit Testing Complete      |  1                 |
| 31| arb/utils/diagnostics.py                      | Yes                   | Unit Testing Complete      | 21                 |
| 32| arb/utils/file_io.py                          | Yes                   | Unit Testing Complete      |  6                 |
| 33| arb/utils/io_wrappers.py                      | Yes                   | Unit Testing Complete      | 22                 |
| 34| arb/utils/json.py                             | Yes                   | Unit Testing Complete      |  4                 |
| 35| arb/utils/log_util.py                         | Yes                   | Unit Testing Recommended   | 23                 |
| 36| arb/utils/misc.py                             | Yes                   | Unit Testing Recommended   | 24                 |
| 37| arb/utils/sql_alchemy.py                      | Yes                   | Unit Testing Recommended   |  2                 |
| 38| arb/utils/web_html.py                         | Yes                   | Unit Testing Recommended   | 25                 |
| 39| arb/utils/wtf_forms_util.py                   | Yes                   | Unit Testing Partial (~)   | 26                 |
| 40| arb/wsgi.py                                   | Yes                   | Not Needed - Trivial       |                    |
| 41| arb/portal/config/__init__.py                 | Yes                   | Not Needed - Trivial       |                    |
| 42| arb/portal/config/accessors.py                | Yes                   | Unit Testing Recommended   | 27                 |
| 43| arb/portal/config/settings.py                 | Yes                   | Unit Testing Recommended   | 28                 |

## Progress Table 2 - Authentication related

| # | File (arb/auth/auth_example_app)              | Enhanced Documentation | Unit Testing Status         |
|---|-----------------------------------------------|:---------------------:|:--------------------------:|
|  1| arb/auth/__init__.py                          | No                    | No                         |
|  2| arb/auth/default_settings.py                  | No                    | No                         |
|  3| arb/auth/email_util.py                        | No                    | No                         |
|  4| arb/auth/forms.py                             | No                    | No                         |
|  5| arb/auth/login_manager.py                     | No                    | No                         |
|  6| arb/auth/migrate_roles.py                     | No                    | No                         |
|  7| arb/auth/models.py                            | No                    | No                         |
|  8| arb/auth/okta_settings.py                     | No                    | No                         |
|  9| arb/auth/role_decorators.py                   | No                    | No                         |
| 10| arb/auth/role_examples.py                     | No                    | No                         |
| 11| arb/auth/routes.py                            | No                    | No                         |
| 12| arb/auth/test_auth.py                         | No                    | No                         |
| 13| arb/auth_example_app/__init__.py              | No                    | No                         |
| 14| arb/auth_example_app/app.py                   | No                    | No                         |
| 15| arb/auth_example_app/config.py                | No                    | No                         |
| 16| arb/auth_example_app/extensions.py            | No                    | No                         |
| 17| arb/auth_example_app/wsgi.py                  | No                    | No                         |

---

## Testing Analysis and Recommendations

### Testing Categories Used:

1. **Not Needed - Trivial**: Files that are empty, contain only imports/constants, or are simple `__init__.py` files with no testable logic.

2. **Unit Testing Recommended**: Files with discrete functions/classes that can be tested in isolation, typically utility functions, data processing, or business logic.

3. **Integration Testing Recommended**: Files that coordinate multiple components and require testing with dependencies (database, Flask app context, etc.).

4. **Unit Testing Complete**: Files that already have comprehensive unit tests.

5. **Unit Testing Partial (~)**: Files with some existing tests but needing completion.

### Detailed Analysis by File:

#### **Not Needed - Trivial (8 files):**
- `arb/__init__.py`, `arb/portal/__init__.py`, `arb/portal/constants.py`, `arb/portal/extensions.py`, `