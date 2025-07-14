"""
Debug script to examine the upload page HTML structure
and identify the correct submit button selectors.
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def debug_upload_page():
  """Debug the upload page to find submit button elements."""
  
  # Setup Chrome WebDriver
  chrome_options = Options()
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument("--disable-dev-shm-usage")
  chrome_options.add_argument("--disable-gpu")
  chrome_options.add_argument("--window-size=1920,1080")
  
  service = Service(ChromeDriverManager().install())
  driver = webdriver.Chrome(service=service, options=chrome_options)
  
  try:
    # Navigate to upload page
    print("Navigating to upload page...")
    driver.get("http://127.0.0.1:5000/upload")
    time.sleep(2)
    
    print(f"Page title: {driver.title}")
    print(f"Current URL: {driver.current_url}")
    
    # Find all buttons
    print("\n=== ALL BUTTONS ===")
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for i, button in enumerate(buttons):
      print(f"Button {i+1}:")
      print(f"  Text: '{button.text}'")
      print(f"  Type: {button.get_attribute('type')}")
      print(f"  Class: {button.get_attribute('class')}")
      print(f"  ID: {button.get_attribute('id')}")
      print(f"  Visible: {button.is_displayed()}")
      print()
    
    # Find all input elements
    print("=== ALL INPUT ELEMENTS ===")
    inputs = driver.find_elements(By.TAG_NAME, "input")
    for i, input_elem in enumerate(inputs):
      print(f"Input {i+1}:")
      print(f"  Type: {input_elem.get_attribute('type')}")
      print(f"  Value: {input_elem.get_attribute('value')}")
      print(f"  Class: {input_elem.get_attribute('class')}")
      print(f"  ID: {input_elem.get_attribute('id')}")
      print(f"  Visible: {input_elem.is_displayed()}")
      print()
    
    # Find all form elements
    print("=== FORM ELEMENTS ===")
    forms = driver.find_elements(By.TAG_NAME, "form")
    for i, form in enumerate(forms):
      print(f"Form {i+1}:")
      print(f"  Action: {form.get_attribute('action')}")
      print(f"  Method: {form.get_attribute('method')}")
      print(f"  Class: {form.get_attribute('class')}")
      print(f"  ID: {form.get_attribute('id')}")
      print()
    
    # Get page source for manual inspection
    print("=== PAGE SOURCE (first 2000 chars) ===")
    page_source = driver.page_source
    print(page_source[:2000])
    
  finally:
    driver.quit()

if __name__ == "__main__":
  debug_upload_page() 