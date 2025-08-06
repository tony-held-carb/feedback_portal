"""
Browser Compatibility Test for EC2
=================================

This script tests which Playwright browsers work on EC2 with older GLIBC versions.
It tries different browsers and launch options to find a working configuration.

Usage:
    python tests/e2e/test_browser_compatibility.py
"""

import sys

from playwright.sync_api import sync_playwright


def check_browser_compatibility(browser_name, launch_options=None):
  """Test if a specific browser can be launched and navigate to a page."""
  try:
    with sync_playwright() as p:
      # Get browser type
      if browser_name == "chromium":
        browser_type = p.chromium
      elif browser_name == "firefox":
        browser_type = p.firefox
      elif browser_name == "webkit":
        browser_type = p.webkit
      else:
        try:
          print(f"❌ Unknown browser: {browser_name}")
        except UnicodeEncodeError:
          print(f"Unknown browser: {browser_name}")
        assert False, f"Unknown browser: {browser_name}"

      # Launch browser with options
      if launch_options:
        browser = browser_type.launch(**launch_options)
      else:
        browser = browser_type.launch(headless=True)

      # Create page and navigate
      page = browser.new_page()
      page.goto('https://example.com')
      title = page.title()

      # Clean up
      browser.close()

      try:
        print(f"✅ {browser_name.upper()} is working!")
      except UnicodeEncodeError:
        print(f"{browser_name.upper()} is working!")
      print(f"   Page title: {title}")
      assert True, f"{browser_name} is working"

  except Exception as e:
    try:
      print(f"❌ {browser_name.upper()} failed: {str(e)[:100]}...")
    except UnicodeEncodeError:
      print(f"{browser_name.upper()} failed: {str(e)[:100]}...")
    assert False, f"{browser_name} failed: {str(e)[:100]}"


def main():
  """Test all browsers with different configurations."""
  print("Testing Playwright Browser Compatibility on EC2")
  print("=" * 50)

  # Import EC2-specific options
  from conftest import EC2_BROWSER_LAUNCH_OPTIONS

  browsers_to_test = [
    ("chromium", None),
    ("chromium", EC2_BROWSER_LAUNCH_OPTIONS),
    ("firefox", None),
    ("firefox", {"headless": True}),
    ("webkit", None),
    ("webkit", {"headless": True}),
  ]

  working_configs = []

  for browser_name, launch_options in browsers_to_test:
    config_name = f"{browser_name}"
    if launch_options:
      config_name += " (with EC2 options)"

    print(f"\nTesting {config_name}...")

    if check_browser_compatibility(browser_name, launch_options):
      working_configs.append((browser_name, launch_options))

  # Summary
  print(f"\n{'=' * 50}")
  print("SUMMARY")
  print(f"{'=' * 50}")

  if working_configs:
    try:
      print("✅ Working browser configurations:")
    except UnicodeEncodeError:
      print("Working browser configurations:")
    for browser_name, launch_options in working_configs:
      config_desc = f"{browser_name}"
      if launch_options:
        config_desc += " (with EC2 options)"
      print(f"   - {config_desc}")

    print(f"\nTo use a working configuration, modify your E2E tests to use:")
    browser_name, launch_options = working_configs[0]
    print(f"   browser = p.{browser_name}.launch(**{launch_options})")

  else:
    try:
      print("❌ No browsers are working on this system.")
    except UnicodeEncodeError:
      print("No browsers are working on this system.")
    print("   This indicates that Playwright cannot run on this EC2 instance")
    print("   due to missing system dependencies that require admin access.")
    print("   Consider using Selenium as an alternative for E2E testing.")

  return len(working_configs) > 0


if __name__ == "__main__":
  success = main()
  sys.exit(0 if success else 1)
