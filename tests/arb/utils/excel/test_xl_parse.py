"""
Unit tests for xl_parse.py functions.

This module provides comprehensive testing of the Excel parsing functionality,
including edge cases, error scenarios, and validation.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Import our new path utility
from arb.utils.path_utils import find_repo_root, get_relative_path_from_repo_root

# Import the functions we're testing
from arb.utils.excel.xl_parse import (
    parse_xl_file, parse_xl_file_2,
    extract_tabs, extract_tabs_2,
    get_spreadsheet_key_value_pairs, get_spreadsheet_key_value_pairs_2,
    ensure_schema, split_compound_keys, convert_upload_to_json, get_json_file_name_old
)


class TestParseXlFile:
    """Test parse_xl_file function."""
    
    def test_function_exists(self):
        """Test that parse_xl_file function exists."""
        assert callable(parse_xl_file)
    
    def test_function_signature(self):
        """Test that parse_xl_file has the expected signature."""
        import inspect
        sig = inspect.signature(parse_xl_file)
        params = list(sig.parameters.keys())
        expected_params = ['xl_path', 'schema_map']
        assert params == expected_params, f"Expected parameters {expected_params}, got {params}"
    
    @patch('arb.utils.excel.xl_parse.openpyxl.load_workbook')
    def test_parse_xl_file_with_mock_data(self, mock_load_workbook):
        """Test parse_xl_file with mock workbook data."""
        # Mock workbook
        mock_wb = Mock()
        mock_wb.sheetnames = ['metadata', 'schema', 'data']
        
        # Mock worksheets
        mock_metadata_ws = Mock()
        mock_schema_ws = Mock()
        mock_data_ws = Mock()
        
        # Mock cell values
        mock_metadata_ws.__getitem__ = Mock(return_value=Mock(value='test_sector'))
        mock_schema_ws.__getitem__ = Mock(return_value=Mock(value='test_schema'))
        mock_data_ws.__getitem__ = Mock(value='test_value')
        
        # Mock workbook access
        mock_wb.__getitem__ = Mock(side_effect=lambda x: {
            'metadata': mock_metadata_ws,
            'schema': mock_schema_ws,
            'data': mock_data_ws
        }[x])
        
        mock_load_workbook.return_value = mock_wb
        
        # Mock dependencies
        with patch('arb.utils.excel.xl_parse.get_spreadsheet_key_value_pairs') as mock_get_kv, \
             patch('arb.utils.excel.xl_parse.extract_tabs') as mock_extract:
            
            mock_get_kv.return_value = {'test_key': 'test_value'}
            mock_extract.return_value = {'metadata': {'test_key': 'test_value'}, 'schemas': {'data': 'test_schema'}, 'tab_contents': {'test_tab': {'test_field': 'test_value'}}}
            
            # Test the function
            result = parse_xl_file('test.xlsx')
            
            assert isinstance(result, dict)
            assert 'metadata' in result
            assert 'schemas' in result
            assert 'tab_contents' in result
    
    def test_parse_xl_file_with_invalid_path(self):
        """Test parse_xl_file with invalid file path."""
        with pytest.raises(Exception):
            parse_xl_file('nonexistent_file.xlsx')


class TestParseXlFile2:
    """Test parse_xl_file_2 function."""
    
    def test_function_exists(self):
        """Test that parse_xl_file_2 function exists."""
        assert callable(parse_xl_file_2)
    
    def test_function_signature(self):
        """Test that parse_xl_file_2 has the expected signature."""
        import inspect
        sig = inspect.signature(parse_xl_file_2)
        params = list(sig.parameters.keys())
        expected_params = ['xl_path', 'schema_map']
        assert params == expected_params, f"Expected parameters {expected_params}, got {params}"
    
    @patch('arb.utils.excel.xl_parse.openpyxl.load_workbook')
    def test_parse_xl_file_2_with_mock_data(self, mock_load_workbook):
        """Test parse_xl_file_2 with mock workbook data."""
        # Mock workbook
        mock_wb = Mock()
        mock_wb.sheetnames = ['metadata', 'schema', 'data']
        
        # Mock worksheets
        mock_metadata_ws = Mock()
        mock_schema_ws = Mock()
        mock_data_ws = Mock()
        
        # Mock cell values
        mock_metadata_ws.__getitem__ = Mock(return_value=Mock(value='test_sector'))
        mock_schema_ws.__getitem__ = Mock(return_value=Mock(value='test_schema'))
        mock_data_ws.__getitem__ = Mock(value='test_value')
        
        # Mock workbook access
        mock_wb.__getitem__ = Mock(side_effect=lambda x: {
            'metadata': mock_metadata_ws,
            'schema': mock_schema_ws,
            'data': mock_data_ws
        }[x])
        
        mock_load_workbook.return_value = mock_wb
        
        # Mock dependencies
        with patch('arb.utils.excel.xl_parse.get_spreadsheet_key_value_pairs_2') as mock_get_kv, \
             patch('arb.utils.excel.xl_parse.extract_tabs_2') as mock_extract:
            
            mock_get_kv.return_value = {'test_key': 'test_value'}
            mock_extract.return_value = {'metadata': {'test_key': 'test_value'}, 'schemas': {'data': 'test_schema'}, 'tab_contents': {'test_tab': {'test_field': 'test_value'}}}
            
            # Test the function
            result = parse_xl_file_2('test.xlsx')
            
            assert isinstance(result, dict)
            assert 'metadata' in result
            assert 'schemas' in result
            assert 'tab_contents' in result


class TestExtractTabs:
    """Test extract_tabs function."""
    
    def test_function_exists(self):
        """Test that extract_tabs function exists."""
        assert callable(extract_tabs)
    
    def test_function_signature(self):
        """Test that extract_tabs has the expected signature."""
        import inspect
        sig = inspect.signature(extract_tabs)
        params = list(sig.parameters.keys())
        expected_params = ['wb', 'schema_map', 'xl_as_dict']
        assert params == expected_params, f"Expected parameters {expected_params}, got {params}"
    
    def test_extract_tabs_with_mock_data(self, mock_openpyxl_workbook, mock_worksheet):
        """Test extract_tabs with mock data."""
        # Mock dependencies
        with patch('arb.utils.excel.xl_parse.ensure_schema') as mock_ensure, \
             patch('arb.utils.excel.xl_parse.sanitize_for_utf8') as mock_sanitize, \
             patch('arb.utils.excel.xl_parse.split_compound_keys') as mock_split, \
             patch('arb.utils.excel.xl_parse.logger') as mock_logger:
            
            mock_ensure.return_value = 'test_schema'
            mock_sanitize.return_value = 'test_value'
            mock_split.return_value = None
            mock_logger.debug = Mock()
            mock_logger.warning = Mock()
            mock_logger.info = Mock()
            
            # Create test data
            xl_as_dict = {
                'schemas': {'data': 'test_schema'},
                'metadata': {},
                'tab_contents': {}
            }
            
            # Mock workbook
            mock_wb = Mock()
            mock_wb.__getitem__ = Mock(return_value=mock_worksheet)
            
            # Test the function with correct parameters
            result = extract_tabs(mock_wb, {'test_schema': {'schema': {}}}, xl_as_dict)
            
            assert isinstance(result, dict)
            assert 'tab_contents' in result
    
    def test_extract_tabs_with_empty_schemas(self):
        """Test extract_tabs with empty schemas."""
        xl_as_dict = {
            'schemas': {},
            'metadata': {},
            'tab_contents': {}
        }
        
        # Mock workbook
        mock_wb = Mock()
        
        result = extract_tabs(mock_wb, {}, xl_as_dict)
        
        # If schemas is empty, tab_contents should not be added
        assert 'tab_contents' not in result


class TestExtractTabs2:
    """Test extract_tabs_2 function."""
    
    def test_function_exists(self):
        """Test that extract_tabs_2 function exists."""
        assert callable(extract_tabs_2)
    
    def test_function_signature(self):
        """Test that extract_tabs_2 has the expected signature."""
        import inspect
        sig = inspect.signature(extract_tabs_2)
        params = list(sig.parameters.keys())
        expected_params = ['wb', 'schema_map', 'xl_as_dict']
        assert params == expected_params, f"Expected parameters {expected_params}, got {params}"


class TestGetSpreadsheetKeyValuePairs:
    """Test get_spreadsheet_key_value_pairs function."""
    
    def test_function_exists(self):
        """Test that get_spreadsheet_key_value_pairs function exists."""
        assert callable(get_spreadsheet_key_value_pairs)
    
    def test_function_signature(self):
        """Test that get_spreadsheet_key_value_pairs has the expected signature."""
        import inspect
        sig = inspect.signature(get_spreadsheet_key_value_pairs)
        params = list(sig.parameters.keys())
        expected_params = ['wb', 'tab_name', 'top_left_cell']
        assert params == expected_params, f"Expected parameters {expected_params}, got {params}"
    
    def test_get_spreadsheet_key_value_pairs_with_mock_worksheet(self, mock_openpyxl_workbook, mock_worksheet):
        """Test get_spreadsheet_key_value_pairs with mock worksheet."""
        # Mock the offset method to return finite data
        def mock_offset(row=0, column=0):
            if row == 0:
                return Mock(value='test_key')
            else:
                return Mock(value=None)  # This will break the while loop
        
        mock_cell = Mock()
        mock_cell.offset = Mock(side_effect=mock_offset)
        
        # Mock worksheet access
        mock_ws = Mock()
        mock_ws.__getitem__ = Mock(return_value=mock_cell)
        
        # Mock workbook
        mock_wb = Mock()
        mock_wb.__getitem__ = Mock(return_value=mock_ws)
        
        # Test the function with correct parameters
        result = get_spreadsheet_key_value_pairs(mock_wb, 'test_tab', 'A1')
        
        assert isinstance(result, dict)


class TestGetSpreadsheetKeyValuePairs2:
    """Test get_spreadsheet_key_value_pairs_2 function."""
    
    def test_function_exists(self):
        """Test that get_spreadsheet_key_value_pairs_2 function exists."""
        assert callable(get_spreadsheet_key_value_pairs_2)
    
    def test_function_signature(self):
        """Test that get_spreadsheet_key_value_pairs_2 has the expected signature."""
        import inspect
        sig = inspect.signature(get_spreadsheet_key_value_pairs_2)
        params = list(sig.parameters.keys())
        expected_params = ['wb', 'tab_name', 'top_left_cell']
        assert params == expected_params, f"Expected parameters {expected_params}, got {params}"


class TestEnsureSchema:
    """Test ensure_schema function."""
    
    def test_function_exists(self):
        """Test that ensure_schema function exists."""
        assert callable(ensure_schema)
    
    def test_ensure_schema_with_valid_schema(self):
        """Test ensure_schema with valid schema."""
        schema_map = {'test_schema': {'fields': ['field1']}}
        result = ensure_schema('test_schema', schema_map)
        assert result == 'test_schema'
    
    def test_ensure_schema_with_missing_schema(self):
        """Test ensure_schema with missing schema."""
        schema_map = {'test_schema': {'fields': ['field1']}}
        result = ensure_schema('missing_schema', schema_map)
        assert result == 'missing_schema'


class TestSplitCompoundKeys:
    """Test split_compound_keys function."""
    
    def test_function_exists(self):
        """Test that split_compound_keys function exists."""
        assert callable(split_compound_keys)
    
    def test_split_compound_keys_with_lat_long(self):
        """Test split_compound_keys with latitude and longitude."""
        test_dict = {'lat_and_long': '37.7749,-122.4194'}
        split_compound_keys(test_dict)
        assert 'lat_arb' in test_dict
        assert 'long_arb' in test_dict
        assert test_dict['lat_arb'] == '37.7749'
        assert test_dict['long_arb'] == '-122.4194'
    
    def test_split_compound_keys_with_empty_lat_long(self):
        """Test split_compound_keys with empty latitude and longitude."""
        test_dict = {'lat_and_long': ''}
        split_compound_keys(test_dict)
        # If lat_and_long is empty, lat_arb and long_arb should not be added
        assert 'lat_arb' not in test_dict
        assert 'long_arb' not in test_dict


class TestConvertUploadToJson:
    """Test convert_upload_to_json function."""
    
    def test_function_exists(self):
        """Test that convert_upload_to_json function exists."""
        assert callable(convert_upload_to_json)
    
    def test_convert_upload_to_json_with_mock_data(self):
        """Test convert_upload_to_json with mock data."""
        # Mock dependencies
        with patch('arb.utils.excel.xl_parse.parse_xl_file') as mock_parse:
            mock_parse.return_value = {'test': 'data'}
            
            result = convert_upload_to_json('test.xlsx')
            assert isinstance(result, dict)
            assert result == {'test': 'data'}


class TestGetJsonFileNameOld:
    """Test get_json_file_name_old function."""
    
    def test_function_exists(self):
        """Test that get_json_file_name_old function exists."""
        assert callable(get_json_file_name_old)
    
    def test_get_json_file_name_old_with_xlsx_file(self):
        """Test get_json_file_name_old with .xlsx file."""
        result = get_json_file_name_old('test.xlsx')
        assert result == 'test.json'
    
    def test_get_json_file_name_old_with_xls_file(self):
        """Test get_json_file_name_old with .xls file."""
        result = get_json_file_name_old('test.xls')
        assert result == 'test.json'
    
    def test_get_json_file_name_old_with_other_extension(self):
        """Test get_json_file_name_old with other file extension."""
        result = get_json_file_name_old('test.txt')
        assert result == 'test.txt.json'


class TestFunctionEquivalence:
    """Test that _2 functions are equivalent to originals."""
    
    def test_parse_xl_file_equivalence(self):
        """Test that parse_xl_file and parse_xl_file_2 have same signature."""
        import inspect
        sig1 = inspect.signature(parse_xl_file)
        sig2 = inspect.signature(parse_xl_file_2)
        assert sig1.parameters == sig2.parameters, "parse_xl_file signatures differ"
    
    def test_extract_tabs_equivalence(self):
        """Test that extract_tabs and extract_tabs_2 have same signature."""
        import inspect
        sig1 = inspect.signature(extract_tabs)
        sig2 = inspect.signature(extract_tabs_2)
        assert sig1.parameters == sig2.parameters, "extract_tabs signatures differ"
    
    def test_get_spreadsheet_key_value_pairs_equivalence(self):
        """Test that get_spreadsheet_key_value_pairs and get_spreadsheet_key_value_pairs_2 have same signature."""
        import inspect
        sig1 = inspect.signature(get_spreadsheet_key_value_pairs)
        sig2 = inspect.signature(get_spreadsheet_key_value_pairs_2)
        assert sig1.parameters == sig2.parameters, "get_spreadsheet_key_value_pairs signatures differ"
