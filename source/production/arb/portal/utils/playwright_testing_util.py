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
  """
  expect(
    page.locator(".upload-marker[data-upload-attempted='true']")
  ).to_have_count(1, timeout=timeout)


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

  This function sets a file into an <input type="file"> field, then waits for a hidden element
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

  expect(
    page.locator(UPLOAD_ATTEMPT_MARKER_SELECTOR)
  ).to_have_count(1, timeout=timeout)


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
  expect(
    page.locator(".upload-marker[data-upload-attempted='true']")
  ).to_have_count(1, timeout=timeout)
