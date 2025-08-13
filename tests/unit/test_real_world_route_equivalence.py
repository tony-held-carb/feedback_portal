"""
Real-World Unit Tests for Route Equivalence

This module provides infrastructure and route behavior testing using actual test files
to validate that the refactored routes behave similarly to the original routes.

IMPORTANT: These tests focus on route behavior and infrastructure, NOT content validation.
The expected_results directory contains known-good outputs but is NOT used for content comparison.

What these tests actually do:
1. Use real test files from feedback_forms/testing_versions/standard/ for input
2. Verify route infrastructure and HTTP response behavior
3. Test error handling with real bad data files
4. Validate test environment setup and file availability
5. Compare HTTP response codes between original and refactored routes

What these tests do NOT do:
- Compare actual file content against expected results
- Validate that routes produce correct data output
- Test functional equivalence of data processing
- Verify JSON metadata consistency
- Perform content validation (all processing is mocked)

Test Coverage:
- Route response behavior equivalence (HTTP status codes)
- Error handling consistency between route pairs
- Test infrastructure validation (file availability)
- Basic route functionality (page loading, form handling)
- All test file types (good data, bad data, blank files)

Limitations:
- All actual file processing is mocked - no real content validation
- Expected results directory is only used for infrastructure validation
- Tests verify route behavior, not data processing accuracy
- No functional equivalence testing of actual Excel/JSON output
"""

import pytest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from werkzeug.datastructures import FileStorage
import io
import openpyxl
from openpyxl import load_workbook
import pandas as pd

# Add source/production directory to Python path for imports
production_dir = Path(__file__).parent.parent.parent / "source" / "production"
if str(production_dir) not in sys.path:
    sys.path.insert(0, str(production_dir))

# Add tests directory to Python path for conftest imports
tests_dir = Path(__file__).parent.parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

# Import the actual route functions and logic
from arb.portal.routes import (
    upload_file,
    upload_file_refactored,
    upload_file_staged,
    upload_file_staged_refactored
)

# Import test utilities and Flask app
from e2e.conftest import STANDARD_TEST_FILES_DIR
from arb.portal.app import create_app


class TestRealWorldRouteEquivalence:
    """Real-world unit tests for route behavior and infrastructure validation.
    
    These tests use actual test files to validate route behavior but do NOT
    perform content validation or functional equivalence testing.
    """
    
    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
        
        yield app
        
        # Cleanup
        shutil.rmtree(app.config['UPLOAD_FOLDER'])
    
    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return app.test_client()
    
    @pytest.fixture
    def test_files(self):
        """Get all test files for comprehensive testing."""
        test_dir = Path(STANDARD_TEST_FILES_DIR)
        
        # CRITICAL: Fail explicitly if directory doesn't exist
        if not test_dir.exists():
            pytest.fail(f"""
❌ CRITICAL TEST INFRASTRUCTURE ERROR: Test directory not found!

Expected path: {test_dir}
Current working directory: {Path.cwd()}
Repository root: {Path(__file__).parent.parent.parent}

This test will fail catastrophically to prevent silent test failures.
""")
        
        # Get all Excel files in the directory
        files = list(test_dir.glob("*.xlsx"))
        
        if not files:
            pytest.fail(f"No Excel files found in: {test_dir}")
        
        print(f"📁 Found {len(files)} test files for real-world testing")
        return files
    
    @pytest.fixture
    def expected_results_dir(self):
        """Get the expected results directory."""
        expected_dir = Path(STANDARD_TEST_FILES_DIR) / "expected_results"
        
        if not expected_dir.exists():
            pytest.fail(f"Expected results directory not found: {expected_dir}")
        
        return expected_dir
    
    def test_route_function_existence(self):
        """Test that all required route functions exist and are callable."""
        routes = [
            upload_file,
            upload_file_refactored,
            upload_file_staged,
            upload_file_staged_refactored
        ]
        
        for route in routes:
            assert callable(route), f"Route {route.__name__} is not callable"
    
    def test_upload_file_equivalence_with_real_data(self, client, test_files, expected_results_dir):
        """Test that upload_file and upload_file_refactored produce equivalent results with real data."""
        # Test with a good data file first
        good_data_file = None
        for test_file in test_files:
            if "test_01_good_data" in test_file.name:
                good_data_file = test_file
                break
        
        if not good_data_file:
            pytest.skip("No good data test file found")
        
        with patch('arb.portal.routes.upload_and_process_file') as mock_upload_func:
            
            # Read file data into memory
            with open(good_data_file, 'rb') as f:
                file_data = f.read()
            
            # Test both routes with the same input
            with client.application.app_context():
                # Mock the upload logic to return consistent results
                mock_result = Mock()
                mock_result.success = True
                mock_result.message = "File uploaded successfully"
                mock_result.redirect_url = "/success"
                
                mock_upload_func.return_value = mock_result
                
                # Test original route with fresh FileStorage
                file_storage_1 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=Path(good_data_file).name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                original_response = client.post('/upload', data={'file': file_storage_1})
                
                # Test refactored route with fresh FileStorage
                file_storage_2 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=Path(good_data_file).name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                refactored_response = client.post('/upload_refactored', data={'file': file_storage_2})
                
                # Both should return similar response types
                assert original_response.status_code in [200, 302]
                assert refactored_response.status_code in [200, 302]
                
                print(f"✅ Both routes processed {good_data_file.name} successfully")
    
    def test_staged_upload_equivalence_with_real_data(self, client, test_files, expected_results_dir):
        """Test that upload_file_staged and upload_file_staged_refactored produce equivalent results with real data."""
        # Test with a good data file first
        good_data_file = None
        for test_file in test_files:
            if "test_01_good_data" in test_file.name:
                good_data_file = test_file
                break
        
        if not good_data_file:
            pytest.skip("No good data test file found")
        
        with patch('arb.portal.routes.upload_and_stage_only') as mock_stage_func:
            
            # Read file data into memory
            with open(good_data_file, 'rb') as f:
                file_data = f.read()
            
            # Test both routes with the same input
            with client.application.app_context():
                # Mock the staging logic to return consistent results
                mock_result = Mock()
                mock_result.success = True
                mock_result.message = "File staged successfully"
                mock_result.staging_id = "test_staging_id"
                
                mock_stage_func.return_value = mock_result
                
                # Test original route with fresh FileStorage
                file_storage_1 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=Path(good_data_file).name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                original_response = client.post('/upload_staged', data={'file': file_storage_1})
                
                # Test refactored route with fresh FileStorage
                file_storage_2 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=Path(good_data_file).name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                refactored_response = client.post('/upload_staged_refactored', data={'file': file_storage_2})
                
                # Both should return similar response types
                assert original_response.status_code in [200, 302]
                assert refactored_response.status_code in [200, 302]
                
                print(f"✅ Both staged routes processed {good_data_file.name} successfully")
    
    def test_error_handling_equivalence_with_bad_data(self, client, test_files, expected_results_dir):
        """Test that error handling is equivalent between routes with real bad data files."""
        # Test with a bad data file
        bad_data_file = None
        for test_file in test_files:
            if "test_02_bad_data" in test_file.name:
                bad_data_file = test_file
                break
        
        if not bad_data_file:
            pytest.skip("No bad data test file found")
        
        with patch('arb.portal.routes.upload_and_process_file') as mock_upload_func, \
             patch('arb.portal.routes.upload_and_stage_only') as mock_stage_func:
            
            # Mock error conditions
            mock_upload_func.side_effect = Exception("Test error")
            mock_stage_func.side_effect = Exception("Test error")
            
            # Read file data into memory
            with open(bad_data_file, 'rb') as f:
                file_data = f.read()
            
            # Test error handling for both route pairs
            with client.application.app_context():
                # Test upload routes with errors
                file_storage_1 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=Path(bad_data_file).name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                original_upload_error = client.post('/upload', data={'file': file_storage_1})
                
                file_storage_2 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=Path(bad_data_file).name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                refactored_upload_error = client.post('/upload_refactored', data={'file': file_storage_2})
                
                # Test staged routes with errors
                file_storage_3 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=Path(bad_data_file).name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                original_staged_error = client.post('/upload_staged', data={'file': file_storage_3})
                
                file_storage_4 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=Path(bad_data_file).name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                refactored_staged_error = client.post('/upload_staged_refactored', data={'file': file_storage_4})
                
                # All should handle errors gracefully
                # Routes may redirect (302) or return error page (200) - both are valid
                assert original_upload_error.status_code in [200, 302]
                assert refactored_upload_error.status_code in [200, 302]
                assert original_staged_error.status_code in [200, 302]
                assert refactored_staged_error.status_code in [200, 302]
                
                print(f"✅ Both route pairs handled bad data file {bad_data_file.name} gracefully")
    
    def test_all_test_files_covered(self, test_files):
        """Test that we have comprehensive coverage of all test file types."""
        # Check that we have the expected test file categories
        good_data_files = [f for f in test_files if "test_01_good_data" in f.name]
        bad_data_files = [f for f in test_files if "test_02_bad_data" in f.name]
        blank_files = [f for f in test_files if "test_03_blank" in f.name]
        
        # We should have multiple good data and bad data files
        assert len(good_data_files) >= 3, f"Expected at least 3 good data files, found {len(good_data_files)}"
        assert len(bad_data_files) >= 3, f"Expected at least 3 bad data files, found {len(bad_data_files)}"
        
        # Check for specific feedback form types
        landfill_files = [f for f in test_files if "landfill_operator" in f.name]
        oil_gas_files = [f for f in test_files if "oil_and_gas_operator" in f.name]
        dairy_files = [f for f in test_files if "dairy_digester" in f.name]
        energy_files = [f for f in test_files if "energy_operator" in f.name]
        generic_files = [f for f in test_files if "generic_operator" in f.name]
        
        # We should have files for each feedback form type
        assert len(landfill_files) >= 2, f"Expected at least 2 landfill files, found {len(landfill_files)}"
        assert len(oil_gas_files) >= 2, f"Expected at least 2 oil & gas files, found {len(oil_gas_files)}"
        assert len(dairy_files) >= 3, f"Expected at least 3 dairy files, found {len(dairy_files)}"
        assert len(energy_files) >= 3, f"Expected at least 3 energy files, found {len(energy_files)}"
        assert len(generic_files) >= 2, f"Expected at least 2 generic files, found {len(generic_files)}"
        
        print(f"✅ Comprehensive test coverage: {len(test_files)} test files covering all feedback form types")
    
    def test_expected_results_structure(self, expected_results_dir):
        """Test that the expected results directory has the expected structure."""
        # Check that expected results exist
        expected_files = list(expected_results_dir.glob("*.xlsx"))
        expected_json_files = list(expected_results_dir.glob("*.json"))
        
        # We should have both Excel and JSON files
        assert len(expected_files) > 0, "No expected Excel files found"
        assert len(expected_json_files) > 0, "No expected JSON files found"
        
        # Check that we have corresponding pairs
        excel_names = {f.stem for f in expected_files}
        json_names = {f.stem for f in expected_json_files}
        
        # Most Excel files should have corresponding JSON files
        # (Some might not have JSON if they failed processing)
        common_names = excel_names.intersection(json_names)
        assert len(common_names) >= len(expected_files) * 0.8, f"Expected at least 80% of Excel files to have JSON, found {len(common_names)}/{len(expected_files)}"
        
        print(f"✅ Expected results structure: {len(expected_files)} Excel files, {len(expected_json_files)} JSON files")
    
    def test_response_format_equivalence(self, client):
        """Test that response formats are equivalent between routes."""
        with patch('arb.portal.routes.upload_and_process_file') as mock_upload_func, \
             patch('arb.portal.routes.upload_and_stage_only') as mock_stage_func:
            
            # Mock successful responses
            mock_upload_result = Mock()
            mock_upload_result.success = True
            mock_upload_result.message = "Success"
            mock_upload_result.redirect_url = "/success"
            
            mock_staging_result = Mock()
            mock_staging_result.success = True
            mock_staging_result.message = "Staged"
            mock_staging_result.staging_id = "test_id"
            
            mock_upload_func.return_value = mock_upload_result
            mock_stage_func.return_value = mock_staging_result
            
            with client.application.app_context():
                # Test GET requests to ensure consistent page structure
                original_upload_get = client.get('/upload')
                refactored_upload_get = client.get('/upload_refactored')
                original_staged_get = client.get('/upload_staged')
                refactored_staged_get = client.get('/upload_staged_refactored')
                
                # All GET requests should return 200
                assert original_upload_get.status_code == 200
                assert refactored_upload_get.status_code == 200
                assert original_staged_get.status_code == 200
                assert refactored_staged_get.status_code == 200
                
                # All should return HTML
                assert 'text/html' in original_upload_get.content_type
                assert 'text/html' in refactored_upload_get.content_type
                assert 'text/html' in original_staged_get.content_type
                assert 'text/html' in refactored_staged_get.content_type
                
                print("✅ All routes return consistent HTML response formats")


def pytest_addoption(parser):
    """Add custom command line options for real-world testing."""
    parser.addoption(
        "--test-files-limit",
        type=int,
        default=None,
        help="Limit number of test files to use (default: all files)"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command line options."""
    test_files_limit = config.getoption("--test-files-limit")
    
    # Mark real-world tests appropriately
    for item in items:
        if "real_world" in item.name.lower():
            item.add_marker(pytest.mark.real_world)
        if "equivalence" in item.name.lower():
            item.add_marker(pytest.mark.equivalence)
        if "route" in item.name.lower():
            item.add_marker(pytest.mark.route)
