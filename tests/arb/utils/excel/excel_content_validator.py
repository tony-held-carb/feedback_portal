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
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime


def normalize_timestamps(content: str) -> str:
    """
    Normalize timestamp patterns in content for consistent comparison.
    
    Args:
        content: String content that may contain timestamps
        
    Returns:
        String with timestamps replaced by placeholders
    """
    # Replace Excel timestamp patterns: ts_YYYY_MM_DD_HH_MM_SS.xlsx
    content = re.sub(r'_ts_\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.xlsx', '_ts_TIMESTAMP.xlsx', content)
    
    # Replace JSON timestamp patterns: ts_YYYY_MM_DD_HH_MM_SS.json
    content = re.sub(r'_ts_\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.json', '_ts_TIMESTAMP.json', content)
    
    # Replace other timestamp patterns that might appear in content
    content = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', 'TIMESTAMP', content)
    content = re.sub(r'\d{2}/\d{2}/\d{4}', 'DATE', content)
    
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
    # Extract base name without extension
    base_name = test_file.stem
    
    # Look for corresponding JSON file
    for json_file in expected_results_dir.glob("*.json"):
        if base_name in json_file.stem:
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
