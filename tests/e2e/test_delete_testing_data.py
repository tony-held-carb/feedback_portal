"""
E2E Test: Delete Testing Range (/delete_testing_range)
=====================================================

Covers:
- Page load and form presence
- Min/Max ID input boxes
- Dry Run checkbox
- Preview (dry run) and Delete (real run) button logic
- Diagnostics messaging (success/error alerts)
- Playwright waiting best practices

Skips gracefully if UI elements are missing.
"""

import pytest
from playwright.sync_api import Page, expect
import os
import conftest
from e2e_helpers import navigate_and_wait_for_ready

# Test configuration - can be overridden by environment variables
BASE_URL = os.environ.get('TEST_BASE_URL', conftest.TEST_BASE_URL)

@pytest.mark.e2e
def test_delete_testing_range_page_loads(page: Page):
    """
    E2E: Loads the Delete Testing Range page and checks for form and input presence.
    """
    page.goto(f"{BASE_URL}/delete_testing_range")
    page.wait_for_load_state("networkidle")
    expect(page.locator("h2")).to_contain_text("Delete Testing Range")
    min_input = page.locator("#min_id")
    max_input = page.locator("#max_id")
    dry_run_checkbox = page.locator("#dry_run")
    preview_btn = page.locator("#delete-preview-btn")
    assert min_input.count() > 0 and max_input.count() > 0, "Min/Max ID inputs should be present"
    assert dry_run_checkbox.count() > 0, "Dry Run checkbox should be present"
    assert preview_btn.count() > 0, "Preview/Delete button should be present"

@pytest.mark.e2e
def test_min_max_id_inputs(page: Page):
    """
    E2E: Min/Max ID input boxes accept values and update form state.
    """
    page.goto(f"{BASE_URL}/delete_testing_range")
    page.wait_for_load_state("networkidle")
    min_input = page.locator("#min_id")
    max_input = page.locator("#max_id")
    min_input.fill("1000000")
    max_input.fill("1000005")
    assert min_input.input_value() == "1000000"
    assert max_input.input_value() == "1000005"

@pytest.mark.e2e
def test_dry_run_checkbox_and_preview(page: Page):
    """
    E2E: Dry Run checkbox toggles Preview/Delete button and triggers dry run preview.
    """
    page.goto(f"{BASE_URL}/delete_testing_range")
    page.wait_for_load_state("networkidle")
    dry_run_checkbox = page.locator("#dry_run")
    preview_btn = page.locator("#delete-preview-btn")
    # Ensure dry run is checked (Preview mode)
    if not dry_run_checkbox.is_checked():
        dry_run_checkbox.check()
    expect(preview_btn).to_have_text("Preview")
    preview_btn.click()
    # Wait for preview results (look for alert/info or table update)
    alerts = page.locator(".alert-info, .alert-success, .alert-danger")
    found_visible = False
    for i in range(alerts.count()):
        if alerts.nth(i).is_visible():
            found_visible = True
            print(f"[ALERT] {alerts.nth(i).inner_text()}")
    assert found_visible, "At least one alert should be visible after preview."

@pytest.mark.e2e
def test_delete_button_and_real_delete(page: Page):
    """
    E2E: Unchecking Dry Run enables Delete mode, triggers confirmation modal, and performs delete.
    """
    page.goto(f"{BASE_URL}/delete_testing_range")
    page.wait_for_load_state("networkidle")
    dry_run_checkbox = page.locator("#dry_run")
    preview_btn = page.locator("#delete-preview-btn")
    # Uncheck dry run (Delete mode)
    if dry_run_checkbox.is_checked():
        dry_run_checkbox.uncheck()
    expect(preview_btn).to_have_text("Delete")
    preview_btn.click()
    # Wait for modal to appear
    modal = page.locator("#deleteConfirmModal")
    expect(modal).to_be_visible()
    # Click Confirm Delete in modal
    confirm_btn = modal.locator("#modal-confirm-delete")
    expect(confirm_btn).to_be_visible()
    with page.expect_navigation():
        confirm_btn.click()
    # Wait for result message
    alerts = page.locator(".alert-info, .alert-success, .alert-danger")
    found_visible = False
    for i in range(alerts.count()):
        if alerts.nth(i).is_visible():
            found_visible = True
            print(f"[ALERT] {alerts.nth(i).inner_text()}")
    assert found_visible, "At least one alert should be visible after delete."

@pytest.mark.e2e
def test_diagnostics_messaging(page: Page):
    """
    E2E: Diagnostics messages (success, error, info) appear after actions.
    """
    page.goto(f"{BASE_URL}/delete_testing_range")
    page.wait_for_load_state("networkidle")
    # Try an invalid range (min > max)
    min_input = page.locator("#min_id")
    max_input = page.locator("#max_id")
    min_input.fill("1000005")
    max_input.fill("1000000")
    preview_btn = page.locator("#delete-preview-btn")
    preview_btn.click()
    # Wait for error message
    alerts = page.locator(".alert-danger")
    found_visible = False
    for i in range(alerts.count()):
        if alerts.nth(i).is_visible():
            found_visible = True
            print(f"[ALERT] {alerts.nth(i).inner_text()}")
    assert found_visible, "At least one error alert should be visible for invalid range."
    # Try a valid dry run
    min_input.fill("1000000")
    max_input.fill("1000001")
    dry_run_checkbox = page.locator("#dry_run")
    if not dry_run_checkbox.is_checked():
        dry_run_checkbox.check()
    preview_btn.click()
    alerts = page.locator(".alert-info, .alert-success")
    found_visible = False
    for i in range(alerts.count()):
        if alerts.nth(i).is_visible():
            found_visible = True
            print(f"[ALERT] {alerts.nth(i).inner_text()}")
    assert found_visible, "At least one info/success alert should be visible for valid dry run." 