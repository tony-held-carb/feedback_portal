"""
Central configuration for E2E tests.
Provides shared constants and configuration for all E2E test modules.
"""

import os
import sys
from pathlib import Path

def find_repo_root() -> Path:
    """
    Find the repository root directory by looking for .git directory.
    This ensures tests work regardless of where they're run from.
    """
    current_path = Path(__file__).resolve()
    while current_path.parent != current_path:  # Stop at filesystem root
        if (current_path / ".git").exists():
            return current_path
        current_path = current_path.parent
    
    # Fallback: assume we're in the workspace root
    return Path.cwd()

# Find repository root
REPO_ROOT = find_repo_root()

# Test configuration - can be overridden by environment variables
TEST_BASE_URL = os.environ.get('TEST_BASE_URL', "http://127.0.0.1:2113")
# TEST_BASE_URL = os.environ.get('TEST_BASE_URL', "http://10.93.112.44:2113/")
# pytest tests/e2e -v  > "pytest_flask_on_ec2_testing_on_work_e2e_21.txt" 2>&1

# Use absolute paths based on repository root
TEST_FILES_DIR = REPO_ROOT / "feedback_forms" / "testing_versions"
STANDARD_TEST_FILES_DIR = REPO_ROOT / "feedback_forms" / "testing_versions" / "standard"

def validate_test_infrastructure():
    """
    Validate that all required test infrastructure exists.
    Fails catastrophically if key directories or files are missing.
    This prevents silent test failures due to missing test data.
    """
    critical_errors = []
    
    # Check if repository root was found
    if not REPO_ROOT.exists():
        critical_errors.append(f"Repository root not found: {REPO_ROOT}")
    
    # Check if .git directory exists in repo root
    if not (REPO_ROOT / ".git").exists():
        critical_errors.append(f".git directory not found in repository root: {REPO_ROOT}")
    
    # Check if test files directory exists
    if not TEST_FILES_DIR.exists():
        critical_errors.append(f"Test files directory not found: {TEST_FILES_DIR}")
    
    # Check if standard test files directory exists
    if not STANDARD_TEST_FILES_DIR.exists():
        critical_errors.append(f"Standard test files directory not found: {STANDARD_TEST_FILES_DIR}")
    
    # Check if there are actual test files in the standard directory
    test_files = list(STANDARD_TEST_FILES_DIR.glob("*.xlsx"))
    if not test_files:
        critical_errors.append(f"No Excel test files found in: {STANDARD_TEST_FILES_DIR}")
    else:
        print(f"✓ Found {len(test_files)} test files in {STANDARD_TEST_FILES_DIR}")
    
    # If there are critical errors, fail catastrophically
    if critical_errors:
        error_msg = "\n".join([f"❌ CRITICAL TEST INFRASTRUCTURE ERROR: {error}" for error in critical_errors])
        error_msg += f"\n\nCurrent working directory: {Path.cwd()}"
        error_msg += f"\nRepository root: {REPO_ROOT}"
        error_msg += f"\nTest files dir: {TEST_FILES_DIR}"
        error_msg += f"\nStandard test files dir: {STANDARD_TEST_FILES_DIR}"
        
        print(error_msg, file=sys.stderr)
        sys.exit(1)
    
    print("✓ Test infrastructure validation passed")

# Validate test infrastructure on import
validate_test_infrastructure()

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
