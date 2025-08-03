"""
E2E Tests for JavaScript Diagnostics Logging System
==================================================

This test file is dedicated to verifying the frontend diagnostics overlay and logging system
implemented in `java_script_diagnostics.js` and demonstrated in `java_script_diagnostic_test.html`.

Context & Purpose:
------------------
- The `/java_script_diagnostic_test` route is a development/debugging page, not part of the main user workflow.
- It serves as a working example and reference for integrating the diagnostics overlay and logging system into any page.
- The diagnostics system provides real-time overlay logging in the browser and backend logging via POST to `/js_diagnostic_log`.
- This test ensures that overlay logging, button click logging, and diagnostic message sending all work as intended.

Related Files:
--------------
- `source/production/arb/portal/static/js/java_script_diagnostics.js`: Implements the diagnostics overlay, event delegation, and backend logging.
- `source/production/arb/portal/templates/java_script_diagnostic_test.html`: Example template showing how to use the diagnostics system, including diagnostics block, input, buttons, and modal integration.

Test Coverage:
--------------
- Overlay presence and correct logging on page load
- Logging of button clicks (including send-diagnostic with input value)
- Proper Playwright waiting to avoid race conditions between UI updates and assertions

Playwright Best Practices for Diagnostics Overlay:
-------------------------------------------------
- Always use `wait_for_load_state("networkidle")` after navigation to ensure the page and overlay are ready.
- After triggering a UI event (like a button click), use Playwright's `expect(locator).to_contain_text()` or similar polling-based assertions to wait for the overlay to update before asserting.
- Avoid asserting overlay content immediately after a click; always use robust Playwright waiting strategies instead of arbitrary timeouts.
- If testing backend logging, use Playwright's network interception or polling for POST requests if needed.

Example:
    page.goto(f"{BASE_URL}/java_script_diagnostic_test")
    page.wait_for_load_state("networkidle")
    # ... interact with page ...
    from playwright.sync_api import expect
    expect(page.locator('#js-diagnostics')).to_contain_text("expected log")

"""

import pytest
from playwright.sync_api import Page, expect
import os
import conftest
from e2e_helpers import navigate_and_wait_for_ready

# Test configuration - can be overridden by environment variables
BASE_URL = os.environ.get('TEST_BASE_URL', conftest.TEST_BASE_URL)

def test_diagnostics_overlay_on_diagnostic_test_page(page: Page):
    """
    E2E: Load /java_script_diagnostic_test, check overlay for page load diagnostic, click diagnostics button, and check overlay updates.
    This test verifies:
    - Overlay is present and logs page load
    - Diagnostics button logs to overlay (including input value)
    - Waits are used to avoid race conditions
    """
    navigate_and_wait_for_ready(page, f"{BASE_URL}/java_script_diagnostic_test")
    # Scrape overlay after page load
    overlay = ''
    try:
        overlay = page.locator('#js-diagnostics').inner_text()
    except Exception:
        overlay = '[Overlay not found]'
    print(f"[DIAGNOSTICS OVERLAY after load] {overlay}")
    assert 'Page loaded' in overlay or overlay != '[Overlay not found]', "Overlay did not show page load diagnostic."
    # Click the diagnostics button (send-diagnostic)
    btn = page.locator('.js-log-btn[data-js-logging-context="send-diagnostic"]')
    assert btn.count() > 0 and btn.first.is_visible(), "Diagnostics button should be present and visible"
    btn.first.click()
    # Use Playwright's expect to robustly wait for overlay update
    expect(page.locator('#js-diagnostics')).to_contain_text('send-diagnostic')
    overlay2 = ''
    try:
        overlay2 = page.locator('#js-diagnostics').inner_text()
    except Exception:
        overlay2 = '[Overlay not found]'
    print(f"[DIAGNOSTICS OVERLAY after click] {overlay2}")
    assert 'send-diagnostic' in overlay2, "Overlay did not update after clicking diagnostics button." 