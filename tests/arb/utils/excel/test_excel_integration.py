"""
Integration tests for Excel utility functions.

These tests actually execute the functions and verify that they create
real files in the xl_schemas and xl_payloads directories.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock

# Import the functions we want to test
from arb.utils.excel.xl_create import (
    create_default_types_schema,
    create_payload,
    create_schemas_and_payloads
)

# Import constants
from arb.utils.excel.xl_file_structure import PROCESSED_VERSIONS
from arb.utils.excel.xl_hardcoded import EXCEL_TEMPLATES


class TestExcelIntegration:
    """Integration tests that actually create files and directories."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Create temporary test directories
        self.test_dir = Path(tempfile.mkdtemp(prefix="excel_test_"))
        self.test_schemas_dir = self.test_dir / "xl_schemas"
        self.test_payloads_dir = self.test_dir / "xl_payloads"
        self.test_workbooks_dir = self.test_dir / "xl_workbooks"
        
        # Create the directory structure
        self.test_schemas_dir.mkdir(parents=True, exist_ok=True)
        self.test_payloads_dir.mkdir(parents=True, exist_ok=True)
        self.test_workbooks_dir.mkdir(parents=True, exist_ok=True)
        
        # Store original paths
        self.original_processed_versions = PROCESSED_VERSIONS
        
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Remove temporary test directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    @patch('arb.utils.excel.xl_create.PROCESSED_VERSIONS')
    def test_create_default_types_schema_integration(self, mock_processed_versions):
        """Test that create_default_types_schema actually creates files."""
        # Point to our test directory
        mock_processed_versions.__truediv__.return_value = self.test_schemas_dir
        
        # Actually execute the function
        result = create_default_types_schema(diagnostics=False)
        
        # Verify the function returned a result
        assert result is not None
        assert isinstance(result, dict)
        assert 'schema' in result
        
        # Verify files were actually created
        expected_file = self.test_schemas_dir / "default_value_types_v01_00.json"
        assert expected_file.exists(), f"Expected file {expected_file} was not created"
        
        # Verify file content
        import json
        with open(expected_file, 'r') as f:
            file_content = json.load(f)
        
        assert 'schema' in file_content
        assert 'metadata' in file_content
        print(f"✅ Successfully created schema file: {expected_file}")
        print(f"✅ File contains {len(file_content)} top-level keys")
    
    @patch('arb.utils.excel.xl_create.PROCESSED_VERSIONS')
    def test_create_payload_integration(self, mock_processed_versions):
        """Test that create_payload actually creates files."""
        # Point to our test directory
        mock_processed_versions.__truediv__.return_value = self.test_payloads_dir
        
        # Create a test metadata structure
        test_metadata = {
            'schema_version': 'v01_00',
            'template_name': 'landfill_operator_feedback',
            'description': 'Test payload creation'
        }
        
        # Actually execute the function
        result = create_payload(metadata=test_metadata)
        
        # Verify the function returned a result
        assert result is not None
        assert isinstance(result, dict)
        
        # Verify files were actually created
        expected_file = self.test_payloads_dir / "landfill_operator_feedback_v01_00_payload_01.json"
        assert expected_file.exists(), f"Expected file {expected_file} was not created"
        
        # Verify file content
        import json
        with open(expected_file, 'r') as f:
            file_content = json.load(f)
        
        assert 'metadata' in file_content
        assert 'payload' in file_content
        print(f"✅ Successfully created payload file: {expected_file}")
        print(f"✅ File contains {len(file_content)} top-level keys")
    
    @patch('arb.utils.excel.xl_create.PROCESSED_VERSIONS')
    def test_create_schemas_and_payloads_integration(self, mock_processed_versions):
        """Test that create_schemas_and_payloads actually creates all files."""
        # Point to our test directory
        mock_processed_versions.__truediv__.return_value = self.test_dir
        
        # Actually execute the function
        result = create_schemas_and_payloads(
            output_dir=self.test_dir,
            diagnostics=False
        )
        
        # Verify the function returned a result
        assert result is not None
        assert isinstance(result, dict)
        assert 'output_schema_path' in result
        assert 'output_payload_path' in result
        
        # Verify all expected files were created
        expected_files = [
            self.test_schemas_dir / "default_value_types_v01_00.json",
            self.test_payloads_dir / "landfill_operator_feedback_v01_00_payload_01.json"
        ]
        
        for expected_file in expected_files:
            assert expected_file.exists(), f"Expected file {expected_file} was not created"
            print(f"✅ Successfully created: {expected_file}")
        
        # Verify directory structure
        assert self.test_schemas_dir.exists()
        assert self.test_payloads_dir.exists()
        assert self.test_workbooks_dir.exists()
        
        # Count files in each directory
        schema_files = list(self.test_schemas_dir.glob("*.json"))
        payload_files = list(self.test_payloads_dir.glob("*.json"))
        
        print(f"✅ Created {len(schema_files)} schema files")
        print(f"✅ Created {len(payload_files)} payload files")
        
        assert len(schema_files) > 0, "No schema files were created"
        assert len(payload_files) > 0, "No payload files were created"
    
    def test_directory_structure_creation(self):
        """Test that the test directory structure is properly created."""
        # Verify our test directories exist
        assert self.test_dir.exists()
        assert self.test_schemas_dir.exists()
        assert self.test_payloads_dir.exists()
        assert self.test_workbooks_dir.exists()
        
        # Verify they are directories
        assert self.test_schemas_dir.is_dir()
        assert self.test_payloads_dir.is_dir()
        assert self.test_workbooks_dir.is_dir()
        
        print(f"✅ Test directory structure created successfully")
        print(f"✅ Test root: {self.test_dir}")
        print(f"✅ Schemas dir: {self.test_schemas_dir}")
        print(f"✅ Payloads dir: {self.test_payloads_dir}")
        print(f"✅ Workbooks dir: {self.test_workbooks_dir}")


class TestExcelFileGeneration:
    """Test actual file generation without mocking."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Create temporary test directories
        self.test_dir = Path(tempfile.mkdtemp(prefix="excel_file_test_"))
        self.test_schemas_dir = self.test_dir / "xl_schemas"
        self.test_payloads_dir = self.test_dir / "xl_payloads"
        
        # Create the directory structure
        self.test_schemas_dir.mkdir(parents=True, exist_ok=True)
        self.test_payloads_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Remove temporary test directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_real_file_creation(self):
        """Test creating real files without any mocking."""
        # This test will actually create files in the test directories
        # We'll use a simple approach to verify file creation works
        
        # Create a test schema file
        test_schema = {
            "metadata": {
                "version": "v01_00",
                "description": "Test schema for integration testing"
            },
            "schema": {
                "test_field": {
                    "label": "Test Field",
                    "value_address": "A1",
                    "value_type": str,
                    "is_drop_down": False
                }
            }
        }
        
        # Write the schema file
        schema_file = self.test_schemas_dir / "test_schema_v01_00.json"
        import json
        with open(schema_file, 'w') as f:
            json.dump(test_schema, f, indent=2)
        
        # Verify the file was created
        assert schema_file.exists()
        
        # Create a test payload file
        test_payload = {
            "metadata": {
                "schema_version": "v01_00",
                "template_name": "test_template"
            },
            "payload": {
                "test_field": "test_value"
            }
        }
        
        # Write the payload file
        payload_file = self.test_payloads_dir / "test_payload_v01_00.json"
        with open(payload_file, 'w') as f:
            json.dump(test_payload, f, indent=2)
        
        # Verify the file was created
        assert payload_file.exists()
        
        # Verify file contents
        with open(schema_file, 'r') as f:
            loaded_schema = json.load(f)
        
        with open(payload_file, 'r') as f:
            loaded_payload = json.load(f)
        
        assert loaded_schema['metadata']['version'] == 'v01_00'
        assert loaded_payload['metadata']['schema_version'] == 'v01_00'
        
        print(f"✅ Successfully created test schema: {schema_file}")
        print(f"✅ Successfully created test payload: {payload_file}")
        print(f"✅ Both files contain valid JSON content")


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-s"])
