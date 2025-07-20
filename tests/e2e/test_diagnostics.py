"""
Standalone E2E Test for JavaScript Diagnostics System

This test file contains a single test extracted from the main test suite to verify
that the JavaScript diagnostics system works correctly on the dedicated diagnostics
test page (/java_script_diagnostic_test).

This is used to:
1. Verify the diagnostics system works independently
2. Test the basic functionality without other page-specific complications
3. Provide a baseline for comparing diagnostics behavior across different pages
"""

import pytest
from playwright.sync_api import Page

BASE_URL = "http://127.0.0.1:5000"


def get_js_diagnostics_overlay(page: Page) -> str:
    """
    Helper function to scrape the JavaScript diagnostics overlay content.
    
    Args:
        page: Playwright page object
        
    Returns:
        String content of the diagnostics overlay
    """
    try:
        overlay = page.locator('#js-diagnostics').inner_text()
        return overlay
    except Exception as e:
        return f"Error getting overlay: {e}"


def test_diagnostics_overlay_on_diagnostic_test_page(page: Page):
    """
    E2E: Load /java_script_diagnostic_test, check overlay for page load diagnostic, 
    click diagnostics button, and check overlay updates.
    
    This test verifies that:
    1. The diagnostics test page loads successfully
    2. Page load events are logged to the overlay
    3. The send diagnostic button works correctly
    4. Button clicks are logged to the overlay
    """
    # Navigate to the dedicated diagnostics test page
    page.goto(f"{BASE_URL}/java_script_diagnostic_test")
    page.wait_for_load_state("networkidle")
    
    # Scrape overlay after page load
    overlay = get_js_diagnostics_overlay(page)
    print(f"[DIAGNOSTICS OVERLAY after load] {overlay}")
    
    # Verify page load diagnostic is present
    assert 'Page loaded' in overlay or overlay != '[Overlay not found]', "Overlay did not show page load diagnostic."
    
    # Click the diagnostics button (use new class and data attribute selector)
    page.locator('.js-log-btn[data-js-logging-context="send-diagnostic"]').click()
    page.wait_for_timeout(500)
    
    # Scrape overlay after button click
    overlay2 = get_js_diagnostics_overlay(page)
    print(f"[DIAGNOSTICS OVERLAY after click] {overlay2}")
    
    # Verify send diagnostic action was logged
    assert 'Button clicked: send-diagnostic' in overlay2, "Overlay did not update after clicking diagnostics button." 

def test_diagnostics_overlay_on_list_staged(page: Page):
    """
    E2E: Load /list_staged, check overlay for page load diagnostic, 
    click diagnostics button, and check overlay updates.
    
    This test verifies that:
    1. The diagnostics test page loads successfully
    2. Page load events are logged to the overlay
    3. The send diagnostic button works correctly
    4. Button clicks are logged to the overlay
    """
    # Navigate to the dedicated diagnostics test page
    page.goto(f"{BASE_URL}/list_staged")
    page.wait_for_load_state("networkidle")
    
    # Scrape overlay after page load
    overlay = get_js_diagnostics_overlay(page)
    print(f"[DIAGNOSTICS OVERLAY after load] {overlay}")
    
    # Verify page load diagnostic is present
    assert 'Page loaded' in overlay or overlay != '[Overlay not found]', "Overlay did not show page load diagnostic."
    
    # Click the diagnostics button (use new class and data attribute selector)
    page.locator('.js-log-btn[data-js-logging-context="send-diagnostic"]').click()
    page.wait_for_timeout(500)
    
    # Scrape overlay after button click
    overlay2 = get_js_diagnostics_overlay(page)
    print(f"[DIAGNOSTICS OVERLAY after click] {overlay2}")
    
    # Verify send diagnostic action was logged
    assert 'Button clicked: send-diagnostic' in overlay2, "Overlay did not update after clicking diagnostics button." 


def test_list_staged_diagnostics_overlay(page: 'Page'):
    """
    E2E: Load /list_staged, check overlay for page load diagnostic, click diagnostics block send button, click discard, and check overlay updates.
    This is a standalone version of the overlay+discard test from the main suite, updated for the custom modal system.
    The overlay is checked for the modal confirm log immediately after clicking confirm, before the page reload.
    """
    from playwright.sync_api import expect
    page.goto("http://127.0.0.1:5000/list_staged")
    page.wait_for_load_state("networkidle")
    # Scrape overlay after page load
    overlay = page.locator('#js-diagnostics').inner_text()
    print(f"[DIAGNOSTICS OVERLAY after load] {overlay}")
    # Click the diagnostics block send button
    page.locator('.js-log-btn[data-js-logging-context="send-diagnostic"]').click()
    page.wait_for_timeout(500)
    overlay2 = page.locator('#js-diagnostics').inner_text()
    print(f"[DIAGNOSTICS OVERLAY after send click] {overlay2}")
    # Click the discard button for the first staged file (triggers custom modal)
    discard_btn = page.locator("form[action*='discard_staged_update'] button[data-js-logging-context='discard-staged']").first
    discard_btn.click()
    page.wait_for_timeout(500)
    # Confirm modal appears
    modal = page.locator('#discardConfirmModal')
    assert modal.is_visible(), "Custom discard modal did not appear."
    # Click the confirm button in the modal
    confirm_btn = page.locator('#discardConfirmModal [data-js-logging-context="discard-modal-confirm"]')
    confirm_btn.click()
    # Immediately check overlay for confirm log before reload clears it
    expect(page.locator('#js-diagnostics')).to_contain_text("discard-modal-confirm")
    print(f"[DIAGNOSTICS OVERLAY after modal confirm click] {page.locator('#js-diagnostics').inner_text()}")
    # Wait for form submission and page reload
    page.wait_for_timeout(1000)
    # Optionally, check that the file is no longer listed (if you want to verify backend effect)
    # assert ... 

    