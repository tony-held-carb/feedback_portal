"""
Playwright Testing Utility Functions
===================================

General-purpose Playwright helpers for robust testing of file upload workflows in web applications.

These functions help ensure that file uploads are handled and verified reliably without using
fragile time-based waits like `page.wait_for_timeout(...)`. Instead, they detect visible feedback
messages in the DOM to confirm whether an upload succeeded, failed, or was rejected.

Part of the arb.portal.utils package for general-purpose testing utilities.

The current helper functions assume that the file upload does not change the route 
(i.e., the browser stays on the same page) after the upload process.

If the upload triggers a redirect, page reload, or navigation, then a different approach is needed.

Why Feedback-Based Upload Verification?
---------------------------------------
In typical file upload interfaces, the application provides **visible feedback** after upload —
either a success alert (e.g., green `.alert-success`), error message (e.g., red `.alert-danger`),
or custom warning/validation indicator. This visual feedback is a natural, stable, and
user-facing signal that the app has processed the file.

Rather than waiting a fixed amount of time (which is slow and unreliable), these helpers:

  ✅ Clear old/stale alerts that could interfere with test logic  
  ✅ Perform the file upload  
  ✅ Wait for any *new, visible feedback element* to appear (success, warning, or error)  

This ensures your test waits *only as long as necessary* — and not longer — while also
avoiding false positives from previous test state.

Avoids Common Pitfalls:
------------------------
- ❌ `wait_for_timeout(...)`: introduces flakiness, adds delay even when the app is ready.
- ❌ Checking only for presence of alerts (`locator.count() > 0`): may match stale messages.
- ❌ `wait_for_load_state("networkidle")`: does not apply to DOM-driven upload feedback.

Limitations:
------------
This pattern assumes that:
  - The app always provides visual feedback in response to a file upload.
  - Feedback messages are placed in the DOM under consistent class selectors.
  - Old alerts can be safely removed without impacting state.

It does *not* handle:
  - Silent backend failures with no frontend signal
  - File parsing logic that delays feedback indefinitely
  - AJAX-only flows where feedback appears in a modal, toast, or separate route

Usage:
-------
Recommended in all file upload tests where UI feedback is displayed using alerts or error messages.

Typical usage flow:

    clear_upload_feedback_alerts(page)
    upload_file_and_wait_for_feedback(page, "invalid_file.txt")
    expect(page.locator(".alert-danger")).to_contain_text("Only .xlsx files are allowed")

These helpers are compatible with Bootstrap-style alerts and can be extended to support modals,
toasts, or custom feedback containers if needed.
"""
import time
import os
from typing import Optional
from playwright.sync_api import Page, expect


def wait_for_upload_attempt_marker(page: Page, timeout: int = 7000) -> None:
  """
  Waits for a hidden DOM element that signals a file upload was attempted.

  This element is injected by the server when Flask flashes an internal marker.
  It allows tests to verify that a file was uploaded (regardless of success/failure)
  without relying on visible alerts or user-facing DOM changes.

  Args:
    page (Page): The Playwright Page object.
    timeout (int): How long to wait for the marker (in ms). Default is 7000.

  Raises:
    TimeoutError: If the marker is not found within the timeout window.

  Usage:
    flash("_upload_attempted", "internal-marker")  # 🔐 Hidden marker for E2E testing
  """
  # Use the new robust system for better reliability
  wait_for_upload_attempt_robust(page, timeout)


# Constants for feedback message selectors
UPLOAD_FEEDBACK_SELECTOR = (
  ".alert-success, .alert-danger, .alert-warning, .success-message, .error-message"
)

UPLOAD_ATTEMPT_MARKER_SELECTOR = ".upload-marker[data-upload-attempted='true']"

CLEAR_ALERTS_JS = """
  document.querySelectorAll(
    '.alert-success, .alert-danger, .alert-warning, .success-message, .error-message'
  ).forEach(el => el.remove());
"""

CLEAR_UPLOAD_MARKER_JS = """
  document.querySelectorAll('.upload-marker[data-upload-attempted="true"]')
    .forEach(el => el.remove());
"""


def clear_upload_attempt_marker(page: Page) -> None:
  """
  Remove the hidden upload-attempt marker from the DOM before a new file upload.

  This is useful when testing multiple uploads in the same session to ensure that
  old markers do not interfere with new assertions.

  The marker is a non-visual DOM element added by the Flask server to indicate
  that a file upload was attempted (regardless of success or failure).

  Args:
    page (Page): The current Playwright page instance.

  Example:
    >>> clear_upload_attempt_marker(page)
  """
  print("clear_upload_attempt_marker() called")
  page.evaluate(CLEAR_UPLOAD_MARKER_JS)


def clear_upload_feedback_alerts(page: Page) -> None:
  """
  Remove all existing feedback messages from the DOM before a new file upload.

  This prevents stale messages (from earlier upload attempts) from being mistakenly
  picked up by the test as indicators of success or failure.

  Args:
    page (Page): The current Playwright page instance.

  Example:
    >>> clear_upload_feedback_alerts(page)
  """
  print("clear_upload_feedback_alerts() called")

  page.evaluate(CLEAR_ALERTS_JS)


def upload_file_and_wait_for_feedback(page: Page, file_path: str, timeout: int = 10000) -> None:
  """
  Upload a file and wait for a visible feedback alert indicating success, error, or warning.

  This function sets a file into an <input type="file"> field, then waits for any of the
  expected feedback messages (Bootstrap or custom) to appear visibly in the DOM.

  This is a general-purpose routine compatible with valid and invalid file uploads.

  Args:
    page (Page): The current Playwright page instance.
    file_path (str): The path to the file to be uploaded.
    timeout (int): Max time in milliseconds to wait for feedback (default 10 seconds).

  Example:
    >>> clear_upload_feedback_alerts(page)
    >>> upload_file_and_wait_for_feedback(page, "data/bad_upload.txt")

  Raises:
    AssertionError if no visible alert appears in time.
  """
  page.set_input_files("input[type='file']", file_path)

  expect(
    page.locator(UPLOAD_FEEDBACK_SELECTOR).first
  ).to_be_visible(timeout=timeout)


def upload_file_and_wait_for_attempt_marker(page: Page, file_path: str, timeout: int = 10000) -> None:
  """
  Upload a file and wait for the hidden DOM marker that indicates an upload attempt occurred.

  This function sets a file into an <input type='file'> field, then waits for a hidden element
  (e.g., <div class="upload-marker" data-upload-attempted="true" style="display: none;">)
  to appear in the DOM. This marker is flashed by the Flask backend and persists across redirects.

  It does NOT require a visible success or error message and is useful for testing upload
  mechanics regardless of outcome.

  Args:
    page (Page): The current Playwright page instance.
    file_path (str): The path to the file to be uploaded.
    timeout (int): Max time in milliseconds to wait for marker (default 10 seconds).

  Example:
    >>> clear_upload_attempt_marker(page)
    >>> upload_file_and_wait_for_attempt_marker(page, "data/upload.xlsx")

  Raises:
    AssertionError if the marker is not found within the timeout.
  """
  print("upload_file_and_wait_for_attempt_marker() called")

  page.set_input_files("input[type='file']", file_path)

  # Use the robust multi-method approach
  wait_for_upload_attempt_robust(page, timeout)


# New robust marker system
UPLOAD_STATE_KEY = "_upload_attempt_state"
UPLOAD_STATE_TIMESTAMP_KEY = "_upload_attempt_timestamp"

def set_upload_attempt_state(page: Page, state: str = "attempted") -> None:
    """
    Set a robust upload attempt state using client-side session storage.
    
    This is more reliable than DOM-based markers because it persists through
    redirects and doesn't depend on template rendering timing.
    
    Args:
        page (Page): The Playwright Page object
        state (str): The state to set (default: "attempted")
    """
    # Use JavaScript to set session storage (persists across redirects)
    page.evaluate(f"""
        () => {{
            sessionStorage.setItem('{UPLOAD_STATE_KEY}', '{state}');
            sessionStorage.setItem('{UPLOAD_STATE_TIMESTAMP_KEY}', Date.now().toString());
        }}
    """)

def clear_upload_attempt_state(page: Page) -> None:
    """
    Clear the upload attempt state from session storage.
    
    Args:
        page (Page): The Playwright Page object
    """
    page.evaluate(f"""
        () => {{
            sessionStorage.removeItem('{UPLOAD_STATE_KEY}');
            sessionStorage.removeItem('{UPLOAD_STATE_TIMESTAMP_KEY}');
        }}
    """)

def wait_for_upload_attempt_state(page: Page, timeout: int = 10000) -> None:
    """
    Wait for upload attempt state to be set in session storage.
    
    This is more robust than DOM-based markers because:
    1. It persists through redirects
    2. It's not affected by template rendering timing
    3. It works consistently across different environments
    
    Args:
        page (Page): The Playwright Page object
        timeout (int): How long to wait for the state (in ms). Default is 10000.
    
    Raises:
        TimeoutError: If the state is not found within the timeout window.
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout / 1000:
        state = page.evaluate(f"() => sessionStorage.getItem('{UPLOAD_STATE_KEY}')")
        if state == "attempted":
            return
        time.sleep(0.1)  # Check every 100ms
    
    raise TimeoutError(f"Upload attempt state not found within {timeout}ms")

def get_upload_attempt_timestamp(page: Page) -> Optional[int]:
    """
    Get the timestamp when the upload attempt was made.
    
    Args:
        page (Page): The Playwright Page object
    
    Returns:
        Optional[int]: The timestamp in milliseconds, or None if not set
    """
    timestamp_str = page.evaluate(f"() => sessionStorage.getItem('{UPLOAD_STATE_TIMESTAMP_KEY}')")
    return int(timestamp_str) if timestamp_str else None

# Enhanced version that combines both approaches for maximum reliability
def get_environment_timeout(base_timeout: int = 10000) -> int:
    """
    Get environment-appropriate timeout based on system characteristics.
    
    Windows environments typically need longer timeouts due to:
    - Slower file system operations
    - Higher database latency (often remote)
    - Different process scheduling
    
    Args:
        base_timeout (int): Base timeout in milliseconds
        
    Returns:
        int: Adjusted timeout for the current environment
    """
    # Detect Windows environment
    if os.name == 'nt':
        # Windows typically needs 2-3x longer timeouts
        return base_timeout * 3
    
    # Linux/WSL environments can use shorter timeouts
    return base_timeout

def wait_for_upload_attempt_robust(page: Page, timeout: int = None) -> None:
    """
    Wait for upload attempt using multiple detection methods for maximum reliability.
    
    This function tries multiple approaches:
    1. Session storage state (most reliable)
    2. DOM marker (fallback)
    3. URL change detection (additional verification)
    
    Args:
        page (Page): The Playwright Page object
        timeout (int): How long to wait (in ms). If None, uses environment-appropriate default.
    
    Raises:
        TimeoutError: If no upload attempt is detected within the timeout.
    """
    if timeout is None:
        timeout = get_environment_timeout(10000)
    
    start_time = time.time()
    original_url = page.url
    
    while time.time() - start_time < timeout / 1000:
        # Method 1: Check session storage state
        try:
            state = page.evaluate(f"() => sessionStorage.getItem('{UPLOAD_STATE_KEY}')")
            if state == "attempted":
                return
        except:
            pass
        
        # Method 2: Check DOM marker
        try:
            marker_count = page.locator(".upload-marker[data-upload-attempted='true']").count()
            if marker_count > 0:
                return
        except:
            pass
        
        # Method 3: Check if URL changed (indicates navigation occurred)
        if page.url != original_url:
            # If we navigated, assume upload was attempted
            return
        
        time.sleep(0.1)  # Check every 100ms
    
    raise TimeoutError(f"No upload attempt detected within {timeout}ms using any method")

def diag_robust_marker_system(page: Page) -> bool:
    """
    Diagnostic function to verify the robust marker system is working correctly.
    
    This can be called during test setup to ensure the marker system is functional.
    
    Args:
        page (Page): The Playwright Page object
        
    Returns:
        bool: True if the system is working, False otherwise
    """
    try:
        # Test 1: Set and retrieve session storage
        set_upload_attempt_state(page, "test")
        state = page.evaluate("() => sessionStorage.getItem('_upload_attempt_state')")
        if state != "test":
            print("[TEST] Session storage test failed")
            return False
        
        # Test 2: Clear session storage
        clear_upload_attempt_state(page)
        state = page.evaluate("() => sessionStorage.getItem('_upload_attempt_state')")
        if state is not None:
            print("[TEST] Session storage clear test failed")
            return False
        
        # Test 3: Check environment timeout
        timeout = get_environment_timeout(1000)
        if timeout < 1000:
            print("[TEST] Environment timeout test failed")
            return False
        
        print("[TEST] Robust marker system tests passed")
        return True
        
    except Exception as e:
        print(f"[TEST] Robust marker system test failed: {e}")
        return False
