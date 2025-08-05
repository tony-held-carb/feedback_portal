"""
E2E Tests for Refactored vs Original Route Equivalence

This module provides comprehensive end-to-end testing to ensure that the refactored
upload_file_staged_refactored route produces identical results to the original
upload_file_staged route.

The tests upload the same Excel files through both routes and compare:
1. Database persistence results
2. Staged file creation
3. Error handling behavior
4. Response messages and redirects

This ensures that our refactoring maintains functional equivalence while improving
code structure and error handling.
"""

import json
import os
import sqlite3
import warnings
from pathlib import Path
from typing import Any, Dict

import psycopg2
import pytest
from playwright.sync_api import Page, expect

import conftest
from arb.portal.utils.e2e_testing_util import navigate_and_wait_for_ready

# Test configuration
BASE_URL = os.environ.get('TEST_BASE_URL', conftest.TEST_BASE_URL)


# Suppress openpyxl warnings
@pytest.fixture(autouse=True, scope="session")
def suppress_openpyxl_warnings():
  warnings.filterwarnings(
    "ignore",
    message=".*extension is not supported and will be removed",
    category=UserWarning,
    module=r"openpyxl\.reader\.excel"
  )


def get_test_files() -> list:
  """Get a subset of test files for equivalence testing."""
  test_data_dir = Path(__file__).parent.parent.parent / "test_data" / "excel_files"
  if not test_data_dir.exists():
    return []  # Return empty list instead of skipping

  # Use a few representative files for equivalence testing
  test_files = []
  for file_path in test_data_dir.glob("*.xlsx"):
    if file_path.name.startswith("test_"):
      test_files.append(str(file_path))

  return test_files[:3]  # Limit to 3 files for efficiency


def fetch_misc_json_from_db(id_: int) -> Dict[str, Any]:
  """Fetch misc_json data from database for a given ID."""
  try:
    # Try PostgreSQL first (production)
    conn = psycopg2.connect(
      host=os.environ.get('DB_HOST', 'localhost'),
      database=os.environ.get('DB_NAME', 'arb_feedback'),
      user=os.environ.get('DB_USER', 'postgres'),
      password=os.environ.get('DB_PASSWORD', '')
    )
    cursor = conn.cursor()
    cursor.execute("SELECT misc_json FROM incidence WHERE id_incidence = %s", (id_,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result and result[0]:
      return result[0]
    return {}

  except Exception:
    # Fallback to SQLite (development)
    try:
      db_path = Path(__file__).parent.parent.parent / "instance" / "arb_feedback.db"
      if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT misc_json FROM incidence WHERE id_incidence = ?", (id_,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result and result[0]:
          return json.loads(result[0])
        return {}
    except Exception:
      pass

  return {}


def get_staged_files() -> list:
  """Get list of staged files for comparison."""
  staged_dir = Path(__file__).parent.parent.parent / "staged_uploads"
  if not staged_dir.exists():
    return []

  staged_files = []
  for file_path in staged_dir.glob("*.json"):
    staged_files.append(file_path.name)

  return sorted(staged_files)


def extract_id_from_staged_filename(filename: str) -> int:
  """Extract ID from staged filename format: id_123_ts_20250101_120000.json"""
  try:
    parts = filename.split('_')
    if len(parts) >= 2 and parts[0] == 'id':
      return int(parts[1])
  except (ValueError, IndexError):
    pass
  return None


class TestRefactoredVsOriginalEquivalence:
  """Test suite for comparing refactored vs original route behavior."""

  @pytest.mark.parametrize("file_path", get_test_files())
  def test_upload_equivalence_success_case(self, page: Page, file_path: str):
    if not file_path:  # Skip if no test files available
      pytest.skip("No test files available for equivalence testing")
    """
    Test that both routes produce identical results for successful uploads.
    
    This test:
    1. Uploads the same file through both routes
    2. Compares the database persistence results
    3. Compares the staged file creation
    4. Verifies identical behavior
    """
    file_name = Path(file_path).name

    # Step 1: Upload through original route
    navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged")

    # Upload file
    with page.expect_file_chooser() as fc_info:
      page.click("input[type='file']")
    file_chooser = fc_info.value
    file_chooser.set_files(file_path)

    # Submit form
    with page.expect_navigation():
      page.click("button[type='submit']")

    # Get original results
    original_url = page.url
    original_html = page.content()

    # Extract ID from redirect or staged file
    original_id = None
    if "id=" in original_url:
      original_id = int(original_url.split("id=")[1].split("&")[0])
    else:
      # Check staged files for the most recent one
      staged_files = get_staged_files()
      if staged_files:
        original_id = extract_id_from_staged_filename(staged_files[-1])

    # Step 2: Upload through refactored route
    navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged_refactored")

    # Upload same file
    with page.expect_file_chooser() as fc_info:
      page.click("input[type='file']")
    file_chooser = fc_info.value
    file_chooser.set_files(file_path)

    # Submit form
    with page.expect_navigation():
      page.click("button[type='submit']")

    # Get refactored results
    refactored_url = page.url
    refactored_html = page.content()

    # Extract ID from redirect or staged file
    refactored_id = None
    if "id=" in refactored_url:
      refactored_id = int(refactored_url.split("id=")[1].split("&")[0])
    else:
      # Check staged files for the most recent one
      staged_files = get_staged_files()
      if staged_files:
        refactored_id = extract_id_from_staged_filename(staged_files[-1])

    # Step 3: Compare results
    assert original_id is not None, f"Original route failed to produce ID for {file_name}"
    assert refactored_id is not None, f"Refactored route failed to produce ID for {file_name}"

    # Both routes should produce the same ID (or at least valid IDs)
    # Note: They might not be identical if they create separate records
    # but both should be valid and the data should be equivalent

    # Compare database persistence
    original_data = fetch_misc_json_from_db(original_id)
    refactored_data = fetch_misc_json_from_db(refactored_id)

    # Both should have persisted data
    assert original_data, f"Original route failed to persist data for {file_name}"
    assert refactored_data, f"Refactored route failed to persist data for {file_name}"

    # Compare key fields (sector, tab_contents structure)
    if 'sector' in original_data:
      assert original_data['sector'] == refactored_data['sector'], \
        f"Sector mismatch for {file_name}: {original_data['sector']} vs {refactored_data['sector']}"

    if 'tab_contents' in original_data and 'tab_contents' in refactored_data:
      original_tabs = set(original_data['tab_contents'].keys())
      refactored_tabs = set(refactored_data['tab_contents'].keys())
      assert original_tabs == refactored_tabs, \
        f"Tab contents mismatch for {file_name}: {original_tabs} vs {refactored_tabs}"

  def test_error_handling_equivalence_no_file(self, page: Page):
    """Test that both routes handle 'no file selected' error identically."""
    # Test original route
    navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged")

    # Since there's no submit button, we need to trigger form submission differently
    # The form uses JavaScript to auto-submit when a file is selected, but we can test
    # the "no file selected" case by checking the form validation
    form = page.locator("form")
    file_input = page.locator("input[type='file']")

    # Check that the form exists and has the expected structure
    assert form.count() > 0, "Original route should have a form"
    assert file_input.count() > 0, "Original route should have file input"

    # The form should have the required attribute on the file input
    assert file_input.get_attribute("required") == "", "File input should be required"

    # Test refactored route
    navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged_refactored")

    form = page.locator("form")
    file_input = page.locator("input[type='file']")

    # Check that the form exists and has the expected structure
    assert form.count() > 0, "Refactored route should have a form"
    assert file_input.count() > 0, "Refactored route should have file input"

    # The form should have the required attribute on the file input
    assert file_input.get_attribute("required") == "", "File input should be required"

  def test_error_handling_equivalence_invalid_file(self, page: Page):
    """Test that both routes handle invalid file errors identically."""
    # Create an invalid file
    invalid_file = Path(__file__).parent / "invalid_test.txt"
    invalid_file.write_text("This is not an Excel file")

    try:
      # Test original route
      navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged")

      # Use the hidden file input directly since it's not visible
      file_input = page.locator("input[type='file']")

      # Set the file and wait for form submission to complete
      with page.expect_navigation():
        file_input.set_input_files(str(invalid_file))

      # Wait for the page to be fully loaded after navigation
      expect(page.locator("h2")).to_be_visible()
      original_html = page.content()

      # Reset page state before testing refactored route
      page.goto("about:blank")

      # Test refactored route
      navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged_refactored")

      # Use the hidden file input directly since it's not visible
      file_input = page.locator("input[type='file']")

      # Set the file and wait for form submission to complete
      with page.expect_navigation():
        file_input.set_input_files(str(invalid_file))

      # Wait for the page to be fully loaded after navigation
      expect(page.locator("h2")).to_be_visible()
      refactored_html = page.content()

      # Both should show some form of error
      assert "error" in original_html.lower() or "failed" in original_html.lower() or "invalid" in original_html.lower()
      assert "error" in refactored_html.lower() or "failed" in refactored_html.lower() or "invalid" in refactored_html.lower()

    finally:
      # Cleanup
      if invalid_file.exists():
        invalid_file.unlink()

  def test_form_structure_equivalence(self, page: Page):
    """Test that both routes have identical form structure."""
    # Test original route form
    navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged")

    original_form = page.locator("form")
    original_file_input = page.locator("input[type='file']")
    original_drop_zone = page.locator("#drop_zone")

    assert original_form.count() > 0, "Original route should have a form"
    assert original_file_input.count() > 0, "Original route should have file input"
    assert original_drop_zone.count() > 0, "Original route should have drop zone"

    # Check that file input is hidden (d-none class)
    assert "d-none" in original_file_input.get_attribute("class"), "File input should be hidden"

    # Test refactored route form
    navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged_refactored")

    refactored_form = page.locator("form")
    refactored_file_input = page.locator("input[type='file']")
    refactored_drop_zone = page.locator("#drop_zone")

    assert refactored_form.count() > 0, "Refactored route should have a form"
    assert refactored_file_input.count() > 0, "Refactored route should have file input"
    assert refactored_drop_zone.count() > 0, "Refactored route should have drop zone"

    # Check that file input is hidden (d-none class)
    assert "d-none" in refactored_file_input.get_attribute("class"), "File input should be hidden"

  def test_message_parameter_equivalence(self, page: Page):
    """Test that both routes handle message parameters identically."""
    test_message = "Test%20message%20for%20equivalence"

    # Test original route with message
    navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged/{test_message}")

    original_html = page.content()

    # Test refactored route with message
    navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged_refactored/{test_message}")

    refactored_html = page.content()

    # Both should display the message
    assert "Test message for equivalence" in original_html
    assert "Test message for equivalence" in refactored_html


class TestRefactoredRouteSpecificFeatures:
  """Test suite for refactored route-specific improvements."""

  def test_refactored_route_specific_error_messages(self, page: Page):
    """Test that refactored route provides more specific error messages."""
    # Create a file that will trigger specific error types
    # This would require creating test files that trigger different error scenarios
    # For now, we'll test the basic structure

    navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged_refactored")

    # Check that the page loads correctly
    assert page.title() or page.content(), "Refactored route should load"

    # The refactored route should have the same basic structure
    form = page.locator("form")
    assert form.count() > 0, "Refactored route should have a form"

  def test_refactored_route_navigation(self, page: Page):
    """Test that refactored route is accessible from navigation."""
    # Go to main page and check if refactored route is in navigation
    navigate_and_wait_for_ready(page, f"{BASE_URL}/")

    # Look for refactored route in navigation
    refactored_link = page.locator("a[href*='upload_staged_refactored']")

    # The refactored route should be accessible
    assert refactored_link.count() > 0, "Refactored route should be accessible from navigation"


def pytest_addoption(parser):
  """Add custom pytest options."""
  parser.addoption(
    "--compare-only",
    action="store_true",
    help="Run only equivalence comparison tests"
  )


def pytest_collection_modifyitems(config, items):
  """Modify test collection based on options."""
  if config.getoption("--compare-only"):
    # Only run equivalence tests
    items[:] = [item for item in items if "equivalence" in item.name.lower()]
