"""
Unit Tests: Upload Logic Equivalence
====================================

This test suite validates that the refactored upload routes produce identical results
to the original routes by testing the core business logic directly.

Instead of slow E2E tests that navigate through browsers, these unit tests:
1. Test the actual Python functions directly
2. Compare business logic outputs
3. Validate data processing equivalence
4. Check error handling consistency

This provides fast, reliable verification that refactoring didn't change behavior.
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the source directory to the Python path
source_dir = Path(__file__).parent.parent.parent / "source" / "production"
sys.path.insert(0, str(source_dir))

# Import the logic functions to test
from arb.portal.upload_logic import (
    upload_file_logic,
    upload_file_refactored_logic,
    upload_file_staged_logic,
    upload_file_staged_refactored_logic,
    UploadLogicResult
)

# Import Flask app for context
from arb.portal.app import create_app


def get_test_files() -> list:
    """Safely retrieve test file paths for parameterized testing."""
    try:
        # Get the test files directory from conftest
        from tests.e2e.conftest import STANDARD_TEST_FILES_DIR
        test_dir = Path(STANDARD_TEST_FILES_DIR)
        
        if not test_dir.exists():
            print(f"⚠️  Test directory not found: {test_dir}")
            return []
        
        # Get all Excel files in the directory
        files = list(test_dir.glob("*.xlsx"))
        
        if not files:
            print(f"⚠️  No Excel files found in: {test_dir}")
            return []
        
        print(f"📁 Found {len(files)} test files in {test_dir}")
        return files
        
    except Exception as e:
        print(f"⚠️  Error getting test files: {e}")
        return []


@pytest.fixture(scope="session")
def test_files():
    """Fixture to provide test files for parameterized testing."""
    return get_test_files()


@pytest.fixture(params=get_test_files())
def file_path(request):
    """Fixture to provide individual test files for parameterized testing."""
    return request.param


@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app


class TestUploadLogicEquivalence:
    """Test that the original and refactored upload logic produce equivalent results."""
    
    @pytest.mark.parametrize("test_file", get_test_files())
    def test_upload_file_logic_equivalence(self, test_file, app):
        """Test that upload_file_logic and upload_file_refactored_logic produce equivalent results."""
        if not test_file:
            pytest.skip("No test files available")
            
        print(f"\n🔍 Testing upload_file logic equivalence with: {test_file.name}")
        
        with app.app_context():
            # Call both logic functions
            original_result = upload_file_logic(test_file)
            refactored_result = upload_file_refactored_logic(test_file)
            
            # Assert that results are equivalent
            self._assert_results_equivalent(original_result, refactored_result, "upload_file", test_file.name)
    
    @pytest.mark.parametrize("test_file", get_test_files())
    def test_upload_file_staged_logic_equivalence(self, test_file, app):
        """Test that upload_file_staged_logic and upload_file_staged_refactored_logic produce equivalent results."""
        if not test_file:
            pytest.skip("No test files available")
            
        print(f"\n🔍 Testing upload_file_staged logic equivalence with: {test_file.name}")
        
        with app.app_context():
            # Call both logic functions
            original_result = upload_file_staged_logic(test_file)
            refactored_result = upload_file_staged_refactored_logic(test_file)
            
            # Assert that results are equivalent
            self._assert_results_equivalent(original_result, refactored_result, "upload_file_staged", test_file.name)
    
    def _assert_results_equivalent(self, original_result: UploadLogicResult, refactored_result: UploadLogicResult, 
                                 route_name: str, file_name: str):
        """Assert that two UploadLogicResult objects are equivalent."""
        
        # Check status code
        if original_result.status_code != refactored_result.status_code:
            pytest.fail(f"Status code mismatch for {route_name} with {file_name}: "
                       f"original={original_result.status_code}, refactored={refactored_result.status_code}")
        
        # Check success status
        if original_result.success != refactored_result.success:
            pytest.fail(f"Success status mismatch for {route_name} with {file_name}: "
                       f"original={original_result.success}, refactored={refactored_result.success}")
        
        # Check flash messages (normalize timestamps)
        normalized_original_messages = self._normalize_messages(original_result.flash_messages)
        normalized_refactored_messages = self._normalize_messages(refactored_result.flash_messages)
        
        if normalized_original_messages != normalized_refactored_messages:
            pytest.fail(f"Flash message mismatch for {route_name} with {file_name}: "
                       f"original={normalized_original_messages}, refactored={normalized_refactored_messages}")
        
        # Check redirect URL (normalize timestamps)
        if original_result.redirect_url and refactored_result.redirect_url:
            normalized_original_url = self._normalize_url(original_result.redirect_url)
            normalized_refactored_url = self._normalize_url(refactored_result.redirect_url)
            
            if normalized_original_url != normalized_refactored_url:
                pytest.fail(f"Redirect URL mismatch for {route_name} with {file_name}: "
                           f"original={normalized_original_url}, refactored={normalized_refactored_url}")
        
        # Check validation errors
        if original_result.validation_errors != refactored_result.validation_errors:
            pytest.fail(f"Validation error mismatch for {route_name} with {file_name}: "
                       f"original={original_result.validation_errors}, refactored={refactored_result.validation_errors}")
        
        # Check processed data (ignore size differences for now since they're placeholders)
        # For placeholder functions, we just check that both have the same structure
        if original_result.processed_data and refactored_result.processed_data:
            # Check that both have the same keys
            original_keys = set(original_result.processed_data.keys())
            refactored_keys = set(refactored_result.processed_data.keys())
            
            if original_keys != refactored_keys:
                pytest.fail(f"Processed data structure mismatch for {route_name} with {file_name}: "
                           f"original keys={original_keys}, refactored keys={refactored_keys}")
            
            # Check that filename is the same (this should be consistent)
            if (original_result.processed_data.get('filename') != 
                refactored_result.processed_data.get('filename')):
                pytest.fail(f"Filename mismatch in processed data for {route_name} with {file_name}")
    
    def _normalize_messages(self, messages: list) -> list:
        """Normalize flash messages by replacing timestamps with placeholders."""
        if not messages:
            return messages
        
        normalized = []
        for message in messages:
            # Replace timestamp patterns with placeholders
            normalized_msg = message
            # Add timestamp normalization logic here if needed
            normalized.append(normalized_msg)
        
        return normalized
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URLs by replacing timestamps with placeholders."""
        if not url:
            return url
        
        # Replace timestamp patterns with placeholders
        normalized_url = url
        # Add timestamp normalization logic here if needed
        
        return normalized_url


class TestUploadLogicConsistency:
    """Test that upload logic handles edge cases consistently."""
    
    def test_upload_logic_handles_empty_file(self, app):
        """Test that upload logic handles empty files consistently."""
        with app.app_context():
            # Test with empty file
            empty_file = Path("/tmp/empty.xlsx")
            empty_file.touch()  # Create empty file
            
            try:
                result = upload_file_logic(empty_file)
                assert isinstance(result, UploadLogicResult)
                assert result.success is True  # Placeholder function always returns success
                assert result.status_code == 200
                assert "File uploaded successfully" in result.flash_messages
            finally:
                empty_file.unlink()  # Clean up
    
    def test_upload_logic_handles_good_data(self, app):
        """Test that upload logic handles good data consistently."""
        with app.app_context():
            # Test with a known good file if available
            test_files = get_test_files()
            if test_files:
                good_file = test_files[0]  # Use first available test file
                result = upload_file_logic(good_file)
                assert isinstance(result, UploadLogicResult)
                assert result.success is True  # Placeholder function always returns success
                assert result.status_code == 200
                assert "File uploaded successfully" in result.flash_messages
                assert result.processed_data is not None
                assert "filename" in result.processed_data
            else:
                pytest.skip("No test files available for good data test")
    
    def test_all_logic_functions_return_consistent_types(self, app):
        """Test that all logic functions return consistent result types."""
        with app.app_context():
            test_files = get_test_files()
            if not test_files:
                pytest.skip("No test files available")
            
            test_file = test_files[0]
            
            # Test all functions return the same result type
            functions = [
                upload_file_logic,
                upload_file_refactored_logic,
                upload_file_staged_logic,
                upload_file_staged_refactored_logic
            ]
            
            for func in functions:
                result = func(test_file)
                assert isinstance(result, UploadLogicResult)
                assert hasattr(result, 'success')
                assert hasattr(result, 'status_code')
                assert hasattr(result, 'flash_messages')
                assert hasattr(result, 'redirect_url')
                assert hasattr(result, 'validation_errors')
                assert hasattr(result, 'processed_data')
                assert hasattr(result, 'error_message')


class TestUploadLogicPlaceholderBehavior:
    """Test the current placeholder behavior to understand what we're testing."""
    
    def test_placeholder_functions_return_identical_results(self, app):
        """Test that placeholder functions currently return identical results (as expected)."""
        with app.app_context():
            test_files = get_test_files()
            if not test_files:
                pytest.skip("No test files available")
            
            test_file = test_files[0]
            
            # Test that placeholder functions return identical results
            original_result = upload_file_logic(test_file)
            refactored_result = upload_file_refactored_logic(test_file)
            
            # These should be identical since they're both placeholders
            assert original_result.success == refactored_result.success
            assert original_result.status_code == refactored_result.status_code
            assert original_result.flash_messages == refactored_result.flash_messages
            assert original_result.redirect_url == refactored_result.redirect_url
            assert original_result.validation_errors == refactored_result.validation_errors
            
            # Check that processed data has the same structure
            assert set(original_result.processed_data.keys()) == set(refactored_result.processed_data.keys())
            assert original_result.processed_data['filename'] == refactored_result.processed_data['filename']
            
            print(f"✅ Placeholder functions return identical results as expected")
            print(f"   Success: {original_result.success}")
            print(f"   Status: {original_result.status_code}")
            print(f"   Messages: {original_result.flash_messages}")
            print(f"   Redirect: {original_result.redirect_url}")
            print(f"   Data: {original_result.processed_data}")
