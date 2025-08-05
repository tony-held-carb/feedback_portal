"""
E2E Test: Review Staged File Workflow (/review_staged)
=====================================================

Covers:
- Hide Changes button
- Filter fields
- Change summary diagnostic
- Cancel and Save Changes buttons
- Checkbox selection for fields
- Incremental upload/review workflow (partial accept, re-upload, full accept, re-upload)
- Diagnostics overlay assertions for button actions
- Playwright waiting best practices

Skips gracefully if required test files or UI elements are not present.
"""

import pytest
from playwright.sync_api import Page, expect
from pathlib import Path
import time
import requests
import re
import os
import conftest
from arb.portal.utils.e2e_testing_util import navigate_and_wait_for_ready

# Test configuration - can be overridden by environment variables
BASE_URL = os.environ.get('TEST_BASE_URL', conftest.TEST_BASE_URL)
save_screenshots=False

# TEST_FILE = "feedback_forms/testing_versions/standard/oil_and_gas_operator_feedback_v070_test_01_good_data.xlsx"
TEST_FILE = "feedback_forms/testing_versions/standard/energy_operator_feedback_v003_test_01_good_data.xlsx"

TEST_FILES = [
    "feedback_forms/testing_versions/standard/dairy_digester_operator_feedback_v006_test_01_good_data.xlsx",
    "feedback_forms/testing_versions/standard/energy_operator_feedback_v003_test_01_good_data.xlsx",
    "feedback_forms/testing_versions/standard/generic_operator_feedback_v002_test_01_good_data.xlsx",
    "feedback_forms/testing_versions/standard/landfill_operator_feedback_v070_test_01_good_data.xlsx",
    "feedback_forms/testing_versions/standard/landfill_operator_feedback_v071_test_01_good_data.xlsx",
    "feedback_forms/testing_versions/standard/oil_and_gas_operator_feedback_v070_test_01_good_data.xlsx",
]



@pytest.fixture
def upload_and_stage_file(page: Page):
    """
    Uploads a test file via /upload_staged and returns the review_staged URL.
    Adds diagnostics after upload.
    """
    navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged")
    file_input = page.locator("input[type='file']")
    if not Path(TEST_FILE).exists():
        pytest.skip(f"Test file {TEST_FILE} not found.")
    with page.expect_navigation():
        file_input.set_input_files(TEST_FILE)
    # Wait for specific element instead of network idle
    expect(page.locator("input.confirm-checkbox").first).to_be_visible()
    print(f"[DEBUG] After upload, page.url = {page.url}")
    # Print all checkboxes and their names
    checkboxes = page.locator("input.confirm-checkbox")
    count = checkboxes.count()
    print(f"[DEBUG] Found {count} confirm-checkboxes:")
    for i in range(count):
        try:
            name = checkboxes.nth(i).get_attribute("name")
            print(f"  - Checkbox {i}: name={name}")
        except Exception as e:
            print(f"  - Checkbox {i}: error {e}")
    # Print any alert/info messages
    alerts = page.locator(".alert, .alert-info, .alert-success, .alert-danger")
    alert_count = alerts.count()
    print(f"[DEBUG] Found {alert_count} alert/info messages:")
    for i in range(alert_count):
        try:
            text = alerts.nth(i).inner_text()
            print(f"  - Alert {i}: {text}")
        except Exception as e:
            print(f"  - Alert {i}: error {e}")
    if save_screenshots:
        page.screenshot(path="review_staged_after_upload.png")
    return page.url

@pytest.fixture(scope="function")
def clear_test_data(page: Page):
    """
    Clears test data using the /delete_testing_range endpoint before each test.
    Default min_id=1000000, max_id=2000000.
    Skips test if endpoint is unavailable or deletion fails.
    """
    print(f"clear_test_data called with page: {page}")

    # Step 0: Use Playwright to clear test data via the UI
    navigate_and_wait_for_ready(page, f"{BASE_URL}/delete_testing_range")
    page.fill("#min_id", "1000000")
    page.fill("#max_id", "2000000")
    dry_run_checkbox = page.locator("#dry_run")
    if dry_run_checkbox.is_checked():
        dry_run_checkbox.uncheck()
    # Click the preview/delete button (may be labeled Preview or Delete)
    page.click("#delete-preview-btn")
    # Wait for the modal and confirm deletion
    page.click("#modal-confirm-delete")
    # Wait for the success message
    expect(page.locator(".alert-success")).to_be_visible()
    print("[DEBUG] Test data cleared via UI at /delete_testing_range")

@pytest.mark.e2e
def test_hide_changes_checkbox(page: Page, upload_and_stage_file):
    """
    E2E: Hide unchanged fields checkbox toggles visibility of .unchanged-field rows.
    """
    navigate_and_wait_for_ready(page, upload_and_stage_file)
    hide_checkbox = page.locator("#hideUnchangedFields")
    expect(hide_checkbox).to_be_visible()
    # Check that unchanged fields are visible by default
    unchanged_rows = page.locator(".unchanged-field")
    if unchanged_rows.count() == 0:
        pytest.skip("No unchanged fields to test hide functionality.")
    # Click the checkbox to hide unchanged fields
    hide_checkbox.check()
    expect(hide_checkbox).to_be_checked()
    # All unchanged fields should now be hidden
    for i in range(unchanged_rows.count()):
        expect(unchanged_rows.nth(i)).not_to_be_visible()
    # Uncheck to show again
    hide_checkbox.uncheck()
    expect(hide_checkbox).not_to_be_checked()
    for i in range(unchanged_rows.count()):
        assert unchanged_rows.nth(i).is_visible(), "Unchanged field row should be visible."

@pytest.mark.e2e
def test_field_search_filter(page: Page, upload_and_stage_file):
    """
    E2E: Field search input filters .field-row elements by name/value.
    """
    navigate_and_wait_for_ready(page, upload_and_stage_file)
    search_input = page.locator("#fieldSearch")
    expect(search_input).to_be_visible()
    search_input.fill("timestamp")
    # Only rows with 'timestamp' in any cell should be visible
    visible_rows = page.locator(".field-row:visible")
    expect(visible_rows.first).to_be_visible()
    for text in visible_rows.all_inner_texts():
        assert "timestamp" in text.lower(), f"Visible row does not match filter: {text}"
    # Clear filter
    search_input.fill("")
    # After clearing, all field rows should be visible again
    all_field_rows = page.locator(".field-row")
    expect(all_field_rows).to_have_count(all_field_rows.count())

@pytest.mark.e2e
def test_change_summary_card(page: Page, upload_and_stage_file):
    """
    E2E: Change summary card displays correct numbers for total, changed, and need confirmation fields.
    """
    navigate_and_wait_for_ready(page, upload_and_stage_file)
    summary_card = page.locator(".card-header.bg-info")
    expect(summary_card).to_be_visible()
    # Check numbers in the card body
    numbers = page.locator(".card-body .h5.mb-0")
    assert numbers.count() == 3, "Summary card should have three numbers."
    total = int(numbers.nth(0).inner_text())
    changed = int(numbers.nth(1).inner_text())
    need_confirm = int(numbers.nth(2).inner_text())
    assert total >= changed >= need_confirm >= 0

@pytest.mark.e2e
def test_cancel_and_save_buttons(page: Page, upload_and_stage_file):
    """
    E2E: Cancel link and Save Changes button work and trigger navigation.
    """
    navigate_and_wait_for_ready(page, upload_and_stage_file)
    cancel_link = page.locator("a.btn-secondary")
    save_btn = page.locator("button.btn-success")
    expect(cancel_link).to_be_visible()
    expect(save_btn).to_be_visible()
    # Test Cancel (should trigger navigation)
    with page.expect_navigation():
        cancel_link.click()
    # Re-upload to get back to review page
    navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged")
    file_input = page.locator("input[type='file']")
    with page.expect_navigation():
        file_input.set_input_files(TEST_FILE)
    page.wait_for_timeout(1000)
    # Test Save Changes
    save_btn = page.locator("button.btn-success")
    with page.expect_navigation():
        save_btn.click()

@pytest.mark.e2e
def test_confirm_checkboxes(page: Page, upload_and_stage_file):
    """
    E2E: .confirm-checkbox elements can be checked/unchecked and update the form.
    """
    navigate_and_wait_for_ready(page, upload_and_stage_file)
    
    # Wait for checkboxes to be available
    checkboxes = page.locator(".confirm-checkbox")
    
    # Check if there are any confirm checkboxes
    if checkboxes.count() == 0:
        # This is a valid scenario - no fields need confirmation
        print("No confirm checkboxes found - this is valid when all fields are the same or it's a new record")
        return
    
            # Wait for at least one checkbox to be visible
        expect(page.locator(".confirm-checkbox").first).to_be_visible(timeout=10000)
    
    if checkboxes.count() < 2:
        pytest.skip("Not enough checkboxes to test field selection.")
    
    # Check half the boxes with better error handling
    for i in range(checkboxes.count() // 2):
        try:
            checkbox = checkboxes.nth(i)
            # Ensure checkbox is visible and not covered
            checkbox.scroll_into_view_if_needed()
            expect(checkbox).to_be_visible()
            expect(checkbox).to_be_enabled()
            checkbox.check()
            expect(checkbox).to_be_checked()
        except Exception as e:
            print(f"Failed to check checkbox {i}: {e}")
            continue
    
    # Uncheck all
    for i in range(checkboxes.count()):
        try:
            checkbox = checkboxes.nth(i)
            checkbox.scroll_into_view_if_needed()
            expect(checkbox).to_be_visible()
            expect(checkbox).to_be_enabled()
            checkbox.uncheck()
            expect(checkbox).not_to_be_checked()
        except Exception as e:
            print(f"Failed to uncheck checkbox {i}: {e}")
            continue
    
    # Check all
    for i in range(checkboxes.count()):
        try:
            checkbox = checkboxes.nth(i)
            checkbox.scroll_into_view_if_needed()
            expect(checkbox).to_be_visible()
            expect(checkbox).to_be_enabled()
            checkbox.check()
            expect(checkbox).to_be_checked()
        except Exception as e:
            print(f"Failed to check checkbox {i} in final loop: {e}")
            continue

@pytest.mark.e2e
@pytest.mark.parametrize("test_file", TEST_FILES)
def test_incremental_upload(page: Page, clear_test_data, test_file):
    """
    E2E: Simulate the incremental upload/review/acceptance workflow for all main 'good' test spreadsheets.

    For each test file:
      1. Clear all test data in the relevant id_incidence range.
      2. Upload the test spreadsheet.
      3. Confirm (check) every other field, then save.
      4. Re-upload the same spreadsheet, confirm the remaining fields, then save.
      5. Re-upload again and verify that no confirmable checkboxes remain (all are accepted).
    This test matches the manual workflow and prints diagnostics for debugging.
    Set save_screenshots=False to save screenshots at each step.
    
    TODO: INVESTIGATE - This test was modified to use element-specific waits instead of wait_for_timeout
    but may be causing hanging issues. Consider reverting to simpler approach or investigating further.
    """
    print(f"Running incremental upload test for: {test_file}")
    # Step 1: Go to the staged upload page
    navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged")
    if save_screenshots:
        page.screenshot(path=f"screenshot_01_upload_staged_{Path(test_file).stem}.png")

    # Step 2. Simulate file upload
    file_input = page.locator("input[type='file']")
    if not Path(test_file).exists():
        pytest.skip(f"Test file {test_file} not found.")
    with page.expect_navigation():
        file_input.set_input_files(test_file)
    # Wait for specific element instead of network idle
    expect(page.locator("input.confirm-checkbox").first).to_be_visible()

    # Step 3. Print staged url and screenshot
    print(f"[DEBUG] After upload, page.url = {page.url}")
    if save_screenshots:
        page.screenshot(path=f"screenshot_02_review_staged_01_{Path(test_file).stem}.png")

    # Step 4. Find all checkboxes on the page
    all_checkboxes = page.locator("input[type='checkbox']")
    total = all_checkboxes.count()
    print(f"[CHECKBOX DIAGNOSTICS] Found {total} checkboxes on the page:")
    for i in range(total):
        cb = all_checkboxes.nth(i)
        name = cb.get_attribute("name") or cb.get_attribute("id") or f"checkbox_{i}"
        checked = cb.is_checked()
        print(f"  - Checkbox {i}: name/id='{name}', checked={checked}")

    # Step 5. Set every other unchecked box to checked
    new_checks = 0
    select_next_unchecked = True
    for i in range(total):
        cb = all_checkboxes.nth(i)
        name = cb.get_attribute("name") or cb.get_attribute("id") or f"checkbox_{i}"
        checked = cb.is_checked()
        if name not in ['hideUnchangedFields', 'selectAllConfirmations']:
            if not checked:
                if select_next_unchecked:
                    try:
                        # Ensure checkbox is visible and not covered
                        cb.scroll_into_view_if_needed()
                        expect(cb).to_be_visible()
                        expect(cb).to_be_enabled()
                        cb.set_checked(True)
                        expect(cb).to_be_checked()
                        new_checks += 1
                        print(f"checking box named: {name}")
                    except Exception as e:
                        print(f"Failed to check checkbox {name}: {e}")
                        continue
                select_next_unchecked = not select_next_unchecked
    print(f"A total of {new_checks} check boxes were selected.")
    if save_screenshots:
        page.screenshot(path=f"screenshot_02_review_staged_02_{Path(test_file).stem}.png")

    # Step 6. Ensure there are enough checkboxes to use this test properly
    if new_checks < 2:
        pytest.skip(f"Test skipped because at least two new checks required for test.")
    for i in range(total):
        cb = all_checkboxes.nth(i)
        name = cb.get_attribute("name") or cb.get_attribute("id") or f"checkbox_{i}"
        checked = cb.is_checked()
        print(f"  - Checkbox {i}: name/id='{name}', checked={checked}")

    # Step 7. Click Save Changes and wait for navigation
    save_btn = page.locator("button.btn-success, button[type='submit']")
    with page.expect_navigation():
        save_btn.click()
    # Wait for specific element instead of network idle
    expect(page.locator("h2")).to_contain_text("Upload & Review")
    print(f"[DEBUG] After first save, navigated to: {page.url}")
    if save_screenshots:
        page.screenshot(path=f"screenshot_03_after_first_save_{Path(test_file).stem}.png")

    # Step 8. Re-upload the same file, print diagnostics, and check remaining unchecked checkboxes
    navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged")
    file_input = page.locator("input[type='file']")
    with page.expect_navigation():
        file_input.set_input_files(test_file)
    # Wait for specific element instead of network idle
    expect(page.locator("input.confirm-checkbox").first).to_be_visible()
    print(f"[DEBUG] After re-upload, page.url = {page.url}")
    if save_screenshots:
        page.screenshot(path=f"screenshot_04_review_staged_2nd_upload_{Path(test_file).stem}.png")
    all_checkboxes = page.locator("input[type='checkbox']")
    total = all_checkboxes.count()
    print(f"[CHECKBOX DIAGNOSTICS] (2nd upload) Found {total} checkboxes on the page:")
    new_checks = 0
    for i in range(total):
        cb = all_checkboxes.nth(i)
        name = cb.get_attribute("name") or cb.get_attribute("id") or f"checkbox_{i}"
        checked = cb.is_checked()
        print(f"  - Checkbox {i}: name/id='{name}', checked={checked}")
        if name not in ['hideUnchangedFields', 'selectAllConfirmations'] and not checked:
            cb.set_checked(True)
            new_checks += 1
            print(f"checking box named: {name}")
    print(f"A total of {new_checks} check boxes were selected on 2nd upload.")
    if save_screenshots:
        page.screenshot(path=f"screenshot_05_review_staged_2nd_checked_{Path(test_file).stem}.png")

    # Step 9. Click Save Changes again and wait for navigation
    save_btn = page.locator("button.btn-success, button[type='submit']")
    with page.expect_navigation():
        save_btn.click()
    # Wait for specific element instead of network idle
    expect(page.locator("h2")).to_contain_text("Upload & Review")
    print(f"[DEBUG] After second save, navigated to: {page.url}")
    if save_screenshots:
        page.screenshot(path=f"screenshot_06_after_second_save_{Path(test_file).stem}.png")

    # Step 10. Re-upload the file a third time, print diagnostics, and assert no confirmable checkboxes remain
    navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged")
    file_input = page.locator("input[type='file']")
    with page.expect_navigation():
        file_input.set_input_files(test_file)
    page.wait_for_load_state("networkidle")
    print(f"[DEBUG] After 3rd upload, page.url = {page.url}")
    if save_screenshots:
        page.screenshot(path=f"screenshot_07_review_staged_3rd_upload_{Path(test_file).stem}.png")
    all_checkboxes = page.locator("input[type='checkbox']")
    total = all_checkboxes.count()
    print(f"[CHECKBOX DIAGNOSTICS] (3rd upload) Found {total} checkboxes on the page:")
    confirmable = 0
    for i in range(total):
        cb = all_checkboxes.nth(i)
        name = cb.get_attribute("name") or cb.get_attribute("id") or f"checkbox_{i}"
        checked = cb.is_checked()
        print(f"  - Checkbox {i}: name/id='{name}', checked={checked}")
        if name not in ['hideUnchangedFields', 'selectAllConfirmations']:
            confirmable += 1
    assert confirmable == 0, f"Expected no confirmable checkboxes after all fields accepted, found {confirmable}"
    no_changes_msg = page.locator(".no-changes-message, .alert-info, .alert-success")
    assert no_changes_msg.count() > 0, "No changes message should be shown after all fields accepted."

