"""
Debug script to examine the upload page HTML structure using Playwright
and identify the correct element selectors.
"""

import time
from playwright.sync_api import sync_playwright

def debug_upload_page():
  """Debug the upload page to find form elements using Playwright."""
  
  with sync_playwright() as p:
    # Launch browser
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    try:
      # Navigate to upload page
      print("Navigating to upload page...")
      page.goto("http://127.0.0.1:5000/upload")
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
  debug_upload_page() 