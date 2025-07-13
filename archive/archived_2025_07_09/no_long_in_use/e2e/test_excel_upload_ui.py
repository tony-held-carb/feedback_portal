"""
E2E UI Automation Tests for Excel Upload Portal

This module provides comprehensive end-to-end testing of the Excel upload UI
using Selenium WebDriver. Tests cover the complete user workflow from
navigating to the upload page through successful file submission.

Requirements:
- Flask app running at http://127.0.0.1:5000
- Chrome browser installed
- Selenium and webdriver-manager packages installed

Test Coverage:
- Basic upload functionality
- File validation and error handling
- Success/failure message verification
- Form submission workflow
- Multiple file types and scenarios
"""

import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExcelUploadE2ETest:
  """End-to-end test suite for Excel upload functionality."""
  
  def __init__(self, base_url: str = "http://127.0.0.1:5000"):
    """Initialize the E2E test suite.
    
    Args:
      base_url: Base URL of the Flask application
    """
    self.base_url = base_url
    self.driver = None
    self.wait = None
    self.test_files_dir = Path("feedback_forms/testing_versions")
    self.generated_files_dir = Path("feedback_forms/testing_versions/generated")
    
  def setup_driver(self):
    """Set up Chrome WebDriver with appropriate options."""
    try:
      chrome_options = Options()
      # Add options for better automation
      chrome_options.add_argument("--no-sandbox")
      chrome_options.add_argument("--disable-dev-shm-usage")
      chrome_options.add_argument("--disable-gpu")
      chrome_options.add_argument("--window-size=1920,1080")
      
      # Use webdriver-manager to automatically download and manage ChromeDriver
      service = Service(ChromeDriverManager().install())
      
      self.driver = webdriver.Chrome(service=service, options=chrome_options)
      self.wait = WebDriverWait(self.driver, 10)
      
      logger.info("Chrome WebDriver initialized successfully")
      
    except Exception as e:
      logger.error(f"Failed to initialize WebDriver: {e}")
      raise
  
  def teardown_driver(self):
    """Clean up WebDriver resources."""
    if self.driver:
      self.driver.quit()
      logger.info("WebDriver closed")
  
  def navigate_to_upload_page(self) -> bool:
    """Navigate to the upload page and verify it loads correctly.
    
    Returns:
      True if navigation successful, False otherwise
    """
    try:
      upload_url = f"{self.base_url}/upload"
      logger.info(f"Navigating to upload page: {upload_url}")
      
      if self.driver is None:
        logger.error("WebDriver not initialized")
        return False
      
      self.driver.get(upload_url)
      
      # Wait for page to load and verify key elements
      if self.wait is None:
        logger.error("WebDriverWait not initialized")
        return False
      
      self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
      
      # Check for common upload form elements
      page_title = self.driver.title
      logger.info(f"Page title: {page_title}")
      
      # Look for file input element
      file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
      logger.info("File input element found")
      
      return True
      
    except TimeoutException:
      logger.error("Timeout waiting for upload page to load")
      return False
    except NoSuchElementException:
      logger.error("Required upload form elements not found")
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
      if self.driver is None:
        logger.error("WebDriver not initialized")
        return False
      
      # Find file input element
      file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
      
      # Convert to absolute path
      abs_file_path = os.path.abspath(file_path)
      logger.info(f"Uploading file: {abs_file_path}")
      
      # Send file path to input element
      file_input.send_keys(abs_file_path)
      
      # Wait a moment for file to be processed
      time.sleep(1)
      
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
      if self.driver is None:
        logger.error("WebDriver not initialized")
        return False
      
      # The upload form auto-submits when a file is selected
      # Wait for the page to change (redirect or form submission)
      logger.info("Waiting for automatic form submission...")
      
      # Wait up to 10 seconds for page to change
      original_url = self.driver.current_url
      original_title = self.driver.title
      
      # Wait for either URL change or page content change
      max_wait = 10
      start_time = time.time()
      
      while time.time() - start_time < max_wait:
        current_url = self.driver.current_url
        current_title = self.driver.title
        
        # Check if page has changed
        if current_url != original_url or current_title != original_title:
          logger.info(f"Page changed - URL: {current_url}, Title: {current_title}")
          return True
        
        # Check if we're on a different page (like the review page)
        page_source = self.driver.page_source.lower()
        if any(indicator in page_source for indicator in ['review', 'update', 'incidence', 'feedback']):
          logger.info("Detected redirect to review/update page")
          return True
        
        time.sleep(0.5)
      
      # If we're still on the same page, check if there's a success/error message
      page_source = self.driver.page_source.lower()
      if any(indicator in page_source for indicator in ['success', 'uploaded', 'processed', 'error', 'invalid']):
        logger.info("Found success/error message on upload page")
        return True
      
      logger.warning("No page change detected after file upload")
      return False
        
    except Exception as e:
      logger.error(f"Error during form submission: {e}")
      return False
  
  def check_success_message(self) -> bool:
    """Check for success message after form submission.
    
    Returns:
      True if success message found, False otherwise
    """
    try:
      # Wait for page to update after submission
      time.sleep(2)
      
      # Look for success indicators
      success_indicators = [
        "success",
        "uploaded",
        "processed",
        "thank you",
        "completed"
      ]
      
      page_text = self.driver.page_source.lower()
      
      for indicator in success_indicators:
        if indicator in page_text:
          logger.info(f"Success indicator found: '{indicator}'")
          return True
      
      # Check for common success message elements
      success_selectors = [
        ".success",
        ".alert-success",
        ".message-success",
        "#success-message"
      ]
      
      for selector in success_selectors:
        try:
          element = self.driver.find_element(By.CSS_SELECTOR, selector)
          if element.is_displayed():
            logger.info(f"Success message element found: {element.text}")
            return True
        except NoSuchElementException:
          continue
      
      logger.warning("No clear success message found")
      return False
      
    except Exception as e:
      logger.error(f"Error checking success message: {e}")
      return False
  
  def check_error_message(self) -> bool:
    """Check for error message after form submission.
    
    Returns:
      True if error message found, False otherwise
    """
    try:
      # Wait for page to update after submission
      time.sleep(2)
      
      # Look for error indicators
      error_indicators = [
        "error",
        "invalid",
        "failed",
        "not allowed",
        "unsupported"
      ]
      
      page_text = self.driver.page_source.lower()
      
      for indicator in error_indicators:
        if indicator in page_text:
          logger.info(f"Error indicator found: '{indicator}'")
          return True
      
      # Check for common error message elements
      error_selectors = [
        ".error",
        ".alert-danger",
        ".message-error",
        "#error-message"
      ]
      
      for selector in error_selectors:
        try:
          element = self.driver.find_element(By.CSS_SELECTOR, selector)
          if element.is_displayed():
            logger.info(f"Error message element found: {element.text}")
            return True
        except NoSuchElementException:
          continue
      
      return False
      
    except Exception as e:
      logger.error(f"Error checking error message: {e}")
      return False
  
  def get_available_test_files(self) -> List[str]:
    """Get list of available test files for upload testing.
    
    Returns:
      List of file paths to test files
    """
    test_files = []
    
    # Check both regular test files and generated files
    for test_dir in [self.test_files_dir, self.generated_files_dir]:
      if test_dir.exists():
        for file_path in test_dir.glob("*.xlsx"):
          test_files.append(str(file_path))
    
    logger.info(f"Found {len(test_files)} test files")
    return test_files
  
  def run_basic_upload_test(self, file_path: str) -> Dict[str, Any]:
    """Run a basic upload test for a single file.
    
    Args:
      file_path: Path to the file to test
      
    Returns:
      Dictionary with test results
    """
    result = {
      'file': file_path,
      'navigation_success': False,
      'upload_success': False,
      'submission_success': False,
      'success_message': False,
      'error_message': False,
      'overall_success': False,
      'error_details': []
    }
    
    try:
      # Step 1: Navigate to upload page
      if not self.navigate_to_upload_page():
        result['error_details'].append("Failed to navigate to upload page")
        return result
      result['navigation_success'] = True
      
      # Step 2: Upload file
      if not self.upload_file(file_path):
        result['error_details'].append("Failed to upload file")
        return result
      result['upload_success'] = True
      
      # Step 3: Submit form
      if not self.submit_form():
        result['error_details'].append("Failed to submit form")
        return result
      result['submission_success'] = True
      
      # Step 4: Check for success/error messages
      result['success_message'] = self.check_success_message()
      result['error_message'] = self.check_error_message()
      
      # Determine overall success
      result['overall_success'] = (
        result['navigation_success'] and
        result['upload_success'] and
        result['submission_success'] and
        (result['success_message'] or not result['error_message'])
      )
      
    except Exception as e:
      result['error_details'].append(f"Unexpected error: {e}")
      logger.error(f"Error in basic upload test: {e}")
    
    return result
  
  def run_comprehensive_test_suite(self) -> Dict[str, Any]:
    """Run comprehensive E2E test suite across all available test files.
    
    Returns:
      Dictionary with comprehensive test results
    """
    logger.info("Starting comprehensive E2E test suite")
    
    # Setup WebDriver
    self.setup_driver()
    
    try:
      # Get available test files
      test_files = self.get_available_test_files()
      
      if not test_files:
        logger.warning("No test files found")
        return {'error': 'No test files available'}
      
      # Run tests for each file
      results = []
      for file_path in test_files[:5]:  # Limit to first 5 files for initial run
        logger.info(f"Testing file: {file_path}")
        result = self.run_basic_upload_test(file_path)
        results.append(result)
        
        # Brief pause between tests
        time.sleep(1)
      
      # Compile summary
      summary = {
        'total_files_tested': len(results),
        'successful_uploads': sum(1 for r in results if r['overall_success']),
        'failed_uploads': sum(1 for r in results if not r['overall_success']),
        'navigation_issues': sum(1 for r in results if not r['navigation_success']),
        'upload_issues': sum(1 for r in results if not r['upload_success']),
        'submission_issues': sum(1 for r in results if not r['submission_success']),
        'detailed_results': results
      }
      
      logger.info(f"Test suite completed. Summary: {summary}")
      return summary
      
    finally:
      self.teardown_driver()
  
  def run_single_file_test(self, file_path: str) -> Dict[str, Any]:
    """Run E2E test for a single file.
    
    Args:
      file_path: Path to the file to test
      
    Returns:
      Dictionary with test results
    """
    logger.info(f"Running single file E2E test: {file_path}")
    
    # Setup WebDriver
    self.setup_driver()
    
    try:
      result = self.run_basic_upload_test(file_path)
      logger.info(f"Single file test completed: {result}")
      return result
      
    finally:
      self.teardown_driver()


def main():
  """Main function to run E2E tests."""
  logger.info("Starting Excel Upload E2E Tests")
  
  # Create test instance
  e2e_test = ExcelUploadE2ETest()
  
  # Run comprehensive test suite
  results = e2e_test.run_comprehensive_test_suite()
  
  # Print summary
  print("\n" + "="*50)
  print("E2E TEST RESULTS SUMMARY")
  print("="*50)
  print(f"Total files tested: {results.get('total_files_tested', 0)}")
  print(f"Successful uploads: {results.get('successful_uploads', 0)}")
  print(f"Failed uploads: {results.get('failed_uploads', 0)}")
  print(f"Navigation issues: {results.get('navigation_issues', 0)}")
  print(f"Upload issues: {results.get('upload_issues', 0)}")
  print(f"Submission issues: {results.get('submission_issues', 0)}")
  print("="*50)
  
  # Print detailed results
  if 'detailed_results' in results:
    print("\nDETAILED RESULTS:")
    for i, result in enumerate(results['detailed_results'], 1):
      print(f"\n{i}. File: {result['file']}")
      print(f"   Overall Success: {result['overall_success']}")
      print(f"   Navigation: {result['navigation_success']}")
      print(f"   Upload: {result['upload_success']}")
      print(f"   Submission: {result['submission_success']}")
      print(f"   Success Message: {result['success_message']}")
      print(f"   Error Message: {result['error_message']}")
      if result['error_details']:
        print(f"   Errors: {result['error_details']}")


if __name__ == "__main__":
  main() 