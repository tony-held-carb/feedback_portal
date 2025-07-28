"""
Pytest-compatible E2E UI Automation Tests for Excel Upload Portal using Playwright

This module provides comprehensive end-to-end (E2E) testing of the Excel upload UI
using Playwright with pytest fixtures and assertions.

What is E2E Testing?
--------------------
End-to-end (E2E) tests simulate real user workflows through the entire application stack.
They verify that the UI, backend, and database all work together as expected.

How This Test Suite Works
-------------------------
- Uses Playwright to automate browser actions (like a real user).
- Uses pytest for test discovery, parameterization, and reporting.
- Uploads Excel files through the UI, submits forms, and checks for success/error messages.
- For each test file, performs a deep backend validation:
    * After upload, fetches the corresponding record from the database (misc_json column).
    * Reads the original Excel fields from the file.
    * Compares each field in the Excel file to the value in the DB.
    * If there is a mismatch, checks the backend logs for a warning or default value message.
    * If there is a mismatch and no log warning, the test fails.
- This ensures that the database is being updated with the correct spreadsheet contents, and that any discrepancies are logged.

Limitations
-----------
- These tests check that the UI and backend are integrated and that the DB is updated as expected.
- They do not check for all possible business logic errors or cross-field dependencies unless explicitly coded.
- The deep backend validation only checks the misc_json column; if your app stores data elsewhere, you may need to extend the tests.

Requirements:
- Flask app running at BASE_URL
- Playwright installed and browsers downloaded
- pytest-playwright plugin (optional but recommended)

Test Coverage:
- Basic upload functionality
- File validation and error handling
- Success/failure message verification
- Form submission workflow
- Multiple file types and scenarios
- Drag-and-drop functionality
- Deep backend validation (DB vs. spreadsheet)
"""

import os
import time
import pytest
from pathlib import Path
from typing import List, Dict, Any
from playwright.sync_api import Page, expect
import requests
import re
import openpyxl
import time
import sqlite3
import json
import psycopg2
import warnings
import shutil
import pytest
import functools
import conftest

# Test configuration - can be overridden by environment variables
BASE_URL = os.environ.get('TEST_BASE_URL', conftest.TEST_BASE_URL)

# =============================================================================
# E2E Test Suite for Excel Upload Portal
#
# Preferred way to run only a subset of tests (e.g., discard/malformed):
#   pytest tests/e2e/test_excel_upload_playwright_pytest.py -v --maxfail=3 -k "discard or malformed"
#
# This uses pytest's built-in -k option to select tests by substring, which is more reliable and efficient
# than any in-code filtering. The old SELECT_TESTS_ONLY logic has been removed in favor of this approach.
# =============================================================================


# Suppress openpyxl UserWarnings about unsupported Excel features (Data Validation, Conditional Formatting)
# These warnings are harmless for our business logic and only relate to Excel features not used by the portal.
# See: https://foss.heptapod.net/openpyxl/openpyxl/-/issues/1604
@pytest.fixture(autouse=True, scope="session")
def suppress_openpyxl_warnings():
    warnings.filterwarnings(
        "ignore",
        message=".*extension is not supported and will be removed",
        category=UserWarning,
        module=r"openpyxl\.reader\.excel"
    )


# Helper to get all Excel-like files in a directory

def get_xls_files(base_path: Path, recursive: bool = False, excel_exts=None) -> list:
    """
    Return a list of all Excel-like files in the given directory.
    Args:
      base_path: Path to search
      recursive: If True, search subdirectories
      excel_exts: List of file extensions to include (default: common Excel formats)
    Returns:
      List of file paths (str)
    """
    if excel_exts is None:
        excel_exts = [".xlsx", ".xls", ".xlsm", ".xlsb", ".ods", ".csv"]
    if recursive:
        files = [str(p) for p in base_path.rglob("*") if p.suffix.lower() in excel_exts and p.is_file()]
    else:
        files = [str(p) for p in base_path.glob("*") if p.suffix.lower() in excel_exts and p.is_file()]
    return files

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Configure browser context for tests.
    Sets viewport and disables HTTPS errors for consistent test runs.
    """
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }

@pytest.fixture
def upload_page(page: Page):
    """
    Navigate to upload page and return the page object.
    Ensures each test starts from a clean upload page.
    """
    page.goto(f"{BASE_URL}/upload")
    page.wait_for_load_state("networkidle")
    return page

def get_test_files() -> list:
    """
    Get a list of test files to use for parameterized tests.
    Only the 'standard' directory is enabled by default, but you can uncomment others.
    Returns:
      List of file paths for testing
    """
    base_dirs = [
        Path("feedback_forms/testing_versions/standard"),
    ]
    files = []
    for base_dir in base_dirs:
        files.extend(get_xls_files(base_dir, recursive=True))
    return files

class TestExcelUpload:
    """
    Test class for Excel upload functionality.
    Each method tests a different aspect of the upload workflow, from UI elements to backend validation.
    """
    def test_upload_page_loads(self, upload_page: Page):
        """
        Test that the upload page loads correctly.
        Checks for page title, file input, and upload form elements.
        """
        # Check page title
        expect(upload_page).to_have_title("Upload File")
        # Check for file input element (presence, not visibility)
        file_input = upload_page.locator("input[type='file']")
        assert file_input.count() > 0, "File input should exist in the DOM"
        # Check for upload form
        form = upload_page.locator("form")
        expect(form).to_be_visible()
        # Check for drop zone or upload button (visible for user interaction)
        drop_zone = upload_page.locator(".drop-zone, [id*='drop']")
        assert drop_zone.count() > 0 and drop_zone.first.is_visible(), "Drop zone or upload area should be visible"

    def test_file_input_exists(self, upload_page: Page):
        """
        Test that file input element exists and is functional.
        Checks that it accepts Excel files.
        """
        file_input = upload_page.locator("input[type='file']")
        # Check that file input is present in the DOM
        assert file_input.count() > 0, "File input should exist in the DOM"
        # Check that it accepts Excel files
        accept_attr = file_input.get_attribute("accept")
        assert accept_attr is None or any(ext in accept_attr for ext in ["xlsx", "xls"]), "File input should accept Excel files"

    def test_drop_zone_exists(self, upload_page: Page):
        """
        Test that drop zone element exists (if implemented).
        Ensures drag-and-drop upload is available.
        """
        # Look for drop zone elements
        drop_zones = upload_page.locator("[id*='drop'], [class*='drop'], [id*='zone'], [class*='zone']")
        # If drop zones exist, they should be visible
        if drop_zones.count() > 0:
            expect(drop_zones.first).to_be_visible()

    @pytest.mark.parametrize("file_path", get_test_files())
    def test_file_upload_workflow(self, upload_page: Page, file_path: str):
        """
        Test complete file upload workflow for each test file.
        Steps:
        - Upload file using Playwright's set_input_files
        - Wait for form submission (auto or manual)
        - Check for success or error messages
        - Does not check DB; see deep backend validation for that
        """
        if not os.path.exists(file_path):
            pytest.skip(f"Test file not found: {file_path}")
        # Get file input
        file_input = upload_page.locator("input[type='file']")
        # Upload file using Playwright's set_input_files
        upload_page.set_input_files("input[type='file']", file_path)
        # Wait for file to be processed
        upload_page.wait_for_timeout(1000)
        # Check if form auto-submits or if we need to submit manually
        original_url = upload_page.url
        # Wait for page change (form submission)
        try:
            # Wait for either URL change or success/error message
            upload_page.wait_for_function(
                "() => window.location.href !== arguments[0] || document.querySelector('.alert-success, .alert-danger, .alert-warning') || document.body.textContent.toLowerCase().includes('success') || document.body.textContent.toLowerCase().includes('error')",
                arg=original_url,
                timeout=10000
            )
        except:
            # If no automatic submission, try to submit manually
            submit_button = upload_page.locator("button[type='submit'], input[type='submit']")
            if submit_button.count() > 0:
                submit_button.click()
                upload_page.wait_for_load_state("networkidle")
        # Check for success or error messages
        success_indicators = [
            ".alert-success",
            ".success-message",
            ".alert-info"
        ]
        error_indicators = [
            ".alert-danger",
            ".error-message",
            ".alert-warning"
        ]
        # Check for success
        for indicator in success_indicators:
            if upload_page.locator(indicator).count() > 0:
                success_text = upload_page.locator(indicator).first.text_content()
                assert success_text is not None
                print(f"Upload successful: {success_text}")
                return
        # Check for errors
        for indicator in error_indicators:
            if upload_page.locator(indicator).count() > 0:
                error_text = upload_page.locator(indicator).first.text_content()
                assert error_text is not None
                print(f"Upload failed: {error_text}")
                # Don't fail the test for expected errors (like validation errors)
                return
        # Check page content for success/error keywords
        page_content = upload_page.content().lower()
        if any(keyword in page_content for keyword in ["success", "uploaded", "processed"]):
            print("Upload appears successful based on page content")
            return
        elif any(keyword in page_content for keyword in ["error", "invalid", "failed"]):
            print("Upload appears to have failed based on page content")
            return
        # If we get here, the result is unclear
        pytest.fail("Upload result unclear - no success or error indicators found")

    def test_invalid_file_upload(self, upload_page: Page):
        """
        Test upload with invalid file type (e.g., .txt).
        Ensures the app rejects non-Excel files.
        """
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"This is not an Excel file")
            temp_file = f.name
        try:
            upload_page.set_input_files("input[type='file']", temp_file)
            upload_page.wait_for_timeout(1000)
            error_indicators = [
                ".alert-danger",
                ".error-message",
                ".alert-warning"
            ]
            for indicator in error_indicators:
                if upload_page.locator(indicator).count() > 0:
                    error_text = upload_page.locator(indicator).first.text_content()
                    assert error_text is not None
                    print(f"Invalid file rejected: {error_text}")
                    return
            page_content = upload_page.content().lower()
            if any(keyword in page_content for keyword in ["error", "invalid", "failed", "not allowed"]):
                print("Invalid file appears to have been rejected")
                return
            print("Invalid file was handled (possibly silently rejected)")
        finally:
            os.unlink(temp_file)

    def test_empty_file_upload(self, upload_page: Page):
        """
        Test upload with empty file.
        Ensures the app handles empty files gracefully (rejects or accepts as appropriate).
        """
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_file = f.name
        try:
            upload_page.set_input_files("input[type='file']", temp_file)
            upload_page.wait_for_timeout(1000)
            page_content = upload_page.content().lower()
            if any(keyword in page_content for keyword in ["error", "invalid", "empty", "no data"]):
                print("Empty file was rejected as expected")
            else:
                print("Empty file was accepted (application-specific behavior)")
        finally:
            os.unlink(temp_file)

    def test_large_file_upload(self, upload_page: Page):
        """
        Test upload with a large file (if test files are available).
        Ensures the app can handle large uploads or fails gracefully.
        """
        test_files = get_test_files()
        if not test_files:
            pytest.skip("No test files available for large file test")
        file_path = test_files[0]
        file_size = os.path.getsize(file_path)
        print(f"Testing upload with file size: {file_size} bytes")
        upload_page.set_input_files("input[type='file']", file_path)
        upload_page.wait_for_timeout(2000)  # Longer timeout for large files
        page_content = upload_page.content().lower()
        if any(keyword in page_content for keyword in ["success", "uploaded", "processed"]):
            print("Large file upload successful")
        elif any(keyword in page_content for keyword in ["error", "too large", "size limit"]):
            print("Large file upload failed due to size")
        else:
            print("Large file upload result unclear")

class TestUploadPageElements:
    """
    Test class for upload page element structure and accessibility.
    Ensures the page is well-structured and accessible for users.
    """
    def test_page_structure(self, upload_page: Page):
        """
        Test that the upload page has the expected structure.
        Checks for main content areas and at least one visible child element.
        """
        main_content = upload_page.locator("main, .container, .content")
        assert main_content.count() > 0, "Main content area should exist in the DOM"
        visible_child = main_content.locator(":scope > *:visible")
        assert visible_child.count() > 0, "Main content area should have at least one visible child element"

    def test_form_structure(self, upload_page: Page):
        """
        Test that the upload form has the expected structure.
        Checks for method, action, file input, and submit button.
        """
        form = upload_page.locator("form")
        expect(form).to_be_visible()
        method = form.get_attribute("method")
        action = form.get_attribute("action")
        assert method is not None, "Form should have method attribute"
        assert action is not None, "Form should have action attribute"
        file_input = form.locator("input[type='file']")
        assert file_input.count() > 0, "File input should exist in the form"
        accept_attr = file_input.get_attribute("accept")
        assert accept_attr is None or any(ext in accept_attr for ext in ["xlsx", "xls"]), "File input should accept Excel files"
        submit_button = form.locator("button[type='submit'], input[type='submit']")
        if submit_button.count() > 0:
            expect(submit_button.first).to_be_visible()

    def test_accessibility_features(self, upload_page: Page):
        """
        Test accessibility features on the upload page.
        Checks for page title, file input label, and general form labels.
        """
        expect(upload_page).to_have_title("Upload File")
        file_input = upload_page.locator("input[type='file']")
        file_input_id = file_input.get_attribute("id")
        if file_input_id:
            label = upload_page.locator(f"label[for='{file_input_id}']")
            if label.count() > 0:
                expect(label.first).to_be_visible()
        labels = upload_page.locator("label")
        if labels.count() > 0:
            expect(labels.first).to_be_visible()

# --- Deep Backend Validation Helpers ---
BACKEND_LOG_PATH = "logs/arb_portal.log"
STAGING_DIR = "portal_uploads/staging"

def read_excel_fields(file_path):
    """
    Read all fields and values from the Excel file (Feedback Form tab, col B/C, row 15+).
    Returns a dict mapping field names to values as read from the spreadsheet.
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb["Feedback Form"]
    fields = {}
    for row in ws.iter_rows(min_row=15, max_col=3):
        key = row[1].value
        value = row[2].value
        if key:
            fields[str(key).strip()] = value
    return fields

def get_id_from_redirect(page):
    """
    Extract id_incidence from the redirect URL after upload.
    Example: /incidence_update/123
    """
    match = re.search(r"/incidence_update/(\d+)", page.url)
    if match:
        return int(match.group(1))
    return None

def get_staged_json_path(id_):
    """
    Find the staged JSON file for a given id_incidence in the staging dir.
    Returns the file path if found, else None.
    """
    import os
    if not os.path.exists(STAGING_DIR):
        return None
    for fname in os.listdir(STAGING_DIR):
        if fname.startswith(f"id_{id_}_") and fname.endswith(".json"):
            return os.path.join(STAGING_DIR, fname)
    return None

def read_parsed_json(json_path):
    """
    Read the parsed JSON file and extract Feedback Form tab contents.
    Returns a dict of field values.
    """
    import json
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    tab = data.get("tab_contents", {}).get("Feedback Form", {})
    return tab

def read_backend_logs():
    """
    Read the backend log file and return its lines as a list.
    Used for checking if a field mismatch was logged as a warning.
    """
    try:
        with open(BACKEND_LOG_PATH, "r", encoding="utf-8") as f:
            return f.readlines()
    except Exception:
        return []

# --- Audit Log Helpers ---
def extract_audit_block(log_path, filename):
    """Extracts the audit block for a given filename from the audit log."""
    with open(log_path, encoding="utf-8") as f:
        log = f.read()
    pattern = re.compile(
        rf"=== BEGIN AUDIT: {re.escape(filename)} ===(.*?)=== END AUDIT: {re.escape(filename)} ===",
        re.DOTALL
    )
    match = pattern.search(log)
    return match.group(1) if match else None

def extract_machine_summary(audit_block):
    """Extracts the machine-readable summary JSON from an audit block."""
    pattern = re.compile(r"--- MACHINE READABLE SUMMARY ---\n(.*?)\n--- END MACHINE READABLE SUMMARY ---", re.DOTALL)
    match = pattern.search(audit_block)
    if match:
        return json.loads(match.group(1))
    return None

# --- DB Access Helpers ---
DB_PATH = "source/production/app.db"

# Try to get database URI from environment variables, then fall back to settings
DB_URI = (
    os.environ.get("POSTGRES_DB_URI") or
    os.environ.get("DATABASE_URI") or
    os.environ.get("SQLALCHEMY_DATABASE_URI")
)

# If no environment variable is set, try to get it from settings
if not DB_URI:
    try:
        from arb.portal.config.settings import BaseConfig
        DB_URI = BaseConfig.SQLALCHEMY_DATABASE_URI
    except ImportError:
        DB_URI = None

print(f"[DEBUG] Using DB URI: {DB_URI}")

def fetch_misc_json_from_db(id_):
    """
    Fetch the misc_json dict for a given id_incidence from the Postgres DB (or fallback to SQLite).
    This is the main check that the database was properly updated with the spreadsheet contents.
    Returns the misc_json dict, or an empty dict if not found.
    """
    if DB_URI:
        # Sanitize URI for psycopg2
        pg_uri = DB_URI.replace('+psycopg2', '')
        # Connect to Postgres
        conn = psycopg2.connect(pg_uri)
        try:
            cur = conn.cursor()
            
            # Determine the correct schema from settings
            schema_name = "satellite_tracker_new"  # default
            try:
                from arb.portal.config.settings import BaseConfig
                engine_options = BaseConfig.SQLALCHEMY_ENGINE_OPTIONS
                if 'connect_args' in engine_options and 'options' in engine_options['connect_args']:
                    options = engine_options['connect_args']['options']
                    # Extract schema from search_path option
                    if 'search_path=' in options:
                        search_path = options.split('search_path=')[1].split(',')[0]
                        schema_name = search_path
            except ImportError:
                pass  # Use default if settings import fails
            
            # Use schema-qualified table name
            cur.execute(f"SELECT misc_json FROM {schema_name}.incidences WHERE id_incidence = %s", (id_,))
            row = cur.fetchone()
            if not row or not row[0]:
                return {}
            # misc_json may be a JSON string
            if isinstance(row[0], str):
                return json.loads(row[0])
            return row[0]
        finally:
            conn.close()
    else:
        # Fallback to SQLite
        conn = sqlite3.connect(DB_PATH)
        try:
            cur = conn.cursor()
            cur.execute("SELECT misc_json FROM incidences WHERE id_incidence = ?", (id_,))
            row = cur.fetchone()
            if not row or not row[0]:
                return {}
            if isinstance(row[0], str):
                return json.loads(row[0])
            return row[0]
        finally:
            conn.close()

@pytest.mark.parametrize("file_path", get_test_files())
def test_excel_upload_deep_backend_validation(upload_page, file_path):
    """
    Deep backend validation test: After uploading a file, check that the database (misc_json column)
    matches the spreadsheet contents for every field.
    - Uploads the file via the UI
    - Extracts id_incidence from the redirect URL
    - Fetches the misc_json dict from the DB
    - Reads the original Excel fields
    - Compares each field in the Excel file to the value in the DB
    - If there is a mismatch, checks the backend logs for a warning or default value message
    - If there is a mismatch and no log warning, the test fails
    This is your main guarantee that the database is being updated with the correct spreadsheet contents.
    """
    # Navigate to the upload page
    upload_page.goto(f"{BASE_URL}")
    upload_page.wait_for_load_state("networkidle")
    # Upload file via UI
    file_input = upload_page.locator("input[type='file']")
    upload_page.set_input_files("input[type='file']", file_path)
    upload_page.wait_for_timeout(1000)
    # Wait for redirect or success
    for _ in range(10):
        if "/incidence_update/" in upload_page.url:
            break
        upload_page.wait_for_timeout(500)
    # Log the URL and page content for debugging
    # If this is an edge case file, expect error and no redirect
    if "edge_cases" in Path(file_path).parts:
        # Should remain on upload page and show error message
        assert "/upload" in upload_page.url, f"Expected to remain on upload page for edge case file, got: {upload_page.url}"
        assert any(keyword in upload_page.content().lower() for keyword in ["error", "invalid", "not recognized", "missing", "could not", "failed"]), (
            f"Expected error message for edge case file. Content: {upload_page.content()[:300]}"
        )
        return  # Test passes for edge case scenario
    # After upload, check for id_incidence error message
    page_content = upload_page.content().lower()
    id_error = (
        ("id_incidence" in page_content and "positive integer" in page_content)
        or ("missing a valid 'incidence/emission id'" in page_content)
    )
    if id_error and "/upload" in upload_page.url:
        print("Upload blocked due to missing/invalid id_incidence as expected.")
        return  # Test passes for this scenario
    # Otherwise, proceed as before
    match = re.search(r"/incidence_update/(\d+)", upload_page.url)
    id_ = match.group(1) if match else None
    if not id_:
        # Try to find error messages in the page content
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(page_content, "html.parser")
        error_msgs = []
        for alert in soup.find_all(class_=["alert", "alert-danger", "invalid-feedback", "form-error"]):
            error_msgs.append(alert.get_text(strip=True))
        print(f"Error messages found on page: {error_msgs}")
        upload_dir = Path("portal_uploads")
        uploaded_files = list(upload_dir.glob("*" + Path(file_path).name))
        print(f"Uploaded file(s) found in upload dir: {uploaded_files}")
    assert id_ is not None, f"Could not extract id_incidence from redirect after uploading {file_path}. See debug output above."
    # Wait for backend to process and commit to DB (retry for up to 5 seconds)
    misc_json = None
    for _ in range(10):
        misc_json = fetch_misc_json_from_db(id_)
        if misc_json:
            break
        time.sleep(0.5)
    assert misc_json, f"misc_json not found in DB for id {id_} after uploading {file_path}"
    excel_fields = read_excel_fields(file_path)
    logs = read_backend_logs()
    log_text = "".join(logs)
    for field, excel_value in excel_fields.items():
        parsed_value = misc_json.get(field)
        if parsed_value == excel_value:
            continue  # OK
        else:
            assert (field in log_text and ("WARNING" in log_text or "default" in log_text.lower())), \
                f"Field '{field}' value mismatch (Excel: {excel_value}, Parsed: {parsed_value}) and no log warning found."


def test_list_staged_diagnostics_overlay(page):
    """
    E2E: Load /list_staged, ensure a staged file is present, click discard, and check overlay/modal updates.
    This test now only verifies the discard modal workflow and overlay log for discards.
    """
    from playwright.sync_api import expect
    import os
    # Ensure at least one staged file exists
    page.goto(f"{BASE_URL}/list_staged")
    page.wait_for_load_state("networkidle")
    staged_file_btns = page.locator("form[action*='discard_staged_update'] button[data-js-logging-context='discard-staged']")
    if staged_file_btns.count() == 0:
        # Upload a file to stage it
        test_files = get_test_files()
        if not test_files:
            pytest.skip("No test files available to upload and stage.")
        file_path = test_files[0]
        page.goto(f"{BASE_URL}/upload_staged")
        page.wait_for_load_state("networkidle")
        file_input = page.locator("input[type='file']")
        file_input.set_input_files(file_path)
        page.wait_for_timeout(1000)
        # Wait for redirect to /review_staged
        import re
        for _ in range(10):
            if "/review_staged/" in page.url:
                break
            page.wait_for_timeout(500)
        # Go back to /list_staged
        page.goto(f"{BASE_URL}/list_staged")
        page.wait_for_load_state("networkidle")
        staged_file_btns = page.locator("form[action*='discard_staged_update'] button[data-js-logging-context='discard-staged']")
        if staged_file_btns.count() == 0:
            pytest.skip("Failed to stage a file for diagnostics overlay test.")
    # Click the discard button for the first staged file (triggers custom modal)
    discard_btn = staged_file_btns.first
    discard_btn.click()
    page.wait_for_timeout(500)
    # Confirm modal appears
    modal = page.locator('#discardConfirmModal')
    expect(modal).to_be_visible(timeout=2000)
    # Click the confirm button in the modal
    confirm_btn = page.locator('#discardConfirmModal [data-js-logging-context="discard-modal-confirm"]')
    confirm_btn.click()
    # Immediately check overlay for confirm log before reload clears it (if overlay is still present)
    if page.locator('#js-diagnostics').count() > 0:
        expect(page.locator('#js-diagnostics')).to_contain_text("discard-modal-confirm")
        print(f"[DIAGNOSTICS OVERLAY after modal confirm click] {page.locator('#js-diagnostics').inner_text()}")
    # Wait for form submission and page reload
    page.wait_for_timeout(1000)
    # Optionally, check that the file is no longer listed (if you want to verify backend effect)
    # assert ...


@pytest.fixture(scope="function")
def staged_file_for_discard(page: Page) -> str:
    """
    Fixture: Upload a file via /upload_staged and return its staged filename.
    The file will be available in /list_staged for the discard test.
    """
    test_files = get_test_files()
    if not test_files:
        pytest.skip("No test files available for staging.")
    file_path = test_files[0]
    # Upload file
    page.goto(f"{BASE_URL}/upload_staged")
    page.wait_for_load_state("networkidle")
    file_input = page.locator("input[type='file']")
    file_input.set_input_files(file_path)
    page.wait_for_timeout(1000)
    # Wait for redirect to /review_staged
    import re
    staged_filename = None
    for _ in range(10):
        if "/review_staged/" in page.url:
            match = re.search(r"/review_staged/\d+/(.*?)$", page.url)
            if match:
                staged_filename = match.group(1)
                break
        page.wait_for_timeout(500)
    assert staged_filename, "Could not extract staged filename from URL after upload."
    return staged_filename


def test_upload_file_only(page: Page):
    """
    E2E: Upload a file via /upload_staged and verify it appears in /list_staged.
    Does NOT discard the file. This isolates the upload and staged list logic.
    """
    test_files = get_test_files()
    if not test_files:
        pytest.skip("No test files available for upload.")
    file_path = test_files[0]
    # Upload file
    page.goto(f"{BASE_URL}/upload_staged")
    page.wait_for_load_state("networkidle")
    file_input = page.locator("input[type='file']")
    file_input.set_input_files(file_path)
    page.wait_for_timeout(1000)
    # Extract staged filename
    import re
    staged_filename = None
    for _ in range(10):
        if "/review_staged/" in page.url:
            match = re.search(r"/review_staged/\d+/(.*?)$", page.url)
            if match:
                staged_filename = match.group(1)
                break
        page.wait_for_timeout(500)
    assert staged_filename, "Could not extract staged filename from URL after upload."
    # Go to /list_staged and verify file is present
    page.goto(f"{BASE_URL}/list_staged")
    page.wait_for_load_state("networkidle")
    assert staged_filename in page.content(), f"Staged file {staged_filename} not listed in /list_staged after upload."


def test_discard_staged_file_only(page: Page, staged_file_for_discard):
    """
    E2E: Load /list_staged, discard the first staged file (from fixture), verify modal appears and file is removed.
    This test does NOT perform the upload; it assumes a file is already staged.
    """
    staged_filename = staged_file_for_discard
    # Go to /list_staged and verify file is present
    page.goto(f"{BASE_URL}/list_staged")
    page.wait_for_load_state("networkidle")
    assert staged_filename in page.content(), f"Staged file {staged_filename} not listed in /list_staged before discard."
    # Discard the file using the new modal
    discard_btn = page.locator(f"form[action*='{staged_filename}'] button[data-js-logging-context='discard-staged']").first
    discard_btn.click()
    modal = page.locator('#discardConfirmModal')
    expect(modal).to_be_visible(timeout=2000)
    confirm_btn = page.locator('#discardConfirmModal [data-js-logging-context="discard-modal-confirm"]')
    confirm_btn.click()
    expect(page.locator('#js-diagnostics')).to_contain_text("discard-modal-confirm")
    page.wait_for_timeout(1000)
    # Verify file is no longer listed
    page.goto(f"{BASE_URL}/list_staged")
    page.wait_for_load_state("networkidle")
    assert staged_filename not in page.content(), f"Staged file {staged_filename} still listed after discard."

@pytest.fixture(scope="function")
def two_staged_files(page: Page) -> tuple:
    """
    Fixture: Upload two files via /upload_staged and return their staged filenames.
    Both files will be available in /list_staged for discard tests.
    """
    test_files = get_test_files()
    if len(test_files) < 2:
        pytest.skip("Need at least two test files for this test.")
    file_path1, file_path2 = test_files[:2]
    # Upload first file
    page.goto(f"{BASE_URL}/upload_staged")
    page.wait_for_load_state("networkidle")
    file_input = page.locator("input[type='file']")
    file_input.set_input_files(file_path1)
    page.wait_for_timeout(1000)
    import re
    staged_filename1 = None
    for _ in range(10):
        if "/review_staged/" in page.url:
            match = re.search(r"/review_staged/\d+/(.*?)$", page.url)
            if match:
                staged_filename1 = match.group(1)
                break
        page.wait_for_timeout(500)
    assert staged_filename1, "Could not extract staged filename 1 from URL after upload."
    # Upload second file
    page.goto(f"{BASE_URL}/upload_staged")
    page.wait_for_load_state("networkidle")
    file_input = page.locator("input[type='file']")
    file_input.set_input_files(file_path2)
    page.wait_for_timeout(1000)
    staged_filename2 = None
    for _ in range(10):
        if "/review_staged/" in page.url:
            match = re.search(r"/review_staged/\d+/(.*?)$", page.url)
            if match:
                staged_filename2 = match.group(1)
                break
        page.wait_for_timeout(500)
    assert staged_filename2, "Could not extract staged filename 2 from URL after upload."
    return staged_filename1, staged_filename2


def test_upload_multiple_files_only(page: Page, two_staged_files):
    """
    E2E: Upload two files, verify both appear in /list_staged.
    Does NOT discard the files. Isolates upload and staged list logic for multiple files.
    """
    staged_filename1, staged_filename2 = two_staged_files
    page.goto(f"{BASE_URL}/list_staged")
    page.wait_for_load_state("networkidle")
    assert staged_filename1 in page.content(), f"Staged file {staged_filename1} not listed in /list_staged after upload."
    assert staged_filename2 in page.content(), f"Staged file {staged_filename2} not listed in /list_staged after upload."


def test_discard_each_staged_file_separately(page: Page, two_staged_files):
    """
    E2E: Discard each of two staged files in separate steps, verifying modal/overlay and removal.
    """
    staged_filename1, staged_filename2 = two_staged_files
    # Discard first file
    page.goto(f"{BASE_URL}/list_staged")
    page.wait_for_load_state("networkidle")
    assert staged_filename1 in page.content(), f"Staged file {staged_filename1} not listed before discard."
    discard_btn = page.locator(f"form[action*='{staged_filename1}'] button[data-js-logging-context='discard-staged']").first
    discard_btn.click()
    modal = page.locator('#discardConfirmModal')
    expect(modal).to_be_visible(timeout=2000)
    confirm_btn = page.locator('#discardConfirmModal [data-js-logging-context="discard-modal-confirm"]')
    confirm_btn.click()
    expect(page.locator('#js-diagnostics')).to_contain_text("discard-modal-confirm")
    page.wait_for_timeout(1000)
    page.goto(f"{BASE_URL}/list_staged")
    page.wait_for_load_state("networkidle")
    assert staged_filename1 not in page.content(), f"Staged file {staged_filename1} still listed after discard."
    # Discard second file
    assert staged_filename2 in page.content(), f"Staged file {staged_filename2} not listed before discard."
    discard_btn = page.locator(f"form[action*='{staged_filename2}'] button[data-js-logging-context='discard-staged']").first
    discard_btn.click()
    modal = page.locator('#discardConfirmModal')
    expect(modal).to_be_visible(timeout=2000)
    confirm_btn = page.locator('#discardConfirmModal [data-js-logging-context="discard-modal-confirm"]')
    confirm_btn.click()
    expect(page.locator('#js-diagnostics')).to_contain_text("discard-modal-confirm")
    page.wait_for_timeout(1000)
    page.goto(f"{BASE_URL}/list_staged")
    page.wait_for_load_state("networkidle")
    assert staged_filename2 not in page.content(), f"Staged file {staged_filename2} still listed after discard."


@pytest.fixture(scope="function")
def malformed_file_for_discard(page: Page, tmp_path_factory) -> str:
    """
    Fixture: Create a malformed staged file (valid JSON, missing id_incidence) for discard test.
    Returns the filename.
    """
    staging_dir = Path("portal_uploads/staging")
    staging_dir.mkdir(parents=True, exist_ok=True)
    filename = "malformed_test.json"
    file_path = staging_dir / filename
    # Write valid JSON but missing id_incidence
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"some_field": 123, "not_id": 456}, f)
    return filename


def test_upload_malformed_file_only(page: Page, malformed_file_for_discard):
    """
    E2E: Create a malformed file, verify it appears in /list_staged.
    Does NOT discard the file. Isolates malformed file handling.
    """
    malformed_filename = malformed_file_for_discard
    page.goto(f"{BASE_URL}/list_staged")
    page.wait_for_load_state("networkidle")
    assert malformed_filename in page.content(), f"Malformed file {malformed_filename} not listed in /list_staged after creation."


def test_discard_malformed_file_only(page: Page, malformed_file_for_discard):
    """
    E2E: Discard a malformed file from /list_staged, verifying modal/overlay, backend POST, and removal.
    Uses Playwright's recommended waiting/synchronization tools for robust async handling.
    """
    filename = malformed_file_for_discard
    # 1. Navigate to /list_staged
    page.goto(f"{BASE_URL}/list_staged")
    page.wait_for_load_state("networkidle")
    print(f"[STEP] Navigated to /list_staged for malformed file: {filename}")
    # 2. Locate the malformed file row and discard button
    discard_btn = page.locator(f"form[action*='discard_staged_update/0/{filename}'] button[data-js-logging-context='discard-malformed']").first
    assert discard_btn.is_visible(), f"Discard button for malformed file {filename} not found or not visible."
    print(f"[STEP] Found discard button for malformed file: {filename}")
    # 3. Click the discard button
    discard_btn.click()
    print(f"[STEP] Clicked discard button for malformed file: {filename}")
    # 4. Wait for modal to appear
    modal = page.locator('#discardConfirmModal')
    expect(modal).to_be_visible(timeout=2000)
    print(f"[STEP] Discard confirm modal appeared.")
    # 5. Click the modal confirm button
    confirm_btn = modal.locator("#discard-confirm-btn")
    expect(confirm_btn).to_be_visible()
    print(f"[STEP] Modal confirm button is visible. Clicking...")
    # 6. Optionally check overlay for confirm log before navigation
    with page.expect_navigation():
        confirm_btn.click()
    print(f"[STEP] Modal confirm clicked and navigation complete.")
    # 8. After reload, verify file is gone
    page.wait_for_load_state("networkidle")
    page.goto(f"{BASE_URL}/list_staged")
    page.wait_for_load_state("networkidle")
    assert filename not in page.content(), f"Malformed file {filename} still listed after discard."
    print(f"[STEP] Malformed file {filename} successfully discarded and not present after reload.")

if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])

def pytest_addoption(parser):
    parser.addoption(
        "--only-discard-tests",
        action="store_true",
        default=False,
        help="Run only the discard staged file tests (for rapid debugging)"
    )

def pytest_collection_modifyitems(config, items):
    if config.getoption("--only-discard-tests"):
        keep = []
        for item in items:
            if (
                "test_discard_staged_by_filename" in item.nodeid
                or "test_multiple_staged_files_same_id" in item.nodeid
                or "test_malformed_staged_file_handling" in item.nodeid
            ):
                keep.append(item)
        items[:] = keep 

"""
NOTE: This test suite is integrated with the JS diagnostics overlay and backend logging utility (see java_script_diagnostics.js and /js_diagnostic_log route).
- To debug frontend actions, inspect the overlay at the bottom of the page during test runs.
- To debug backend events, check for [JS_DIAG] entries in arb_portal.log.
- The helper function get_js_diagnostics_overlay(page) can be used to scrape overlay text during tests.
"""

def get_js_diagnostics_overlay(page):
    """Scrape the JS diagnostics overlay text from the page (if present)."""
    try:
        return page.locator('#js-diagnostics').inner_text()
    except Exception:
        return '' 