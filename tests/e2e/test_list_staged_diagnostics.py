"""
E2E Tests for /list_staged page JavaScript Diagnostics

This test file focuses specifically on testing the JavaScript diagnostics functionality
on the /list_staged page, using the same components and patterns from the working
java_script_diagnostic_test page.

The goal is to verify that:
1. The diagnostics overlay is properly displayed
2. Page load events are logged
3. The diagnostics block buttons work correctly
4. The overlay captures and displays diagnostic messages

Once these basic diagnostics are working, we can expand to test more complex
functionality like discard operations.
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


def test_list_staged_page_load_diagnostics(page: Page):
    """
    E2E: Test that /list_staged page loads and logs basic diagnostics to overlay.
    
    This test verifies that:
    1. The page loads successfully
    2. The diagnostics overlay is present and visible
    3. Page load events are logged to the overlay
    """
    # Navigate to /list_staged
    page.goto(f"{BASE_URL}/list_staged")
    page.wait_for_load_state("networkidle")
    
    # Check that the page loaded successfully
    assert page.url == f"{BASE_URL}/list_staged"
    
    # Verify the diagnostics overlay is present
    overlay_element = page.locator('#js-diagnostics')
    assert overlay_element.is_visible(), "Diagnostics overlay should be visible"
    
    # Get overlay content and verify it contains expected page load logs
    overlay_content = get_js_diagnostics_overlay(page)
    print(f"[DIAGNOSTICS OVERLAY] {overlay_content}")
    
    # Check for expected page load diagnostics
    assert "Page loaded (list_staged)" in overlay_content, "Should log page load event"
    assert "[JS_DIAG]" in overlay_content, "Should contain JS diagnostic markers"


def test_list_staged_diagnostics_block_functionality(page: Page):
    """
    E2E: Test that the diagnostics block on /list_staged works correctly.
    
    This test verifies that:
    1. The diagnostics block is present on the page
    2. The send diagnostic button works
    3. The return home button works with confirmation modal
    4. All actions are logged to the overlay
    """
    # Navigate to /list_staged
    page.goto(f"{BASE_URL}/list_staged")
    page.wait_for_load_state("networkidle")
    
    # Verify the diagnostics block is present
    diagnostics_block = page.locator('.js-diagnostics-block')
    assert diagnostics_block.is_visible(), "Diagnostics block should be visible"
    
    # Check that the block has the correct data-page attribute
    data_page = diagnostics_block.get_attribute('data-page')
    assert data_page == "list_staged", f"Expected data-page='list_staged', got '{data_page}'"
    
    # Get initial overlay content
    initial_overlay = get_js_diagnostics_overlay(page)
    print(f"[INITIAL OVERLAY] {initial_overlay}")
    
    # Test the send diagnostic button
    send_btn = page.locator(".js-log-btn[data-js-logging-context='send-diagnostic']")
    assert send_btn.is_visible(), "Send diagnostic button should be visible"
    
    # Click the send button and check overlay updates
    send_btn.click()
    page.wait_for_timeout(500)  # Wait for async operations
    
    after_send_overlay = get_js_diagnostics_overlay(page)
    print(f"[AFTER SEND OVERLAY] {after_send_overlay}")
    
    # Verify the send action was logged
    assert "Send Diagnostic clicked" in after_send_overlay, "Send button click should be logged"
    assert "Diagnostic from /list_staged page" in after_send_overlay, "Should include the diagnostic message"
    
    # Test the return home button (should show confirmation modal)
    return_btn = page.locator('.js-return-home-btn')
    assert return_btn.is_visible(), "Return home button should be visible"
    
    # Click return button and verify Bootstrap modal appears
    return_btn.click()
    page.wait_for_timeout(500)
    
    # Check that the Bootstrap modal is visible
    modal = page.locator('.js-confirm-return-modal')
    assert modal.is_visible(), "Bootstrap modal should be visible after clicking return button"
    
    # Check overlay after return button click
    after_return_overlay = get_js_diagnostics_overlay(page)
    print(f"[AFTER RETURN OVERLAY] {after_return_overlay}")
    
    # Verify return action was logged (even if cancelled)
    assert "Return to Homepage button clicked" in after_return_overlay, "Return button click should be logged"


def test_list_staged_diagnostics_text_input(page: Page):
    """
    E2E: Test that the diagnostics text input works correctly.
    
    This test verifies that:
    1. The text input is present and editable
    2. Custom messages can be entered and sent
    3. The custom message appears in the overlay
    """
    # Navigate to /list_staged
    page.goto(f"{BASE_URL}/list_staged")
    page.wait_for_load_state("networkidle")
    
    # Find the diagnostic text input
    text_input = page.locator('.js-diagnostic-text')
    assert text_input.is_visible(), "Diagnostic text input should be visible"
    
    # Check initial value
    initial_value = text_input.input_value()
    assert "Diagnostic from /list_staged page" in initial_value, "Should have default diagnostic message"
    
    # Enter a custom message
    custom_message = "Custom test message from E2E test"
    text_input.fill(custom_message)
    
    # Verify the input was updated
    updated_value = text_input.input_value()
    assert updated_value == custom_message, f"Input should contain custom message, got '{updated_value}'"
    
    # Send the custom message
    send_btn = page.locator(".js-log-btn[data-js-logging-context='send-diagnostic']")
    send_btn.click()
    page.wait_for_timeout(500)
    
    # Check that custom message appears in overlay
    overlay_content = get_js_diagnostics_overlay(page)
    print(f"[CUSTOM MESSAGE OVERLAY] {overlay_content}")
    
    assert custom_message in overlay_content, "Custom message should appear in overlay"
    assert "Send Diagnostic clicked" in overlay_content, "Send action should be logged"


def test_list_staged_diagnostics_structure(page: Page):
    """
    E2E: Test that the diagnostics block has the correct structure and elements.
    
    This test verifies that all required elements are present and properly configured.
    """
    # Navigate to /list_staged
    page.goto(f"{BASE_URL}/list_staged")
    page.wait_for_load_state("networkidle")
    
    # Check that all required elements are present
    required_elements = [
        '.js-diagnostics-block',
        '.js-diagnostic-text',
        '.js-log-btn[data-js-logging-context="send-diagnostic"]',
        '.js-return-home-btn',
        '.js-confirm-return-modal',
        '.js-confirm-return-btn',
        '.js-cancel-return-btn'
    ]
    
    for selector in required_elements:
        element = page.locator(selector)
        assert element.count() > 0, f"Required element '{selector}' should be present"
    
    # Verify the modal structure
    modal = page.locator('.js-confirm-return-modal')
    assert modal.get_attribute('tabindex') == '-1', "Modal should have tabindex='-1'"
    
    # Check that the modal has the correct Bootstrap classes
    modal_classes = modal.get_attribute('class')
    assert modal_classes is not None, "Modal should have a class attribute"
    assert 'modal' in modal_classes, "Modal should have 'modal' class"
    
    # Verify the modal content structure exists (but may not be visible by default)
    modal_title = page.locator('.js-confirm-return-modal .modal-title')
    assert modal_title.count() > 0, "Modal should have a title element"
    
    modal_body = page.locator('.js-confirm-return-modal .modal-body')
    assert modal_body.count() > 0, "Modal should have a body element"
    
    # Check that the page has the required scripts loaded
    # This is a basic check - in a real scenario you might want to verify script execution
    page_content = page.content()
    assert 'java_script_diagnostics.js' in page_content, "Page should include the diagnostics JS file" 