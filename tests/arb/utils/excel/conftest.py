"""
Pytest configuration for Excel module tests.

This file provides shared fixtures and configuration for all Excel-related tests.
"""

import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path


@pytest.fixture(scope="session")
def excel_test_data_dir():
    """Directory containing test Excel files."""
    # This would point to actual test Excel files in a real implementation
    return Path(__file__).parent / "test_data"


@pytest.fixture
def mock_openpyxl_workbook():
    """Mock OpenPyXL workbook for testing."""
    mock_wb = Mock()
    mock_wb.sheetnames = ['metadata', 'schema', 'data']
    
    # Mock worksheet access
    mock_ws = Mock()
    mock_wb.__getitem__ = Mock(return_value=mock_ws)
    
    return mock_wb


@pytest.fixture
def mock_worksheet():
    """Mock worksheet for testing."""
    mock_ws = Mock()
    
    # Mock cell access with offset method
    mock_cell = Mock()
    mock_cell.offset = Mock(return_value=Mock(value='test_value'))
    mock_ws.__getitem__ = Mock(return_value=mock_cell)
    
    return mock_ws


@pytest.fixture
def sample_schema_map():
    """Sample schema map for testing."""
    return {
        'test_schema': {
            'schema': {
                'field1': {
                    'value_address': 'A1',
                    'value_type': str,
                    'is_drop_down': False,
                    'label': 'Test Field',
                    'label_address': 'B1'
                },
                'field2': {
                    'value_address': 'A2',
                    'value_type': int,
                    'is_drop_down': False
                }
            }
        }
    }


@pytest.fixture
def sample_xl_dict():
    """Sample Excel dictionary structure for testing."""
    return {
        'metadata': {
            'sector': 'test_sector',
            'version': '1.0'
        },
        'schemas': {
            'data': 'test_schema'
        },
        'tab_contents': {}
    }


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    return Mock()


@pytest.fixture
def sample_schema_alias():
    """Sample schema alias mapping for testing."""
    return {
        'old_schema_v1': 'new_schema_v2',
        'deprecated_schema': 'current_schema'
    }
