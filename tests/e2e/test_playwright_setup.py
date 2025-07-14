"""
Simple test to verify Playwright setup is working correctly.
This test doesn't require the Flask app to be running.
"""

from playwright.sync_api import sync_playwright

def test_playwright_setup():
    """Test that Playwright can launch a browser and navigate to a simple page."""
    print("Testing Playwright setup...")
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigate to a simple page
            print("Navigating to example.com...")
            page.goto("https://example.com")
            
            # Check page title
            title = page.title()
            print(f"Page title: {title}")
            
            # Check for expected content
            content = page.content()
            if "Example Domain" in content:
                print("✅ Playwright setup is working correctly!")
                return True
            else:
                print("❌ Unexpected page content")
                return False
                
        except Exception as e:
            print(f"❌ Error during Playwright test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_playwright_setup()
    if success:
        print("\n🎉 Playwright migration completed successfully!")
        print("You can now run E2E tests with Playwright.")
    else:
        print("\n❌ Playwright setup test failed.")
        print("Please check your Playwright installation.")
    
    exit(0 if success else 1) 