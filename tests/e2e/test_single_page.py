"""
Playwright Upload Page Diagnostics Script
========================================

This script is designed to help both beginners and advanced users debug and inspect the HTML structure of a web application's upload page using Playwright (Python).

Purpose:
--------
- Quickly identify the correct selectors for form elements (buttons, inputs, file uploads, drop zones, etc.) on a single web page.
- Print detailed information about each relevant element to the console for easy inspection.
- Save a screenshot of the page for visual reference.
- Output the first 2000 characters of the page source for manual review.

Typical Use Cases:
------------------
- When writing or debugging Playwright end-to-end tests and you need to determine the best selectors for interacting with page elements.
- When the upload page changes and you want to quickly see what elements are present and how they are structured.
- When onboarding new developers or QA engineers to the project, to help them understand the upload page's DOM structure.

Prerequisites:
--------------
- Python 3.8+
- Playwright Python package installed (`pip install playwright`)
- Playwright browsers installed (`playwright install`)

Usage:
------
1. Ensure the target web application is running and accessible (default: http://127.0.0.1:5000/upload).
2. Run this script directly:

    python tests/e2e/test_single_page.py

   Optionally, modify the `page_url` variable at the bottom of the script to point to a different page.

3. The script will launch a Chromium browser (not headless), navigate to the page, and print detailed diagnostics to the console. A screenshot will be saved as 'debug_upload_page.png' in the current directory.

Output:
-------
- Console output listing all buttons, inputs, forms, file inputs, and drop zones with their attributes and visibility.
- The first 2000 characters of the page's HTML source.
- A screenshot of the page for visual debugging.

"""

import time
from playwright.sync_api import sync_playwright
import conftest
import os

# Test configuration - can be overridden by environment variables
BASE_URL = os.environ.get('TEST_BASE_URL', conftest.TEST_BASE_URL)



def single_page_diagnostics(page_url: str|None=None):
  """
  Launches a Chromium browser using Playwright, navigates to the specified page URL, and prints detailed diagnostics about the page's form-related elements.

  Args:
      page_url (str): The URL of the page to inspect. If None, the function will not navigate.

  What this function does:
  - Navigates to the given page URL.
  - Waits for the page to finish loading (network idle).
  - Enumerates and prints all <button>, <input>, <form>, and file input elements, including their attributes and visibility.
  - Searches for likely drop zone elements by id/class substring matching ('drop', 'zone').
  - Prints the first 2000 characters of the page's HTML source for manual inspection.
  - Takes a full-page screenshot and saves it as 'debug_upload_page.png'.

  This is intended for manual, interactive use. It is not a test, but a diagnostics and inspection tool.
  """
  
  with sync_playwright() as p:
    # Launch browser
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    try:
      # Navigate to upload page
      print(f"Navigating to page: {page_url} ...")
      page.goto(page_url)
      page.wait_for_load_state("networkidle")
      
      print(f"Page title: {page.title()}")
      print(f"Current URL: {page.url}")
      
      # Find all buttons
      print("\n=== ALL BUTTONS ===")
      buttons = page.locator("button").all()
      for i, button in enumerate(buttons):
        print(f"Button {i+1}:")
        print(f"  Text: '{button.text_content()}'")
        print(f"  Type: {button.get_attribute('type')}")
        print(f"  Class: {button.get_attribute('class')}")
        print(f"  ID: {button.get_attribute('id')}")
        print(f"  Visible: {button.is_visible()}")
        print()
      
      # Find all input elements
      print("=== ALL INPUT ELEMENTS ===")
      inputs = page.locator("input").all()
      for i, input_elem in enumerate(inputs):
        print(f"Input {i+1}:")
        print(f"  Type: {input_elem.get_attribute('type')}")
        print(f"  Value: {input_elem.get_attribute('value')}")
        print(f"  Class: {input_elem.get_attribute('class')}")
        print(f"  ID: {input_elem.get_attribute('id')}")
        print(f"  Visible: {input_elem.is_visible()}")
        print()
      
      # Find all form elements
      print("=== FORM ELEMENTS ===")
      forms = page.locator("form").all()
      for i, form in enumerate(forms):
        print(f"Form {i+1}:")
        print(f"  Action: {form.get_attribute('action')}")
        print(f"  Method: {form.get_attribute('method')}")
        print(f"  Class: {form.get_attribute('class')}")
        print(f"  ID: {form.get_attribute('id')}")
        print()
      
      # Find file input specifically
      print("=== FILE INPUT ELEMENTS ===")
      file_inputs = page.locator("input[type='file']").all()
      for i, file_input in enumerate(file_inputs):
        print(f"File Input {i+1}:")
        print(f"  Class: {file_input.get_attribute('class')}")
        print(f"  ID: {file_input.get_attribute('id')}")
        print(f"  Name: {file_input.get_attribute('name')}")
        print(f"  Accept: {file_input.get_attribute('accept')}")
        print(f"  Visible: {file_input.is_visible()}")
        print()
      
      # Find drop zone elements
      print("=== DROP ZONE ELEMENTS ===")
      drop_zones = page.locator("[id*='drop'], [class*='drop'], [id*='zone'], [class*='zone']").all()
      for i, drop_zone in enumerate(drop_zones):
        print(f"Drop Zone {i+1}:")
        print(f"  Tag: {drop_zone.evaluate('el => el.tagName')}")
        print(f"  Class: {drop_zone.get_attribute('class')}")
        print(f"  ID: {drop_zone.get_attribute('id')}")
        print(f"  Visible: {drop_zone.is_visible()}")
        print()
      
      # Get page source for manual inspection
      print("=== PAGE SOURCE (first 2000 chars) ===")
      page_source = page.content()
      print(page_source[:2000])
      
      # Take a screenshot for visual debugging
      print("\n=== TAKING SCREENSHOT ===")
      page.screenshot(path="debug_upload_page.png", full_page=True)
      print("Screenshot saved as debug_upload_page.png")
      
    finally:
      browser.close()

if __name__ == "__main__":
  page_url = f"{BASE_URL}/upload"
  single_page_diagnostics(page_url) 