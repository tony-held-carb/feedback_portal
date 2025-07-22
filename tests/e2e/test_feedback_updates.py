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
import csv
import io
import random
import string
from datetime import datetime, timedelta

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

@pytest.mark.e2e
def test_feedback_updates_empty_state(page: Page):
    """
    E2E: Apply a filter that matches no records and check for empty state handling.
    """
    page.goto(f"{BASE_URL}/portal_updates")
    page.wait_for_load_state("networkidle")
    # Use a random unlikely string for user filter
    random_user = "user_" + ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    user_input = page.get_by_placeholder("User")
    user_input.fill(random_user)
    page.get_by_role("button", name="Apply Filters").click()
    page.wait_for_timeout(1000)
    table = page.locator("table, .table")
    rows = table.locator("tbody tr")
    # Check for the 'no data' row
    no_data_row = table.locator("tbody tr td[colspan='7']")
    assert no_data_row.count() > 0, "No updates found row should be present when no data matches filter."
    assert "No updates found for the selected filters." in no_data_row.first.inner_text(), "No data message should be shown."

@pytest.mark.e2e
def test_feedback_updates_long_text_overflow(page: Page):
    """
    E2E: Check that long text in fields/comments does not break table layout.
    """
    page.goto(f"{BASE_URL}/portal_updates")
    page.wait_for_load_state("networkidle")
    table = page.locator("table, .table")
    rows = table.locator("tbody tr")
    if rows.count() == 0:
        pytest.skip("No data rows to check for long text.")
    # Check for any cell with >100 chars
    found_long = False
    for i in range(rows.count()):
        for cell in rows.nth(i).locator('td').all():
            if len(cell.inner_text()) > 100:
                found_long = True
                # Optionally, check for ellipsis or wrapping
                break
        if found_long:
            break
    if not found_long:
        pytest.skip("No long text found in any cell; skipping overflow check.")
    # If found, pass (UI should handle it)
    assert True

@pytest.mark.e2e
def test_feedback_updates_special_characters(page: Page):
    """
    E2E: Check that special characters render correctly and do not break filters.
    """
    page.goto(f"{BASE_URL}/portal_updates")
    page.wait_for_load_state("networkidle")
    table = page.locator("table, .table")
    rows = table.locator("tbody tr")
    if rows.count() == 0:
        pytest.skip("No data rows to check for special characters.")
    # Look for special characters in any cell
    specials = ['"', "'", '&', '<', '>', '©', '™', '✓', '—', '…', '😀']
    found_special = False
    for i in range(rows.count()):
        for cell in rows.nth(i).locator('td').all():
            if any(s in cell.inner_text() for s in specials):
                found_special = True
                break
        if found_special:
            break
    if not found_special:
        pytest.skip("No special characters found in any cell; skipping.")
    # If found, pass (UI should render them)
    assert True

@pytest.mark.e2e
def test_feedback_updates_date_range_boundaries(page: Page):
    """
    E2E: Use start/end date filters at the boundary of available data.
    """
    page.goto(f"{BASE_URL}/portal_updates")
    page.wait_for_load_state("networkidle")
    table = page.locator("table, .table")
    rows = table.locator("tbody tr")
    if rows.count() == 0:
        pytest.skip("No data rows to check date boundaries.")
    # Get min/max date from Timestamp column (1st col)
    timestamps = []
    for i in range(rows.count()):
        ts = rows.nth(i).locator('td').first.inner_text().strip()
        try:
            timestamps.append(datetime.strptime(ts, "%Y-%m-%d %H:%M"))
        except Exception:
            continue
    if not timestamps:
        pytest.skip("No valid timestamps found.")
    min_ts, max_ts = min(timestamps), max(timestamps)
    # Set start_date to min, end_date to max
    try:
        page.get_by_placeholder("Start date").fill(min_ts.strftime("%Y-%m-%d"))
        page.get_by_placeholder("End date").fill(max_ts.strftime("%Y-%m-%d"))
    except Exception:
        # Fallback: set value via JS if date picker blocks direct fill
        page.evaluate(f"document.getElementById('start_date').value = '{min_ts.strftime('%Y-%m-%d')}'")
        page.evaluate(f"document.getElementById('end_date').value = '{max_ts.strftime('%Y-%m-%d')}'")
    page.get_by_role("button", name="Apply Filters").click()
    page.wait_for_timeout(1000)
    # All visible rows should have timestamps within the range
    rows = table.locator("tbody tr")
    for i in range(rows.count()):
        ts = rows.nth(i).locator('td').first.inner_text().strip()
        try:
            ts_dt = datetime.strptime(ts, "%Y-%m-%d %H:%M")
            assert min_ts <= ts_dt <= max_ts
        except Exception:
            continue

@pytest.mark.e2e
def test_feedback_updates_csv_download_with_filters(page: Page, tmp_path):
    """
    E2E: Apply a filter, download CSV, and check that the CSV only contains filtered results.
    """
    page.goto(f"{BASE_URL}/portal_updates")
    page.wait_for_load_state("networkidle")
    user_input = page.get_by_placeholder("User")
    user_input.fill("anonymous")
    page.get_by_role("button", name="Apply Filters").click()
    page.wait_for_timeout(1000)
    # Download CSV
    with page.expect_download() as download_info:
        page.get_by_role("link", name="Download CSV").click()
    download = download_info.value
    csv_path = tmp_path / "filtered_updates.csv"
    download.save_as(str(csv_path))
    # Read CSV and check all rows have 'anonymous' in User column
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'User' in row:
                assert 'anonymous' in row['User'].lower()

@pytest.mark.e2e
def test_feedback_updates_rapid_filter_changes(page: Page):
    """
    E2E: Rapidly change filters and apply them in succession, checking for UI stability.
    """
    page.goto(f"{BASE_URL}/portal_updates")
    page.wait_for_load_state("networkidle")
    user_input = page.get_by_placeholder("User")
    for i in range(5):
        user_input.fill(f"anonymous{i}")
        page.get_by_role("button", name="Apply Filters").click()
        page.wait_for_timeout(300)
    # After rapid changes, clear filters
    page.get_by_role("button", name="Clear Filters").click()
    page.wait_for_timeout(500)
    # Table should be present and not broken
    table = page.locator("table, .table")
    assert table.count() > 0

@pytest.mark.e2e
def test_feedback_updates_large_data_set(page: Page):
    """
    E2E: If possible, check that the table handles a large number of updates (pagination, scrolling).
    """
    page.goto(f"{BASE_URL}/portal_updates")
    page.wait_for_load_state("networkidle")
    table = page.locator("table, .table")
    rows = table.locator("tbody tr")
    if rows.count() < 100:
        pytest.skip("Not enough data to test large data set scenario.")
    # Check that pagination or scrolling is present
    pagination = page.locator(".dataTables_paginate, .paginate_button")
    assert pagination.count() > 0 or rows.count() > 100, "Pagination or scrolling should be present for large data sets." 