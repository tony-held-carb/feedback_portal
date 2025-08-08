# Stage Testing Analysis

This document summarizes the results of the E2E Playwright-based discard and malformed file tests, grouped by outcome.
Each test is listed with its name, intent, and result.

| Outcome       | Count |
|---------------|-------|
| ❌ Failed      | 15    |
| ✅ Passed      | 12    |
| ⏭️ Skipped    | 13    |
| 💤 Deselected | 65    |

---

## ❌ Failed Tests (15)

1. *
   *TestExcelUploadStaged.test_discard_staged_by_filename[chromium-feedback_forms\\testing_versions\\standard\\dairy_digester_operator_feedback_v006_test_01_good_data.xlsx]
   **
    - *Intent:* Upload and discard a file, verify removal from UI and staging dir.
    - *Result:* File remains after discard.
2. **TestExcelUploadStaged.test_malformed_staged_file_handling[chromium]**
    - *Intent:* Create, detect, and discard a malformed file.
    - *Result:* Malformed file remains after discard.
3. *
   *TestExcelUploadStaged.test_discard_staged_by_filename[chromium-feedback_forms\\testing_versions\\standard\\dairy_digester_operator_feedback_v006_test_02_bad_data.xlsx]
   **
    - *Intent:* Upload and discard a file, verify removal from UI and staging dir.
    - *Result:* File remains after discard.
4. *
   *TestExcelUploadStaged.test_discard_staged_by_filename[chromium-feedback_forms\\testing_versions\\standard\\dairy_digester_operator_feedback_v006_test_03_blank.xlsx]
   **
    - *Intent:* Upload and discard a blank file.
    - *Result:* Could not extract staged filename; test cannot proceed.
5. *
   *test_discard_staged_by_filename_with_overlay_logging[chromium-feedback_forms\\testing_versions\\standard\\dairy_digester_operator_feedback_v006_test_03_blank.xlsx]
   **
    - *Intent:* Upload and discard a blank file with overlay logging.
    - *Result:* Could not extract staged filename; test cannot proceed.
6. *
   *TestExcelUploadStaged.test_discard_staged_by_filename[chromium-feedback_forms\\testing_versions\\standard\\energy_operator_feedback_v003_test_01_good_data.xlsx]
   **
    - *Intent:* Upload and discard a file, verify removal from UI and staging dir.
    - *Result:* File remains after discard.
7. *
   *TestExcelUploadStaged.test_discard_staged_by_filename[chromium-feedback_forms\\testing_versions\\standard\\energy_operator_feedback_v003_test_02_bad_data.xlsx]
   **
    - *Intent:* Upload and discard a file, verify removal from UI and staging dir.
    - *Result:* File remains after discard.
8. *
   *TestExcelUploadStaged.test_discard_staged_by_filename[chromium-feedback_forms\\testing_versions\\standard\\generic_operator_feedback_v002_test_01_good_data.xlsx]
   **
    - *Intent:* Upload and discard a file, verify removal from UI and staging dir.
    - *Result:* File remains after discard.
9. *
   *TestExcelUploadStaged.test_discard_staged_by_filename[chromium-feedback_forms\\testing_versions\\standard\\generic_operator_feedback_v002_test_02_bad_data.xlsx]
   **
    - *Intent:* Upload and discard a file, verify removal from UI and staging dir.
    - *Result:* File remains after discard.
10. *
    *TestExcelUploadStaged.test_discard_staged_by_filename[chromium-feedback_forms\\testing_versions\\standard\\landfill_operator_feedback_v070_test_01_good_data.xlsx]
    **
    - *Intent:* Upload and discard a file, verify removal from UI and staging dir.
    - *Result:* File remains after discard.
11. *
    *TestExcelUploadStaged.test_discard_staged_by_filename[chromium-feedback_forms\\testing_versions\\standard\\landfill_operator_feedback_v070_test_02_bad_data.xlsx]
    **
    - *Intent:* Upload and discard a file, verify removal from UI and staging dir.
    - *Result:* File remains after discard.
12. *
    *TestExcelUploadStaged.test_discard_staged_by_filename[chromium-feedback_forms\\testing_versions\\standard\\landfill_operator_feedback_v071_test_01_good_data.xlsx]
    **
    - *Intent:* Upload and discard a file, verify removal from UI and staging dir.
    - *Result:* File remains after discard.
13. *
    *TestExcelUploadStaged.test_discard_staged_by_filename[chromium-feedback_forms\\testing_versions\\standard\\landfill_operator_feedback_v071_test_02_bad_data.xlsx]
    **
    - *Intent:* Upload and discard a file, verify removal from UI and staging dir.
    - *Result:* File remains after discard.
14. *
    *TestExcelUploadStaged.test_discard_staged_by_filename[chromium-feedback_forms\\testing_versions\\standard\\oil_and_gas_operator_feedback_v070_test_01_good_data.xlsx]
    **
    - *Intent:* Upload and discard a file, verify removal from UI and staging dir.
    - *Result:* File remains after discard.
15. *
    *TestExcelUploadStaged.test_discard_staged_by_filename[chromium-feedback_forms\\testing_versions\\standard\\oil_and_gas_operator_feedback_v070_test_02_bad_data.xlsx]
    **
    - *Intent:* Upload and discard a file, verify removal from UI and staging dir.
    - *Result:* File remains after discard.

---

## ✅ Passed Tests (12)

1. *
   *test_discard_staged_by_filename_with_overlay_logging[chromium-feedback_forms\\testing_versions\\standard\\dairy_digester_operator_feedback_v006_test_01_good_data.xlsx]
   **
    - *Intent:* Upload and discard a file with overlay logging.
    - *Result:* File successfully discarded.
2. *
   *test_discard_staged_by_filename_with_overlay_logging[chromium-feedback_forms\\testing_versions\\standard\\dairy_digester_operator_feedback_v006_test_02_bad_data.xlsx]
   **
    - *Intent:* Upload and discard a file with overlay logging.
    - *Result:* File successfully discarded.
3. *
   *test_discard_staged_by_filename_with_overlay_logging[chromium-feedback_forms\\testing_versions\\standard\\energy_operator_feedback_v003_test_01_good_data.xlsx]
   **
    - *Intent:* Upload and discard a file with overlay logging.
    - *Result:* File successfully discarded.
4. *
   *test_discard_staged_by_filename_with_overlay_logging[chromium-feedback_forms\\testing_versions\\standard\\energy_operator_feedback_v003_test_02_bad_data.xlsx]
   **
    - *Intent:* Upload and discard a file with overlay logging.
    - *Result:* File successfully discarded.
5. *
   *test_discard_staged_by_filename_with_overlay_logging[chromium-feedback_forms\\testing_versions\\standard\\generic_operator_feedback_v002_test_01_good_data.xlsx]
   **
    - *Intent:* Upload and discard a file with overlay logging.
    - *Result:* File successfully discarded.
6. *
   *test_discard_staged_by_filename_with_overlay_logging[chromium-feedback_forms\\testing_versions\\standard\\generic_operator_feedback_v002_test_02_bad_data.xlsx]
   **
    - *Intent:* Upload and discard a file with overlay logging.
    - *Result:* File successfully discarded.
7. *
   *test_discard_staged_by_filename_with_overlay_logging[chromium-feedback_forms\\testing_versions\\standard\\landfill_operator_feedback_v070_test_01_good_data.xlsx]
   **
    - *Intent:* Upload and discard a file with overlay logging.
    - *Result:* File successfully discarded.
8. *
   *test_discard_staged_by_filename_with_overlay_logging[chromium-feedback_forms\\testing_versions\\standard\\landfill_operator_feedback_v070_test_02_bad_data.xlsx]
   **
    - *Intent:* Upload and discard a file with overlay logging.
    - *Result:* File successfully discarded.
9. *
   *test_discard_staged_by_filename_with_overlay_logging[chromium-feedback_forms\\testing_versions\\standard\\landfill_operator_feedback_v071_test_01_good_data.xlsx]
   **
    - *Intent:* Upload and discard a file with overlay logging.
    - *Result:* File successfully discarded.
10. *
    *test_discard_staged_by_filename_with_overlay_logging[chromium-feedback_forms\\testing_versions\\standard\\landfill_operator_feedback_v071_test_02_bad_data.xlsx]
    **
    - *Intent:* Upload and discard a file with overlay logging.
    - *Result:* File successfully discarded.
11. *
    *test_discard_staged_by_filename_with_overlay_logging[chromium-feedback_forms\\testing_versions\\standard\\oil_and_gas_operator_feedback_v070_test_01_good_data.xlsx]
    **
    - *Intent:* Upload and discard a file with overlay logging.
    - *Result:* File successfully discarded.
12. *
    *test_discard_staged_by_filename_with_overlay_logging[chromium-feedback_forms\\testing_versions\\standard\\oil_and_gas_operator_feedback_v070_test_02_bad_data.xlsx]
    **
    - *Intent:* Upload and discard a file with overlay logging.
    - *Result:* File successfully discarded.

---

## ⏭️ Skipped Tests (13)

1. *
   *TestExcelUploadStaged.test_excel_upload_staged_discard[chromium-feedback_forms\\testing_versions\\standard\\dairy_digester_operator_feedback_v006_test_01_good_data.xlsx]
   **
2. *
   *TestExcelUploadStaged.test_excel_upload_staged_discard[chromium-feedback_forms\\testing_versions\\standard\\dairy_digester_operator_feedback_v006_test_02_bad_data.xlsx]
   **
3. *
   *TestExcelUploadStaged.test_excel_upload_staged_discard[chromium-feedback_forms\\testing_versions\\standard\\dairy_digester_operator_feedback_v006_test_03_blank.xlsx]
   **
4. *
   *TestExcelUploadStaged.test_excel_upload_staged_discard[chromium-feedback_forms\\testing_versions\\standard\\energy_operator_feedback_v003_test_01_good_data.xlsx]
   **
5. *
   *TestExcelUploadStaged.test_excel_upload_staged_discard[chromium-feedback_forms\\testing_versions\\standard\\energy_operator_feedback_v003_test_02_bad_data.xlsx]
   **
6. *
   *TestExcelUploadStaged.test_excel_upload_staged_discard[chromium-feedback_forms\\testing_versions\\standard\\generic_operator_feedback_v002_test_01_good_data.xlsx]
   **
7. *
   *TestExcelUploadStaged.test_excel_upload_staged_discard[chromium-feedback_forms\\testing_versions\\standard\\generic_operator_feedback_v002_test_02_bad_data.xlsx]
   **
8. *
   *TestExcelUploadStaged.test_excel_upload_staged_discard[chromium-feedback_forms\\testing_versions\\standard\\landfill_operator_feedback_v070_test_01_good_data.xlsx]
   **
9. *
   *TestExcelUploadStaged.test_excel_upload_staged_discard[chromium-feedback_forms\\testing_versions\\standard\\landfill_operator_feedback_v070_test_02_bad_data.xlsx]
   **
10. *
    *TestExcelUploadStaged.test_excel_upload_staged_discard[chromium-feedback_forms\\testing_versions\\standard\\landfill_operator_feedback_v071_test_01_good_data.xlsx]
    **
11. *
    *TestExcelUploadStaged.test_excel_upload_staged_discard[chromium-feedback_forms\\testing_versions\\standard\\landfill_operator_feedback_v071_test_02_bad_data.xlsx]
    **
12. *
    *TestExcelUploadStaged.test_excel_upload_staged_discard[chromium-feedback_forms\\testing_versions\\standard\\oil_and_gas_operator_feedback_v070_test_01_good_data.xlsx]
    **
13. *
    *TestExcelUploadStaged.test_excel_upload_staged_discard[chromium-feedback_forms\\testing_versions\\standard\\oil_and_gas_operator_feedback_v070_test_02_bad_data.xlsx]
    **
- *Intent:* Upload and discard a file using a different workflow or fixture.
- *Result:* Test was skipped, likely due to a marker, fixture, or test configuration. No result available.

---

## 💤 Deselected Tests (65)

- Not listed here; these tests were not relevant to the "discard or malformed" keyword filter.
