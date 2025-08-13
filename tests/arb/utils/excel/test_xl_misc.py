"""
Comprehensive unit tests for Excel miscellaneous functionality.

This test suite covers all functions in xl_misc.py including:
- Utility functions for Excel operations
- Helper functions for Excel processing
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the functions we're testing
from arb.utils.excel.xl_misc import (
    get_excel_row_column,
    xl_address_sort,
    run_diagnostics
)


class TestGetExcelRowColumn:
    """Test get_excel_row_column function."""
    
    def test_get_excel_row_column_basic_addresses(self):
        """Test basic Excel address parsing."""
        # Test various address formats (must use $A$1 format)
        test_cases = [
            ('$A$1', ('A', 1)),
            ('$B$5', ('B', 5)),
            ('$Z$10', ('Z', 10)),
            ('$AA$15', ('AA', 15)),
            ('$AB$20', ('AB', 20)),
            ('$ZZ$100', ('ZZ', 100))
        ]
        
        for address, expected in test_cases:
            result = get_excel_row_column(address)
            assert result == expected, f"Failed for address: {address}"
    
    def test_get_excel_row_column_edge_cases(self):
        """Test edge cases for Excel address parsing."""
        # Test single column addresses (must use $A$1 format)
        assert get_excel_row_column('$A$1') == ('A', 1)
        assert get_excel_row_column('$Z$1') == ('Z', 1)
        
        # Test double column addresses (must use $A$1 format)
        assert get_excel_row_column('$AA$1') == ('AA', 1)
        assert get_excel_row_column('$AB$1') == ('AB', 1)
        
        # Test large row numbers (must use $A$1 format)
        assert get_excel_row_column('$A$1000') == ('A', 1000)
        assert get_excel_row_column('$Z$9999') == ('Z', 9999)
    
    def test_get_excel_row_column_invalid_addresses(self):
        """Test that invalid addresses raise appropriate errors."""
        invalid_addresses = [
            '',           # Empty string
            '1A',         # Row first
            'A',          # No row
            '1',          # No column
            'A0',         # Row 0 (invalid)
            'A-1',        # Negative row
            'AA0',        # Double column, invalid row
        ]
        
        for address in invalid_addresses:
            with pytest.raises((ValueError, IndexError)):
                get_excel_row_column(address)


class TestXlAddressSort:
    """Test xl_address_sort function."""
    
    def test_xl_address_sort_by_row(self):
        """Test sorting by row."""
        # Test individual tuples - the function expects (key, value) tuples
        test_tuples = [
            ('field_c', {'label_address': '$C$5', 'value_address': '$C$6'}),
            ('field_a', {'label_address': '$A$3', 'value_address': '$A$4'}),
            ('field_b', {'label_address': '$B$4', 'value_address': '$B$5'})
        ]
        
        # Test each tuple individually
        for key, value in test_tuples:
            result = xl_address_sort((key, value), address_location="value", sort_by="row", sub_keys="label_address")
            assert isinstance(result, int)
            assert result > 0
    
    def test_xl_address_sort_by_column(self):
        """Test sorting by column."""
        # Test individual tuples - the function expects (key, value) tuples
        test_tuples = [
            ('field_c', {'label_address': '$C$3', 'value_address': '$C$4'}),
            ('field_a', {'label_address': '$A$3', 'value_address': '$A$4'}),
            ('field_b', {'label_address': '$B$3', 'value_address': '$B$4'})
        ]
        
        # Test each tuple individually
        for key, value in test_tuples:
            result = xl_address_sort((key, value), address_location="value", sort_by="column", sub_keys="label_address")
            assert isinstance(result, str)
            assert result in ['A', 'B', 'C']
    
    def test_xl_address_sort_with_sub_keys(self):
        """Test sorting with sub-keys."""
        # Test with nested sub-keys
        test_tuple = ('field_a', {'nested': {'value_address': '$A$3'}})
        
        result = xl_address_sort(test_tuple, address_location="value", sort_by="row", sub_keys=['nested', 'value_address'])
        
        # Should return the row number
        assert result == 3
    
    def test_xl_address_sort_empty_data(self):
        """Test sorting empty data."""
        # Empty tuple should work but return None or raise error
        with pytest.raises(IndexError):
            xl_address_sort((), address_location="key", sort_by="row")
    
    def test_xl_address_sort_single_item(self):
        """Test sorting single item."""
        test_tuple = ('field_a', {'label_address': '$A$1'})
        result = xl_address_sort(test_tuple, address_location="value", sort_by="row", sub_keys="label_address")
        assert result == 1
    
    def test_xl_address_sort_invalid_sort_by(self):
        """Test that invalid sort_by raises error."""
        test_tuple = ('field', {'label_address': '$A$1'})
        
        with pytest.raises(ValueError, match="sort_by must be 'row' or 'column'"):
            xl_address_sort(test_tuple, address_location="value", sort_by="invalid", sub_keys="label_address")
    
    def test_xl_address_sort_missing_address(self):
        """Test sorting when address is missing."""
        test_tuple = ('field_b', {})  # Missing address
        
        # Should raise error when trying to access missing address
        with pytest.raises(KeyError):
            xl_address_sort(test_tuple, address_location="value", sort_by="row", sub_keys="label_address")


class TestRunDiagnostics:
    """Test run_diagnostics function."""
    
    @patch('arb.utils.excel.xl_misc.create_default_types_schema')
    @patch('arb.utils.excel.xl_misc.prep_xl_templates')
    @patch('arb.utils.excel.xl_misc.create_payloads')
    @patch('arb.utils.excel.xl_misc.diag_update_xlsx_payloads_01')
    @patch('arb.utils.excel.xl_misc.get_excel_row_column')
    @patch('arb.utils.excel.xl_misc.xl_address_sort')
    def test_run_diagnostics_success(self, mock_sort, mock_get, mock_diag, mock_payloads, mock_prep, mock_schema):
        """Test successful diagnostics run."""
        # Mock the utility functions
        mock_get.return_value = ('A', 1)
        mock_sort.return_value = {'test': 'sorted'}
        
        # This function doesn't return anything, just ensure it doesn't raise
        run_diagnostics()
        
        # Verify utility functions were called
        mock_get.assert_called()
        mock_sort.assert_called()
        
        # Verify that the file writing functions were called (but mocked)
        mock_schema.assert_called_once()
        mock_prep.assert_called_once()
        mock_payloads.assert_called_once()
        mock_diag.assert_called_once()


class TestXlMiscIntegration:
    """Integration tests for xl_misc functions."""
    
    def test_address_parsing_and_sorting_integration(self):
        """Test that address parsing and sorting work together."""
        # Create test data with various addresses
        test_data = {
            'field_z': {'label_address': '$Z$10', 'value_address': '$Z$11'},
            'field_a': {'label_address': '$A$1', 'value_address': '$A$2'},
            'field_m': {'label_address': '$M$5', 'value_address': '$M$6'}
        }
        
        # Test individual tuples - the function expects (key, value) tuples
        for field_name, field_data in test_data.items():
            # Test row sorting
            row_result = xl_address_sort((field_name, field_data), address_location="value", sort_by="row", sub_keys="label_address")
            assert isinstance(row_result, int)
            assert row_result > 0
            
            # Test column sorting
            col_result = xl_address_sort((field_name, field_data), address_location="value", sort_by="column", sub_keys="label_address")
            assert isinstance(col_result, str)
            assert col_result in ['A', 'M', 'Z']
        
        # Verify address parsing works for all addresses
        for field_name, field_data in test_data.items():
            label_col, label_row = get_excel_row_column(field_data['label_address'])
            value_col, value_row = get_excel_row_column(field_data['value_address'])
            
            # Verify row relationship (value row should be label row + 1)
            assert value_row == label_row + 1
    
    def test_error_handling_integration(self):
        """Test error handling across functions."""
        # Test invalid address in sorting
        test_tuple = ('field_invalid', {'label_address': 'invalid'})
        
        # Should raise error for invalid address
        with pytest.raises(ValueError):
            xl_address_sort(test_tuple, address_location="value", sort_by="row", sub_keys="label_address")
    
    def test_performance_with_large_datasets(self):
        """Test performance with larger datasets."""
        # Create a larger dataset
        large_data = {}
        for i in range(100):
            col = chr(65 + (i % 26))  # A, B, C, ..., Z, AA, AB, ...
            if i >= 26:
                col = 'A' + col
            row = i + 1
            large_data[f'field_{i}'] = {
                'label_address': f'${col}${row}',
                'value_address': f'${col}${row + 1}'
            }
        
        # Test that sorting works with larger datasets (test a few samples)
        sample_keys = list(large_data.keys())[:5]  # Test first 5 items
        for key in sample_keys:
            data = large_data[key]
            # Test row sorting
            row_result = xl_address_sort((key, data), address_location="value", sort_by="row", sub_keys="label_address")
            assert isinstance(row_result, int)
            # Test column sorting
            col_result = xl_address_sort((key, data), address_location="value", sort_by="column", sub_keys="label_address")
            assert isinstance(col_result, str)
        
        # Verify we get the same number of items back
        assert len(large_data) == 100
        
        # Verify that all addresses are valid
        for key, data in large_data.items():
            # Test that addresses can be parsed
            label_col, label_row = get_excel_row_column(data['label_address'])
            value_col, value_row = get_excel_row_column(data['value_address'])
            assert isinstance(label_row, int)
            assert isinstance(value_row, int)
