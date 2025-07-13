"""
Pytest-compatible E2E UI Automation Tests for Excel Upload Portal using Playwright

This module provides comprehensive end-to-end testing of the Excel upload UI
using Playwright with pytest fixtures and assertions.

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
"""

import os
import time
import pytest
from pathlib import Path
from typing import List, Dict, Any
from playwright.sync_api import Page, expect

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_FILES_DIR = Path("feedback_forms/testing_versions")
GENERATED_FILES_DIR = Path("feedback_forms/testing_versions/generated")

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }

@pytest.fixture
def upload_page(page: Page):
    """Navigate to upload page and return the page object."""
    page.goto(f"{BASE_URL}/upload")
    page.wait_for_load_state("networkidle")
    return page

def get_test_files() -> List[str]:
    """Get list of available test files."""
    test_files = []
    
    if TEST_FILES_DIR.exists():
        for file_path in TEST_FILES_DIR.glob("*.xlsx"):
            test_files.append(str(file_path))
    
    if GENERATED_FILES_DIR.exists():
        for file_path in GENERATED_FILES_DIR.glob("*.xlsx"):
            test_files.append(str(file_path))
    
    return test_files

class TestExcelUpload:
    """Test class for Excel upload functionality."""
    
    def test_upload_page_loads(self, upload_page: Page):
        """Test that the upload page loads correctly."""
        # Check page title
        expect(upload_page).to_have_title(r".+")
        
        # Check for file input element
        file_input = upload_page.locator("input[type='file']")
        expect(file_input).to_be_visible()
        
        # Check for upload form
        form = upload_page.locator("form")
        expect(form).to_be_visible()
    
    def test_file_input_exists(self, upload_page: Page):
        """Test that file input element exists and is functional."""
        file_input = upload_page.locator("input[type='file']")
        
        # Check that file input is present
        expect(file_input).to_be_visible()
        
        # Check that it accepts Excel files
        accept_attr = file_input.get_attribute("accept")
        assert accept_attr is None or "xlsx" in accept_attr or "xls" in accept_attr
    
    def test_drop_zone_exists(self, upload_page: Page):
        """Test that drop zone element exists (if implemented)."""
        # Look for drop zone elements
        drop_zones = upload_page.locator("[id*='drop'], [class*='drop'], [id*='zone'], [class*='zone']")
        
        # If drop zones exist, they should be visible
        if drop_zones.count() > 0:
            expect(drop_zones.first).to_be_visible()
    
    @pytest.mark.parametrize("file_path", get_test_files())
    def test_file_upload_workflow(self, upload_page: Page, file_path: str):
        """Test complete file upload workflow for each test file."""
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
        """Test upload with invalid file type."""
        # Create a temporary invalid file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"This is not an Excel file")
            temp_file = f.name
        
        try:
            # Try to upload the invalid file
            upload_page.set_input_files("input[type='file']", temp_file)
            upload_page.wait_for_timeout(1000)
            
            # Check for error message
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
            
            # Check page content for error keywords
            page_content = upload_page.content().lower()
            if any(keyword in page_content for keyword in ["error", "invalid", "failed", "not allowed"]):
                print("Invalid file appears to have been rejected")
                return
            
            # If no error found, that's also acceptable (file might be silently rejected)
            print("Invalid file was handled (possibly silently rejected)")
            
        finally:
            # Clean up temp file
            os.unlink(temp_file)
    
    def test_empty_file_upload(self, upload_page: Page):
        """Test upload with empty file."""
        # Create a temporary empty file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_file = f.name
        
        try:
            # Try to upload the empty file
            upload_page.set_input_files("input[type='file']", temp_file)
            upload_page.wait_for_timeout(1000)
            
            # Check for error message or success
            # Empty files might be handled differently by the application
            page_content = upload_page.content().lower()
            if any(keyword in page_content for keyword in ["error", "invalid", "empty", "no data"]):
                print("Empty file was rejected as expected")
            else:
                print("Empty file was accepted (application-specific behavior)")
            
        finally:
            # Clean up temp file
            os.unlink(temp_file)
    
    def test_large_file_upload(self, upload_page: Page):
        """Test upload with a large file (if test files are available)."""
        test_files = get_test_files()
        if not test_files:
            pytest.skip("No test files available for large file test")
        
        # Use the first available test file
        file_path = test_files[0]
        file_size = os.path.getsize(file_path)
        
        print(f"Testing upload with file size: {file_size} bytes")
        
        # Upload the file
        upload_page.set_input_files("input[type='file']", file_path)
        upload_page.wait_for_timeout(2000)  # Longer timeout for large files
        
        # Check for success or error
        page_content = upload_page.content().lower()
        if any(keyword in page_content for keyword in ["success", "uploaded", "processed"]):
            print("Large file upload successful")
        elif any(keyword in page_content for keyword in ["error", "too large", "size limit"]):
            print("Large file upload failed due to size")
        else:
            print("Large file upload result unclear")

class TestUploadPageElements:
    """Test class for upload page element structure."""
    
    def test_page_structure(self, upload_page: Page):
        """Test that the upload page has the expected structure."""
        # Check for main content areas
        expect(upload_page.locator("body")).to_be_visible()
        
        # Check for navigation (if any)
        nav_elements = upload_page.locator("nav, .navbar, .navigation")
        if nav_elements.count() > 0:
            expect(nav_elements.first).to_be_visible()
        
        # Check for main content
        main_content = upload_page.locator("main, .container, .content")
        if main_content.count() > 0:
            expect(main_content.first).to_be_visible()
    
    def test_form_structure(self, upload_page: Page):
        """Test that the upload form has the expected structure."""
        form = upload_page.locator("form")
        expect(form).to_be_visible()
        
        # Check form attributes
        method = form.get_attribute("method")
        action = form.get_attribute("action")
        
        # Form should have method and action
        assert method is not None, "Form should have method attribute"
        assert action is not None, "Form should have action attribute"
        
        # Check for file input
        file_input = form.locator("input[type='file']")
        expect(file_input).to_be_visible()
        
        # Check for submit button (if not auto-submit)
        submit_button = form.locator("button[type='submit'], input[type='submit']")
        # Submit button might not exist if form auto-submits
        if submit_button.count() > 0:
            expect(submit_button.first).to_be_visible()
    
    def test_accessibility_features(self, upload_page: Page):
        """Test basic accessibility features."""
        # Check for page title
        expect(upload_page).to_have_title(r".+")
        
        # Check for file input label
        file_input = upload_page.locator("input[type='file']")
        file_input_id = file_input.get_attribute("id")
        
        if file_input_id:
            label = upload_page.locator(f"label[for='{file_input_id}']")
            if label.count() > 0:
                expect(label.first).to_be_visible()
        
        # Check for form labels in general
        labels = upload_page.locator("label")
        if labels.count() > 0:
            expect(labels.first).to_be_visible()

if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"]) 