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

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:5000/"

SHOW_MENU_ITEMS = [
    "Show Log File",
    "Show Database Structure",
    "Show Dropdowns",
    "Show Feedback Form Structure",
    "Show Diagnostics"
]

def test_developer_utilities_show_menu_links(page: Page):
    """
    E2E: Verify the Developer Utilities dropdown menu contains all 'Show ...' links with valid href attributes.
    This test does NOT click the links or assert on the new tab's URL.
    """
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    # Open the Developer Utilities dropdown
    dev_dropdown = page.locator(".nav-link", has_text="Developer Utilities")
    dev_dropdown.click()
    # Wait for dropdown to be visible
    dropdown_menu = page.locator(".dropdown-menu:visible").nth(-1)
    expect(dropdown_menu).to_be_visible()
    # Check each 'Show ...' menu item
    for link_text in SHOW_MENU_ITEMS:
        link = dropdown_menu.locator(f"a.dropdown-item:text('{link_text}')")
        expect(link).to_be_visible()
        href = link.get_attribute("href")
        assert href and href != "#", f"Link '{link_text}' should have a valid href, got: {href}"
    print("All Developer Utilities 'Show ...' menu links verified (presence, href).") 