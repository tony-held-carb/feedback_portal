"""
Shared pytest fixtures for Excel module tests.

This module provides common test fixtures and utilities for testing
the Excel parsing and processing functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
import sys

# Import our new path utility
from arb.utils.path_utils import find_repo_root, get_relative_path_from_repo_root


@pytest.fixture
def excel_test_data_dir():
    """Provide path to Excel test data directory."""
    repo_root = find_repo_root(Path(__file__))
    return repo_root / "tests" / "arb" / "utils" / "excel" / "test_data"


@pytest.fixture
def test_files_dir():
    """Provide path to standard test files directory."""
    repo_root = find_repo_root(Path(__file__))
    return repo_root / "feedback_forms" / "testing_versions" / "standard"


@pytest.fixture
def expected_results_dir():
    """Provide path to expected results directory."""
    repo_root = find_repo_root(Path(__file__))
    return repo_root / "feedback_forms" / "testing_versions" / "standard" / "expected_results"


@pytest.fixture
def mock_openpyxl_workbook():
    """Mock OpenPyXL Workbook object."""
    mock_wb = Mock()
    mock_wb.sheetnames = ['Sheet1', 'Sheet2']
    return mock_wb


@pytest.fixture
def mock_worksheet():
    """Mock OpenPyXL Worksheet object."""
    mock_ws = Mock()
    mock_cell = Mock()
    mock_cell.value = 'test_value'
    mock_ws.__getitem__ = Mock(return_value=mock_cell)
    return mock_ws


@pytest.fixture
def sample_schema_map():
    """Sample schema mapping for testing."""
    return {
        'test_schema': {
            'fields': ['field1', 'field2'],
            'required': ['field1']
        }
    }


@pytest.fixture
def sample_xl_dict():
    """Sample Excel dictionary structure for testing."""
    return {
        'metadata': {'version': '1.0'},
        'schemas': {'test_schema': {'fields': ['field1']}},
        'tab_contents': {'Sheet1': {'field1': 'value1'}}
    }


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    return Mock()


@pytest.fixture
def sample_schema_alias():
    """Sample schema alias for testing."""
    return 'test_alias'
