# Unit Test Coverage Tracker

## How to Run Your Tests

**From the command line (project root):**

    pytest

To run a specific test file:

    pytest tests/arb/utils/test_date_and_time.py

To see more detailed output:

    pytest -v

**Important:**
If you get import errors, set your PYTHONPATH before running pytest. It should be set to the absolute path of your repo's `source/production` directory. To avoid overwriting your existing PYTHONPATH, prepend your path like this (run from the repo root):

    set PYTHONPATH=D:\local\cursor\feedback_portal\source\production;%PYTHONPATH%

(Replace with your actual repo path if different.)

This ensures you add to the existing PYTHONPATH rather than replacing it.

**In PyCharm:**
- Right-click the test file or function and select “Run pytest…”

*Make sure pytest is installed in your environment:*

    pip install pytest

---

## Legend
- [x] = Unit tests implemented and passing
- [ ] = No unit tests yet
- [~] = Partial coverage or in progress

## arb/utils/
- [x] date_and_time.py
- [ ] json.py
- [ ] misc.py
- [ ] file_io.py
- [ ] generate_github_file_metadata.py
- [ ] time_launch.py
- [ ] constants.py
- [ ] io_wrappers.py
- [~] wtf_forms_util.py (partial, complex/mixed)
- [ ] diagnostics.py
- [ ] web_html.py
- [ ] log_util.py
- [ ] sql_alchemy.py
- [ ] database.py

## arb/portal/
- [ ] constants.py
- [ ] json_update_util.py
- [ ] db_hardcoded.py
- [ ] globals.py
- [ ] wtf_upload.py
- [ ] routes.py (Flask routes, integration tests recommended)
- [ ] sqla_models.py (models, integration tests recommended)
- [ ] extensions.py
- [ ] app.py

*Update this file as you add or improve test coverage!* 