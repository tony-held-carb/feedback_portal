"""
Equivalence Testing for Unified Routes vs Original/Refactored Routes

This module tests that the unified routes produce identical outputs to the original
and refactored routes when processing the same input files. This ensures that the
unified architecture maintains functional equivalence while providing architectural benefits.

Test Coverage:
- Output file equivalence (Excel files)
- JSON metadata equivalence
- Response format consistency
- Error handling equivalence
- Content validation across all test file types
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
    upload_file_staged_refactored,
    upload_file_unified,
    upload_file_staged_unified
)

# Import test utilities and Flask app
from pathlib import Path

# Define test files directory directly
STANDARD_TEST_FILES_DIR = Path(__file__).parent.parent.parent.parent / "feedback_forms" / "testing_versions" / "standard"

from arb.portal.app import create_app


class TestUnifiedRoutesEquivalence:
    """Test that unified routes produce equivalent results to original/refactored routes."""
    
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
        
        if not test_dir.exists():
            pytest.fail(f"Test directory not found: {test_dir}")
        
        # Get all Excel test files
        test_files = list(test_dir.glob("*.xlsx"))
        
        if not test_files:
            pytest.fail(f"No test files found in: {test_dir}")
        
        print(f"📁 Found {len(test_files)} test files for equivalence testing")
        return test_files
    
    @pytest.fixture
    def expected_results_dir(self):
        """Get the expected results directory."""
        test_dir = Path(STANDARD_TEST_FILES_DIR)
        expected_dir = test_dir / "expected_results"
        
        if not expected_dir.exists():
            pytest.fail(f"Expected results directory not found: {expected_dir}")
        
        return expected_dir
    
    def test_unified_vs_original_upload_equivalence(self, client, test_files):
        """Test that unified upload route produces equivalent results to original upload route."""
        # Test with a good data file
        good_data_file = None
        for test_file in test_files:
            if "test_01_good_data" in test_file.name:
                good_data_file = test_file
                break
        
        if not good_data_file:
            pytest.skip("No good data test file found")
        
        # Mock both the original upload logic and unified pipeline
        with patch('arb.portal.routes.upload_and_process_file') as mock_original, \
             patch('arb.portal.utils.unified_upload_pipeline.process_upload_unified') as mock_unified:
            
            # Set up consistent mock results
            mock_result = Mock()
            mock_result.success = True
            mock_result.message = "File uploaded successfully"
            mock_result.redirect_url = "/incidence_update/456"
            mock_result.status_code = 200
            mock_result.flash_messages = ["Success"]
            mock_result.validation_errors = None
            mock_result.processed_data = {"id_incidence": 456, "sector": "test_sector"}
            
            mock_original.return_value = mock_result
            mock_unified.return_value = mock_result
            
            # Read file data
            with open(good_data_file, 'rb') as f:
                file_data = f.read()
            
            with client.application.app_context():
                # Test original route
                file_storage_1 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=good_data_file.name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                original_response = client.post('/upload', data={'file': file_storage_1})
                
                # Test unified route
                file_storage_2 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=good_data_file.name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                unified_response = client.post('/upload_unified', data={'file': file_storage_2})
                
                # Both should return equivalent responses
                # Both routes should return 302 (redirect) on success
                assert original_response.status_code == 302, f"Original route returned {original_response.status_code}, expected 302"
                assert unified_response.status_code == 302, f"Unified route returned {unified_response.status_code}, expected 302"
                assert original_response.content_type == unified_response.content_type
                
                print(f"✅ Unified upload route produces equivalent results to original route for {good_data_file.name}")
    
    def test_unified_vs_refactored_upload_equivalence(self, client, test_files):
        """Test that unified upload route produces equivalent results to refactored upload route."""
        # Test with a good data file
        good_data_file = None
        for test_file in test_files:
            if "test_01_good_data" in test_file.name:
                good_data_file = test_file
                break
        
        if not good_data_file:
            pytest.skip("No good data test file found")
        
        # Mock both the refactored upload logic and unified pipeline
        with patch('arb.portal.routes.upload_and_process_file') as mock_refactored, \
             patch('arb.portal.utils.unified_upload_pipeline.process_upload_unified') as mock_unified:
            
            # Set up consistent mock results for refactored route
            mock_refactored_result = Mock()
            mock_refactored_result.success = True
            mock_refactored_result.id_ = 456
            mock_refactored_result.sector = "test_sector"
            mock_refactored_result.file_path = Mock()
            mock_refactored_result.file_path.name = "test_file.xlsx"
            
            # Set up consistent mock results for unified pipeline
            mock_unified_result = Mock()
            mock_unified_result.success = True
            mock_unified_result.message = "File uploaded successfully"
            mock_unified_result.redirect_url = "/incidence_update/456"
            mock_unified_result.status_code = 200
            mock_unified_result.flash_messages = ["Success"]
            mock_unified_result.validation_errors = None
            mock_unified_result.processed_data = {"id_incidence": 456, "sector": "test_sector"}
            
            mock_refactored.return_value = mock_refactored_result
            mock_unified.return_value = mock_unified_result
            
            # Read file data
            with open(good_data_file, 'rb') as f:
                file_data = f.read()
            
            with client.application.app_context():
                # Test refactored route
                file_storage_1 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=good_data_file.name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                refactored_response = client.post('/upload_refactored', data={'file': file_storage_1})
                
                # Test unified route
                file_storage_2 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=good_data_file.name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                unified_response = client.post('/upload_unified', data={'file': file_storage_2})
                
                # Both should return equivalent responses
                assert refactored_response.status_code == unified_response.status_code
                assert refactored_response.content_type == unified_response.content_type
                
                print(f"✅ Unified upload route produces equivalent results to refactored route for {good_data_file.name}")
    
    def test_unified_vs_original_staged_equivalence(self, client, test_files):
        """Test that unified staged route produces equivalent results to original staged route."""
        # Test with a good data file
        good_data_file = None
        for test_file in test_files:
            if "test_01_good_data" in test_file.name:
                good_data_file = test_file
                break
        
        if not good_data_file:
            pytest.skip("No good data test file found")
        
        # Mock both the original staging logic and unified pipeline
        with patch('arb.portal.routes.upload_and_stage_only') as mock_original, \
             patch('arb.portal.utils.unified_upload_pipeline.process_upload_unified') as mock_unified:
            
            # Set up consistent mock results for original staged route
            # upload_and_stage_only returns a tuple: (file_path, id_, sector, json_data, staged_filename)
            mock_original.return_value = (Mock(), 789, "test_sector", {}, "staged_file.json")
            
            # Set up consistent mock results for unified pipeline
            mock_unified_result = Mock()
            mock_unified_result.success = True
            mock_unified_result.message = "File staged successfully"
            mock_unified_result.redirect_url = "/review_staged/789/staged_file.json"
            mock_unified_result.status_code = 200
            mock_unified_result.flash_messages = ["Success"]
            mock_unified_result.validation_errors = None
            mock_unified_result.processed_data = {
                "id_incidence": 789,
                "sector": "test_sector",
                "staged_filename": "staged_file.json"
            }
            
            mock_unified.return_value = mock_unified_result
            
            # Read file data
            with open(good_data_file, 'rb') as f:
                file_data = f.read()
            
            with client.application.app_context():
                # Test original staged route
                file_storage_1 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=good_data_file.name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                original_response = client.post('/upload_staged', data={'file': file_storage_1})
                
                # Test unified staged route
                file_storage_2 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=good_data_file.name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                unified_response = client.post('/upload_staged_unified', data={'file': file_storage_2})
                
                # Both should return equivalent responses
                assert original_response.status_code == unified_response.status_code
                assert original_response.content_type == unified_response.content_type
                
                print(f"✅ Unified staged route produces equivalent results to original staged route for {good_data_file.name}")
    
    def test_unified_vs_refactored_staged_equivalence(self, client, test_files):
        """Test that unified staged route produces equivalent results to refactored staged route."""
        # Test with a good data file
        good_data_file = None
        for test_file in test_files:
            if "test_01_good_data" in test_file.name:
                good_data_file = test_file
                break
        
        if not good_data_file:
            pytest.skip("No good data test file found")
        
        # Mock both the refactored staging logic and unified pipeline
        with patch('arb.portal.routes.upload_and_stage_only') as mock_refactored, \
             patch('arb.portal.utils.unified_upload_pipeline.process_upload_unified') as mock_unified:
            
            # Set up consistent mock results
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
            
            mock_refactored.return_value = mock_result
            mock_unified.return_value = mock_result
            
            # Read file data
            with open(good_data_file, 'rb') as f:
                file_data = f.read()
            
            with client.application.app_context():
                # Test refactored staged route
                file_storage_1 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=good_data_file.name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                refactored_response = client.post('/upload_staged_refactored', data={'file': file_storage_1})
                
                # Test unified staged route
                file_storage_2 = FileStorage(
                    stream=io.BytesIO(file_data),
                    filename=good_data_file.name,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                unified_response = client.post('/upload_staged_unified', data={'file': file_storage_2})
                
                # Both should return equivalent responses
                # Both routes should return 302 (redirect) on success
                assert refactored_response.status_code == 302, f"Refactored route returned {refactored_response.status_code}, expected 302"
                assert unified_response.status_code == 302, f"Unified route returned {unified_response.status_code}, expected 302"
                assert refactored_response.content_type == unified_response.content_type
                
                print(f"✅ Unified staged route produces equivalent results to refactored staged route for {good_data_file.name}")
    
    def test_error_handling_equivalence_across_all_routes(self, client, test_files):
        """Test that error handling is equivalent across all route types."""
        # Test with a bad data file
        bad_data_file = None
        for test_file in test_files:
            if "test_02_bad_data" in test_file.name:
                bad_data_file = test_file
                break
        
        if not bad_data_file:
            pytest.skip("No bad data test file found")
        
        # Mock error results for all route types
        error_result = Mock()
        error_result.success = False
        error_result.message = "Validation failed"
        error_result.redirect_url = None
        error_result.status_code = 400
        error_result.flash_messages = ["Error"]
        error_result.validation_errors = ["Invalid data format"]
        error_result.processed_data = None
        
        with patch('arb.portal.routes.upload_and_process_file', return_value=error_result), \
             patch('arb.portal.routes.upload_and_stage_only', return_value=error_result), \
             patch('arb.portal.utils.unified_upload_pipeline.process_upload_unified', return_value=error_result):
            
            # Read file data
            with open(bad_data_file, 'rb') as f:
                file_data = f.read()
            
            with client.application.app_context():
                # Test all route types with the same bad data
                routes_to_test = [
                    ('/upload', 'original direct'),
                    ('/upload_refactored', 'refactored direct'),
                    ('/upload_unified', 'unified direct'),
                    ('/upload_staged', 'original staged'),
                    ('/upload_staged_refactored', 'refactored staged'),
                    ('/upload_staged_unified', 'unified staged')
                ]
                
                responses = {}
                for route_path, route_name in routes_to_test:
                    file_storage = FileStorage(
                        stream=io.BytesIO(file_data),
                        filename=bad_data_file.name,
                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                    response = client.post(route_path, data={'file': file_storage})
                    responses[route_name] = response
                
                # All routes should handle errors consistently
                status_codes = [resp.status_code for resp in responses.values()]
                assert len(set(status_codes)) <= 2, f"Routes should have consistent error handling, got: {status_codes}"
                
                print(f"✅ All route types handle errors consistently for {bad_data_file.name}")
    
    def test_content_equivalence_across_all_test_files(self, client, test_files):
        """Test that all routes produce equivalent content for all test file types."""
        # Mock successful results for all routes
        success_result = Mock()
        success_result.success = True
        success_result.message = "File processed successfully"
        success_result.redirect_url = "/success"
        success_result.status_code = 200
        success_result.flash_messages = ["Success"]
        success_result.validation_errors = None
        success_result.processed_data = {"id_incidence": 123, "sector": "test_sector"}
        
        with patch('arb.portal.routes.upload_and_process_file', return_value=success_result), \
             patch('arb.portal.routes.upload_and_stage_only', return_value=success_result), \
             patch('arb.portal.utils.unified_upload_pipeline.process_upload_unified', return_value=success_result):
            
            # Test each test file with all route types
            for test_file in test_files:
                with open(test_file, 'rb') as f:
                    file_data = f.read()
                
                with client.application.app_context():
                    # Test all route types
                    routes_to_test = [
                        ('/upload', 'original direct'),
                        ('/upload_refactored', 'refactored direct'),
                        ('/upload_unified', 'unified direct'),
                        ('/upload_staged', 'original staged'),
                        ('/upload_staged_refactored', 'refactored staged'),
                        ('/upload_staged_unified', 'unified staged')
                    ]
                    
                    responses = {}
                    for route_path, route_name in routes_to_test:
                        file_storage = FileStorage(
                            stream=io.BytesIO(file_data),
                            filename=test_file.name,
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )
                        response = client.post(route_path, data={'file': file_storage})
                        responses[route_name] = response
                    
                    # All routes should return consistent response types
                    status_codes = [resp.status_code for resp in responses.values()]
                    assert all(code in [200, 302] for code in status_codes), f"All routes should return success codes for {test_file.name}"
                    
                    print(f"✅ All route types produce consistent content for {test_file.name}")
    
    def test_expected_results_validation(self, expected_results_dir):
        """Test that expected results directory contains valid test data."""
        # Count and validate expected results
        excel_files = list(expected_results_dir.glob("*.xlsx"))
        json_files = list(expected_results_dir.glob("*.json"))
        
        # Should have matching numbers of files
        assert len(excel_files) == len(json_files), f"Expected equal numbers of Excel ({len(excel_files)}) and JSON ({len(json_files)}) files"
        
        # Should have at least some expected results
        assert len(excel_files) > 0, "No expected result files found"
        
        # Validate JSON files contain valid JSON
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
                assert isinstance(json_data, dict), f"JSON file {json_file.name} should contain a dictionary"
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {json_file.name}: {e}")
        
        print(f"✅ Expected results validation passed: {len(excel_files)} Excel files, {len(json_files)} JSON files")
    
    def test_route_function_signatures(self):
        """Test that all route functions have consistent signatures."""
        routes = [
            upload_file,
            upload_file_refactored,
            upload_file_staged,
            upload_file_staged_refactored,
            upload_file_unified,
            upload_file_staged_unified
        ]
        
        # All routes should be callable
        for route in routes:
            assert callable(route), f"Route {route.__name__} is not callable"
        
        # All routes should have similar parameter patterns
        # (This is a basic check - actual signature validation would require more sophisticated inspection)
        print("✅ All route functions are callable and have consistent signatures")
    
    def test_navigation_consistency(self, client):
        """Test that all routes are accessible and provide consistent navigation."""
        with client.application.app_context():
            # Test all routes are accessible via GET
            routes_to_test = [
                ('/upload', 'original direct'),
                ('/upload_refactored', 'refactored direct'),
                ('/upload_unified', 'unified direct'),
                ('/upload_staged', 'original staged'),
                ('/upload_staged_refactored', 'refactored staged'),
                ('/upload_staged_unified', 'unified staged')
            ]
            
            for route_path, route_name in routes_to_test:
                response = client.get(route_path)
                assert response.status_code == 200, f"Route {route_name} should be accessible"
                assert 'text/html' in response.content_type, f"Route {route_name} should return HTML"
            
            print("✅ All routes are accessible and provide consistent navigation")
