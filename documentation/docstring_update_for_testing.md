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

## Progress Table

| File (portal/util)                | Enhanced Documentation | Unit Testing Status         |
|-----------------------------------|:---------------------:|:--------------------------:|
| portal/constants.py               | No                    | No                         |
| portal/json_update_util.py        | No                    | No                         |
| portal/db_hardcoded.py            | No                    | No                         |
| portal/globals.py                 | No                    | No                         |
| portal/wtf_upload.py              | No                    | No                         |
| portal/routes.py                  | No                    | No (integration suggested) |
| portal/sqla_models.py             | No                    | No (integration suggested) |
| portal/extensions.py              | No                    | No                         |
| portal/app.py                     | No                    | No                         |
| utils/date_and_time.py            | Yes                   | Yes                        |
| utils/json.py                     | Yes                   | No                         |
| utils/misc.py                     | Yes                   | No                         |
| utils/file_io.py                  | Yes                   | No                         |
| utils/constants.py                | Yes                   | No                         |
| utils/io_wrappers.py              | Yes                   | No                         |
| utils/wtf_forms_util.py           | Yes                   | Partial (~)                |
| utils/diagnostics.py              | Yes                   | No                         |
| utils/web_html.py                 | Yes                   | No                         |
| utils/log_util.py                 | Yes                   | No                         |
| utils/sql_alchemy.py              | Yes                   | No                         |
| utils/database.py                 | Yes                   | No                         | 

---

**Update (YYYY-MM-DD):**
As of today, all functions in `utils/wtf_forms_util.py` have been reviewed and enhanced for docstring clarity, explicit argument edge case documentation, and consistently formatted examples. This completes the documentation enhancement phase for this file. 

---

**Comprehensively Refactored utils Files (docstrings, edge cases, examples):**
- date_and_time.py
- json.py
- misc.py
- file_io.py
- constants.py
- io_wrappers.py
- wtf_forms_util.py
- diagnostics.py
- web_html.py
- log_util.py
- sql_alchemy.py
- database.py 