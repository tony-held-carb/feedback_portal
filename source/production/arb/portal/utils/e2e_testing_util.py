"""
E2E Testing Utility Functions
============================

This module contains shared utility functions for end-to-end testing with Playwright.
These functions provide consistent, reliable patterns for common E2E testing operations.

Part of the arb.portal.utils package for general-purpose testing utilities.

These utilities are designed to work with the custom E2E readiness marker system
implemented in the feedback portal application.
"""

from playwright.sync_api import Page
from typing import Optional


def wait_for_e2e_readiness(page: Page, timeout: int = 7000) -> None:
    """
    Helper function to wait for the E2E readiness marker.
    
    This function waits for the page to set the 'data-e2e-ready' attribute,
    which indicates that the page has finished rendering and JavaScript
    initialization has completed.
    
    Args:
        page: Playwright page object
        timeout: Maximum time to wait in milliseconds (default: 7000)
    
    Raises:
        TimeoutError: If the readiness marker is not set within the timeout period
    """
    try:
        page.wait_for_selector("html[data-e2e-ready='true']", timeout=timeout)
    except TimeoutError:
        print(f"❌ E2E readiness marker not found on {page.url}")
        page.screenshot(path="debug_e2e_timeout.png", full_page=True)
        raise


def navigate_and_wait_for_ready(page: Page, url: str, timeout: int = 7000) -> None:
    """
    Navigate to a URL and wait for the page to be ready for E2E testing.
    
    This is a convenience function that combines page.goto() with wait_for_e2e_readiness().
    
    Args:
        page: Playwright page object
        url: URL to navigate to
        timeout: Maximum time to wait for readiness in milliseconds (default: 7000)
    
    Raises:
        TimeoutError: If the readiness marker is not set within the timeout period
    """
    page.goto(url, wait_until="load")
    wait_for_e2e_readiness(page, timeout) 