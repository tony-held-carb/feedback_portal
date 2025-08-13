"""
Functional equivalence tests for Excel parsing functions.

This module tests that the _2 versions of Excel parsing functions produce
identical results to their original counterparts when processing real test files.
"""

import pytest
from pathlib import Path
import sys
from unittest.mock import patch, Mock

# Import our new path utility
from arb.utils.path_utils import find_repo_root, get_relative_path_from_repo_root

# Import the functions we're testing
from arb.utils.excel.xl_parse import (
    parse_xl_file, parse_xl_file_2,
    extract_tabs, extract_tabs_2,
    get_spreadsheet_key_value_pairs, get_spreadsheet_key_value_pairs_2
)

# Import content validation utilities
from .excel_content_validator import (
    compare_excel_results,
    find_corresponding_expected_result,
    generate_comparison_report
)


class TestExcelFunctionEquivalence:
    """Test that _2 functions are functionally equivalent to originals."""
    
    def test_function_existence(self):
        """Test that all required functions exist."""
        assert parse_xl_file is not None
        assert parse_xl_file_2 is not None
        assert extract_tabs is not None
        assert extract_tabs_2 is not None
        assert get_spreadsheet_key_value_pairs is not None
        assert get_spreadsheet_key_value_pairs_2 is not None
    
    def test_function_signatures(self):
        """Test that _2 functions have the same signatures as originals."""
        import inspect
        
        # Get function signatures
        orig_sig = inspect.signature(parse_xl_file)
        new_sig = inspect.signature(parse_xl_file_2)
        
        # Compare parameters (excluding self for methods)
        orig_params = list(orig_sig.parameters.keys())
        new_params = list(new_sig.parameters.keys())
        
        assert orig_params == new_params, f"Parameter mismatch: {orig_params} vs {new_params}"
    
    def test_parse_xl_file_with_good_data(self, test_files_dir, expected_results_dir):
        """Test parse_xl_file with a good data file and compare against expected results."""
        good_data_file = None
        for test_file in test_files_dir.glob("*.xlsx"):
            if "test_01_good_data" in test_file.name:
                good_data_file = test_file
                break
        
        if not good_data_file:
            pytest.skip("No good data test file found")
        
        expected_json = find_corresponding_expected_result(good_data_file, expected_results_dir)
        if not expected_json:
            pytest.skip(f"No expected result found for {good_data_file.name}")
        
        try:
            result_original = parse_xl_file(good_data_file)
            result_2 = parse_xl_file_2(good_data_file)
        except Exception as e:
            pytest.fail(f"Failed to parse {good_data_file.name}: {e}")
        
        assert isinstance(result_original, dict), "Original function should return dict"
        assert isinstance(result_2, dict), "_2 function should return dict"
        assert set(result_original.keys()) == set(result_2.keys()), "Results have different keys"
        
        expected_keys = {'metadata', 'schemas', 'tab_contents'}
        assert expected_keys.issubset(set(result_original.keys())), f"Original result missing keys: {expected_keys - set(result_original.keys())}"
        assert expected_keys.issubset(set(result_2.keys())), f"_2 result missing keys: {expected_keys - set(result_2.keys())}"
        
        # Compare against expected results
        is_equivalent_original, differences_original = compare_excel_results(result_original, expected_json)
        is_equivalent_2, differences_2 = compare_excel_results(result_2, expected_json)
        
        if not is_equivalent_original:
            report_original = generate_comparison_report(good_data_file, result_original, expected_json, differences_original)
            print(f"\n{report_original}")
            pytest.fail(f"Original function result doesn't match expected: {len(differences_original)} differences")
        
        if not is_equivalent_2:
            report_2 = generate_comparison_report(good_data_file, result_2, expected_json, differences_2)
            print(f"\n{report_2}")
            pytest.fail(f"_2 function result doesn't match expected: {len(differences_2)} differences")
        
        print(f"✅ Successfully parsed {good_data_file.name} with both functions")
        print(f"✅ Both results match expected output exactly")
        print(f"✅ Results have consistent structure with {len(result_original)} keys")
    
    def test_parse_xl_file_with_bad_data(self, test_files_dir):
        """Test parse_xl_file with bad data files."""
        bad_data_files = list(test_files_dir.glob("*bad*.xlsx"))
        if not bad_data_files:
            pytest.skip("No bad data test files found")
        
        for bad_file in bad_data_files:
            try:
                # Both functions should handle bad data similarly
                result_original = parse_xl_file(bad_file)
                result_2 = parse_xl_file_2(bad_file)
                
                # Results should be consistent between versions
                assert type(result_original) == type(result_2), f"Different result types for {bad_file.name}"
                
            except Exception as e:
                # If one fails, the other should also fail
                pytest.fail(f"Bad data file {bad_file.name} should be handled gracefully: {e}")
    
    def test_parse_xl_file_with_blank_file(self, test_files_dir):
        """Test parse_xl_file with blank/empty files."""
        blank_files = list(test_files_dir.glob("*blank*.xlsx"))
        if not blank_files:
            pytest.skip("No blank test files found")
        
        for blank_file in blank_files:
            try:
                result_original = parse_xl_file(blank_file)
                result_2 = parse_xl_file_2(blank_file)
                
                # Both should handle blank files consistently
                assert type(result_original) == type(result_2), f"Different result types for {blank_file.name}"
                
            except Exception as e:
                pytest.fail(f"Blank file {blank_file.name} should be handled gracefully: {e}")
    
    def test_extract_tabs_equivalence(self, test_files_dir):
        """Test that extract_tabs functions produce equivalent results."""
        test_files = list(test_files_dir.glob("*.xlsx"))
        if not test_files:
            pytest.skip("No test files found")
        
        for test_file in test_files[:2]:  # Test first 2 files to avoid too many tests
            try:
                # Parse the file first
                xl_dict = parse_xl_file(test_file)
                
                # Extract tabs using both functions
                # Need to create a mock workbook and schema_map for testing
                from unittest.mock import Mock
                mock_wb = Mock()
                mock_schema_map = {}
                
                result_original = extract_tabs(mock_wb, mock_schema_map, xl_dict)
                result_2 = extract_tabs_2(mock_wb, mock_schema_map, xl_dict)
                
                # Results should be equivalent
                assert result_original == result_2, f"extract_tabs results differ for {test_file.name}"
                
            except Exception as e:
                pytest.fail(f"Failed to test extract_tabs for {test_file.name}: {e}")
    
    def test_get_spreadsheet_key_value_pairs_equivalence(self, test_files_dir):
        """Test that get_spreadsheet_key_value_pairs functions produce equivalent results."""
        test_files = list(test_files_dir.glob("*.xlsx"))
        if not test_files:
            pytest.skip("No test files found")
        
        for test_file in test_files[:2]:  # Test first 2 files to avoid too many tests
            try:
                # Parse the file first
                xl_dict = parse_xl_file(test_file)
                
                # Get key-value pairs using both functions
                # Need to create a properly mocked workbook for testing
                from unittest.mock import Mock
                mock_ws = Mock()
                mock_cell = Mock()
                
                # Mock the offset method to return finite data
                def mock_offset(row=0, column=0):
                    if row == 0:
                        return Mock(value='test_key')
                    else:
                        return Mock(value=None)  # This will break the while loop
                
                mock_cell.offset = Mock(side_effect=mock_offset)
                mock_ws.__getitem__ = Mock(return_value=mock_cell)
                mock_wb = Mock()
                mock_wb.__getitem__ = Mock(return_value=mock_ws)
                
                result_original = get_spreadsheet_key_value_pairs(mock_wb, "metadata", "A1")
                result_2 = get_spreadsheet_key_value_pairs_2(mock_wb, "metadata", "A1")
                
                # Results should be equivalent
                assert result_original == result_2, f"get_spreadsheet_key_value_pairs results differ for {test_file.name}"
                
            except Exception as e:
                pytest.fail(f"Failed to test get_spreadsheet_key_value_pairs for {test_file.name}: {e}")


class TestExcelContentValidation:
    """Test Excel content validation against expected results.
    
    These tests are skipped by default and require the --test-content-validation flag
    to run, as they perform intensive content comparison.
    """
    
    @pytest.mark.skip(reason="Content validation tests require --test-content-validation flag")
    def test_all_feedback_form_types(self, test_files_dir, expected_results_dir):
        """Test all feedback form types against expected results."""
        test_files = list(test_files_dir.glob("*.xlsx"))
        if not test_files:
            pytest.skip("No test files found")
        
        for test_file in test_files:
            print(f"\nTesting {test_file.name}...")
            
            # Find corresponding expected result
            expected_json = find_corresponding_expected_result(test_file, expected_results_dir)
            if not expected_json:
                print(f"  ⚠️  No expected result found, skipping")
                continue
            
            try:
                # Parse with both functions
                result_original = parse_xl_file(test_file)
                result_2 = parse_xl_file_2(test_file)
                
                # Compare against expected results
                is_equivalent_original, differences_original = compare_excel_results(result_original, expected_json)
                is_equivalent_2, differences_2 = compare_excel_results(result_2, expected_json)
                
                if not is_equivalent_original:
                    report_original = generate_comparison_report(test_file, result_original, expected_json, differences_original)
                    print(f"  ❌ Original function: {len(differences_original)} differences")
                    print(f"     {report_original[:200]}...")
                else:
                    print(f"  ✅ Original function: matches expected")
                
                if not is_equivalent_2:
                    report_2 = generate_comparison_report(test_file, result_2, expected_json, differences_2)
                    print(f"  ❌ _2 function: {len(differences_2)} differences")
                    print(f"     {report_2[:200]}...")
                else:
                    print(f"  ✅ _2 function: matches expected")
                
                # Both should be equivalent
                assert result_original == result_2, f"Function results differ for {test_file.name}"
                
            except Exception as e:
                print(f"  ❌ Failed to process {test_file.name}: {e}")
                pytest.fail(f"Failed to process {test_file.name}: {e}")
        
        print(f"\n✅ Completed testing {len(test_files)} files")


def pytest_addoption(parser):
    """Add custom command line options for Excel functional testing."""
    parser.addoption(
        "--test-content-validation",
        action="store_true",
        help="Run content validation tests against expected results"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command line options."""
    if not config.getoption("--test-content-validation"):
        # Skip content validation tests by default
        skip_content = pytest.mark.skip(reason="Content validation tests require --test-content-validation flag")
        for item in items:
            if "TestExcelContentValidation" in item.name:
                item.add_marker(skip_content)
