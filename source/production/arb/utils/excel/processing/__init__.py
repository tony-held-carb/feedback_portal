"""
Processing module for Excel data extraction and transformation.

This module provides comprehensive data processing capabilities for Excel files,
including cell value processing, schema resolution, and tab data extraction.

Classes:
    CellValueProcessor: Handles cell value processing and type conversion
    SchemaResolver: Handles schema resolution and aliasing
    TabExtractor: Handles the extraction of data from individual tabs

Author: AI Assistant
Created: 2025-01-27
Version: 1.0
"""

from .excel_processor import ExcelProcessor

__all__ = [
    'ExcelProcessor'
]

__version__ = "1.0.0"
__author__ = "AI Assistant"
__created__ = "2025-01-27"
