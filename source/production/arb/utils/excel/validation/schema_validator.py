"""
Schema validation module for Excel processing.

This module provides comprehensive validation capabilities for Excel schemas,
including schema structure validation, cell reference validation, data type
validation, and field definition validation.

Classes:
    SchemaValidator: Handles all schema validation operations

Author: AI Assistant
Created: 2025-01-27
Version: 1.0
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple

import openpyxl
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from ..core import (
    ValidationResult,
    SchemaError,
    ValidationError,
    ErrorCodes
)


class SchemaValidator:
    """
    Handles all schema validation operations.
    
    This class provides comprehensive validation for Excel schemas including:
    - Schema definition structure validation
    - Cell reference validation
    - Data type validation
    - Field definition validation
    - Schema compatibility validation
    
    The validator ensures that schemas are properly structured and contain
    valid field definitions that can be processed by the Excel parser.
    
    Example:
        validator = SchemaValidator()
        
        # Validate schema definition
        result = validator.validate_schema_definition(schema_dict)
        if not result.is_valid:
            print(f"Schema validation failed: {result.message}")
        
        # Validate cell references
        result = validator.validate_cell_references(schema_dict, workbook)
    """
    
    def __init__(self):
        """Initialize the schema validator."""
        # Valid data types for Excel fields
        self.valid_data_types = {
            'string', 'str', 'text',
            'integer', 'int', 'number',
            'float', 'decimal', 'double',
            'boolean', 'bool', 'logical',
            'datetime', 'date', 'time',
            'email', 'url', 'hyperlink'
        }
        
        # Required schema fields
        self.required_schema_fields = {'fields', 'tab_name', 'schema_name'}
        
        # Required field properties
        self.required_field_properties = {'name', 'cell_reference', 'data_type'}
    
    def validate_schema_definition(self, schema: Dict[str, Any]) -> ValidationResult:
        """
        Validate the structure and content of a schema definition.
        
        This method performs comprehensive validation of schema structure:
        - Required fields are present
        - Field definitions are complete
        - Data types are valid
        - Cell references are properly formatted
        
        Args:
            schema: Schema dictionary to validate
            
        Returns:
            ValidationResult: Result of the schema validation
        """
        try:
            if not isinstance(schema, dict):
                return ValidationResult(
                    field_name="schema_structure",
                    is_valid=False,
                    message="Schema must be a dictionary",
                    severity="ERROR",
                    location="schema"
                )
            
            # Check required schema fields
            missing_fields = self.required_schema_fields - set(schema.keys())
            if missing_fields:
                return ValidationResult(
                    field_name="schema_structure",
                    is_valid=False,
                    message=f"Schema missing required fields: {missing_fields}",
                    severity="ERROR",
                    location="schema",
                    context={"missing_fields": list(missing_fields)}
                )
            
            # Validate schema name
            schema_name = schema.get('schema_name', '')
            if not schema_name or not isinstance(schema_name, str):
                return ValidationResult(
                    field_name="schema_name",
                    is_valid=False,
                    message="Schema must have a valid string name",
                    severity="ERROR",
                    location="schema"
                )
            
            # Validate tab name
            tab_name = schema.get('tab_name', '')
            if not tab_name or not isinstance(tab_name, str):
                return ValidationResult(
                    field_name="tab_name",
                    is_valid=False,
                    message="Schema must have a valid string tab name",
                    severity="ERROR",
                    location="schema"
                )
            
            # Validate fields structure
            fields = schema.get('fields', [])
            if not isinstance(fields, list):
                return ValidationResult(
                    field_name="fields",
                    is_valid=False,
                    message="Schema fields must be a list",
                    severity="ERROR",
                    location="schema"
                )
            
            if not fields:
                return ValidationResult(
                    field_name="fields",
                    is_valid=False,
                    message="Schema must contain at least one field",
                    severity="ERROR",
                    location="schema"
                )
            
            # Validate individual fields
            field_validation_results = []
            for i, field in enumerate(fields):
                if not isinstance(field, dict):
                    field_validation_results.append(ValidationResult(
                        field_name=f"field_{i}",
                        is_valid=False,
                        message=f"Field at index {i} must be a dictionary",
                        severity="ERROR",
                        location=f"schema.fields[{i}]"
                    ))
                    continue
                
                field_result = self._validate_field_definition(field, i)
                field_validation_results.append(field_result)
            
            # Check if any field validations failed
            failed_fields = [r for r in field_validation_results if not r.is_valid]
            if failed_fields:
                return ValidationResult(
                    field_name="schema_fields",
                    is_valid=False,
                    message=f"Schema contains {len(failed_fields)} invalid field definitions",
                    severity="ERROR",
                    location="schema",
                    context={"failed_fields": failed_fields}
                )
            
            return ValidationResult(
                field_name="schema_structure",
                is_valid=True,
                message=f"Schema '{schema_name}' is valid with {len(fields)} fields",
                severity="INFO",
                location="schema",
                context={
                    "schema_name": schema_name,
                    "tab_name": tab_name,
                    "field_count": len(fields)
                }
            )
            
        except Exception as e:
            return ValidationResult(
                field_name="schema_structure",
                is_valid=False,
                message=f"Schema validation error: {str(e)}",
                severity="ERROR",
                location="schema",
                context={"exception": str(e)}
            )
    
    def validate_cell_references(self, schema: Dict[str, Any], wb: Workbook) -> ValidationResult:
        """
        Validate that all cell references in the schema are valid.
        
        This method checks that:
        - Cell references are properly formatted
        - Referenced cells exist in the worksheet
        - Cell references are within reasonable bounds
        
        Args:
            schema: Schema dictionary to validate
            wb: OpenPyXL workbook object
            
        Returns:
            ValidationResult: Result of the cell reference validation
        """
        try:
            tab_name = schema.get('tab_name', '')
            if not tab_name:
                return ValidationResult(
                    field_name="cell_references",
                    is_valid=False,
                    message="Schema missing tab_name for cell reference validation",
                    severity="ERROR",
                    location="schema"
                )
            
            # Get the worksheet
            try:
                ws = wb[tab_name]
            except KeyError:
                return ValidationResult(
                    field_name="cell_references",
                    is_valid=False,
                    message=f"Worksheet '{tab_name}' not found in workbook",
                    severity="ERROR",
                    location=f"workbook.{tab_name}"
                )
            
            fields = schema.get('fields', [])
            invalid_references = []
            
            for i, field in enumerate(fields):
                cell_ref = field.get('cell_reference', '')
                if not cell_ref:
                    continue
                
                # Validate cell reference format
                if not self._is_valid_cell_reference(cell_ref):
                    invalid_references.append({
                        'field_index': i,
                        'field_name': field.get('name', f'field_{i}'),
                        'cell_reference': cell_ref,
                        'issue': 'Invalid cell reference format'
                    })
                    continue
                
                # Check if cell reference is within worksheet bounds
                if not self._is_cell_reference_in_bounds(cell_ref, ws):
                    invalid_references.append({
                        'field_index': i,
                        'field_name': field.get('name', f'field_{i}'),
                        'cell_reference': cell_ref,
                        'issue': 'Cell reference outside worksheet bounds'
                    })
                    continue
            
            if invalid_references:
                return ValidationResult(
                    field_name="cell_references",
                    is_valid=False,
                    message=f"Schema contains {len(invalid_references)} invalid cell references",
                    severity="ERROR",
                    location=f"schema.{tab_name}",
                    context={"invalid_references": invalid_references}
                )
            
            return ValidationResult(
                field_name="cell_references",
                is_valid=True,
                message=f"All cell references in schema '{schema.get('schema_name', '')}' are valid",
                severity="INFO",
                location=f"schema.{tab_name}",
                context={"field_count": len(fields)}
            )
            
        except Exception as e:
            return ValidationResult(
                field_name="cell_references",
                is_valid=False,
                message=f"Cell reference validation error: {str(e)}",
                severity="ERROR",
                location="schema",
                context={"exception": str(e)}
            )
    
    def validate_data_types(self, schema: Dict[str, Any]) -> ValidationResult:
        """
        Validate that data types are supported and consistent.
        
        This method checks that:
        - All data types are supported
        - Data types are consistent across similar fields
        - Required data type properties are present
        
        Args:
            schema: Schema dictionary to validate
            
        Returns:
            ValidationResult: Result of the data type validation
        """
        try:
            fields = schema.get('fields', [])
            invalid_types = []
            type_inconsistencies = []
            
            # Track data types by field category for consistency checking
            type_by_category = {}
            
            for i, field in enumerate(fields):
                data_type = field.get('data_type', '')
                field_name = field.get('name', f'field_{i}')
                
                # Check if data type is specified
                if not data_type:
                    invalid_types.append({
                        'field_index': i,
                        'field_name': field_name,
                        'issue': 'Missing data type'
                    })
                    continue
                
                # Check if data type is valid
                if not isinstance(data_type, str):
                    invalid_types.append({
                        'field_index': i,
                        'field_name': field_name,
                        'data_type': data_type,
                        'issue': 'Data type must be a string'
                    })
                    continue
                
                # Normalize data type for comparison
                normalized_type = data_type.lower().strip()
                
                # Check if data type is supported
                if normalized_type not in self.valid_data_types:
                    invalid_types.append({
                        'field_index': i,
                        'field_name': field_name,
                        'data_type': data_type,
                        'issue': f'Unsupported data type: {data_type}'
                    })
                    continue
                
                # Check for type consistency by field category
                field_category = self._get_field_category(field_name)
                if field_category:
                    if field_category in type_by_category:
                        expected_type = type_by_category[field_category]
                        if normalized_type != expected_type:
                            type_inconsistencies.append({
                                'field_name': field_name,
                                'field_category': field_category,
                                'actual_type': normalized_type,
                                'expected_type': expected_type,
                                'issue': 'Inconsistent data type for field category'
                            })
                    else:
                        type_by_category[field_category] = normalized_type
            
            # Build validation result
            if invalid_types or type_inconsistencies:
                issues = []
                if invalid_types:
                    issues.append(f"{len(invalid_types)} invalid data types")
                if type_inconsistencies:
                    issues.append(f"{len(type_inconsistencies)} type inconsistencies")
                
                return ValidationResult(
                    field_name="data_types",
                    is_valid=False,
                    message=f"Data type validation failed: {', '.join(issues)}",
                    severity="ERROR",
                    location="schema",
                    context={
                        "invalid_types": invalid_types,
                        "type_inconsistencies": type_inconsistencies
                    }
                )
            
            return ValidationResult(
                field_name="data_types",
                is_valid=True,
                message=f"All data types in schema are valid and consistent",
                severity="INFO",
                location="schema",
                context={"field_count": len(fields)}
            )
            
        except Exception as e:
            return ValidationResult(
                field_name="data_types",
                is_valid=False,
                message=f"Data type validation error: {str(e)}",
                severity="ERROR",
                location="schema",
                context={"exception": str(e)}
            )
    
    def validate_field_definitions(self, schema: Dict[str, Any]) -> ValidationResult:
        """
        Validate individual field definitions within a schema.
        
        This method performs detailed validation of each field:
        - Required properties are present
        - Property values are valid
        - Field constraints are reasonable
        
        Args:
            schema: Schema dictionary to validate
            
        Returns:
            ValidationResult: Result of the field definition validation
        """
        try:
            fields = schema.get('fields', [])
            field_validation_results = []
            
            for i, field in enumerate(fields):
                field_result = self._validate_field_definition(field, i)
                field_validation_results.append(field_result)
            
            # Check overall field validation results
            failed_fields = [r for r in field_validation_results if not r.is_valid]
            if failed_fields:
                return ValidationResult(
                    field_name="field_definitions",
                    is_valid=False,
                    message=f"Schema contains {len(failed_fields)} invalid field definitions",
                    severity="ERROR",
                    location="schema",
                    context={"failed_fields": failed_fields}
                )
            
            return ValidationResult(
                field_name="field_definitions",
                is_valid=True,
                message=f"All {len(fields)} field definitions are valid",
                severity="INFO",
                location="schema",
                context={"field_count": len(fields)}
            )
            
        except Exception as e:
            return ValidationResult(
                field_name="field_definitions",
                is_valid=False,
                message=f"Field definition validation error: {str(e)}",
                severity="ERROR",
                location="schema",
                context={"exception": str(e)}
            )
    
    def validate_schema_compatibility(self, schema: Dict[str, Any], tab_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate that a schema is compatible with the tab data.
        
        This method checks that:
        - Schema fields match available data
        - Data types are appropriate for the actual data
        - Required fields are present in the data
        
        Args:
            schema: Schema dictionary to validate
            tab_data: Data extracted from the tab
            
        Returns:
            ValidationResult: Result of the schema compatibility validation
        """
        try:
            fields = schema.get('fields', [])
            schema_field_names = {field.get('name', '') for field in fields}
            
            # Check if all schema fields are present in the data
            missing_fields = schema_field_names - set(tab_data.keys())
            if missing_fields:
                return ValidationResult(
                    field_name="schema_compatibility",
                    is_valid=False,
                    message=f"Schema fields missing from tab data: {missing_fields}",
                    severity="ERROR",
                    location="schema",
                    context={
                        "missing_fields": list(missing_fields),
                        "available_fields": list(tab_data.keys())
                    }
                )
            
            # Check data type compatibility for each field
            type_compatibility_issues = []
            for field in fields:
                field_name = field.get('name', '')
                expected_type = field.get('data_type', '')
                actual_value = tab_data.get(field_name)
                
                if actual_value is not None and expected_type:
                    if not self._is_value_compatible_with_type(actual_value, expected_type):
                        type_compatibility_issues.append({
                            'field_name': field_name,
                            'expected_type': expected_type,
                            'actual_value': str(actual_value),
                            'issue': 'Value type incompatible with schema definition'
                        })
            
            if type_compatibility_issues:
                return ValidationResult(
                    field_name="schema_compatibility",
                    is_valid=False,
                    message=f"Schema contains {len(type_compatibility_issues)} type compatibility issues",
                    severity="WARNING",
                    location="schema",
                    context={"type_compatibility_issues": type_compatibility_issues}
                )
            
            return ValidationResult(
                field_name="schema_compatibility",
                is_valid=True,
                message="Schema is compatible with tab data",
                severity="INFO",
                location="schema",
                context={
                    "field_count": len(fields),
                    "compatible_fields": len(fields)
                }
            )
            
        except Exception as e:
            return ValidationResult(
                field_name="schema_compatibility",
                is_valid=False,
                message=f"Schema compatibility validation error: {str(e)}",
                severity="ERROR",
                location="schema",
                context={"exception": str(e)}
            )
    
    def _validate_field_definition(self, field: Dict[str, Any], index: int) -> ValidationResult:
        """
        Validate a single field definition.
        
        Args:
            field: Field dictionary to validate
            index: Index of the field in the schema
            
        Returns:
            ValidationResult: Result of the field validation
        """
        try:
            # Check required properties
            missing_properties = self.required_field_properties - set(field.keys())
            if missing_properties:
                return ValidationResult(
                    field_name=f"field_{index}",
                    is_valid=False,
                    message=f"Field missing required properties: {missing_properties}",
                    severity="ERROR",
                    location=f"schema.fields[{index}]",
                    context={"missing_properties": list(missing_properties)}
                )
            
            # Validate field name
            field_name = field.get('name', '')
            if not field_name or not isinstance(field_name, str):
                return ValidationResult(
                    field_name=f"field_{index}",
                    is_valid=False,
                    message="Field name must be a non-empty string",
                    severity="ERROR",
                    location=f"schema.fields[{index}]"
                )
            
            # Validate cell reference
            cell_ref = field.get('cell_reference', '')
            if not cell_ref or not isinstance(cell_ref, str):
                return ValidationResult(
                    field_name=f"field_{index}",
                    is_valid=False,
                    message="Field must have a valid cell reference",
                    severity="ERROR",
                    location=f"schema.fields[{index}]"
                )
            
            if not self._is_valid_cell_reference(cell_ref):
                return ValidationResult(
                    field_name=f"field_{index}",
                    is_valid=False,
                    message=f"Invalid cell reference format: {cell_ref}",
                    severity="ERROR",
                    location=f"schema.fields[{index}]"
                )
            
            # Validate data type
            data_type = field.get('data_type', '')
            if not data_type or not isinstance(data_type, str):
                return ValidationResult(
                    field_name=f"field_{index}",
                    is_valid=False,
                    message="Field must have a valid data type",
                    severity="ERROR",
                    location=f"schema.fields[{index}]"
                )
            
            normalized_type = data_type.lower().strip()
            if normalized_type not in self.valid_data_types:
                return ValidationResult(
                    field_name=f"field_{index}",
                    is_valid=False,
                    message=f"Unsupported data type: {data_type}",
                    severity="ERROR",
                    location=f"schema.fields[{index}]"
                )
            
            return ValidationResult(
                field_name=f"field_{index}",
                is_valid=True,
                message=f"Field '{field_name}' is valid",
                severity="INFO",
                location=f"schema.fields[{index}]",
                context={
                    "field_name": field_name,
                    "cell_reference": cell_ref,
                    "data_type": data_type
                }
            )
            
        except Exception as e:
            return ValidationResult(
                field_name=f"field_{index}",
                is_valid=False,
                message=f"Field validation error: {str(e)}",
                severity="ERROR",
                location=f"schema.fields[{index}]",
                context={"exception": str(e)}
            )
    
    def _is_valid_cell_reference(self, cell_ref: str) -> bool:
        """
        Check if a cell reference is valid.
        
        Args:
            cell_ref: Cell reference string to validate
            
        Returns:
            bool: True if cell reference is valid, False otherwise
        """
        # Excel cell reference pattern: [A-Z]+[0-9]+
        pattern = r'^[A-Z]+\d+$'
        return bool(re.match(pattern, cell_ref))
    
    def _is_cell_reference_in_bounds(self, cell_ref: str, ws: Worksheet) -> bool:
        """
        Check if a cell reference is within worksheet bounds.
        
        Args:
            cell_ref: Cell reference string
            ws: Worksheet to check bounds against
            
        Returns:
            bool: True if cell reference is in bounds, False otherwise
        """
        try:
            # Parse cell reference
            match = re.match(r'^([A-Z]+)(\d+)$', cell_ref)
            if not match:
                return False
            
            col_str, row_str = match.groups()
            row = int(row_str)
            
            # Convert column letters to number
            col = 0
            for char in col_str:
                col = col * 26 + (ord(char) - ord('A') + 1)
            
            # Check bounds (reasonable limits)
            if row < 1 or row > 1000000:  # 1 million rows
                return False
            
            if col < 1 or col > 16384:  # Excel column limit
                return False
            
            return True
            
        except (ValueError, IndexError):
            return False
    
    def _get_field_category(self, field_name: str) -> Optional[str]:
        """
        Get the category of a field based on its name.
        
        Args:
            field_name: Name of the field
            
        Returns:
            Optional[str]: Field category if identifiable, None otherwise
        """
        field_name_lower = field_name.lower()
        
        # Common field categories
        if any(word in field_name_lower for word in ['name', 'title', 'description']):
            return 'text'
        elif any(word in field_name_lower for word in ['date', 'time', 'created', 'updated']):
            return 'datetime'
        elif any(word in field_name_lower for word in ['count', 'number', 'quantity', 'amount']):
            return 'numeric'
        elif any(word in field_name_lower for word in ['email', 'url', 'link']):
            return 'contact'
        elif any(word in field_name_lower for word in ['active', 'enabled', 'status']):
            return 'boolean'
        
        return None
    
    def _is_value_compatible_with_type(self, value: Any, expected_type: str) -> bool:
        """
        Check if a value is compatible with the expected data type.
        
        Args:
            value: Value to check
            expected_type: Expected data type
            
        Returns:
            bool: True if value is compatible, False otherwise
        """
        try:
            normalized_type = expected_type.lower().strip()
            
            if normalized_type in ['string', 'str', 'text']:
                return isinstance(value, str)
            elif normalized_type in ['integer', 'int', 'number']:
                if isinstance(value, int):
                    return True
                elif isinstance(value, float):
                    return value.is_integer()
                return False
            elif normalized_type in ['float', 'decimal', 'double']:
                return isinstance(value, (int, float))
            elif normalized_type in ['boolean', 'bool', 'logical']:
                return isinstance(value, bool)
            elif normalized_type in ['datetime', 'date', 'time']:
                # Check if it's a datetime-like object or can be parsed
                return hasattr(value, 'year') or isinstance(value, str)
            elif normalized_type in ['email', 'url', 'hyperlink']:
                return isinstance(value, str) and len(value) > 0
            
            return True  # Unknown types are considered compatible
            
        except Exception:
            return False
