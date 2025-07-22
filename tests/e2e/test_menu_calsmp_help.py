"""
E2E Test: CalSMP & Help Dropdown Menu Links
==========================================

This test verifies that the CalSMP & Help dropdown menu contains all expected links with the correct href and target attributes.
It does NOT click the links or assert on the new tab's URL, since external resources may redirect to login pages or be inaccessible from the test environment.

Test Coverage:
- Loads the main page
- Opens the CalSMP & Help dropdown
- Verifies each menu item is present, has the correct href substring, and target="_blank"

This test is intentionally isolated from other E2E suites to focus on menu navigation and external link correctness.
"""

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:5000/"

def test_calsmp_help_menu_links(page: Page):
    """
    E2E: Verify the CalSMP & Help dropdown menu contains all expected links with correct href and target attributes.
    This test does NOT click the links or assert on the new tab's URL, since external resources may redirect to login pages or be inaccessible.
    """
    expected_links = [
        ("Plume Processing Resources", "Plume%20Processing%20Resources.docx"),
        ("Daily Protocol", "Daily%20CalSMP%20Protocol.docx"),
        ("Daily Processing Log", "Daily%20Plume%20Processing%20Log.docx"),
        ("Open Items Log", "Open%20items%20log.xlsx"),
        ("Plume Tracker", "10.93.112.44:5003"),
        ("Contact Manager", "internal-smdms-sdb-lb-shared-182971779.us-west-2.elb.amazonaws.com"),
        ("Feedback Portal Source Code & Documentation", "tony-held-carb.github.io/feedback_portal/")
    ]
    # Go to the main page
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    # Open the CalSMP & Help dropdown
    help_dropdown = page.locator(".nav-link", has_text="CalSMP & Help")
    help_dropdown.click()
    # Wait for dropdown to be visible
    dropdown_menu = page.locator(".dropdown-menu:visible").nth(-1)
    expect(dropdown_menu).to_be_visible()
    # Check each expected link
    for link_text, href_substring in expected_links:
        link = dropdown_menu.locator(f"a.dropdown-item:text('{link_text}')")
        expect(link).to_be_visible()
        href = link.get_attribute("href")
        target = link.get_attribute("target")
        assert href_substring in href, f"Link '{link_text}' href does not contain expected substring: {href_substring}"
        assert target == "_blank", f"Link '{link_text}' should have target='_blank'"
    print("All CalSMP & Help menu links verified (presence, href, target).") 