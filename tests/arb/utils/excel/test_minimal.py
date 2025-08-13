"""
Minimal test file to isolate import issues.
"""

import pytest

# Import specific functions to test if this causes Excel file modifications
from arb.utils.excel.xl_create import sort_xl_schema, schema_to_json_file


def test_hello_world():
    """Minimal test that just prints hello world."""
    print("hello world")
    assert True


def test_import_xl_create():
    """Test importing xl_create module (not as *)."""
    print("Testing import of xl_create module...")
    import arb.utils.excel.xl_create
    print("Successfully imported xl_create module")
    assert True

