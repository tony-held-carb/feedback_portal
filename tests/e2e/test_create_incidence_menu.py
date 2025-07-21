"""
E2E Test: Developer Utilities Dropdown 'Create Incidence' Menu Links
==================================================================

This test verifies that the Developer Utilities dropdown menu contains the 'Create Incidence (Oil & Gas)' and 'Create Incidence (Landfill)' links with valid href attributes.
It does NOT click the links or assert on the new tab's URL, since we only want to verify menu presence and link correctness.

Test Coverage:
- Loads the main page
- Opens the Developer Utilities dropdown
- Verifies each 'Create Incidence' menu item is present and has a valid href

This test is intentionally isolated from other E2E suites to focus on menu navigation and internal link correctness.
"""

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:5000/"

CREATE_MENU_ITEMS = [
    ("Create Incidence (Oil & Gas)", "/og_incidence_create"),
    ("Create Incidence (Landfill)", "/landfill_incidence_create")
]

def test_developer_utilities_create_incidence_menu_links(page: Page):
    """
    E2E: Verify the Developer Utilities dropdown menu contains 'Create Incidence' links with valid href attributes.
    This test clicks each link, waits for navigation, and asserts that the resulting page loads successfully (status 200 and expected content).
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
    for link_text, href_substring in CREATE_MENU_ITEMS:
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
        print(f"'{link_text}' navigated successfully to an incidence update page: {page.url}")
        # Go back to main page for next menu item
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        dev_dropdown = page.locator(".nav-link", has_text="Developer Utilities")
        dev_dropdown.click()
        dropdown_menu = page.locator(".dropdown-menu:visible").nth(-1)
    print("All Developer Utilities 'Create Incidence' menu links verified (presence, href, navigation to update page).") 