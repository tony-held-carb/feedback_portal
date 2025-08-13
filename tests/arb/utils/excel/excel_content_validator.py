"""
Excel Content Validation Utilities

This module provides utilities for comparing Excel parsing results against
expected results to validate functional equivalence and accuracy.

Functions:
- compare_excel_results: Compare parsed Excel results against expected JSON
- normalize_timestamps: Remove timestamp differences for comparison
- validate_structure: Ensure parsed results have expected structure
- compare_metadata: Compare metadata fields between results
- compare_tab_contents: Compare tab content data between results
- find_corresponding_expected_result: Find expected result files
- generate_comparison_report: Generate detailed comparison reports
- validate_excel_file_integrity: Check Excel file structure and content
- compare_schemas: Compare schema definitions between results
"""

import json
import re
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime
import zipfile
import xml.etree.ElementTree as ET


def normalize_timestamps(content: str) -> str:
    """
    Normalize timestamp patterns in content for consistent comparison.
    
    Args:
        content: String content that may contain timestamps
        
    Returns:
        String with timestamps replaced by placeholders
    """
    if not isinstance(content, str):
        return content
    
    # Replace Excel timestamp patterns: ts_YYYY_MM_DD_HH_MM_SS.xlsx
    content = re.sub(r'_ts_\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.xlsx', '_ts_TIMESTAMP.xlsx', content)
    
    # Replace JSON timestamp patterns: ts_YYYY_MM_DD_HH_MM_SS.json
    content = re.sub(r'_ts_\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.json', '_ts_TIMESTAMP.json', content)
    
    # Replace other timestamp patterns that might appear in content
    content = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', 'TIMESTAMP', content)
    content = re.sub(r'\d{2}/\d{2}/\d{4}', 'DATE', content)
    
    # Replace Excel internal timestamps (OLE automation dates)
    content = re.sub(r'\d+\.\d+', 'EXCEL_TIMESTAMP', content)
    
    # Replace file modification timestamps
    content = re.sub(r'\d{10,}', 'FILE_TIMESTAMP', content)
    
    return content


def validate_structure(parsed_result: Dict[str, Any], expected_keys: set) -> Tuple[bool, List[str]]:
    """
    Validate that parsed result has the expected structure.
    
    Args:
        parsed_result: Result from Excel parsing function
        expected_keys: Set of expected top-level keys
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    if not isinstance(parsed_result, dict):
        issues.append("Result is not a dictionary")
        return False, issues
    
    # Check for required keys
    missing_keys = expected_keys - set(parsed_result.keys())
    if missing_keys:
        issues.append(f"Missing required keys: {missing_keys}")
    
    # Check for unexpected keys
    unexpected_keys = set(parsed_result.keys()) - expected_keys
    if unexpected_keys:
        issues.append(f"Unexpected keys: {unexpected_keys}")
    
    # Check that required keys have the right types
    if 'metadata' in parsed_result and not isinstance(parsed_result['metadata'], dict):
        issues.append("metadata should be a dictionary")
    
    if 'schemas' in parsed_result and not isinstance(parsed_result['schemas'], dict):
        issues.append("schemas should be a dictionary")
    
    if 'tab_contents' in parsed_result and not isinstance(parsed_result['tab_contents'], dict):
        issues.append("tab_contents should be a dictionary")
    
    # Check for empty required sections
    if 'metadata' in parsed_result and not parsed_result['metadata']:
        issues.append("metadata section is empty")
    
    if 'schemas' in parsed_result and not parsed_result['schemas']:
        issues.append("schemas section is empty")
    
    if 'tab_contents' in parsed_result and not parsed_result['tab_contents']:
        issues.append("tab_contents section is empty")
    
    return len(issues) == 0, issues


def compare_metadata(parsed_metadata: Dict[str, Any], expected_metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Compare metadata between parsed and expected results.
    
    Args:
        parsed_metadata: Metadata from parsed Excel file
        expected_metadata: Metadata from expected JSON result
        
    Returns:
        Tuple of (is_equivalent, list_of_differences)
    """
    differences = []
    
    # Check that both have the same keys
    parsed_keys = set(parsed_metadata.keys())
    expected_keys = set(expected_metadata.keys())
    
    missing_in_parsed = expected_keys - parsed_keys
    if missing_in_parsed:
        differences.append(f"Missing metadata fields in parsed result: {missing_in_parsed}")
    
    missing_in_expected = parsed_keys - expected_keys
    if missing_in_expected:
        differences.append(f"Extra metadata fields in parsed result: {missing_in_expected}")
    
    # Compare common fields
    common_keys = parsed_keys.intersection(expected_keys)
    for key in common_keys:
        parsed_value = parsed_metadata[key]
        expected_value = expected_metadata[key]
        
        # Normalize values for comparison (handle timestamps, etc.)
        if isinstance(parsed_value, str) and isinstance(expected_value, str):
            normalized_parsed = normalize_timestamps(parsed_value)
            normalized_expected = normalize_timestamps(expected_value)
            if normalized_parsed != normalized_expected:
                differences.append(f"Metadata field '{key}' differs: parsed='{parsed_value}' vs expected='{expected_value}'")
        elif parsed_value != expected_value:
            differences.append(f"Metadata field '{key}' differs: parsed={parsed_value} vs expected={expected_value}")
    
    return len(differences) == 0, differences


def compare_schemas(parsed_schemas: Dict[str, Any], expected_schemas: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Compare schema definitions between parsed and expected results.
    
    Args:
        parsed_schemas: Schemas from parsed Excel file
        expected_schemas: Schemas from expected JSON result
        
    Returns:
        Tuple of (is_equivalent, list_of_differences)
    """
    differences = []
    
    # Check that both have the same keys
    parsed_keys = set(parsed_schemas.keys())
    expected_keys = set(expected_schemas.keys())
    
    missing_in_parsed = expected_keys - parsed_keys
    if missing_in_parsed:
        differences.append(f"Missing schema tabs in parsed result: {missing_in_parsed}")
    
    missing_in_expected = parsed_keys - expected_keys
    if missing_in_expected:
        differences.append(f"Extra schema tabs in parsed result: {missing_in_expected}")
    
    # Compare common schema tabs
    common_keys = parsed_keys.intersection(expected_keys)
    for key in common_keys:
        parsed_schema = parsed_schemas[key]
        expected_schema = expected_schemas[key]
        
        if parsed_schema != expected_schema:
            differences.append(f"Schema for tab '{key}' differs: parsed={parsed_schema} vs expected={expected_schema}")
    
    return len(differences) == 0, differences


def compare_tab_contents(parsed_tab_contents: Dict[str, Any], expected_tab_contents: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Compare tab content data between parsed and expected results.
    
    Args:
        parsed_tab_contents: Tab contents from parsed Excel file
        expected_tab_contents: Tab contents from expected JSON result
        
    Returns:
        Tuple of (is_equivalent, list_of_differences)
    """
    differences = []
    
    # Check that both have the same tabs
    parsed_tabs = set(parsed_tab_contents.keys())
    expected_tabs = set(expected_tab_contents.keys())
    
    missing_in_parsed = expected_tabs - parsed_tabs
    if missing_in_parsed:
        differences.append(f"Missing tabs in parsed result: {missing_in_parsed}")
    
    missing_in_expected = parsed_tabs - expected_tabs
    if missing_in_expected:
        differences.append(f"Extra tabs in parsed result: {missing_in_expected}")
    
    # Compare common tabs
    common_tabs = parsed_tabs.intersection(expected_tabs)
    for tab_name in common_tabs:
        parsed_tab = parsed_tab_contents[tab_name]
        expected_tab = expected_tab_contents[tab_name]
        
        if not isinstance(parsed_tab, dict) or not isinstance(expected_tab, dict):
            differences.append(f"Tab '{tab_name}' content is not a dictionary")
            continue
        
        # Compare fields within the tab
        parsed_fields = set(parsed_tab.keys())
        expected_fields = set(expected_tab.keys())
        
        missing_fields = expected_fields - parsed_fields
        if missing_fields:
            differences.append(f"Missing fields in tab '{tab_name}': {missing_fields}")
        
        extra_fields = parsed_fields - expected_fields
        if extra_fields:
            differences.append(f"Extra fields in tab '{tab_name}': {extra_fields}")
        
        # Compare common fields
        common_fields = parsed_fields.intersection(expected_fields)
        for field_name in common_fields:
            parsed_value = parsed_tab[field_name]
            expected_value = expected_tab[field_name]
            
            # Normalize values for comparison
            if isinstance(parsed_value, str) and isinstance(expected_value, str):
                normalized_parsed = normalize_timestamps(parsed_value)
                normalized_expected = normalize_timestamps(expected_value)
                if normalized_parsed != normalized_expected:
                    differences.append(f"Field '{field_name}' in tab '{tab_name}' differs: parsed='{parsed_value}' vs expected='{expected_value}'")
            elif parsed_value != expected_value:
                differences.append(f"Field '{field_name}' in tab '{tab_name}' differs: parsed={parsed_value} vs expected={expected_value}")
    
    return len(differences) == 0, differences


def validate_excel_file_integrity(excel_file_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate the integrity of an Excel file by checking its structure.
    
    Args:
        excel_file_path: Path to Excel file to validate
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    if not excel_file_path.exists():
        issues.append(f"Excel file does not exist: {excel_file_path}")
        return False, issues
    
    if not excel_file_path.is_file():
        issues.append(f"Path is not a file: {excel_file_path}")
        return False, issues
    
    # Check file extension
    if excel_file_path.suffix.lower() not in ['.xlsx', '.xls']:
        issues.append(f"File is not an Excel file: {excel_file_path.suffix}")
        return False, issues
    
    # For .xlsx files, check ZIP structure
    if excel_file_path.suffix.lower() == '.xlsx':
        try:
            with zipfile.ZipFile(excel_file_path, 'r') as zip_file:
                # Check for required Excel files
                required_files = [
                    'xl/workbook.xml',
                    'xl/worksheets/sheet1.xml',
                    '[Content_Types].xml'
                ]
                
                for required_file in required_files:
                    if required_file not in zip_file.namelist():
                        issues.append(f"Missing required Excel file: {required_file}")
                
                # Check for at least one worksheet
                worksheet_files = [f for f in zip_file.namelist() if f.startswith('xl/worksheets/')]
                if not worksheet_files:
                    issues.append("No worksheets found in Excel file")
                
        except zipfile.BadZipFile:
            issues.append("Excel file is not a valid ZIP archive")
        except Exception as e:
            issues.append(f"Error reading Excel file: {e}")
    
    return len(issues) == 0, issues


def compare_excel_results(parsed_result: Dict[str, Any], expected_json_path: Path) -> Tuple[bool, List[str]]:
    """
    Compare parsed Excel result against expected JSON result.
    
    Args:
        parsed_result: Result from Excel parsing function
        expected_json_path: Path to expected JSON result file
        
    Returns:
        Tuple of (is_equivalent, list_of_differences)
    """
    differences = []
    
    # Load expected result
    try:
        with open(expected_json_path, 'r') as f:
            expected_data = json.load(f)
    except Exception as e:
        differences.append(f"Failed to load expected result: {e}")
        return False, differences
    
    # Validate structure
    expected_keys = {'metadata', 'schemas', 'tab_contents'}
    is_valid, structure_issues = validate_structure(parsed_result, expected_keys)
    if not is_valid:
        differences.extend(structure_issues)
        return False, differences
    
    # Compare metadata
    if 'metadata' in parsed_result and 'metadata' in expected_data:
        is_equivalent, metadata_diffs = compare_metadata(parsed_result['metadata'], expected_data['metadata'])
        if not is_equivalent:
            differences.extend(metadata_diffs)
    
    # Compare schemas
    if 'schemas' in parsed_result and 'schemas' in expected_data:
        is_equivalent, schema_diffs = compare_schemas(parsed_result['schemas'], expected_data['schemas'])
        if not is_equivalent:
            differences.extend(schema_diffs)
    
    # Compare tab contents
    if 'tab_contents' in parsed_result and 'tab_contents' in expected_data:
        is_equivalent, content_diffs = compare_tab_contents(parsed_result['tab_contents'], expected_data['tab_contents'])
        if not is_equivalent:
            differences.extend(content_diffs)
    
    return len(differences) == 0, differences


def find_corresponding_expected_result(test_file: Path, expected_results_dir: Path) -> Optional[Path]:
    """
    Find the corresponding expected result file for a test file.
    
    Args:
        test_file: Path to test Excel file
        expected_results_dir: Directory containing expected results
        
    Returns:
        Path to corresponding expected result file, or None if not found
    """
    if not expected_results_dir.exists():
        return None
    
    # Extract base name without extension
    base_name = test_file.stem
    
    # Look for corresponding JSON file
    for json_file in expected_results_dir.glob("*.json"):
        if base_name in json_file.stem:
            return json_file
    
    # Also check for files with similar names (case-insensitive)
    for json_file in expected_results_dir.glob("*.json"):
        if base_name.lower() in json_file.stem.lower():
            return json_file
    
    return None


def generate_comparison_report(test_file: Path, parsed_result: Dict[str, Any], 
                             expected_result_path: Path, differences: List[str]) -> str:
    """
    Generate a human-readable comparison report.
    
    Args:
        test_file: Path to test file that was processed
        parsed_result: Result from Excel parsing function
        expected_result_path: Path to expected result file
        differences: List of differences found
        
    Returns:
        Formatted comparison report
    """
    report = []
    report.append("=" * 80)
    report.append("EXCEL CONTENT VALIDATION REPORT")
    report.append("=" * 80)
    report.append(f"Test File: {test_file.name}")
    report.append(f"Expected Result: {expected_result_path.name}")
    report.append(f"Validation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    if not differences:
        report.append("✅ VALIDATION PASSED - No differences found")
    else:
        report.append(f"❌ VALIDATION FAILED - {len(differences)} differences found")
        report.append("")
        report.append("Differences:")
        for i, diff in enumerate(differences, 1):
            report.append(f"  {i}. {diff}")
    
    report.append("")
    report.append("Parsed Result Structure:")
    report.append(f"  Keys: {list(parsed_result.keys())}")
    
    if 'metadata' in parsed_result:
        report.append(f"  Metadata fields: {list(parsed_result['metadata'].keys())}")
    
    if 'schemas' in parsed_result:
        report.append(f"  Schema tabs: {list(parsed_result['schemas'].keys())}")
    
    if 'tab_contents' in parsed_result:
        report.append(f"  Data tabs: {list(parsed_result['tab_contents'].keys())}")
    
    report.append("=" * 80)
    
    return "\n".join(report)


def validate_excel_schema_structure(schema_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate that Excel schema data has the correct structure.
    
    Args:
        schema_data: Schema data to validate
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    if not isinstance(schema_data, dict):
        issues.append("Schema data is not a dictionary")
        return False, issues
    
    # Check for required schema structure
    if 'schema' not in schema_data:
        issues.append("Schema data missing 'schema' key")
        return False, issues
    
    schema = schema_data['schema']
    if not isinstance(schema, dict):
        issues.append("Schema 'schema' value is not a dictionary")
        return False, issues
    
    # Check each field in the schema
    for field_name, field_config in schema.items():
        if not isinstance(field_config, dict):
            issues.append(f"Field '{field_name}' configuration is not a dictionary")
            continue
        
        # Check for required field attributes
        required_attrs = ['value_address', 'value_type']
        for attr in required_attrs:
            if attr not in field_config:
                issues.append(f"Field '{field_name}' missing required attribute '{attr}'")
        
        # Validate value_address format if present
        if 'value_address' in field_config:
            address = field_config['value_address']
            if not isinstance(address, str) or not re.match(r'^\$[A-Z]+\$\d+$', address):
                issues.append(f"Field '{field_name}' has invalid value_address format: {address}")
    
    return len(issues) == 0, issues


def compare_excel_files(file1: Path, file2: Path, ignore_timestamps: bool = True) -> Tuple[bool, List[str]]:
    """
    Compare two Excel files for content equivalence.
    
    Args:
        file1: Path to first Excel file
        file2: Path to second Excel file
        ignore_timestamps: Whether to ignore timestamp differences
        
    Returns:
        Tuple of (is_equivalent, list_of_differences)
    """
    differences = []
    
    # Validate both files
    for file_path in [file1, file2]:
        is_valid, issues = validate_excel_file_integrity(file_path)
        if not is_valid:
            differences.extend([f"File {file_path.name}: {issue}" for issue in issues])
    
    if differences:
        return False, differences
    
    # For now, just check file sizes and basic properties
    # In a real implementation, you might want to parse both files and compare content
    
    if file1.stat().st_size != file2.stat().st_size:
        differences.append(f"File sizes differ: {file1.name} ({file1.stat().st_size} bytes) vs {file2.name} ({file2.stat().st_size} bytes)")
    
    return len(differences) == 0, differences


def create_test_excel_file(output_path: Path, content: Dict[str, Any]) -> bool:
    """
    Create a test Excel file with specified content for testing purposes.
    
    Args:
        output_path: Path where to create the test file
        content: Content to include in the Excel file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # This is a simplified implementation
        # In a real scenario, you might use openpyxl or similar to create actual Excel files
        
        # For now, just create a JSON file that represents Excel content
        with open(output_path.with_suffix('.json'), 'w') as f:
            json.dump(content, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error creating test file: {e}")
        return False


def validate_excel_parsing_result(result: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate that an Excel parsing result has the expected structure and content.
    
    Args:
        result: Result from Excel parsing function
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Basic structure validation
    if not isinstance(result, dict):
        issues.append("Result is not a dictionary")
        return False, issues
    
    # Check for required sections
    required_sections = ['metadata', 'schemas', 'tab_contents']
    for section in required_sections:
        if section not in result:
            issues.append(f"Missing required section: {section}")
        elif not isinstance(result[section], dict):
            issues.append(f"Section '{section}' is not a dictionary")
    
    # Validate metadata structure
    if 'metadata' in result and isinstance(result['metadata'], dict):
        for key, value in result['metadata'].items():
            if not isinstance(key, str):
                issues.append(f"Metadata key is not a string: {key}")
    
    # Validate schemas structure
    if 'schemas' in result and isinstance(result['schemas'], dict):
        for tab_name, schema_ref in result['schemas'].items():
            if not isinstance(tab_name, str):
                issues.append(f"Schema tab name is not a string: {tab_name}")
            if not isinstance(schema_ref, str):
                issues.append(f"Schema reference is not a string: {schema_ref}")
    
    # Validate tab contents structure
    if 'tab_contents' in result and isinstance(result['tab_contents'], dict):
        for tab_name, tab_data in result['tab_contents'].items():
            if not isinstance(tab_name, str):
                issues.append(f"Tab name is not a string: {tab_name}")
            if not isinstance(tab_data, dict):
                issues.append(f"Tab data is not a dictionary: {tab_name}")
    
    return len(issues) == 0, issues


def generate_validation_summary(results: List[Tuple[str, bool, List[str]]]) -> str:
    """
    Generate a summary of validation results.
    
    Args:
        results: List of (test_name, passed, issues) tuples
        
    Returns:
        Formatted validation summary
    """
    summary = []
    summary.append("=" * 80)
    summary.append("EXCEL VALIDATION SUMMARY")
    summary.append("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, passed, _ in results if passed)
    failed_tests = total_tests - passed_tests
    
    summary.append(f"Total Tests: {total_tests}")
    summary.append(f"Passed: {passed_tests}")
    summary.append(f"Failed: {failed_tests}")
    summary.append(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    summary.append("")
    
    if failed_tests > 0:
        summary.append("Failed Tests:")
        for test_name, passed, issues in results:
            if not passed:
                summary.append(f"  ❌ {test_name}")
                for issue in issues:
                    summary.append(f"    - {issue}")
        summary.append("")
    
    summary.append("=" * 80)
    
    return "\n".join(summary)
