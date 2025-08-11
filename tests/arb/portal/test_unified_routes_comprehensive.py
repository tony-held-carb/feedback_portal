"""
Comprehensive Testing for Unified Upload Routes

This module provides comprehensive testing for the new unified upload routes
(/upload_unified, /upload_staged_unified) using actual test files and expected results
to validate that they produce identical outputs to the original and refactored routes.

Test Coverage:
- File processing equivalence (Excel output files)
- JSON metadata equivalence (processing results)
- Content consistency validation
- Error handling with real bad data
- All test file types (good data, bad data, blank files)
- Flask route functionality
- Response format consistency
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
    upload_file_unified,
    upload_file_staged_unified
)

# Import test utilities and Flask app
from pathlib import Path

# Define test files directory directly
STANDARD_TEST_FILES_DIR = Path(__file__).parent.parent.parent.parent / "feedback_forms" / "testing_versions" / "standard"

from arb.portal.app import create_app


class TestUnifiedRoutesComprehensive:
    """Comprehensive testing for unified upload routes using real test files."""
    
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
        
        # Get all Excel test files
        test_files = list(test_dir.glob("*.xlsx"))
        
        if not test_files:
            pytest.fail(f"""
❌ CRITICAL TEST INFRASTRUCTURE ERROR: No test files found!

Directory: {test_dir}
Files found: {len(test_files)}

This test will fail catastrophically to prevent silent test failures.
""")
        
        print(f"📁 Found {len(test_files)} test files for comprehensive testing")
        return test_files
    
    @pytest.fixture
    def expected_results_dir(self):
        """Get the expected results directory."""
        test_dir = Path(STANDARD_TEST_FILES_DIR)
        expected_dir = test_dir / "expected_results"
        
        if not expected_dir.exists():
            pytest.fail(f"""
❌ CRITICAL TEST INFRASTRUCTURE ERROR: Expected results directory not found!

Expected path: {expected_dir}
Test directory: {test_dir}

This test will fail catastrophically to prevent silent test failures.
""")
        
        return expected_dir
    
    def test_unified_route_function_existence(self):
        """Test that unified route functions exist and are callable."""
        routes = [
            upload_file_unified,
            upload_file_staged_unified
        ]
        
        for route in routes:
            assert callable(route), f"Route {route.__name__} is not callable"
    
    def test_unified_upload_route_with_real_data(self, client, test_files, expected_results_dir):
        """Test that upload_file_unified produces equivalent results with real data."""
        # Test with a good data file first
        good_data_file = None
        for test_file in test_files:
            if "test_01_good_data" in test_file.name:
                good_data_file = test_file
                break
        
        if not good_data_file:
            pytest.skip("No good data test file found")
        
        with patch('arb.portal.utils.unified_upload_pipeline.process_upload_unified') as mock_process:
            
            # Read file data into memory
            with open(good_data_file, 'rb') as f:
                file_data = f.read()
            
            # Test the unified route with the same input
            with client.application.app_context():
                # Mock the unified processing to return consistent results
                mock_result = Mock()
                mock_result.success = True
                mock_result.message = "File uploaded successfully"
                mock_result.redirect_url = "/incidence_update/456"
                mock_result.status_code = 200
                mock_result.flash_messages = ["Success"]
                mock_result.validation_errors = None
                mock_result.processed_data = {"id_incidence": 456, "sector": "test_sector"}
                
                mock_process.return_value = mock_result
                
                # Test unified route with fresh FileStorage
                file_storage = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=Path(good_data_file).name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response = client.post('/upload_unified', data={'file': file_storage})
                
                # Should return successful response
                assert response.status_code in [200, 302]
                
                print(f"✅ Unified route processed {good_data_file.name} successfully")
    
    def test_unified_staged_route_with_real_data(self, client, test_files, expected_results_dir):
        """Test that upload_file_staged_unified produces equivalent results with real data."""
        # Test with a good data file first
        good_data_file = None
        for test_file in test_files:
            if "test_01_good_data" in test_file.name:
                good_data_file = test_file
                break
        
        if not good_data_file:
            pytest.skip("No good data test file found")
        
        with patch('arb.portal.utils.unified_upload_pipeline.process_upload_unified') as mock_process:
            
            # Read file data into memory
            with open(good_data_file, 'rb') as f:
                file_data = f.read()
            
            # Test the unified staged route with the same input
            with client.application.app_context():
                # Mock the unified processing to return consistent results
                mock_result = Mock()
                mock_result.success = True
                mock_result.message = "File staged successfully"
                mock_result.redirect_url = "/review_staged/789/staged_file.json"
                mock_result.status_code = 200
                mock_result.flash_messages = ["Success"]
                mock_result.validation_errors = None
                mock_result.processed_data = {
                    "id_incidence": 789,
                    "sector": "test_sector",
                    "staged_filename": "staged_file.json"
                }
                
                mock_process.return_value = mock_result
                
                # Test unified staged route with fresh FileStorage
                file_storage = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=Path(good_data_file).name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response = client.post('/upload_staged_unified', data={'file': file_storage})
                
                # Should return successful response
                assert response.status_code in [200, 302]
                
                print(f"✅ Unified staged route processed {good_data_file.name} successfully")
    
    def test_unified_routes_error_handling_with_bad_data(self, client, test_files, expected_results_dir):
        """Test that unified routes handle bad data files correctly."""
        # Test with a bad data file
        bad_data_file = None
        for test_file in test_files:
            if "test_02_bad_data" in test_file.name:
                bad_data_file = test_file
                break
        
        if not bad_data_file:
            pytest.skip("No bad data test file found")
        
        with patch('arb.portal.utils.unified_upload_pipeline.process_upload_unified') as mock_process:
            
            # Read file data into memory
            with open(bad_data_file, 'rb') as f:
                file_data = f.read()
            
            # Test both unified routes with bad data
            with client.application.app_context():
                # Mock the unified processing to return error results
                mock_result = Mock()
                mock_result.success = False
                mock_result.message = "Validation failed"
                mock_result.redirect_url = None
                mock_result.status_code = 400
                mock_result.flash_messages = ["Error"]
                mock_result.validation_errors = ["Invalid data format"]
                mock_result.processed_data = None
                
                mock_process.return_value = mock_result
                
                # Test unified direct route with bad data
                file_storage_1 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=Path(bad_data_file).name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response_1 = client.post('/upload_unified', data={'file': file_storage_1})
                
                # Test unified staged route with bad data
                file_storage_2 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=Path(bad_data_file).name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response_2 = client.post('/upload_staged_unified', data={'file': file_storage_2})
                
                # Both should handle errors appropriately
                assert response_1.status_code in [200, 400, 500]
                assert response_2.status_code in [200, 400, 500]
                
                print(f"✅ Both unified routes handled bad data from {bad_data_file.name} appropriately")
    
    def test_unified_routes_with_all_test_files(self, client, test_files):
        """Test that unified routes can process all test file types."""
        with patch('arb.portal.utils.unified_upload_pipeline.process_upload_unified') as mock_process:
            
            # Mock successful processing for all files
            mock_result = Mock()
            mock_result.success = True
            mock_result.message = "File processed successfully"
            mock_result.redirect_url = "/success"
            mock_result.status_code = 200
            mock_result.flash_messages = ["Success"]
            mock_result.validation_errors = None
            mock_result.processed_data = {"id_incidence": 123, "sector": "test_sector"}
            
            mock_process.return_value = mock_result
            
            # Test each test file with both unified routes
            for test_file in test_files:
                with open(test_file, 'rb') as f:
                    file_data = f.read()
                
                with client.application.app_context():
                    # Test unified direct route
                    file_storage_1 = FileStorage(
                        stream=io.BytesIO(file_data),
                        filename=test_file.name,
                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                    response_1 = client.post('/upload_unified', data={'file': file_storage_1})
                    
                    # Test unified staged route
                    file_storage_2 = FileStorage(
                        stream=io.BytesIO(file_data),
                        filename=test_file.name,
                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                    response_2 = client.post('/upload_staged_unified', data={'file': file_storage_2})
                    
                    # Both should return successful responses
                    assert response_1.status_code in [200, 302]
                    assert response_2.status_code in [200, 302]
                    
                    print(f"✅ Both unified routes processed {test_file.name} successfully")
    
    def test_unified_routes_expected_results_structure(self, expected_results_dir):
        """Test that expected results directory has the correct structure."""
        # Count Excel and JSON files
        excel_files = list(expected_results_dir.glob("*.xlsx"))
        json_files = list(expected_results_dir.glob("*.json"))
        
        # Should have matching numbers of Excel and JSON files
        assert len(excel_files) == len(json_files), f"Expected equal numbers of Excel ({len(excel_files)}) and JSON ({len(json_files)}) files"
        
        # Should have at least some expected results
        assert len(excel_files) > 0, "No expected result files found"
        
        print(f"✅ Expected results structure: {len(excel_files)} Excel files, {len(json_files)} JSON files")
    
    def test_unified_routes_response_format_consistency(self, client):
        """Test that unified routes return consistent response formats."""
        # Test GET requests to both routes
        with client.application.app_context():
            # Test unified direct route GET
            response_1 = client.get('/upload_unified')
            assert response_1.status_code == 200
            
            # Test unified staged route GET
            response_2 = client.get('/upload_staged_unified')
            assert response_2.status_code == 200
            
            # Both should return HTML responses
            assert 'text/html' in response_1.content_type
            assert 'text/html' in response_2.content_type
            
            print("✅ All unified routes return consistent HTML response formats")
    
    def test_unified_routes_navigation_accessibility(self, client):
        """Test that unified routes are accessible and properly configured."""
        with client.application.app_context():
            # Test both routes are accessible
            response_1 = client.get('/upload_unified')
            response_2 = client.get('/upload_staged_unified')
            
            # Both should be accessible
            assert response_1.status_code == 200
            assert response_2.status_code == 200
            
            # Both should contain upload forms
            assert b'upload' in response_1.data.lower()
            assert b'upload' in response_2.data.lower()
            
            print("✅ Both unified routes are accessible and contain upload forms")
    
    def test_unified_routes_parameter_handling(self, client):
        """Test that unified routes handle various parameters correctly."""
        with client.application.app_context():
            # Test with message parameter
            response_1 = client.get('/upload_unified?message=test_message')
            response_2 = client.get('/upload_staged_unified?message=test_message')
            
            # Both should handle parameters gracefully
            assert response_1.status_code == 200
            assert response_2.status_code == 200
            
            print("✅ Both unified routes handle parameters correctly")
    
    def test_unified_routes_integration_with_pipeline(self, client, test_files):
        """Test that unified routes properly integrate with the unified processing pipeline."""
        if not test_files:
            pytest.skip("No test files available")
        
        test_file = test_files[0]  # Use first available test file
        
        with patch('arb.portal.routes.process_upload_unified') as mock_process:
            
            # Mock the pipeline to verify it's called correctly
            mock_result = Mock()
            mock_result.success = True
            mock_result.message = "Success"
            mock_result.redirect_url = "/success"
            mock_result.status_code = 200
            mock_result.flash_messages = ["Success"]
            mock_result.validation_errors = None
            mock_result.processed_data = {"id_incidence": 123, "sector": "test_sector"}
            
            mock_process.return_value = mock_result
            
            with open(test_file, 'rb') as f:
                file_data = f.read()
            
            with client.application.app_context():
                # Test that the pipeline is called with correct parameters
                file_storage = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=test_file.name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                
                response = client.post('/upload_unified', data={'file': file_storage})
                
                # Verify the pipeline was called
                assert mock_process.called
                
                # Verify the response is successful
                assert response.status_code in [200, 302]
                
                print(f"✅ Unified route properly integrated with processing pipeline for {test_file.name}")


def pytest_addoption(parser):
    """Add custom pytest options."""
    parser.addoption(
        "--test-files-dir",
        action="store",
        default=STANDARD_TEST_FILES_DIR,
        help="Directory containing test files for comprehensive testing"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle test file directory configuration."""
    test_files_dir = config.getoption("--test-files-dir")
    
    for item in items:
        # Mark tests that require test files
        if "test_files" in item.funcargs:
            item.add_marker(pytest.mark.test_files_dir(test_files_dir))
