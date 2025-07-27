"""
Central configuration for E2E tests.
Provides shared constants and configuration for all E2E test modules.
"""

import os
from pathlib import Path

# Test configuration - can be overridden by environment variables
TEST_BASE_URL = os.environ.get('TEST_BASE_URL', "http://127.0.0.1:5000")
TEST_FILES_DIR = Path("feedback_forms/testing_versions")

# Browser configuration
BROWSER_VIEWPORT = {
    "width": 1920, 
    "height": 1080
}

# Timeout settings
PAGE_LOAD_TIMEOUT = 30000  # 30 seconds
ELEMENT_WAIT_TIMEOUT = 10000  # 10 seconds 