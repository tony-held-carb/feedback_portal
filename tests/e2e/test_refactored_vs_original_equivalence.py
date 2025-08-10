"""
Test file to ensure refactored upload routes produce identical results to original routes.

This test suite validates that:
1. upload_file_refactored produces identical results to upload_file
2. upload_file_staged_refactored produces identical results to upload_file_staged

It tests all files in feedback_forms/testing_versions/standard to ensure comprehensive coverage.
"""

import json
import os
import time
import warnings
from pathlib import Path
from typing import Dict, Any, Tuple

import openpyxl
import pytest
from playwright.sync_api import Page, expect

import conftest
from arb.portal.utils.e2e_testing_util import navigate_and_wait_for_ready
from arb.portal.utils.playwright_testing_util import (
    clear_upload_attempt_marker,
    upload_file_and_wait_for_attempt_marker,
    wait_for_upload_attempt_marker
)

# Test configuration
BASE_URL = os.environ.get('TEST_BASE_URL', conftest.TEST_BASE_URL)

# Suppress openpyxl warnings
@pytest.fixture(autouse=True, scope="session")
def suppress_openpyxl_warnings():
    warnings.filterwarnings(
        "ignore",
        message=".*extension is not supported and will be removed",
        category=UserWarning,
        module=r"openpyxl\.reader\.excel"
    )

def get_all_test_files() -> list:
    """Get all test files from the standard directory."""
    test_files = list(conftest.STANDARD_TEST_FILES_DIR.glob("*.xlsx"))
    if not test_files:
        pytest.fail(f"No test files found in {conftest.STANDARD_TEST_FILES_DIR}")
    return test_files

def read_excel_fields(file_path: Path) -> Dict[str, Any]:
    """Read Excel file and extract field values."""
    try:
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        sheet = workbook.active
        
        fields = {}
        for row in sheet.iter_rows(min_row=1, max_row=100, values_only=True):
            if row[0] and isinstance(row[0], str) and row[1] is not None:
                fields[str(row[0]).strip()] = row[1]
        
        workbook.close()
        return fields
    except Exception as e:
        pytest.fail(f"Failed to read Excel file {file_path}: {e}")

def upload_file_and_get_response(page: Page, route: str, file_path: Path) -> Tuple[str, Dict[str, Any]]:
    """Upload a file to a specific route and return the response details."""
    # Navigate to the route
    navigate_and_wait_for_ready(page, f"{BASE_URL}/{route}")
    
    # Clear any previous upload markers
    clear_upload_attempt_marker(page)
    
    # Upload the file
    file_input = page.locator("input[type='file']")
    file_input.set_input_files(str(file_path))
    
    # Wait for upload completion
    upload_file_and_wait_for_attempt_marker(page, str(file_path))
    
    # Get the response details
    response_data = {
        'url': page.url,
        'title': page.title(),
        'content': page.content(),
        'alerts': [],
        'errors': [],
        'success_messages': []
    }
    
    # Check for alerts and messages
    alerts = page.locator(".alert, .alert-info, .alert-success, .alert-danger, .alert-warning")
    for i in range(alerts.count()):
        alert = alerts.nth(i)
        alert_text = alert.inner_text().strip()
        alert_class = alert.get_attribute("class") or ""
        
        if "success" in alert_class.lower():
            response_data['success_messages'].append(alert_text)
        elif "danger" in alert_class.lower() or "error" in alert_class.lower():
            response_data['errors'].append(alert_text)
        else:
            response_data['alerts'].append(alert_text)
    
    return page.url, response_data

def compare_upload_responses(original_response: Dict[str, Any], refactored_response: Dict[str, Any], 
                           route_name: str, file_name: str) -> None:
    """Compare responses from original and refactored routes."""
    differences = []
    
    # Compare URL patterns (they might be different but should follow similar patterns)
    if "upload" in original_response['url'] and "upload" not in refactored_response['url']:
        differences.append(f"URL mismatch: original={original_response['url']}, refactored={refactored_response['url']}")
    
    # Compare page titles
    if original_response['title'] != refactored_response['title']:
        differences.append(f"Title mismatch: original='{original_response['title']}', refactored='{refactored_response['title']}'")
    
    # Compare success messages
    if original_response['success_messages'] != refactored_response['success_messages']:
        differences.append(f"Success messages mismatch: original={original_response['success_messages']}, refactored={refactored_response['success_messages']}")
    
    # Compare error messages
    if original_response['errors'] != refactored_response['errors']:
        differences.append(f"Error messages mismatch: original={original_response['errors']}, refactored={refactored_response['errors']}")
    
    # Compare general alerts
    if original_response['alerts'] != refactored_response['alerts']:
        differences.append(f"Alerts mismatch: original={original_response['alerts']}, refactored={refactored_response['alerts']}")
    
    # If there are differences, fail the test with detailed information
    if differences:
        error_msg = f"\n❌ Route equivalence test failed for {route_name} with file {file_name}\n"
        error_msg += "\n".join([f"  - {diff}" for diff in differences])
        error_msg += f"\n\nOriginal response: {json.dumps(original_response, indent=2)}"
        error_msg += f"\nRefactored response: {json.dumps(refactored_response, indent=2)}"
        pytest.fail(error_msg)

class TestRefactoredVsOriginalEquivalence:
    """Test class for ensuring refactored routes produce identical results to original routes."""
    
    @pytest.mark.parametrize("test_file", get_all_test_files())
    def test_upload_file_equivalence(self, page: Page, test_file: Path):
        """
        Test that upload_file_refactored produces identical results to upload_file.
        
        This test ensures that the refactored route maintains the same behavior,
        response patterns, and user experience as the original route.
        """
        print(f"\n🔍 Testing upload_file equivalence with: {test_file.name}")
        
        # Test original route
        original_url, original_response = upload_file_and_get_response(
            page, "upload", test_file
        )
        
        # Test refactored route
        refactored_url, refactored_response = upload_file_and_get_response(
            page, "upload_refactored", test_file
        )
        
        # Compare responses
        compare_upload_responses(
            original_response, refactored_response, 
            "upload_file", test_file.name
        )
        
        print(f"✅ upload_file equivalence test passed for {test_file.name}")
    
    @pytest.mark.parametrize("test_file", get_all_test_files())
    def test_upload_file_staged_equivalence(self, page: Page, test_file: Path):
        """
        Test that upload_file_staged_refactored produces identical results to upload_file_staged.
        
        This test ensures that the refactored staged route maintains the same behavior,
        response patterns, and user experience as the original staged route.
        """
        print(f"\n🔍 Testing upload_file_staged equivalence with: {test_file.name}")
        
        # Test original staged route
        original_url, original_response = upload_file_and_get_response(
            page, "upload_staged", test_file
        )
        
        # Test refactored staged route
        refactored_url, refactored_response = upload_file_and_get_response(
            page, "upload_staged_refactored", test_file
        )
        
        # Compare responses
        compare_upload_responses(
            original_response, refactored_response, 
            "upload_file_staged", test_file.name
        )
        
        print(f"✅ upload_file_staged equivalence test passed for {test_file.name}")
    
    def test_route_availability(self, page: Page):
        """Test that all required routes are accessible."""
        routes_to_test = [
            "upload",
            "upload_refactored", 
            "upload_staged",
            "upload_staged_refactored"
        ]
        
        for route in routes_to_test:
            try:
                navigate_and_wait_for_ready(page, f"{BASE_URL}/{route}")
                assert page.url.endswith(route), f"Route {route} not accessible"
                print(f"✅ Route {route} is accessible")
            except Exception as e:
                pytest.fail(f"Route {route} is not accessible: {e}")
    
    def test_file_upload_functionality_consistency(self, page: Page):
        """Test that file upload functionality is consistent across routes."""
        # Use a simple test file for this test
        test_file = next(conftest.STANDARD_TEST_FILES_DIR.glob("*test_01_good_data.xlsx"))
        
        routes_to_test = [
            "upload",
            "upload_refactored",
            "upload_staged", 
            "upload_staged_refactored"
        ]
        
        upload_results = {}
        
        for route in routes_to_test:
            try:
                url, response = upload_file_and_get_response(page, route, test_file)
                upload_results[route] = {
                    'success': True,
                    'url': url,
                    'has_file_input': 'input[type="file"]' in response['content'],
                    'has_form': 'form' in response['content']
                }
            except Exception as e:
                upload_results[route] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Verify all routes have consistent basic functionality
        for route, result in upload_results.items():
            if not result['success']:
                pytest.fail(f"Route {route} failed: {result['error']}")
            
            if not result['has_file_input']:
                pytest.fail(f"Route {route} missing file input")
            
            if not result['has_form']:
                pytest.fail(f"Route {route} missing form")
        
        print("✅ File upload functionality consistency verified across all routes")

def pytest_collection_modifyitems(config, items):
    """Add markers to tests for better organization."""
    for item in items:
        if "equivalence" in item.name:
            item.add_marker(pytest.mark.equivalence)
        if "upload" in item.name:
            item.add_marker(pytest.mark.upload)
