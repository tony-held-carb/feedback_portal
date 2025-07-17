"""
Simple test to verify Playwright setup is working correctly.
This test doesn't require the Flask app to be running.
"""

import pytest
import asyncio
from playwright.async_api import async_playwright

@pytest.mark.asyncio
async def test_playwright_setup():
    """Test that Playwright can launch a browser and navigate to a simple page (async version)."""
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