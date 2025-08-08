# E2E Test Coverage Summary: Main Menu and Dropdowns

This document summarizes the main menu items, their dropdown options, associated routes, and the status of end-to-end (
E2E) test coverage for the Feedback Portal at http://127.0.0.1:5000/portal_updates.

---

## Main Menu Structure & E2E Test Coverage

### 1. Spreadsheet/Uploads

| Dropdown Item                  | Route            | E2E Test File(s)                                               | Status   |
|--------------------------------|------------------|----------------------------------------------------------------|----------|
| Upload Feedback Spreadsheet    | `/upload`        | `test_excel_upload_workflows.py`, `test_single_page.py`        | **Full** |
| Stage Feedback Spreadsheet     | `/upload_staged` | `test_excel_upload_workflows.py`                               | **Full** |
| View Staged Files              | `/list_staged`   | `test_excel_upload_workflows.py`, `test_javascript_logging.py` | **Full** |
| List Uploaded Files            | `/list_uploads`  | `test_list_uploads.py`                                         | **Full** |
| Something else here (disabled) | —                | —                                                              | N/A      |

### 2. Analysis Tools

| Dropdown Item               | Route                 | E2E Test File(s)           | Status   |
|-----------------------------|-----------------------|----------------------------|----------|
| Feedback Updates            | `/portal_updates`     | `test_feedback_updates.py` | **Full** |
| Update Incidence (disabled) | `/incidence_update/1` | —                          | N/A      |

### 3. Developer Utilities

| Dropdown Item                | Route                           | E2E Test File(s)                                        | Status        |
|------------------------------|---------------------------------|---------------------------------------------------------|---------------|
| Show Log File                | `/show_log_file`                | `test_developer_utilities_menu.py` (link presence only) | **Menu Only** |
| Show Database Structure      | `/show_database_structure`      | `test_developer_utilities_menu.py` (link presence only) | **Menu Only** |
| Show Dropdowns               | `/show_dropdown_dict`           | `test_developer_utilities_menu.py` (link presence only) | **Menu Only** |
| Show Feedback Form Structure | `/show_feedback_form_structure` | `test_developer_utilities_menu.py` (link presence only) | **Menu Only** |
| Show Diagnostics             | `/diagnostics`                  | `test_developer_utilities_menu.py` (link presence only) | **Menu Only** |
| Create Incidence (Oil & Gas) | `/og_incidence_create`          | `test_create_incidence_menu.py`                         | **Full**      |
| Create Incidence (Landfill)  | `/landfill_incidence_create`    | `test_create_incidence_menu.py`                         | **Full**      |
| Delete Testing Range (Dev)   | `/delete_testing_range`         | `test_developer_utilities_menu.py` (link presence only) | **Menu Only** |
| JavaScript Diagnostics       | `/java_script_diagnostic_test`  | `test_javascript_logging.py`                            | **Full**      |

### 4. CalSMP & Help

| Dropdown Item                               | Route/Link (may be external) | E2E Test File(s)                                | Status        |
|---------------------------------------------|------------------------------|-------------------------------------------------|---------------|
| Plume Processing Resources                  | (external .docx)             | `test_calsmp_help_menu.py` (link presence only) | **Menu Only** |
| Daily Protocol                              | (external .docx)             | `test_calsmp_help_menu.py` (link presence only) | **Menu Only** |
| Daily Processing Log                        | (external .docx)             | `test_calsmp_help_menu.py` (link presence only) | **Menu Only** |
| Open Items Log                              | (external .xlsx)             | `test_calsmp_help_menu.py` (link presence only) | **Menu Only** |
| Plume Tracker                               | (external site)              | `test_calsmp_help_menu.py` (link presence only) | **Menu Only** |
| Contact Manager                             | (external site)              | `test_calsmp_help_menu.py` (link presence only) | **Menu Only** |
| Feedback Portal Source Code & Documentation | (external site)              | `test_calsmp_help_menu.py` (link presence only) | **Menu Only** |

---

## Legend

- **Full**: Route is covered by E2E tests that verify page load, UI, and main workflows.
- **Menu Only**: E2E tests verify the presence and correctness of the menu link, but do not click through or test the
  destination page.
- **N/A**: Disabled or not applicable.

---

## Summary Table

| Main Menu           | Dropdown Item                | Route/Link                    | E2E Test File(s)                 | Status    |
|---------------------|------------------------------|-------------------------------|----------------------------------|-----------|
| Spreadsheet/Uploads | Upload Feedback Spreadsheet  | /upload                       | test_excel_upload_workflows.py   | Full      |
|                     | Stage Feedback Spreadsheet   | /upload_staged                | test_excel_upload_workflows.py   | Full      |
|                     | View Staged Files            | /list_staged                  | test_excel_upload_workflows.py   | Full      |
|                     | List Uploaded Files          | /list_uploads                 | test_list_uploads.py             | Full      |
| Analysis Tools      | Feedback Updates             | /portal_updates               | test_feedback_updates.py         | Full      |
| Developer Utilities | Show Log File                | /show_log_file                | test_developer_utilities_menu.py | Menu Only |
|                     | Show Database Structure      | /show_database_structure      | test_developer_utilities_menu.py | Menu Only |
|                     | Show Dropdowns               | /show_dropdown_dict           | test_developer_utilities_menu.py | Menu Only |
|                     | Show Feedback Form Structure | /show_feedback_form_structure | test_developer_utilities_menu.py | Menu Only |
|                     | Show Diagnostics             | /diagnostics                  | test_developer_utilities_menu.py | Menu Only |
|                     | Create Incidence (Oil & Gas) | /og_incidence_create          | test_create_incidence_menu.py    | Full      |
|                     | Create Incidence (Landfill)  | /landfill_incidence_create    | test_create_incidence_menu.py    | Full      |
|                     | Delete Testing Range (Dev)   | /delete_testing_range         | test_developer_utilities_menu.py | Menu Only |
|                     | JavaScript Diagnostics       | /java_script_diagnostic_test  | test_javascript_logging.py       | Full      |
| CalSMP & Help       | (all items)                  | (external)                    | test_calsmp_help_menu.py         | Menu Only |

---

If you want to add full E2E coverage for any of the “Menu Only” items, or need a more detailed breakdown, let me know!
