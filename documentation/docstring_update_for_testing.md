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

# Comments and Guidance for Next Documentation Analysis (portal directory)

- **What to communicate in the new chat:**
  - You are continuing a systematic, comprehensive docstring and documentation enhancement process, now focusing on the `portal` directory.
  - The goal is to prepare for robust, maintainable unit testing by ensuring all functions/classes have clear, explicit docstrings, argument edge case documentation, and consistently formatted Input/Output examples.
  - The process includes:
    - 2-space indentation for all docstrings
    - Explicit Args/Returns/Raises/Examples/Notes sections
    - Retaining and clearly formatting examples (Input/Output style, no `>>>`)
    - Documenting ambiguous or risky argument handling with Notes or TODOs
    - Only making code changes for linter safety or to clarify docstring/code alignment
  - Mention that the process was previously applied to all `utils` modules, and the Progress Table in this file tracks status.
  - If the assistant gets confused about which files have been processed, clarify by referencing the Progress Table and your own notes.
  - If you change strategy (e.g., batch vs. file-by-file, or how you handle ambiguous arguments), note it in the chat and in this file for future reference.
  - If you encounter files with legacy or unclear code, add TODOs or notes for follow-up during unit testing.

- **Tips for a smooth transition:**
  - Start the new chat with a summary of the process, rationale, and your documentation style preferences.
  - Reference this file for the current status and policies.
  - Ask the assistant to update this file as you progress through the `portal` directory.
  - If you pause and resume, always clarify which files have been fully processed and which are in progress.
  - Use clear commit messages and keep the Progress Table up to date.

- **Strategy changes or lessons learned:**
  - Explicitly documenting edge cases and example formatting up front saves time and confusion later.
  - When in doubt, over-document rather than under-document, especially for ambiguous or risky argument handling.
  - If the assistant loses track of progress, use the Progress Table and your own notes to realign.
  - Keep communication explicit about what is in scope for each phase (docstrings only, then code/linter fixes, then unit tests). 

