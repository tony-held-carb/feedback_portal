"""
E2E Test: Developer Utilities Dropdown 'Show ...' Menu Links
==========================================================

This test verifies that the Developer Utilities dropdown menu contains all expected 'Show ...' links with valid href attributes.
It does NOT click the links or assert on the new tab's URL, since these are internal routes and we only want to verify menu presence and link correctness.

Test Coverage:
- Loads the main page
- Opens the Developer Utilities dropdown
- Verifies each 'Show ...' menu item is present and has a valid href

This test is intentionally isolated from other E2E suites to focus on menu navigation and internal link correctness.
"""

import os
import re

from playwright.sync_api import Page, expect

import conftest
from arb.portal.utils.e2e_testing_util import navigate_and_wait_for_ready

# Test configuration - can be overridden by environment variables
BASE_URL = os.environ.get('TEST_BASE_URL', conftest.TEST_BASE_URL)

ALL_MENU_ITEMS = [
  ("Show Log File", None),
  ("Show Database Structure", None),
  ("Show Dropdowns", None),
  ("Show Feedback Form Structure", None),
  ("Show Diagnostics", None),
  ("Create Incidence (Oil & Gas)", "/og_incidence_create"),
  ("Create Incidence (Landfill)", "/landfill_incidence_create"),
  ("Delete Testing Range (Dev)", None),
  ("JavaScript Diagnostics", None),
]

CREATE_MENU_ITEMS = [
  ("Create Incidence (Oil & Gas)", "/og_incidence_create", "og"),
  ("Create Incidence (Landfill)", "/landfill_incidence_create", "landfill")
]


def get_expected_dummy_data(sector):
  if sector == "og":
    return {
      "id_incidence": "1002050",
      "id_plume": "1001",
      "facility_name": "facility_name response",
      "contact_name": "contact_name response",
      "contact_phone": "(555) 555-5555",
      "contact_email": "my_email@email.com",
      "id_arb_eggrt": "1001",
      "venting_description_1": "venting_description_1 response",
      "venting_description_2": "venting_description_2 response",
      "initial_leak_concentration": "1004",
      "initial_mitigation_plan": "initial_mitigation_plan response",
      "equipment_other_description": "equipment_other_description response",
      "component_other_description": "component_other_description response",
    }
  elif sector == "landfill":
    return {
      "id_incidence": "1002030",
      "id_plume": "1002",
      "facility_name": "facility_name",
      "contact_name": "contact_name",
      "contact_phone": "(555) 555-5555",
      "contact_email": "my_email@email.com",
      "id_arb_swis": "id_arb_swis",
      "id_message": "id_message",
      "additional_activities": "additional_activities",
      "additional_notes": "additional_notes",
      "emission_cause_notes": "emission_cause_notes",
      "emission_location_notes": "emission_location_notes",
      "included_in_last_lmr_description": "included_in_last_lmr_description",
      "initial_leak_concentration": "1002.5",
      "instrument": "instrument",
    }
  else:
    return {}


def test_developer_utilities_menu_links_and_create_incidence(page: Page):
  """
  E2E: Verify the Developer Utilities dropdown menu contains all expected items with valid hrefs.
  For 'Create Incidence' items, click and check dummy data as before.
  """
  navigate_and_wait_for_ready(page, BASE_URL)
  dev_dropdown = page.locator(".nav-link", has_text="Developer Utilities")
  dev_dropdown.click()
  dropdown_menu = page.locator(".dropdown-menu:visible").nth(-1)
  expect(dropdown_menu).to_be_visible()
  # Check all menu items for presence and href
  for link_text, href_substring in ALL_MENU_ITEMS:
    link = dropdown_menu.locator(f"a.dropdown-item:text('{link_text}')")
    expect(link).to_be_visible()
    href = link.get_attribute("href")
    assert href and href != "#", f"Link '{link_text}' should have a valid href, got: {href}"
    if href_substring:
      assert href_substring in href, f"Link '{link_text}' should have href containing '{href_substring}', got: {href}"
  # Now test Create Incidence navigation and dummy data
  for link_text, href_substring, sector in CREATE_MENU_ITEMS:
    link = dropdown_menu.locator(f"a.dropdown-item:text('{link_text}')")
    expect(link).to_be_visible()
    href = link.get_attribute("href")
    assert href and href_substring in href, f"Link '{link_text}' should have a valid href containing '{href_substring}', got: {href}"
    with page.expect_navigation():
      link.click()
    assert "/incidence_update/" in page.url, f"After clicking '{link_text}', expected to land on an incidence update page, got: {page.url}"
    expect(page).not_to_have_title("404")
    expect(page.locator("body")).not_to_contain_text("Not Found")
    expected_data = get_expected_dummy_data(sector)
    for key, value in expected_data.items():
      if re.match(r"^\d+(\.\d+)?$", value):
        assert value in page.content(), f"Expected value '{value}' for field '{key}' not found in page content after clicking '{link_text}'."
      else:
        assert value in page.content(), f"Expected value '{value}' for field '{key}' not found in page content after clicking '{link_text}'."
    date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
    assert date_pattern.search(
      page.content()), f"Expected a date (YYYY-MM-DD) in page content after clicking '{link_text}'."
    print(
      f"'{link_text}' navigated successfully to an incidence update page: {page.url} and all dummy data fields were found.")
    # Go back to main page for next menu item
    navigate_and_wait_for_ready(page, BASE_URL)
    dev_dropdown = page.locator(".nav-link", has_text="Developer Utilities")
    dev_dropdown.click()
    dropdown_menu = page.locator(".dropdown-menu:visible").nth(-1)
  print(
    "All Developer Utilities menu links verified (presence, href, navigation to update page, all dummy data fields present).")
