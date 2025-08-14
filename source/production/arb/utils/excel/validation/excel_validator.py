"""
Excel file validation module.

This module provides comprehensive validation capabilities for Excel files,
including file existence, format validation, size limits, and workbook
structure validation.

Classes:
    ExcelValidator: Handles all Excel file validation operations

Author: AI Assistant
Created: 2025-01-27
Version: 1.0
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple

import openpyxl
from openpyxl.workbook.workbook import Workbook

from ..core import (
    ExcelParseConfig,
    ValidationResult,
    FileError,
    ValidationError,
    ErrorCodes
)


class ExcelValidator:
    """
    Handles all Excel file validation operations.
    
    This class provides comprehensive validation for Excel files including:
    - File existence and accessibility
    - File format validation
    - File size limits
    - Workbook structure validation
    - Required tab validation
    
    The validator uses configuration-driven settings to determine validation
    behavior and generates structured validation results for all checks.
    
    Example:
        validator = ExcelValidator()
        config = ExcelParseConfig(max_file_size_mb=50)
        
        # Validate file path
        result = validator.validate_file_path(Path("sample.xlsx"))
        if not result.is_valid:
            print(f"File validation failed: {result.message}")
        
        # Validate workbook structure
        wb = openpyxl.load_workbook("sample.xlsx")
        result = validator.validate_workbook_structure(wb)
    """
    
    def __init__(self, config: Optional[ExcelParseConfig] = None):
        """
        Initialize the Excel validator.
        
        Args:
            config: Configuration for validation behavior. If None, uses default settings.
        """
        self.config = config or ExcelParseConfig()
    
    def validate_file_path(self, path: Path) -> ValidationResult:
        """
        Validate that the file path exists and is accessible.
        
        This method performs basic file validation including:
        - File existence check
        - File accessibility (read permissions)
        - Path validity
        
        Args:
            path: Path to the file to validate
            
        Returns:
            ValidationResult: Result of the file path validation
            
        Raises:
            FileError: If file validation fails and strict mode is enabled
        """
        try:
            # Check if path is valid
            if not isinstance(path, Path):
                return ValidationResult(
                    field_name="file_path",
                    is_valid=False,
                    message="File path must be a Path object",
                    severity="ERROR",
                    location=str(path)
                )
            
            # Check if file exists
            if not path.exists():
                return ValidationResult(
                    field_name="file_path",
                    is_valid=False,
                    message=f"File does not exist: {path}",
                    severity="ERROR",
                    location=str(path)
                )
            
            # Check if it's a file (not a directory)
            if not path.is_file():
                return ValidationResult(
                    field_name="file_path",
                    is_valid=False,
                    message=f"Path is not a file: {path}",
                    severity="ERROR",
                    location=str(path)
                )
            
            # Check if file is readable
            if not os.access(path, os.R_OK):
                return ValidationResult(
                    field_name="file_path",
                    is_valid=False,
                    message=f"File is not readable: {path}",
                    severity="ERROR",
                    location=str(path)
                )
            
            return ValidationResult(
                field_name="file_path",
                is_valid=True,
                message=f"File path is valid and accessible: {path}",
                severity="INFO",
                location=str(path)
            )
            
        except Exception as e:
            return ValidationResult(
                field_name="file_path",
                is_valid=False,
                message=f"File path validation error: {str(e)}",
                severity="ERROR",
                location=str(path),
                context={"exception": str(e)}
            )
    
    def validate_file_format(self, path: Path) -> ValidationResult:
        """
        Validate that the file has a supported Excel format.
        
        This method checks the file extension and attempts to validate
        that the file is a valid Excel file by checking its header.
        
        Args:
            path: Path to the file to validate
            
        Returns:
            ValidationResult: Result of the file format validation
        """
        try:
            # Check file extension
            file_extension = path.suffix.lower()
            if file_extension not in self.config.allowed_extensions:
                return ValidationResult(
                    field_name="file_format",
                    is_valid=False,
                    message=f"File extension '{file_extension}' not supported. Allowed: {self.config.allowed_extensions}",
                    severity="ERROR",
                    location=str(path),
                    context={
                        "file_extension": file_extension,
                        "allowed_extensions": self.config.allowed_extensions
                    }
                )
            
            # For .xlsx files, check if it's a valid ZIP archive (Excel files are ZIP archives)
            if file_extension == '.xlsx':
                try:
                    import zipfile
                    with zipfile.ZipFile(path, 'r') as zip_file:
                        # Check for required Excel file structure
                        required_files = ['xl/workbook.xml', 'xl/worksheets/']
                        for required_file in required_files:
                            if not any(name.startswith(required_file) for name in zip_file.namelist()):
                                return ValidationResult(
                                    field_name="file_format",
                                    is_valid=False,
                                    message=f"File does not appear to be a valid Excel file: missing {required_file}",
                                    severity="ERROR",
                                    location=str(path),
                                    context={"missing_structure": required_file}
                                )
                except zipfile.BadZipFile:
                    return ValidationResult(
                        field_name="file_format",
                        is_valid=False,
                        message="File is not a valid ZIP archive (corrupted Excel file)",
                        severity="ERROR",
                        location=str(path)
                    )
            
            # For .xls files, check if it's a valid OLE2 compound file
            elif file_extension == '.xls':
                try:
                    # Basic check for OLE2 compound file header
                    with open(path, 'rb') as f:
                        header = f.read(8)
                        if header != b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
                            return ValidationResult(
                                field_name="file_format",
                                is_valid=False,
                                message="File does not appear to be a valid Excel .xls file (invalid header)",
                                severity="ERROR",
                                location=str(path)
                            )
                except Exception as e:
                    return ValidationResult(
                        field_name="file_format",
                        is_valid=False,
                        message=f"Error reading .xls file header: {str(e)}",
                        severity="ERROR",
                        location=str(path),
                        context={"exception": str(e)}
                    )
            
            return ValidationResult(
                field_name="file_format",
                is_valid=True,
                message=f"File format is valid: {file_extension}",
                severity="INFO",
                location=str(path),
                context={"file_extension": file_extension}
            )
            
        except Exception as e:
            return ValidationResult(
                field_name="file_format",
                is_valid=False,
                message=f"File format validation error: {str(e)}",
                severity="ERROR",
                location=str(path),
                context={"exception": str(e)}
            )
    
    def validate_file_size(self, path: Path, max_size_mb: Optional[int] = None) -> ValidationResult:
        """
        Validate that the file size is within acceptable limits.
        
        Args:
            path: Path to the file to validate
            max_size_mb: Maximum allowed file size in MB. If None, uses config default.
            
        Returns:
            ValidationResult: Result of the file size validation
        """
        try:
            # Use provided max size or config default
            max_size = max_size_mb or self.config.max_file_size_mb
            
            # Get file size in bytes
            file_size_bytes = path.stat().st_size
            file_size_mb = file_size_bytes / (1024 * 1024)
            
            if file_size_mb > max_size:
                return ValidationResult(
                    field_name="file_size",
                    is_valid=False,
                    message=f"File size {file_size_mb:.2f}MB exceeds maximum allowed {max_size}MB",
                    severity="ERROR",
                    location=str(path),
                    context={
                        "file_size_mb": file_size_mb,
                        "max_size_mb": max_size,
                        "file_size_bytes": file_size_bytes
                    }
                )
            
            return ValidationResult(
                field_name="file_size",
                is_valid=True,
                message=f"File size {file_size_mb:.2f}MB is within limits",
                severity="INFO",
                location=str(path),
                context={
                    "file_size_mb": file_size_mb,
                    "max_size_mb": max_size,
                    "file_size_bytes": file_size_bytes
                }
            )
            
        except Exception as e:
            return ValidationResult(
                field_name="file_size",
                is_valid=False,
                message=f"File size validation error: {str(e)}",
                severity="ERROR",
                location=str(path),
                context={"exception": str(e)}
            )
    
    def validate_workbook_structure(self, wb: Workbook) -> ValidationResult:
        """
        Validate the internal structure of the workbook.
        
        This method performs basic structural validation including:
        - Workbook has at least one worksheet
        - Worksheet names are valid
        - Basic workbook properties are accessible
        
        Args:
            wb: OpenPyXL workbook object to validate
            
        Returns:
            ValidationResult: Result of the workbook structure validation
        """
        try:
            # Check if workbook has worksheets
            if not wb.worksheets:
                return ValidationResult(
                    field_name="workbook_structure",
                    is_valid=False,
                    message="Workbook contains no worksheets",
                    severity="ERROR",
                    location="workbook"
                )
            
            # Check worksheet count against config limit
            if len(wb.worksheets) > self.config.max_tabs:
                return ValidationResult(
                    field_name="workbook_structure",
                    is_valid=False,
                    message=f"Workbook has {len(wb.worksheets)} worksheets, exceeds limit of {self.config.max_tabs}",
                    severity="ERROR",
                    location="workbook",
                    context={
                        "worksheet_count": len(wb.worksheets),
                        "max_tabs": self.config.max_tabs
                    }
                )
            
            # Validate worksheet names
            invalid_names = []
            for ws in wb.worksheets:
                if not self._is_valid_worksheet_name(ws.title):
                    invalid_names.append(ws.title)
            
            if invalid_names:
                return ValidationResult(
                    field_name="workbook_structure",
                    is_valid=False,
                    message=f"Workbook contains invalid worksheet names: {invalid_names}",
                    severity="ERROR",
                    location="workbook",
                    context={"invalid_names": invalid_names}
                )
            
            # Check workbook properties
            try:
                # Basic property access test
                _ = wb.properties
                _ = wb.active
            except Exception as e:
                return ValidationResult(
                    field_name="workbook_structure",
                    is_valid=False,
                    message=f"Workbook properties are not accessible: {str(e)}",
                    severity="ERROR",
                    location="workbook",
                    context={"exception": str(e)}
                )
            
            return ValidationResult(
                field_name="workbook_structure",
                is_valid=True,
                message=f"Workbook structure is valid with {len(wb.worksheets)} worksheets",
                severity="INFO",
                location="workbook",
                context={
                    "worksheet_count": len(wb.worksheets),
                    "worksheet_names": [ws.title for ws in wb.worksheets]
                }
            )
            
        except Exception as e:
            return ValidationResult(
                field_name="workbook_structure",
                is_valid=False,
                message=f"Workbook structure validation error: {str(e)}",
                severity="ERROR",
                location="workbook",
                context={"exception": str(e)}
            )
    
    def validate_required_tabs(self, wb: Workbook, required_tabs: List[str]) -> ValidationResult:
        """
        Validate that required tabs are present in the workbook.
        
        Args:
            wb: OpenPyXL workbook object to validate
            required_tabs: List of required worksheet names
            
        Returns:
            ValidationResult: Result of the required tabs validation
        """
        try:
            if not required_tabs:
                return ValidationResult(
                    field_name="required_tabs",
                    is_valid=True,
                    message="No required tabs specified",
                    severity="INFO",
                    location="workbook"
                )
            
            # Get actual worksheet names
            actual_tabs = [ws.title for ws in wb.worksheets]
            missing_tabs = [tab for tab in required_tabs if tab not in actual_tabs]
            
            if missing_tabs:
                return ValidationResult(
                    field_name="required_tabs",
                    is_valid=False,
                    message=f"Required tabs missing: {missing_tabs}",
                    severity="ERROR",
                    location="workbook",
                    context={
                        "required_tabs": required_tabs,
                        "actual_tabs": actual_tabs,
                        "missing_tabs": missing_tabs
                    }
                )
            
            return ValidationResult(
                field_name="required_tabs",
                is_valid=True,
                message=f"All required tabs are present: {required_tabs}",
                severity="INFO",
                location="workbook",
                context={
                    "required_tabs": required_tabs,
                    "actual_tabs": actual_tabs
                }
            )
            
        except Exception as e:
            return ValidationResult(
                field_name="required_tabs",
                is_valid=False,
                message=f"Required tabs validation error: {str(e)}",
                severity="ERROR",
                location="workbook",
                context={"exception": str(e)}
            )
    
    def validate_file_comprehensive(self, path: Path, required_tabs: Optional[List[str]] = None) -> List[ValidationResult]:
        """
        Perform comprehensive file validation including all checks.
        
        This method runs all validation checks and returns a list of results.
        It's useful for getting a complete picture of file validity.
        
        Args:
            path: Path to the file to validate
            required_tabs: Optional list of required worksheet names
            
        Returns:
            List[ValidationResult]: List of all validation results
        """
        results = []
        
        # File path validation
        if self.config.validate_file_exists:
            results.append(self.validate_file_path(path))
        
        # File format validation
        if self.config.validate_file_format:
            results.append(self.validate_file_format(path))
        
        # File size validation
        results.append(self.validate_file_size(path))
        
        # If basic validations pass, try to validate workbook structure
        basic_validations = [r for r in results if r.field_name in ['file_path', 'file_format', 'file_size']]
        if all(r.is_valid for r in basic_validations):
            try:
                wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
                
                # Workbook structure validation
                results.append(self.validate_workbook_structure(wb))
                
                # Required tabs validation
                if required_tabs:
                    results.append(self.validate_required_tabs(wb, required_tabs))
                
                wb.close()
                
            except Exception as e:
                results.append(ValidationResult(
                    field_name="workbook_loading",
                    is_valid=False,
                    message=f"Failed to load workbook for validation: {str(e)}",
                    severity="ERROR",
                    location=str(path),
                    context={"exception": str(e)}
                ))
        
        return results
    
    def is_file_valid(self, path: Path, required_tabs: Optional[List[str]] = None) -> bool:
        """
        Check if a file passes all validation checks.
        
        This is a convenience method that returns a simple boolean
        indicating whether the file is valid according to all checks.
        
        Args:
            path: Path to the file to validate
            required_tabs: Optional list of required worksheet names
            
        Returns:
            bool: True if file passes all validations, False otherwise
        """
        results = self.validate_file_comprehensive(path, required_tabs)
        return all(result.is_valid for result in results)
    
    def get_validation_summary(self, results: List[ValidationResult]) -> str:
        """
        Get a human-readable summary of validation results.
        
        Args:
            results: List of validation results to summarize
            
        Returns:
            str: Human-readable summary of validation results
        """
        if not results:
            return "No validation results to summarize"
        
        total_checks = len(results)
        passed_checks = sum(1 for r in results if r.is_valid)
        failed_checks = total_checks - passed_checks
        
        summary = f"Validation Summary: {passed_checks}/{total_checks} checks passed"
        
        if failed_checks > 0:
            failed_details = [f"{r.field_name}: {r.message}" for r in results if not r.is_valid]
            summary += f"\nFailed checks:\n" + "\n".join(f"  - {detail}" for detail in failed_details)
        
        return summary
    
    def _is_valid_worksheet_name(self, name: str) -> bool:
        """
        Check if a worksheet name is valid.
        
        Excel worksheet names have certain restrictions:
        - Cannot be empty
        - Cannot exceed 31 characters
        - Cannot contain certain characters: [ ] : * ? / \
        
        Args:
            name: Worksheet name to validate
            
        Returns:
            bool: True if name is valid, False otherwise
        """
        if not name or len(name.strip()) == 0:
            return False
        
        if len(name) > 31:
            return False
        
        # Check for invalid characters
        invalid_chars = ['[', ']', ':', '*', '?', '/', '\\']
        if any(char in name for char in invalid_chars):
            return False
        
        return True
