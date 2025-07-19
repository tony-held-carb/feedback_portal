# E2E Testing Summary

## Directory Structure

```
feedback_forms/testing_versions/
├── standard/      # Main "good" and "bad" test files for each sector and scenario
├── edge_cases/    # Files designed to trigger edge-case or error handling
├── generated/     # Programmatically generated files for schema/logic/validation testing
├── old/           # Legacy or previous-version test files
```

---

## Test File Purposes

### **standard/**
- **Purpose:** Contains canonical "good" and "bad" data files for each sector (dairy, landfill, oil & gas, energy, generic).
- **Tested for:** Successful upload, backend validation, staged upload, and review workflows.

### **edge_cases/**
- **Purpose:** Contains files that are intentionally malformed, incomplete, or otherwise designed to trigger error handling.
- **Tested for:** Proper rejection, error messages, and no database update.

### **generated/**
- **Purpose:** Contains files generated to test schema logic, conditional fields, missing/extra fields, invalid types, and large file handling.
- **Tested for:** Both positive and negative validation, but many fail backend or staged validation.

### **old/**
- **Purpose:** Legacy test files from previous versions, retained for regression and compatibility testing.

---

## E2E Test Types

- **test_file_upload_workflow:** Uploads each file and checks for success or error.
- **test_excel_upload_deep_backend_validation:** Uploads each file and checks that all fields are imported as expected, or that warnings/errors are logged for mismatches.
- **test_excel_upload_staged_workflow:** Uploads each file via the staged workflow, reviews, confirms, and checks DB.
- **test_excel_upload_staged_discard:** (Skipped) Would test discarding staged uploads.

---

## Test Results by Directory

### **standard/**

| File Name                                         | Upload | Backend Validation | Staged Upload | Notes                |
|---------------------------------------------------|--------|--------------------|---------------|----------------------|
| dairy_digester_operator_feedback_v006_test_01_good_data.xlsx | ✅     | ✅                 | ✅            |                      |
| dairy_digester_operator_feedback_v006_test_02_bad_data.xlsx  | ✅     | ✅                 | ✅            |                      |
| dairy_digester_operator_feedback_v006_test_03_blank.xlsx     | ✅     | ✅                 | ❌            | Staged upload fails  |
| energy_operator_feedback_v003_test_01_good_data.xlsx         | ✅     | ✅                 | ✅            |                      |
| energy_operator_feedback_v003_test_02_bad_data.xlsx          | ✅     | ✅                 | ✅            |                      |
| generic_operator_feedback_v002_test_01_good_data.xlsx        | ✅     | ✅                 | ✅            |                      |
| generic_operator_feedback_v002_test_02_bad_data.xlsx         | ✅     | ✅                 | ✅            |                      |
| landfill_operator_feedback_v070_test_01_good_data.xlsx       | ✅     | ✅                 | ✅            |                      |
| landfill_operator_feedback_v070_test_02_bad_data.xlsx        | ✅     | ✅                 | ✅            |                      |
| landfill_operator_feedback_v071_test_01_good_data.xlsx       | ✅     | ✅                 | ✅            |                      |
| landfill_operator_feedback_v071_test_02_bad_data.xlsx        | ✅     | ✅                 | ✅            |                      |
| oil_and_gas_operator_feedback_v070_test_01_good_data.xlsx    | ✅     | ✅                 | ✅            |                      |
| oil_and_gas_operator_feedback_v070_test_02_bad_data.xlsx     | ✅     | ✅                 | ✅            |                      |

### **edge_cases/**

_All edge case files are expected to be rejected and show error messages. All tests pass for these files (i.e., the app correctly rejects them)._

| File Name           | Upload | Backend Validation | Staged Upload | Notes                |
|---------------------|--------|--------------------|---------------|----------------------|
| corrupted_file.xlsx | ✅     | ✅                 | ✅            | Rejected as invalid  |
| data_only.xlsx      | ✅     | ✅                 | ✅            | Rejected as invalid  |
| duplicate_fields.xlsx| ✅    | ✅                 | ✅            | Rejected as invalid  |
| extra_columns.xlsx  | ✅     | ✅                 | ✅            | Rejected as invalid  |
| headers_only.xlsx   | ✅     | ✅                 | ✅            | Rejected as invalid  |
| large_file.xlsx     | ✅     | ✅                 | ✅            | Rejected as invalid  |
| missing_columns.xlsx| ✅     | ✅                 | ✅            | Rejected as invalid  |
| mixed_types.xlsx    | ✅     | ✅                 | ✅            | Rejected as invalid  |
| unicode_fields.xlsx | ✅     | ✅                 | ✅            | Rejected as invalid  |

### **generated/**

_Most files in this directory **pass the upload workflow** but **fail backend or staged validation** (❌). These are good candidates to move to `edge_cases` if they are meant to test negative/edge scenarios._

| File Name                        | Upload | Backend Validation | Staged Upload | Notes                |
|-----------------------------------|--------|--------------------|---------------|----------------------|
| dairy_conditional_logic.xlsx      | ✅     | ❌                 | ❌            |                      |
| dairy_extra_fields.xlsx           | ✅     | ❌                 | ❌            |                      |
| dairy_invalid_types.xlsx          | ✅     | ❌                 | ❌            |                      |
| dairy_large.xlsx                  | ✅     | ❌                 | ❌            |                      |
| dairy_missing_required.xlsx       | ✅     | ❌                 | ❌            |                      |
| dairy_valid.xlsx                  | ✅     | ❌                 | ❌            |                      |
| energy_conditional_logic.xlsx     | ✅     | ❌                 | ❌            |                      |
| energy_extra_fields.xlsx          | ✅     | ❌                 | ❌            |                      |
| energy_invalid_types.xlsx         | ✅     | ❌                 | ❌            |                      |
| energy_large.xlsx                 | ✅     | ❌                 | ❌            |                      |
| energy_missing_required.xlsx      | ✅     | ❌                 | ❌            |                      |
| energy_valid.xlsx                 | ✅     | ❌                 | ❌            |                      |
| generic_conditional_logic.xlsx    | ✅     | ❌                 | ❌            |                      |
| generic_extra_fields.xlsx         | ✅     | ❌                 | ❌            |                      |
| generic_invalid_types.xlsx        | ✅     | ❌                 | ❌            |                      |
| generic_large.xlsx                | ✅     | ❌                 | ❌            |                      |
| generic_missing_required.xlsx     | ✅     | ❌                 | ❌            |                      |
| generic_valid.xlsx                | ✅     | ❌                 | ❌            |                      |
| landfill_conditional_logic.xlsx   | ✅     | ❌                 | ❌            |                      |
| landfill_extra_fields.xlsx        | ✅     | ❌                 | ❌            |                      |
| landfill_invalid_types.xlsx       | ✅     | ❌                 | ❌            |                      |
| landfill_large.xlsx               | ✅     | ❌                 | ❌            |                      |
| landfill_missing_required.xlsx    | ✅     | ❌                 | ❌            |                      |
| landfill_valid.xlsx               | ✅     | ❌                 | ❌            |                      |
| oil_and_gas_conditional_logic.xlsx| ✅     | ❌                 | ❌            |                      |
| oil_and_gas_extra_fields.xlsx     | ✅     | ❌                 | ❌            |                      |
| oil_and_gas_invalid_types.xlsx    | ✅     | ❌                 | ❌            |                      |
| oil_and_gas_large.xlsx            | ✅     | ❌                 | ❌            |                      |
| oil_and_gas_missing_required.xlsx | ✅     | ❌                 | ❌            |                      |
| oil_and_gas_valid.xlsx            | ✅     | ❌                 | ❌            |                      |

---

## How to Use This Summary

- **Files in `generated/` that consistently fail backend or staged validation** are strong candidates to move to `edge_cases/`.
- **Files in `standard/` should always pass all tests** (except for known edge cases like blank files).
- **Use this table to decide which files to reclassify or further investigate.**

---

Let me know if you want to add more details or explanations for any specific test or file! 