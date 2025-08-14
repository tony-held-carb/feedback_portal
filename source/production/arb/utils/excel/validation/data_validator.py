"""
Data validation module for Excel processing.

This module provides comprehensive validation capabilities for data during
Excel processing operations, including cell value validation, required
field validation, and field constraint validation.

Classes:
    DataValidator: Handles all data validation operations

Author: AI Assistant
Created: 2025-01-27
Version: 1.0
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..core import (
    ValidationResult,
    DataError,
    ValidationError,
    ErrorCodes
)


class DataValidator:
    """
    Handles all data validation operations during Excel processing.
    
    This class provides comprehensive validation for data values including:
    - Cell value type validation
    - Required field validation
    - Field constraint validation (min/max, patterns, etc.)
    - Data format validation
    - Business rule validation
    
    The validator ensures that extracted data meets quality standards
    and conforms to expected formats and constraints.
    
    Example:
        validator = DataValidator()
        
        # Validate cell value
        result = validator.validate_cell_value("123", int, "quantity")
        if not result.is_valid:
            print(f"Cell validation failed: {result.message}")
        
        # Validate required fields
        result = validator.validate_required_fields(data_dict, ["name", "email"])
    """
    
    def __init__(self):
        """Initialize the data validator."""
        # Common validation patterns
        self.validation_patterns = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^[\+]?[1-9][\d]{0,15}$',
            'url': r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$',
            'zip_code': r'^\d{5}(-\d{4})?$',
            'ssn': r'^\d{3}-\d{2}-\d{4}$',
            'credit_card': r'^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$'
        }
        
        # Common validation functions
        self.validation_functions = {
            'email': self._validate_email,
            'phone': self._validate_phone,
            'url': self._validate_url,
            'zip_code': self._validate_zip_code,
            'ssn': self._validate_ssn,
            'credit_card': self._validate_credit_card
        }
    
    def validate_cell_value(self, value: Any, expected_type: type, field_name: str) -> ValidationResult:
        """
        Validate that a cell value matches the expected type.
        
        This method performs type validation and basic format checking
        for common data types like dates, numbers, and strings.
        
        Args:
            value: The cell value to validate
            expected_type: The expected Python type
            field_name: Name of the field being validated
            
        Returns:
            ValidationResult: Result of the cell value validation
        """
        try:
            # Handle None/empty values
            if value is None:
                return ValidationResult(
                    field_name=field_name,
                    is_valid=False,
                    message="Cell value is None/empty",
                    severity="ERROR",
                    location=field_name,
                    context={"value": value, "expected_type": expected_type.__name__}
                )
            
            # Check if value is already the expected type
            if isinstance(value, expected_type):
                return ValidationResult(
                    field_name=field_name,
                    is_valid=True,
                    message=f"Cell value is valid {expected_type.__name__}",
                    severity="INFO",
                    location=field_name,
                    context={"value": value, "actual_type": type(value).__name__}
                )
            
            # Try to convert value to expected type
            try:
                converted_value = self._convert_to_type(value, expected_type)
                return ValidationResult(
                    field_name=field_name,
                    is_valid=True,
                    message=f"Cell value converted to {expected_type.__name__}",
                    severity="INFO",
                    location=field_name,
                    context={
                        "original_value": value,
                        "converted_value": converted_value,
                        "original_type": type(value).__name__,
                        "expected_type": expected_type.__name__
                    }
                )
            except (ValueError, TypeError) as e:
                return ValidationResult(
                    field_name=field_name,
                    is_valid=False,
                    message=f"Cannot convert value '{value}' to {expected_type.__name__}: {str(e)}",
                    severity="ERROR",
                    location=field_name,
                    context={
                        "value": value,
                        "expected_type": expected_type.__name__,
                        "conversion_error": str(e)
                    }
                )
                
        except Exception as e:
            return ValidationResult(
                field_name=field_name,
                is_valid=False,
                message=f"Cell value validation error: {str(e)}",
                severity="ERROR",
                location=field_name,
                context={"exception": str(e)}
            )
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> ValidationResult:
        """
        Validate that all required fields are present in the data.
        
        Args:
            data: Dictionary containing the data to validate
            required_fields: List of field names that are required
            
        Returns:
            ValidationResult: Result of the required fields validation
        """
        try:
            if not required_fields:
                return ValidationResult(
                    field_name="required_fields",
                    is_valid=True,
                    message="No required fields specified",
                    severity="INFO",
                    location="data"
                )
            
            missing_fields = []
            empty_fields = []
            
            for field_name in required_fields:
                if field_name not in data:
                    missing_fields.append(field_name)
                elif data[field_name] is None or (isinstance(data[field_name], str) and not data[field_name].strip()):
                    empty_fields.append(field_name)
            
            if missing_fields or empty_fields:
                issues = []
                if missing_fields:
                    issues.append(f"{len(missing_fields)} missing fields")
                if empty_fields:
                    issues.append(f"{len(empty_fields)} empty fields")
                
                return ValidationResult(
                    field_name="required_fields",
                    is_valid=False,
                    message=f"Required fields validation failed: {', '.join(issues)}",
                    severity="ERROR",
                    location="data",
                    context={
                        "missing_fields": missing_fields,
                        "empty_fields": empty_fields,
                        "required_fields": required_fields,
                        "available_fields": list(data.keys())
                    }
                )
            
            return ValidationResult(
                field_name="required_fields",
                is_valid=True,
                message=f"All {len(required_fields)} required fields are present and non-empty",
                severity="INFO",
                location="data",
                context={
                    "required_fields": required_fields,
                    "field_count": len(required_fields)
                }
            )
            
        except Exception as e:
            return ValidationResult(
                field_name="required_fields",
                is_valid=False,
                message=f"Required fields validation error: {str(e)}",
                severity="ERROR",
                location="data",
                context={"exception": str(e)}
            )
    
    def validate_field_constraints(self, value: Any, constraints: Dict[str, Any]) -> ValidationResult:
        """
        Validate field values against constraints.
        
        This method validates values against various constraints including:
        - Min/max values for numbers
        - String length limits
        - Pattern matching (regex)
        - Custom validation functions
        - Enumeration values
        
        Args:
            value: The value to validate
            constraints: Dictionary of constraints to apply
            
        Returns:
            ValidationResult: Result of the constraint validation
        """
        try:
            if not constraints:
                return ValidationResult(
                    field_name="field_constraints",
                    is_valid=True,
                    message="No constraints specified",
                    severity="INFO",
                    location="value"
                )
            
            validation_errors = []
            
            # Min/max value constraints
            if 'min_value' in constraints and value is not None:
                try:
                    min_val = constraints['min_value']
                    if value < min_val:
                        validation_errors.append({
                            'constraint': 'min_value',
                            'value': value,
                            'limit': min_val,
                            'message': f"Value {value} is less than minimum {min_val}"
                        })
                except (TypeError, ValueError):
                    pass  # Skip if comparison not possible
            
            if 'max_value' in constraints and value is not None:
                try:
                    max_val = constraints['max_value']
                    if value > max_val:
                        validation_errors.append({
                            'constraint': 'max_value',
                            'value': value,
                            'limit': max_val,
                            'message': f"Value {value} is greater than maximum {max_val}"
                        })
                except (TypeError, ValueError):
                    pass  # Skip if comparison not possible
            
            # String length constraints
            if isinstance(value, str):
                if 'min_length' in constraints:
                    min_len = constraints['min_length']
                    if len(value) < min_len:
                        validation_errors.append({
                            'constraint': 'min_length',
                            'value': len(value),
                            'limit': min_len,
                            'message': f"String length {len(value)} is less than minimum {min_len}"
                        })
                
                if 'max_length' in constraints:
                    max_len = constraints['max_length']
                    if len(value) > max_len:
                        validation_errors.append({
                            'constraint': 'max_length',
                            'value': len(value),
                            'limit': max_len,
                            'message': f"String length {len(value)} is greater than maximum {max_len}"
                        })
            
            # Pattern matching constraints
            if 'pattern' in constraints and isinstance(value, str):
                pattern = constraints['pattern']
                if not re.match(pattern, value):
                    validation_errors.append({
                        'constraint': 'pattern',
                        'value': value,
                        'pattern': pattern,
                        'message': f"Value '{value}' does not match pattern '{pattern}'"
                    })
            
            # Enumeration constraints
            if 'enum' in constraints:
                enum_values = constraints['enum']
                if value not in enum_values:
                    validation_errors.append({
                        'constraint': 'enum',
                        'value': value,
                        'allowed_values': enum_values,
                        'message': f"Value '{value}' is not in allowed values: {enum_values}"
                    })
            
            # Custom validation function
            if 'custom_validator' in constraints:
                custom_func = constraints['custom_validator']
                if callable(custom_func):
                    try:
                        if not custom_func(value):
                            validation_errors.append({
                                'constraint': 'custom_validator',
                                'value': value,
                                'message': "Custom validation function returned False"
                            })
                    except Exception as e:
                        validation_errors.append({
                            'constraint': 'custom_validator',
                            'value': value,
                            'message': f"Custom validation function error: {str(e)}"
                        })
            
            # Build validation result
            if validation_errors:
                return ValidationResult(
                    field_name="field_constraints",
                    is_valid=False,
                    message=f"Field constraint validation failed: {len(validation_errors)} violations",
                    severity="ERROR",
                    location="value",
                    context={
                        "validation_errors": validation_errors,
                        "constraints": constraints
                    }
                )
            
            return ValidationResult(
                field_name="field_constraints",
                is_valid=True,
                message="All field constraints are satisfied",
                severity="INFO",
                location="value",
                context={"constraints": constraints}
            )
            
        except Exception as e:
            return ValidationResult(
                field_name="field_constraints",
                is_valid=False,
                message=f"Field constraint validation error: {str(e)}",
                severity="ERROR",
                location="value",
                context={"exception": str(e)}
            )
    
    def validate_data_format(self, value: Any, format_type: str) -> ValidationResult:
        """
        Validate data format using predefined patterns.
        
        Args:
            value: The value to validate
            format_type: Type of format to validate against
            
        Returns:
            ValidationResult: Result of the format validation
        """
        try:
            if not isinstance(value, str):
                return ValidationResult(
                    field_name="data_format",
                    is_valid=False,
                    message=f"Format validation requires string value, got {type(value).__name__}",
                    severity="ERROR",
                    location="value",
                    context={"value": value, "format_type": format_type}
                )
            
            if format_type not in self.validation_patterns:
                return ValidationResult(
                    field_name="data_format",
                    is_valid=False,
                    message=f"Unknown format type: {format_type}",
                    severity="ERROR",
                    location="value",
                    context={"format_type": format_type, "available_formats": list(self.validation_patterns.keys())}
                )
            
            pattern = self.validation_patterns[format_type]
            if re.match(pattern, value):
                return ValidationResult(
                    field_name="data_format",
                    is_valid=True,
                    message=f"Value matches {format_type} format",
                    severity="INFO",
                    location="value",
                    context={"format_type": format_type, "pattern": pattern}
                )
            else:
                return ValidationResult(
                    field_name="data_format",
                    is_valid=False,
                    message=f"Value does not match {format_type} format",
                    severity="ERROR",
                    location="value",
                    context={"format_type": format_type, "pattern": pattern, "value": value}
                )
                
        except Exception as e:
            return ValidationResult(
                field_name="data_format",
                is_valid=False,
                message=f"Data format validation error: {str(e)}",
                severity="ERROR",
                location="value",
                context={"exception": str(e)}
            )
    
    def validate_business_rules(self, data: Dict[str, Any], rules: List[Dict[str, Any]]) -> List[ValidationResult]:
        """
        Validate data against business rules.
        
        Business rules are complex validation logic that may involve
        multiple fields or conditional validation.
        
        Args:
            data: Dictionary containing the data to validate
            rules: List of business rule dictionaries
            
        Returns:
            List[ValidationResult]: Results of business rule validation
        """
        try:
            results = []
            
            for i, rule in enumerate(rules):
                try:
                    rule_name = rule.get('name', f'rule_{i}')
                    rule_condition = rule.get('condition')
                    rule_message = rule.get('message', f'Business rule {rule_name} failed')
                    
                    if not rule_condition or not callable(rule_condition):
                        results.append(ValidationResult(
                            field_name=f"business_rule_{i}",
                            is_valid=False,
                            message=f"Invalid business rule: {rule_name}",
                            severity="ERROR",
                            location="business_rules",
                            context={"rule": rule, "issue": "Invalid condition function"}
                        ))
                        continue
                    
                    # Execute business rule
                    try:
                        rule_passed = rule_condition(data)
                        results.append(ValidationResult(
                            field_name=f"business_rule_{i}",
                            is_valid=rule_passed,
                            message=rule_message if not rule_passed else f"Business rule {rule_name} passed",
                            severity="ERROR" if not rule_passed else "INFO",
                            location="business_rules",
                            context={"rule_name": rule_name, "rule_passed": rule_passed}
                        ))
                    except Exception as e:
                        results.append(ValidationResult(
                            field_name=f"business_rule_{i}",
                            is_valid=False,
                            message=f"Business rule {rule_name} execution error: {str(e)}",
                            severity="ERROR",
                            location="business_rules",
                            context={"rule_name": rule_name, "exception": str(e)}
                        ))
                        
                except Exception as e:
                    results.append(ValidationResult(
                        field_name=f"business_rule_{i}",
                        is_valid=False,
                        message=f"Business rule validation error: {str(e)}",
                        severity="ERROR",
                        location="business_rules",
                        context={"rule_index": i, "exception": str(e)}
                    ))
            
            return results
            
        except Exception as e:
            return [ValidationResult(
                field_name="business_rules",
                is_valid=False,
                message=f"Business rules validation error: {str(e)}",
                severity="ERROR",
                location="business_rules",
                context={"exception": str(e)}
            )]
    
    def _convert_to_type(self, value: Any, target_type: type) -> Any:
        """
        Convert a value to the target type.
        
        Args:
            value: Value to convert
            target_type: Target type to convert to
            
        Returns:
            Converted value
            
        Raises:
            ValueError: If conversion is not possible
            TypeError: If conversion is not supported
        """
        if target_type == str:
            return str(value)
        elif target_type == int:
            if isinstance(value, str):
                return int(float(value))  # Handle "123.0" -> 123
            return int(value)
        elif target_type == float:
            return float(value)
        elif target_type == bool:
            if isinstance(value, str):
                value_lower = value.lower()
                if value_lower in ('true', '1', 'yes', 'on'):
                    return True
                elif value_lower in ('false', '0', 'no', 'off'):
                    return False
                else:
                    raise ValueError(f"Cannot convert '{value}' to boolean")
            return bool(value)
        elif target_type == datetime:
            if isinstance(value, datetime):
                return value
            elif isinstance(value, str):
                # Try common date formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
                raise ValueError(f"Cannot parse date string: {value}")
            else:
                raise ValueError(f"Cannot convert {type(value).__name__} to datetime")
        else:
            raise TypeError(f"Conversion to {target_type.__name__} not supported")
    
    def _validate_email(self, value: str) -> bool:
        """Validate email format."""
        return bool(re.match(self.validation_patterns['email'], value))
    
    def _validate_phone(self, value: str) -> bool:
        """Validate phone number format."""
        return bool(re.match(self.validation_patterns['phone'], value))
    
    def _validate_url(self, value: str) -> bool:
        """Validate URL format."""
        return bool(re.match(self.validation_patterns['url'], value))
    
    def _validate_zip_code(self, value: str) -> bool:
        """Validate US ZIP code format."""
        return bool(re.match(self.validation_patterns['zip_code'], value))
    
    def _validate_ssn(self, value: str) -> bool:
        """Validate Social Security Number format."""
        return bool(re.match(self.validation_patterns['ssn'], value))
    
    def _validate_credit_card(self, value: str) -> bool:
        """Validate credit card number format."""
        return bool(re.match(self.validation_patterns['credit_card'], value))
