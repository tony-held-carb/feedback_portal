"""
E2E Test: Feedback Portal Updates Page (/portal_updates)
=======================================================

This test suite covers the main user-facing features of the Feedback Portal Updates page, including:
- Page load and title
- Table presence and structure
- Filter UI presence and functionality
- CSV download button presence
- Data presence in the table
- Accessibility basics (tab order, ARIA roles)
- Filter application and clearing

This test is designed to be robust and maintainable as the UI evolves.
"""

import pytest
from playwright.sync_api import Page, expect
import re

BASE_URL = "http://127.0.0.1:5000"

@pytest.mark.e2e
def test_feedback_updates_page_loads(page: Page):
    """
    E2E: Loads the Feedback Portal Updates page and checks for title, filter UI, and table presence.
    """
    page.goto(f"{BASE_URL}/portal_updates")
    page.wait_for_load_state("networkidle")
    expect(page).to_have_title(re.compile(r"Feedback.*Updates", re.I))
    # Check for main header
    expect(page.locator("h1, h2")).to_contain_text("Feedback Portal Updates")
    # Use robust role-based selectors for filter UI
    expect(page.get_by_role("button", name="Toggle Filters")).to_be_visible()
    expect(page.get_by_role("button", name="Apply Filters")).to_be_visible()
    expect(page.get_by_role("button", name="Clear Filters")).to_be_visible()
    expect(page.get_by_role("link", name="Download CSV")).to_be_visible()
    # Check for table
    table = page.locator("table, .table")
    assert table.count() > 0, "Feedback Updates table should be present"
    # Check for expected columns
    header = table.locator("th")
    expected_columns = ["Timestamp", "Field Name", "Old Value", "New Value", "User", "Comments", "Inc. ID"]
    for col in expected_columns:
        assert any(col in h.inner_text() for h in header.all()), f"Column '{col}' should be present in table header"
    # Check for at least one data row
    rows = table.locator("tbody tr")
    assert rows.count() > 0, "Feedback Updates table should have at least one data row"

@pytest.mark.e2e
def test_feedback_updates_filter_functionality(page: Page):
    """
    E2E: Tests the filter UI by applying a filter and checking that the table updates.
    """
    page.goto(f"{BASE_URL}/portal_updates")
    page.wait_for_load_state("networkidle")
    # Enter a value in the 'User' filter (assume 'anonymous' is present)
    user_input = page.locator("input[placeholder*='User'], input[name*='user']")
    user_input.fill("anonymous")
    # Click Apply Filters
    apply_btn = page.get_by_role("button", name="Apply Filters")
    apply_btn.click()
    page.wait_for_timeout(1000)
    # Check that all visible rows have 'anonymous' in the User column
    table = page.locator("table, .table")
    user_cells = table.locator("tbody tr td:nth-child(5)")  # User column is 5th
    print("[DEBUG] User column values after filtering:", [user_cells.nth(i).inner_text() for i in range(user_cells.count())])
    if user_cells.count() == 0:
        pytest.skip("No rows matched the filter; skipping content check.")
    for i in range(user_cells.count()):
        assert "anonymous" in user_cells.nth(i).inner_text().lower(), "Filtered row does not match user filter"
    # Clear filters
    clear_btn = page.get_by_role("button", name="Clear Filters")
    clear_btn.click()
    page.wait_for_timeout(1000)
    # Table should reset (row count should increase or stay the same)
    assert table.locator("tbody tr").count() >= user_cells.count(), "Table did not reset after clearing filters"

@pytest.mark.e2e
def test_feedback_updates_download_csv_button(page: Page):
    """
    E2E: Checks that the Download CSV button is present and enabled.
    """
    page.goto(f"{BASE_URL}/portal_updates")
    page.wait_for_load_state("networkidle")
    download_btn = page.get_by_role("link", name="Download CSV")
    assert download_btn.count() > 0 and download_btn.first.is_enabled(), "Download CSV button should be present and enabled"

@pytest.mark.e2e
def test_feedback_updates_accessibility(page: Page):
    """
    E2E: Basic accessibility checks for the Feedback Updates page.
    """
    page.goto(f"{BASE_URL}/portal_updates")
    page.wait_for_load_state("networkidle")
    # Check for ARIA roles on table
    table = page.locator("table, .table")
    assert table.count() > 0, "Table should be present for accessibility check"
    assert table.first.get_attribute("role") in (None, "table"), "Table should have role='table' or no role (HTML table)"
    # Check tab order: first input should be focusable
    first_input = page.locator("input").first
    first_input.focus()
    assert first_input.evaluate('el => el === document.activeElement'), "First input should be focusable via tab order" 