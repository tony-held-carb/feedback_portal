"""
E2E Test: Developer Utilities Dropdown 'Create Incidence' Menu Links
==================================================================

This test verifies that the Developer Utilities dropdown menu contains the 'Create Incidence (Oil & Gas)' and 'Create Incidence (Landfill)' links with valid href attributes.
After clicking each link, it asserts that the resulting page loads successfully and that **all key-value pairs from the dummy data** (from db_hardcoded.py) are present in the page content. This provides maximum confidence that the backend and frontend are in sync for new incidence creation.
If this test becomes too cumbersome to maintain as the UI/dummy data evolves, it can be relaxed in the future.

Test Coverage:
- Loads the main page
- Opens the Developer Utilities dropdown
- Verifies each 'Create Incidence' menu item is present and has a valid href
- Clicks each link, waits for navigation, and asserts that all dummy data fields are present on the resulting page

This test is intentionally isolated from other E2E suites to focus on menu navigation and backend/frontend contract correctness.
"""

import pytest
from playwright.sync_api import Page, expect
import datetime
import re

BASE_URL = "http://127.0.0.1:5000/"

CREATE_MENU_ITEMS = [
    ("Create Incidence (Oil & Gas)", "/og_incidence_create", "og"),
    ("Create Incidence (Landfill)", "/landfill_incidence_create", "landfill")
]

def get_expected_dummy_data(sector):
    # Inline the expected dummy data for maximum test reliability
    if sector == "og":
        # From db_hardcoded.get_og_dummy_form_data()
        return {
            "id_incidence": "2050",
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
            # Dates will be checked as YYYY-MM-DD
        }
    elif sector == "landfill":
        # From db_hardcoded.get_landfill_dummy_form_data()
        return {
            "id_incidence": "2030",
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
            # Dates will be checked as YYYY-MM-DD
        }
    else:
        return {}

def test_developer_utilities_create_incidence_menu_links(page: Page):
    """
    E2E: Verify the Developer Utilities dropdown menu contains 'Create Incidence' links with valid href attributes.
    After clicking each link, assert that all dummy data fields are present on the resulting page.
    """
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    # Open the Developer Utilities dropdown
    dev_dropdown = page.locator(".nav-link", has_text="Developer Utilities")
    dev_dropdown.click()
    # Wait for dropdown to be visible
    dropdown_menu = page.locator(".dropdown-menu:visible").nth(-1)
    expect(dropdown_menu).to_be_visible()
    # Check and click each 'Create Incidence' menu item
    for link_text, href_substring, sector in CREATE_MENU_ITEMS:
        link = dropdown_menu.locator(f"a.dropdown-item:text('{link_text}')")
        expect(link).to_be_visible()
        href = link.get_attribute("href")
        assert href and href_substring in href, f"Link '{link_text}' should have a valid href containing '{href_substring}', got: {href}"
        # Click the link and wait for navigation
        with page.expect_navigation():
            link.click()
        # After navigation, check that the page loaded successfully and redirected to an incidence update page
        assert "/incidence_update/" in page.url, f"After clicking '{link_text}', expected to land on an incidence update page, got: {page.url}"
        expect(page).not_to_have_title("404")
        expect(page.locator("body")).not_to_contain_text("Not Found")
        # Check all expected dummy data fields
        expected_data = get_expected_dummy_data(sector)
        for key, value in expected_data.items():
            # For numbers, allow string or numeric match
            if re.match(r"^\d+(\.\d+)?$", value):
                assert value in page.content(), f"Expected value '{value}' for field '{key}' not found in page content after clicking '{link_text}'."
            else:
                assert value in page.content(), f"Expected value '{value}' for field '{key}' not found in page content after clicking '{link_text}'."
        # For datetime fields, check for YYYY-MM-DD in page content
        date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
        assert date_pattern.search(page.content()), f"Expected a date (YYYY-MM-DD) in page content after clicking '{link_text}'."
        print(f"'{link_text}' navigated successfully to an incidence update page: {page.url} and all dummy data fields were found.")
        # Go back to main page for next menu item
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        dev_dropdown = page.locator(".nav-link", has_text="Developer Utilities")
        dev_dropdown.click()
        dropdown_menu = page.locator(".dropdown-menu:visible").nth(-1)
    print("All Developer Utilities 'Create Incidence' menu links verified (presence, href, navigation to update page, all dummy data fields present).") 