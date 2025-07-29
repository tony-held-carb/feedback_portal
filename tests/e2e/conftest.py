"""
Central configuration for E2E tests.
Provides shared constants and configuration for all E2E test modules.
"""

import os
import pytest
from pathlib import Path

# Test configuration - can be overridden by environment variables
# TEST_BASE_URL = os.environ.get('TEST_BASE_URL', "http://127.0.0.1:2113")
TEST_BASE_URL = os.environ.get('TEST_BASE_URL', "http://10.93.112.44:2113/")
# pytest tests/e2e -v  > "pytest_flask_on_ec2_testing_on_work_e2e_21.txt" 2>&1

TEST_FILES_DIR = Path("feedback_forms/testing_versions")

# Browser configuration
BROWSER_VIEWPORT = {
    "width": 1920, 
    "height": 1080
}

# Timeout settings
PAGE_LOAD_TIMEOUT = 30000  # 30 seconds
ELEMENT_WAIT_TIMEOUT = 10000  # 10 seconds

# EC2-specific browser launch options to work around dependency issues
EC2_BROWSER_LAUNCH_OPTIONS = {
    "headless": True,
    "args": [
        "--no-sandbox",
        "--disable-dev-shm-usage", 
        "--disable-gpu",
        "--disable-extensions",
        "--disable-plugins",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--disable-features=TranslateUI",
        "--disable-ipc-flooding-protection"
    ]
}

