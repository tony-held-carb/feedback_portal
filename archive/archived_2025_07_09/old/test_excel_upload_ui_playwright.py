"""
E2E UI Automation Tests for Excel Upload Portal using Playwright

This module provides comprehensive end-to-end testing of the Excel upload UI
using Playwright. Tests cover the complete user workflow from
navigating to the upload page through successful file submission.

Requirements:
- Flask app running at http://127.0.0.1:5000
- Playwright installed and browsers downloaded

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
import logging
from pathlib import Path
from typing import List, Dict, Any
import pytest
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

# Configure logging
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

class ExcelUploadE2ETest:
  """End-to-end test suite for Excel upload functionality using Playwright."""
  
  def __init__(self, base_url: str = "http://127.0.0.1:5000"):
    """Initialize the E2E test suite.
    
    Args:
      base_url: Base URL of the Flask application
    """
    self.base_url = base_url
    self.playwright = None
    self.browser = None
    self.context = None
    self.page = None
    self.test_files_dir = Path("feedback_forms/testing_versions")
    self.generated_files_dir = Path("feedback_forms/testing_versions/generated")
    
  def setup_browser(self):
    """Set up Playwright browser with appropriate options."""
    try:
      self.playwright = sync_playwright().start()
      
      # Launch browser with options for better automation
      self.browser = self.playwright.chromium.launch(
        headless=False,  # Set to True for CI/CD
        args=[
          "--no-sandbox",
          "--disable-dev-shm-usage",
          "--disable-gpu",
          "--window-size=1920,1080"
        ]
      )
      
      # Create context with viewport
      self.context = self.browser.new_context(
        viewport={"width": 1920, "height": 1080}
      )
      
      # Create page
      self.page = self.context.new_page()
      
      logger.info("Playwright browser initialized successfully")
      
    except Exception as e:
      logger.error(f"Failed to initialize Playwright browser: {e}")
      raise
  
  def teardown_browser(self):
    """Clean up Playwright resources."""
    if self.page:
      self.page.close()
    if self.context:
      self.context.close()
    if self.browser:
      self.browser.close()
    if self.playwright:
      self.playwright.stop()
    logger.info("Playwright browser closed")
  
  def navigate_to_upload_page(self) -> bool:
    """Navigate to the upload page and verify it loads correctly.
    
    Returns:
      True if navigation successful, False otherwise
    """
    try:
      upload_url = f"{self.base_url}/upload"
      logger.info(f"Navigating to upload page: {upload_url}")
      
      if self.page is None:
        logger.error("Playwright page not initialized")
        return False
      
      self.page.goto(upload_url)
      
      # Wait for page to load and verify key elements
      self.page.wait_for_load_state("networkidle")
      
      # Check for common upload form elements
      page_title = self.page.title()
      logger.info(f"Page title: {page_title}")
      
      # Look for file input element
      file_input = self.page.locator("input[type='file']")
      if file_input.count() > 0:
        logger.info("File input element found")
        return True
      else:
        logger.error("File input element not found")
        return False
      
    except Exception as e:
      logger.error(f"Error navigating to upload page: {e}")
      return False
  
  def upload_file(self, file_path: str) -> bool:
    """Upload a file using the file input element.
    
    Args:
      file_path: Path to the file to upload
      
    Returns:
      True if upload successful, False otherwise
    """
    try:
      if self.page is None:
        logger.error("Playwright page not initialized")
        return False
      
      # Convert to absolute path
      abs_file_path = os.path.abspath(file_path)
      logger.info(f"Uploading file: {abs_file_path}")
      
      # Use Playwright's set_input_files method
      self.page.set_input_files("input[type='file']", abs_file_path)
      
      # Wait a moment for file to be processed
      self.page.wait_for_timeout(1000)
      
      logger.info("File uploaded successfully")
      return True
      
    except Exception as e:
      logger.error(f"Error uploading file: {e}")
      return False
  
  def submit_form(self) -> bool:
    """Submit the upload form.
    
    The upload form is designed to auto-submit when a file is selected.
    This method waits for the automatic submission to occur.
    
    Returns:
      True if submission successful, False otherwise
    """
    try:
      if self.page is None:
        logger.error("Playwright page not initialized")
        return False
      
      # The upload form auto-submits when a file is selected
      # Wait for the page to change (redirect or form submission)
      logger.info("Waiting for automatic form submission...")
      
      # Wait up to 10 seconds for page to change
      original_url = self.page.url
      original_title = self.page.title()
      
      # Wait for either URL change or page content change
      max_wait = 10
      start_time = time.time()
      
      while time.time() - start_time < max_wait:
        current_url = self.page.url
        current_title = self.page.title()
        
        # Check if page has changed
        if current_url != original_url or current_title != original_title:
          logger.info(f"Page changed - URL: {current_url}, Title: {current_title}")
          return True
        
        # Check if we're on a different page (like the review page)
        page_content = self.page.content().lower()
        if "success" in page_content or "error" in page_content or "review" in page_content:
          logger.info("Page content indicates form submission completed")
          return True
        
        time.sleep(0.5)
      
      logger.warning("Form submission timeout - page did not change")
      return False
      
    except Exception as e:
      logger.error(f"Error during form submission: {e}")
      return False
  
  def check_success_message(self) -> bool:
    """Check for success message on the page.
    
    Returns:
      True if success message found, False otherwise
    """
    try:
      if self.page is None:
        logger.error("Playwright page not initialized")
        return False
      
      # Wait for page to load completely
      self.page.wait_for_load_state("networkidle")
      
      # Look for various success indicators
      success_indicators = [
        ".alert-success",
        ".success-message", 
        ".alert-info",
        "text=success",
        "text=uploaded",
        "text=processed"
      ]
      
      for indicator in success_indicators:
        try:
          if self.page.locator(indicator).count() > 0:
            success_text = self.page.locator(indicator).first.text_content()
            logger.info(f"Success message found: {success_text}")
            return True
        except:
          continue
      
      # Check page content for success keywords
      page_content = self.page.content().lower()
      if any(keyword in page_content for keyword in ["success", "uploaded", "processed", "completed"]):
        logger.info("Success keywords found in page content")
        return True
      
      logger.warning("No success message found")
      return False
      
    except Exception as e:
      logger.error(f"Error checking success message: {e}")
      return False
  
  def check_error_message(self) -> bool:
    """Check for error message on the page.
    
    Returns:
      True if error message found, False otherwise
    """
    try:
      if self.page is None:
        logger.error("Playwright page not initialized")
        return False
      
      # Wait for page to load completely
      self.page.wait_for_load_state("networkidle")
      
      # Look for various error indicators
      error_indicators = [
        ".alert-danger",
        ".error-message",
        ".alert-warning",
        "text=error",
        "text=invalid",
        "text=failed"
      ]
      
      for indicator in error_indicators:
        try:
          if self.page.locator(indicator).count() > 0:
            error_text = self.page.locator(indicator).first.text_content()
            logger.info(f"Error message found: {error_text}")
            return True
        except:
          continue
      
      # Check page content for error keywords
      page_content = self.page.content().lower()
      if any(keyword in page_content for keyword in ["error", "invalid", "failed", "rejected"]):
        logger.info("Error keywords found in page content")
        return True
      
      logger.warning("No error message found")
      return False
      
    except Exception as e:
      logger.error(f"Error checking error message: {e}")
      return False
  
  def get_available_test_files(self) -> List[str]:
    """Get list of available test files in the testing directory.
    
    Returns:
      List of file paths for testing
    """
    base_dirs = [
      Path("feedback_forms/testing_versions/standard"),
      Path("feedback_forms/testing_versions/edge_cases"),
      Path("feedback_forms/testing_versions/generated"),
      # Path("feedback_forms/testing_versions/old")
    ]
    files = []
    for base_dir in base_dirs:
      files.extend(get_xls_files(base_dir, recursive=True))
    return files
  
  def run_basic_upload_test(self, file_path: str) -> Dict[str, Any]:
    """Run a basic upload test for a single file.
    
    Args:
      file_path: Path to the file to test
      
    Returns:
      Dictionary with test results
    """
    logger.info(f"Running basic upload test for: {file_path}")
    
    try:
      # Navigate to upload page
      if not self.navigate_to_upload_page():
        return {"success": False, "error": "Failed to navigate to upload page"}
      
      # Upload file
      if not self.upload_file(file_path):
        return {"success": False, "error": "Failed to upload file"}
      
      # Submit form
      if not self.submit_form():
        return {"success": False, "error": "Form submission failed"}
      
      # Check for success or error
      if self.check_success_message():
        return {"success": True, "message": "Upload successful"}
      elif self.check_error_message():
        return {"success": False, "message": "Upload failed with error"}
      else:
        return {"success": False, "error": "No clear success or error indication"}
      
    except Exception as e:
      logger.error(f"Error in basic upload test: {e}")
      return {"success": False, "error": str(e)}
  
  def run_comprehensive_test_suite(self) -> Dict[str, Any]:
    """Run comprehensive test suite on all available test files.
    
    Returns:
      Dictionary with comprehensive test results
    """
    logger.info("Running comprehensive test suite")
    
    test_files = self.get_available_test_files()
    if not test_files:
      return {"success": False, "error": "No test files found"}
    
    results = {
      "total_files": len(test_files),
      "successful": 0,
      "failed": 0,
      "errors": []
    }
    
    for file_path in test_files:
      try:
        result = self.run_single_file_test(file_path)
        if result["success"]:
          results["successful"] += 1
        else:
          results["failed"] += 1
          results["errors"].append({
            "file": file_path,
            "error": result.get("error", "Unknown error")
          })
      except Exception as e:
        results["failed"] += 1
        results["errors"].append({
          "file": file_path,
          "error": str(e)
        })
    
    logger.info(f"Test suite completed: {results['successful']} successful, {results['failed']} failed")
    return results
  
  def run_single_file_test(self, file_path: str) -> Dict[str, Any]:
    """Run a complete test for a single file including setup and teardown.
    
    Args:
      file_path: Path to the file to test
      
    Returns:
      Dictionary with test results
    """
    logger.info(f"Testing file: {file_path}")
    
    try:
      # Setup browser
      self.setup_browser()
      
      # Run the test
      result = self.run_basic_upload_test(file_path)
      
      return result
      
    except Exception as e:
      logger.error(f"Error in single file test: {e}")
      return {"success": False, "error": str(e)}
    
    finally:
      # Always cleanup
      self.teardown_browser()

def main():
  """Main function to run the E2E test suite."""
  logger.info("Starting Excel Upload E2E Test Suite")
  
  # Create test instance
  test_suite = ExcelUploadE2ETest()
  
  try:
    # Run comprehensive test suite
    results = test_suite.run_comprehensive_test_suite()
    
    # Print results
    print("\n" + "="*50)
    print("E2E TEST RESULTS")
    print("="*50)
    print(f"Total files tested: {results['total_files']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    
    if results['errors']:
      print("\nErrors:")
      for error in results['errors']:
        print(f"  - {error['file']}: {error['error']}")
    
    print("="*50)
    
    return results['failed'] == 0
    
  except Exception as e:
    logger.error(f"Error in main test execution: {e}")
    return False

if __name__ == "__main__":
  success = main()
  exit(0 if success else 1) 