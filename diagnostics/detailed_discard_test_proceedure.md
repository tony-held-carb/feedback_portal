# Detailed E2E Discard Malformed File Test Procedure

## **Test Intent**
- To verify that a malformed staged file (e.g., missing or invalid `id_incidence`) can be correctly identified in the UI, presented with a discard button, and deleted via the custom modal and backend route.
- To ensure the backend receives the correct POST request and the file is removed from both the UI and the staging directory.

## **Expected HTML Structure**
- The malformed file should appear in the "Malformed or Corrupt Staged Files" section of `/list_staged`.
- The row for the malformed file should look like:
  ```html
  <tr>
    <td>malformed_test.json</td>
    <td>...</td>
    <td>...</td>
    <td>Missing required fields: ...</td>
    <td>
      <form method="POST" action="/discard_staged_update/0/malformed_test.json" class="d-inline">
        <button type="submit" class="btn btn-outline-danger btn-sm js-log-btn"
                data-js-logging-context="discard-malformed"
                data-filename="malformed_test.json"
                data-file-id="0">
          🗑️ Discard
        </button>
      </form>
    </td>
  </tr>
  ```
- The discard button must have:
  - `class="js-log-btn"`
  - `data-js-logging-context="discard-malformed"`
  - Be inside a form whose action is `/discard_staged_update/0/malformed_test.json`

## **User/Test Actions (Simulated by Playwright)**
1. **Navigate to `/list_staged`**
   - Wait for the page to fully load.
2. **Locate the malformed file row**
   - Find the row where the filename cell is `malformed_test.json`.
3. **Find the discard button**
   - Selector: `form[action*='malformed_test.json'] button[data-js-logging-context='discard-malformed']`
   - Confirm the button is present and visible.
4. **Click the discard button**
   - This should trigger the custom Bootstrap modal (`#discardConfirmModal`).
5. **Confirm the modal appears**
   - Selector: `#discardConfirmModal`
   - Confirm it is visible.
6. **Click the modal confirm button**
   - Selector: `#discardConfirmModal #discard-confirm-btn` (or `[data-js-logging-context='discard-modal-confirm']`)
   - Confirm it is visible, then click.
7. **Wait for navigation/reload**
   - Use Playwright's `with page.expect_navigation(): confirm_btn.click()` to ensure the POST is sent and the page reloads.
8. **Verify overlay logs**
   - Check that the overlay contains `discard-modal-confirm` before reload.
9. **After reload, verify file is gone**
   - Assert that `malformed_test.json` is no longer present in the page content.

## **Expected Backend Behavior**
- The backend should receive a POST to `/discard_staged_update/0/malformed_test.json`.
- The log should show:
  - `route called: discard_staged_update with id_: 0 and filename: malformed_test.json`
  - `[DISCARD] Discarded staged upload file: .../malformed_test.json`
- The file should be deleted from the staging directory.

## **Test Success Criteria**
- The discard button for the malformed file is found and clicked.
- The modal appears and is confirmed.
- The backend receives the correct POST and deletes the file.
- The overlay logs the confirm action.
- After reload, the file is no longer present in the UI or on disk.

## **Failure Modes and Debugging**
- **Button not found:** The file is not classified as malformed, or the selector is wrong.
- **Modal does not appear:** JS or selector issue.
- **POST not sent:** Form not submitted, or modal confirm handler broken.
- **File not deleted:** Backend route not called, or deletion failed.
- **File still present after reload:** Test did not wait for navigation, or backend did not delete.

## **Why Each Step Matters**
- Each selector and action is chosen to uniquely identify the malformed file and its discard button.
- Waiting for navigation ensures the backend has time to process the deletion.
- Checking overlay logs and backend logs provides full traceability.
- The test is only a success if all steps pass—no ambiguity.

---
This procedure is a reference for both developers and testers to ensure the E2E test for discarding malformed files is robust, unambiguous, and fully traceable. 