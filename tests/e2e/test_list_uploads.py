"""
E2E Test: List Uploaded Files Page (/list_uploads)
=================================================

This test covers the main features of the List Uploaded Files page:
- Page load and title
- Table presence and structure
- File links
- Accessibility basics
- Empty state handling

Skips gracefully if no files are present.
"""

import os

import pytest
from playwright.sync_api import Page, expect

import conftest
from arb.portal.utils.e2e_testing_util import navigate_and_wait_for_ready

# Test configuration - can be overridden by environment variables
BASE_URL = os.environ.get('TEST_BASE_URL', conftest.TEST_BASE_URL)


@pytest.mark.e2e
def test_list_uploads_page_loads(page: Page):
  """
  E2E: Loads the List Uploaded Files page and checks for title and table presence.
  """
  navigate_and_wait_for_ready(page, f"{BASE_URL}/list_uploads")
  expect(page).to_have_title("Uploaded Files")
  # Check for main header
  expect(page.locator("h2")).to_contain_text("Uploaded Files")
  # Check for table
  table = page.locator("table, .table")
  assert table.count() > 0, "Uploaded files table should be present"


@pytest.mark.e2e
def test_list_uploads_file_links(page: Page):
  """
  E2E: Checks that file links are present and valid in the uploaded files table.
  """
  # Use our standard navigation approach
  navigate_and_wait_for_ready(page, f"{BASE_URL}/list_uploads")

  # Wait for the table to be present
  expect(page.locator("table, .table")).to_be_visible(timeout=30000)

  table = page.locator("table, .table")
  rows = table.locator("tbody tr")
  if rows.count() == 0:
    pytest.skip("No uploaded files to check links.")

  # Check that each row has a link - limit to first 10 rows for performance
  max_rows_to_check = min(rows.count(), 10)
  for i in range(max_rows_to_check):
    link = rows.nth(i).locator("a")
    assert link.count() > 0, f"Row {i} should have a file link"
    href = link.first.get_attribute("href")
    assert href and href != "#", f"File link in row {i} should have a valid href"


@pytest.mark.e2e
def test_list_uploads_accessibility(page: Page):
  """
  E2E: Basic accessibility checks for the List Uploaded Files page.
  """
  navigate_and_wait_for_ready(page, f"{BASE_URL}/list_uploads")
  table = page.locator("table, .table")
  assert table.count() > 0, "Table should be present for accessibility check"
  # Check tab order: first link should be focusable
  first_link = table.locator("a").first
  if first_link.count() == 0:
    pytest.skip("No file links to check focusability.")
  first_link.focus()
  assert first_link.evaluate('el => el === document.activeElement'), "First file link should be focusable via tab order"


@pytest.mark.e2e
def test_list_uploads_empty_state(page: Page):
  """
  E2E: Checks that the page handles the empty state (no uploaded files) gracefully.
  """
  navigate_and_wait_for_ready(page, f"{BASE_URL}/list_uploads")
  table = page.locator("table, .table")
  rows = table.locator("tbody tr")
  if rows.count() > 0:
    pytest.skip("Uploaded files are present; skipping empty state check.")
  # Check for empty state message or row
  assert table.inner_text().strip() != "", "Table should render even if empty (no files)."
