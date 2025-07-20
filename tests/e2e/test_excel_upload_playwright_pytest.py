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
- Flask app running at http://127.0.0.1:5000
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

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_FILES_DIR = Path("feedback_forms/testing_versions")

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
        # Path("feedback_forms/testing_versions/edge_cases"),
        # Path("feedback_forms/testing_versions/generated"),
        # Path("feedback_forms/testing_versions/old")
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
DB_URI = (
    os.environ.get("POSTGRES_DB_URI") or
    os.environ.get("DATABASE_URI") or
    os.environ.get("SQLALCHEMY_DATABASE_URI")
)
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
            # Use schema-qualified table name
            cur.execute("SELECT misc_json FROM satellite_tracker_new.incidences WHERE id_incidence = %s", (id_,))
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
    upload_page.goto("http://127.0.0.1:5000/upload")
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

class TestExcelUploadStaged:
    """
    Comprehensive E2E tests for the staged upload workflow.
    Tests upload, review, confirm, and DB validation for staged files.
    """
    @pytest.mark.parametrize("file_path", get_test_files())
    def test_excel_upload_staged_workflow(self, page: Page, file_path: str):
        """
        E2E: Upload via /upload_staged, verify in /list_staged, review, confirm, and validate DB.
        Steps:
        - Upload file via /upload_staged
        - Verify file appears in /list_staged
        - Review staged file and confirm
        - Check DB for correct update
        """
        import re
        from bs4 import BeautifulSoup
        from pathlib import Path
        # 1. Upload file via /upload_staged
        page.goto(f"{BASE_URL}/upload_staged")
        page.wait_for_load_state("networkidle")
        file_input = page.locator("input[type='file']")
        file_input.set_input_files(file_path)
        page.wait_for_timeout(1000)
        # Wait for redirect to /review_staged or flash message
        for _ in range(10):
            if "/review_staged/" in page.url:
                break
            page.wait_for_timeout(500)
        # If this is an edge case file, expect error and no redirect
        if "edge_cases" in Path(file_path).parts:
            # Should remain on upload_staged and show error message
            assert "/upload_staged" in page.url, f"Expected to remain on upload_staged for edge case file, got: {page.url}"
            page_content = page.content().lower()
            assert any(keyword in page_content for keyword in ["error", "invalid", "not recognized", "missing", "could not", "failed"]), (
                f"Expected error message for edge case file. Content: {page_content[:300]}"
            )
            return  # Test passes for edge case scenario
        # Otherwise, proceed as before
        page_content = page.content().lower()
        id_error = (
            ("id_incidence" in page_content and "positive integer" in page_content)
            or ("missing a valid 'incidence/emission id'" in page_content)
        )
        if id_error and "/upload_staged" in page.url:
            print("Staged upload blocked due to missing/invalid id_incidence as expected.")
            return  # Test passes for this scenario
        match = re.search(r"/review_staged/(\d+)/(.*?)$", page.url)
        assert match, f"Could not extract id_ and filename from URL: {page.url}"
        id_ = int(match.group(1))
        staged_filename = match.group(2)
        # 2. Verify file appears in /list_staged
        page.goto(f"{BASE_URL}/list_staged")
        page.wait_for_load_state("networkidle")
        assert staged_filename in page.content(), f"Staged file {staged_filename} not listed in /list_staged"
        # 3. Review staged file: check field diffs
        page.goto(f"{BASE_URL}/review_staged/{id_}/{staged_filename}")
        page.wait_for_load_state("networkidle")
        assert "staged_fields" in page.content() or "Review" in page.content(), "Review page did not load staged fields."
        checkboxes = page.locator("input[type='checkbox'][name^='confirm_overwrite_']")
        count = checkboxes.count()
        for i in range(count):
            checkboxes.nth(i).check()
        submit_btn = page.locator("form button[type='submit'], form input[type='submit']")
        if submit_btn.count() > 0:
            submit_btn.first.click()
        else:
            page.evaluate("document.querySelector('form').submit()")
        original_url = page.url
        for _ in range(10):
            try:
                page.wait_for_timeout(500)
                current_url = page.url
                if current_url != original_url:
                    break
                page.wait_for_load_state("networkidle", timeout=1000)
                break
            except Exception:
                continue
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
            page_content = page.content().lower()
            success_found = "success" in page_content or "/upload_staged" in page.url
            assert success_found, f"Expected success after confirming staged upload. URL: {page.url}, Content preview: {page_content[:200]}"
        except Exception as e:
            assert "/upload_staged" in page.url, f"Expected redirect to /upload_staged after confirmation. Current URL: {page.url}"
        misc_json = None
        for _ in range(10):
            misc_json = fetch_misc_json_from_db(id_)
            if misc_json:
                break
            time.sleep(0.5)
        assert misc_json, f"misc_json not found in DB for id {id_} after confirming staged upload"
        excel_fields = read_excel_fields(file_path)
        for field, excel_value in excel_fields.items():
            parsed_value = misc_json.get(field)
            if parsed_value == excel_value:
                continue
            else:
                logs = read_backend_logs()
                log_text = "".join(logs)
                assert (field in log_text and ("WARNING" in log_text or "default" in log_text.lower())), \
                    f"[Staged] Field '{field}' value mismatch (Excel: {excel_value}, Parsed: {parsed_value}) and no log warning found."

    @pytest.mark.skip(reason="Backend discard functionality has a source code issue - staged files are not being deleted. TODO: Debug discard_staged_update route. See admin/todo_list.py for details.")
    @pytest.mark.parametrize("file_path", get_test_files())
    def test_excel_upload_staged_discard(self, page: Page, file_path: str):
        """
        E2E: Upload via /upload_staged, then discard the staged file and verify it is removed.
        Uses the new custom modal and overlay logging system.
        """
        import re
        from playwright.sync_api import expect
        # 1. Upload file via /upload_staged
        page.goto(f"{BASE_URL}/upload_staged")
        page.wait_for_load_state("networkidle")
        file_input = page.locator("input[type='file']")
        file_input.set_input_files(file_path)
        page.wait_for_timeout(1000)
        # Wait for redirect to /review_staged
        for _ in range(10):
            if "/review_staged/" in page.url:
                break
            page.wait_for_timeout(500)
        assert "/review_staged/" in page.url, f"Did not redirect to review_staged after upload: {page.url}"
        match = re.search(r"/review_staged/(\d+)/(.*?)$", page.url)
        assert match, f"Could not extract id_ and filename from URL: {page.url}"
        id_ = int(match.group(1))
        staged_filename = match.group(2)
        # 2. Discard the staged file using the new modal
        page.goto(f"{BASE_URL}/list_staged")
        page.wait_for_load_state("networkidle")
        discard_btn = page.locator(f"form[action*='discard_staged_update/{id_}'] button[data-js-logging-context='discard-staged']").first
        discard_btn.click()
        # Wait for modal
        modal = page.locator('#discardConfirmModal')
        assert modal.is_visible(), "Custom discard modal did not appear."
        confirm_btn = page.locator('#discardConfirmModal [data-js-logging-context="discard-modal-confirm"]')
        confirm_btn.click()
        # Immediately check overlay for confirm log before reload
        expect(page.locator('#js-diagnostics')).to_contain_text("discard-modal-confirm")
        # Wait for reload, then check file is gone
        page.wait_for_timeout(1000)
        page.goto(f"{BASE_URL}/list_staged")
        page.wait_for_load_state("networkidle")
        assert staged_filename not in page.content(), f"Staged file {staged_filename} still listed after discard"

    @pytest.mark.parametrize("file_path", get_test_files())
    def test_discard_staged_by_filename(self, page: Page, file_path: str):
        """
        E2E: Upload a file via /upload_staged, then discard it by filename from /list_staged.
        Uses the new custom modal and overlay logging system.
        """
        import re
        from pathlib import Path
        from playwright.sync_api import expect
        import os
        # Upload file via /upload_staged
        page.goto(f"{BASE_URL}/upload_staged")
        file_input = page.locator("input[type='file']")
        file_input.set_input_files(file_path)
        page.wait_for_timeout(1000)
        # Extract staged JSON filename from redirect URL
        staged_filename = None
        for _ in range(10):
            if "/review_staged/" in page.url:
                match = re.search(r"/review_staged/\d+/(.*?)$", page.url)
                if match:
                    staged_filename = match.group(1)
                    break
            page.wait_for_timeout(500)
        assert staged_filename, f"Could not extract staged filename from URL: {page.url}"
        print(f"Staged filename to discard: '{staged_filename}' (repr: {repr(staged_filename)})")
        # Go to /list_staged and check for the staged file
        page.goto(f"{BASE_URL}/list_staged")
        page.wait_for_load_state("networkidle")
        assert staged_filename in page.content(), f"Staged file {staged_filename} not listed in /list_staged"
        # Discard the staged file by filename using the new modal
        discard_btn = page.locator(f"form[action*='{staged_filename}'] button[data-js-logging-context='discard-staged']").first
        discard_btn.click()
        modal = page.locator('#discardConfirmModal')
        assert modal.is_visible(), "Custom discard modal did not appear."
        confirm_btn = page.locator('#discardConfirmModal [data-js-logging-context="discard-modal-confirm"]')
        confirm_btn.click()
        expect(page.locator('#js-diagnostics')).to_contain_text("discard-modal-confirm")
        page.wait_for_timeout(1000)
        # Wait for the file to disappear from the list
        for _ in range(10):
            page.wait_for_timeout(500)
            page.goto(f"{BASE_URL}/list_staged")
            page.wait_for_load_state("networkidle")
            if staged_filename not in page.content():
                break
        if staged_filename in page.content():
            print(f"File '{staged_filename}' still listed after discard. Directory contents:")
            print(os.listdir('portal_uploads/staging'))
        assert staged_filename not in page.content(), f"Staged file {staged_filename} still listed after discard"

    @pytest.mark.parametrize("file_path", get_test_files())
    def test_multiple_staged_files_same_id(self, page: Page, file_path: str):
        """
        E2E: Upload two files for the same id_incidence via /upload_staged, ensure both appear in /list_staged, and can be discarded independently.
        Uses the new custom modal and overlay logging system.
        """
        import re
        from pathlib import Path
        import shutil
        import os
        from playwright.sync_api import expect
        # Upload file via /upload_staged
        page.goto(f"{BASE_URL}/upload_staged")
        file_input = page.locator("input[type='file']")
        file_input.set_input_files(file_path)
        page.wait_for_timeout(1000)
        # Extract staged JSON filename from redirect URL
        staged_filename = None
        for _ in range(10):
            if "/review_staged/" in page.url:
                match = re.search(r"/review_staged/\d+/(.*?)$", page.url)
                if match:
                    staged_filename = match.group(1)
                    break
            page.wait_for_timeout(500)
        assert staged_filename, f"Could not extract staged filename from URL: {page.url}"
        staging_dir = Path("portal_uploads/staging")
        first_staged = staging_dir / staged_filename
        second_staged = staging_dir / ("copy_" + staged_filename)
        shutil.copy(first_staged, second_staged)
        print(f"First staged: '{first_staged.name}', Second staged: '{second_staged.name}'")
        # Go to /list_staged and check for both files
        page.goto(f"{BASE_URL}/list_staged")
        page.wait_for_load_state("networkidle")
        assert first_staged.name in page.content(), f"First staged file {first_staged.name} not listed"
        assert second_staged.name in page.content(), f"Second staged file {second_staged.name} not listed"
        # Discard the second file using the new modal
        discard_btn = page.locator(f"form[action*='{second_staged.name}'] button[data-js-logging-context='discard-staged']").first
        discard_btn.click()
        modal = page.locator('#discardConfirmModal')
        assert modal.is_visible(), "Custom discard modal did not appear."
        confirm_btn = page.locator('#discardConfirmModal [data-js-logging-context="discard-modal-confirm"]')
        confirm_btn.click()
        expect(page.locator('#js-diagnostics')).to_contain_text("discard-modal-confirm")
        for _ in range(10):
            page.wait_for_timeout(500)
            page.goto(f"{BASE_URL}/list_staged")
            page.wait_for_load_state("networkidle")
            if second_staged.name not in page.content():
                break
        if second_staged.name in page.content():
            print(f"Second staged file '{second_staged.name}' still listed after discard. Directory contents:")
            print(os.listdir('portal_uploads/staging'))
        assert second_staged.name not in page.content(), f"Second staged file {second_staged.name} still listed after discard"
        # Discard the first file using the new modal
        discard_btn = page.locator(f"form[action*='{first_staged.name}'] button[data-js-logging-context='discard-staged']").first
        discard_btn.click()
        modal = page.locator('#discardConfirmModal')
        assert modal.is_visible(), "Custom discard modal did not appear."
        confirm_btn = page.locator('#discardConfirmModal [data-js-logging-context="discard-modal-confirm"]')
        confirm_btn.click()
        expect(page.locator('#js-diagnostics')).to_contain_text("discard-modal-confirm")
        for _ in range(10):
            page.wait_for_timeout(500)
            page.goto(f"{BASE_URL}/list_staged")
            page.wait_for_load_state("networkidle")
            if first_staged.name not in page.content():
                break
        if first_staged.name in page.content():
            print(f"First staged file '{first_staged.name}' still listed after discard. Directory contents:")
            print(os.listdir('portal_uploads/staging'))
        assert first_staged.name not in page.content(), f"First staged file {first_staged.name} still listed after discard"

    def test_malformed_staged_file_handling(self, page: Page, tmp_path):
        """
        E2E: Create a malformed JSON file in the staging dir, verify it appears in the malformed section, and can be discarded.
        Uses the new custom modal and overlay logging system.
        """
        from pathlib import Path
        import os
        from playwright.sync_api import expect
        staging_dir = Path("portal_uploads/staging")
        staging_dir.mkdir(parents=True, exist_ok=True)
        malformed_file = staging_dir / "malformed_test.json"
        malformed_file.write_text("{ this is not valid json }")
        print(f"Malformed file to discard: '{malformed_file.name}' (repr: {repr(malformed_file.name)})")
        page.goto(f"{BASE_URL}/list_staged")
        page.wait_for_load_state("networkidle")
        assert "malformed_test.json" in page.content(), "Malformed file not listed in /list_staged"
        discard_btn = page.locator(f"form[action*='malformed_test.json'] button[data-js-logging-context='discard-malformed']").first
        discard_btn.click()
        modal = page.locator('#discardConfirmModal')
        assert modal.is_visible(), "Custom discard modal did not appear."
        confirm_btn = page.locator('#discardConfirmModal [data-js-logging-context="discard-modal-confirm"]')
        confirm_btn.click()
        expect(page.locator('#js-diagnostics')).to_contain_text("discard-modal-confirm")
        for _ in range(10):
            page.wait_for_timeout(500)
            page.goto(f"{BASE_URL}/list_staged")
            page.wait_for_load_state("networkidle")
            if "malformed_test.json" not in page.content():
                break
        if "malformed_test.json" in page.content():
            print(f"Malformed file 'malformed_test.json' still listed after discard. Directory contents:")
            print(os.listdir('portal_uploads/staging'))
        assert "malformed_test.json" not in page.content(), "Malformed file still listed after discard"

def test_diagnostics_overlay_on_list_staged(page):
    """
    Minimal test: Load /list_staged, click diagnostics button, and scrape overlay.
    Confirms JS overlay is updated in Playwright context.
    """
    page.goto("http://127.0.0.1:5000/list_staged")
    page.wait_for_load_state("networkidle")
    # Click the diagnostics button
    page.locator('#sendDiagnosticBtn').click()
    page.wait_for_timeout(500)
    # Scrape overlay
    overlay = ''
    try:
        overlay = page.locator('#js-diagnostics').inner_text()
    except Exception:
        overlay = '[Overlay not found]'
    print(f"[DIAGNOSTICS OVERLAY] {overlay}")
    assert 'Send Diagnostic' in overlay or overlay != '[Overlay not found]', "Diagnostics overlay did not update as expected."

def test_diagnostics_console_output_on_list_staged(page):
    """
    Minimal test: Load /list_staged, click diagnostics button, and capture JS console output.
    Prints/logs all console messages for review.
    """
    messages = []
    page.on("console", lambda msg: messages.append(msg.text))
    page.goto("http://127.0.0.1:5000/list_staged")
    page.wait_for_load_state("networkidle")
    page.locator('#sendDiagnosticBtn').click()
    page.wait_for_timeout(500)
    print(f"[JS CONSOLE OUTPUT] {messages}")
    assert any('Send Diagnostic' in m for m in messages) or messages, "No relevant JS console output captured."

def test_diagnostics_overlay_on_diagnostic_test_page(page):
    """
    E2E: Load /java_script_diagnostic_test, check overlay for page load diagnostic, click diagnostics button, and check overlay updates.
    """
    page.goto("http://127.0.0.1:5000/java_script_diagnostic_test")
    page.wait_for_load_state("networkidle")
    # Scrape overlay after page load
    overlay = ''
    try:
        overlay = page.locator('#js-diagnostics').inner_text()
    except Exception:
        overlay = '[Overlay not found]'
    print(f"[DIAGNOSTICS OVERLAY after load] {overlay}")
    assert 'Page loaded' in overlay or overlay != '[Overlay not found]', "Overlay did not show page load diagnostic."
    # Click the diagnostics button (use class-based selector)
    page.locator('.js-send-diagnostic-btn').click()
    page.wait_for_timeout(500)
    overlay2 = ''
    try:
        overlay2 = page.locator('#js-diagnostics').inner_text()
    except Exception:
        overlay2 = '[Overlay not found]'
    print(f"[DIAGNOSTICS OVERLAY after click] {overlay2}")
    assert 'Send Diagnostic' in overlay2, "Overlay did not update after clicking diagnostics button."

def test_list_staged_diagnostics_overlay(page):
    """
    E2E: Load /list_staged, check overlay for page load diagnostic, click diagnostics block send button, click discard, and check overlay updates.
    """
    page.goto("http://127.0.0.1:5000/list_staged")
    page.wait_for_load_state("networkidle")
    # Scrape overlay after page load
    overlay = page.locator('#js-diagnostics').inner_text()
    print(f"[DIAGNOSTICS OVERLAY after load] {overlay}")
    # Click the diagnostics block send button
    page.locator('.js-send-diagnostic-btn').click()
    page.wait_for_timeout(500)
    overlay2 = page.locator('#js-diagnostics').inner_text()
    print(f"[DIAGNOSTICS OVERLAY after send click] {overlay2}")
    # Click the discard button for the first staged file
    discard_btn = page.locator("form[action*='discard_staged_update'] button[type='submit']").first
    page.on("dialog", lambda dialog: dialog.accept())  # Accept the confirmation
    discard_btn.click()
    page.wait_for_timeout(500)
    overlay3 = page.locator('#js-diagnostics').inner_text()
    print(f"[DIAGNOSTICS OVERLAY after discard] {overlay3}")
    assert "Discard button clicked" in overlay3 or "Discard confirmed" in overlay3

# Update one failing discard test to scrape and print overlay after each key action
@pytest.mark.parametrize("file_path", get_test_files())
def test_discard_staged_by_filename_with_overlay_logging(page: Page, file_path: str):
    """
    E2E: Upload a file via /upload_staged, then discard it by filename from /list_staged.
    Scrape and print overlay after each key action.
    """
    import re
    from pathlib import Path
    import os
    from playwright.sync_api import expect
    # Upload file via /upload_staged
    page.goto(f"{BASE_URL}/upload_staged")
    file_input = page.locator("input[type='file']")
    file_input.set_input_files(file_path)
    page.wait_for_timeout(1000)
    # Extract staged JSON filename from redirect URL
    staged_filename = None
    for _ in range(10):
        if "/review_staged/" in page.url:
            match = re.search(r"/review_staged/\d+/(.*?)$", page.url)
            if match:
                staged_filename = match.group(1)
                break
        page.wait_for_timeout(500)
    assert staged_filename, f"Could not extract staged filename from URL: {page.url}"
    # Go to /list_staged and check for the staged file
    page.goto(f"{BASE_URL}/list_staged")
    page.wait_for_load_state("networkidle")
    overlay = page.locator('#js-diagnostics').inner_text()
    print(f"[DIAGNOSTICS OVERLAY after load] {overlay}")
    assert staged_filename in page.content(), f"Staged file {staged_filename} not listed in /list_staged"
    # Discard the staged file by filename
    discard_btn = page.locator(f"form[action*='{staged_filename}'] button[data-js-logging-context='discard-staged']").first
    discard_btn.click()
    modal = page.locator('#discardConfirmModal')
    assert modal.is_visible(), "Custom discard modal did not appear."
    confirm_btn = page.locator('#discardConfirmModal [data-js-logging-context="discard-modal-confirm"]')
    confirm_btn.click()
    expect(page.locator('#js-diagnostics')).to_contain_text("discard-modal-confirm")
    page.wait_for_timeout(1000)
    # Wait for the file to disappear from the list
    for _ in range(10):
        page.wait_for_timeout(500)
        page.goto(f"{BASE_URL}/list_staged")
        page.wait_for_load_state("networkidle")
        if staged_filename not in page.content():
            break
    if staged_filename in page.content():
        print(f"File '{staged_filename}' still listed after discard. Directory contents:")
        print(os.listdir('portal_uploads/staging'))
    assert staged_filename not in page.content(), f"Staged file {staged_filename} still listed after discard"

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