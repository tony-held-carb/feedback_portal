"""
Playwright Setup Verification Script
===================================

This script provides a simple test to verify that your Playwright Python installation is working correctly.
It is intended for both beginners and advanced users who want to confirm that Playwright is installed and functional.

Purpose:
--------
- Ensure that Playwright and its Python bindings are correctly installed and configured.
- Verify that Playwright can launch a browser, navigate to a page, and interact with it.
- Provide a quick diagnostic before running more complex end-to-end (E2E) tests.

Typical Use Cases:
------------------
- After installing Playwright and its dependencies, to confirm the setup is correct.
- When troubleshooting E2E test failures that may be related to Playwright installation or environment issues.
- As a basic health check in CI/CD pipelines.

Prerequisites:
--------------
- Python 3.8+
- Playwright Python package installed (`pip install playwright`)
- Playwright browsers installed (`playwright install`)

Usage:
------
1. You do NOT need the Flask app or any local server running for this test.
2. Run this script directly:

    python tests/e2e/test_playwright_setup.py

   Or run as a pytest test:

    pytest tests/e2e/test_playwright_setup.py

3. The script will launch a headless Chromium browser, navigate to https://example.com, and check the page content.

Output:
-------
- Console output indicating the progress of the test.
- Success or failure message indicating whether Playwright is set up correctly.

"""

import pytest
import asyncio
import sniffio
from playwright.async_api import async_playwright

# NOTE: This is not an application E2E test. It is a Playwright installation check and causes unrelated failures
# due to async backend issues (pytest runs with both asyncio and trio, but Playwright only supports asyncio).
# For a clean E2E test run, this test is always skipped. Remove or uncomment if you need to debug Playwright setup.

# @pytest.mark.skip(reason="Not an application E2E test; causes unrelated failures due to async backend issues.")
@pytest.mark.asyncio
async def test_playwright_setup():
    """
    Asynchronously verifies that Playwright is installed and functional by:
    - Launching a headless Chromium browser
    - Navigating to https://example.com
    - Checking that the page loads and contains the expected content
    - Printing progress and result messages to the console

    Skips the test if the current async library is not asyncio (required by Playwright).
    """
    if sniffio.current_async_library() != "asyncio":
        pytest.skip("Playwright only supports asyncio backend")
    print("Testing Playwright setup (async)...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print("Navigating to example.com...")
            await page.goto("https://example.com")
            title = await page.title()
            print(f"Page title: {title}")
            content = await page.content()
            assert "Example Domain" in content, "❌ Unexpected page content"
            print("✅ Playwright setup is working correctly!")
        finally:
            await browser.close()

if __name__ == "__main__":
    success = test_playwright_setup()
    if success:
        print("\n🎉 Playwright migration completed successfully!")
        print("You can now run E2E tests with Playwright.")
    else:
        print("\n❌ Playwright setup test failed.")
        print("Please check your Playwright installation.")
    
    exit(0 if success else 1) 