"""
import_audit.py

This module generates a robust, human-readable audit trail for Excel file imports in the feedback portal.

Purpose:
    - To provide a double-check of the import process by independently reading the Excel file and comparing its contents to the schema and the output of parse_xl_file.
    - To help users and developers diagnose issues with field mapping, type conversion, whitespace, and dropdown validation.
    - To provide a clear, aligned, per-field diagnostic log for compliance and debugging.

How it works:
    - Takes the output of parse_xl_file(file_path) (parse_result) and the schema map.
    - Independently opens the Excel file with openpyxl.
    - For each field in the schema for the tab of interest (e.g., 'Feedback Form'), it:
        * Reads the raw value and label from the spreadsheet.
        * Compares them to the schema.
        * Attempts type conversion and whitespace cleaning, logging any issues.
        * Summarizes label and value matches.

Limitations:
    - This audit does NOT use the portal's main logging infrastructure or business logic; it is a static, schema-driven check.
    - It may not catch all business logic errors, cross-field dependencies, or dynamic validation rules enforced elsewhere in the portal.
    - It is intended as a best-effort, field-level diagnostic and not a full validation of the import pipeline.

Usage:
    generate_import_audit(file_path, parse_result, schema_map, logs=None, route="")

Output:
    Returns a string suitable for writing to a log file.
"""

from typing import Optional, Any, Dict, List, Tuple
from pathlib import Path
import openpyxl
import json
import datetime
from arb.utils.json import json_serializer

# =========================
# Utility Functions
# =========================
def pad_label(label: str, width: int = 21) -> str:
    """Pad a label to a fixed width for aligned output."""
    return label.ljust(width)

def normalize_label(label: Any) -> str:
    """Normalize a label for audit display (strip, replace line breaks)."""
    if isinstance(label, str):
        return label.strip().replace('\n', ' ').replace('\r', ' ')
    return label

# =========================
# Header Section
# =========================
def format_header(file_path: Path, route: str, parse_result: Dict) -> List[str]:
    """
    Generate the audit log header with file, schema, and sector info.
    Args:
        file_path: Path to the imported file.
        route: Route or context for the import (for logging).
        parse_result: Output of parse_xl_file (metadata, schemas, tab_contents).
    Returns:
        List of header lines for the audit log.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"Import of file named {file_path.name} began at {now}."]
    if route:
        lines.append(f"Route: {route}")
    lines.append("")
    meta = parse_result.get('metadata', {})
    schema_tab = parse_result.get('schemas', {})
    lines.append("the following information was extracted from the _json_schema tab:")
    lines.append(json.dumps(schema_tab, indent=2, default=json_serializer))
    lines.append("")
    lines.append("the following information was extracted from the _json_metadata tab:")
    lines.append(json.dumps(meta, indent=2, default=json_serializer))
    lines.append("")
    sector = meta.get('sector') or meta.get('Sector')
    schema_name = None
    if schema_tab:
        schema_name = next(iter(schema_tab.values()), None)
    lines.append(f"the sector for this file is: {sector}")
    lines.append(f"the schema for this file is: {schema_name}")
    lines.append("")
    return lines

# =========================
# Type Conversion & Cleaning
# =========================
def try_type_conversion(raw_value: Any, value_type: Any) -> Tuple[Any, List[str]]:
    """
    Attempt to convert raw_value to value_type. Return (converted_value, logs).
    Logs are human-readable explanations of what happened.
    """
    logs = []
    db_value = raw_value
    if raw_value is not None:
        if value_type and not isinstance(raw_value, value_type):
            if raw_value == "":
                db_value = None
                logs.append(f"Type conversion failed: empty string for expected type {getattr(value_type, '__name__', str(value_type))}. Value set to None.")
            else:
                try:
                    if value_type == datetime.datetime:
                        from arb.utils.date_and_time import excel_str_to_naive_datetime, is_datetime_naive
                        excel_val = raw_value
                        if not isinstance(excel_val, str):
                            excel_val = str(excel_val)
                        local_datetime = excel_str_to_naive_datetime(excel_val)
                        if local_datetime and not is_datetime_naive(local_datetime):
                            logs.append(f"Type conversion failed: parsed datetime is not naive for value '{raw_value}'. Value set to None.")
                            db_value = None
                        elif local_datetime is None:
                            logs.append(f"Type conversion failed: could not parse '{raw_value}' as datetime. Value set to None.")
                            db_value = None
                        else:
                            db_value = local_datetime
                            logs.append(f"Type conversion successful: '{raw_value}' → {db_value} (datetime)")
                    else:
                        converted = value_type(raw_value)
                        db_value = converted
                        logs.append(f"Type conversion successful: '{raw_value}' → {db_value} ({getattr(value_type, '__name__', str(value_type))})")
                except (ValueError, TypeError) as e:
                    logs.append(f"Type conversion failed: could not convert '{raw_value}' to {getattr(value_type, '__name__', str(value_type))}: {e}. Value set to None.")
                    db_value = None
    return db_value, logs

# =========================
# Field Diagnostics Section
# =========================
def field_diagnostics(
    field: str,
    lookup: Dict,
    ws: Any,
    logs: List[str]
) -> List[str]:
    """
    Generate diagnostics for a single field, including label/value comparison,
    whitespace warnings, type conversion logs, and dropdown validation.
    Args:
        field: Field name (schema key).
        lookup: Schema dict for this field.
        ws: openpyxl worksheet for the tab.
        logs: List of log messages from the import process.
    Returns:
        List of lines for this field's diagnostics.
    """
    pad = lambda label: pad_label(label, 21)
    field_lines = []
    schema_label = lookup.get('label')
    label_address = lookup.get('label_address')
    value_address = lookup.get('value_address')
    value_type = lookup.get('value_type')
    is_drop_down = lookup.get('is_drop_down')
    # Spreadsheet label
    spreadsheet_label = None
    if label_address:
        try:
            cell = ws[label_address]
            if isinstance(cell, tuple):
                cell = cell[0]
            spreadsheet_label = cell.value
        except Exception:
            spreadsheet_label = None
    label_match = (spreadsheet_label == schema_label) if (spreadsheet_label is not None and schema_label is not None) else None
    # Spreadsheet value
    spreadsheet_raw_value = None
    if value_address:
        try:
            cell = ws[value_address]
            if isinstance(cell, tuple):
                cell = cell[0]
            spreadsheet_raw_value = cell.value
        except Exception:
            spreadsheet_raw_value = None
    # Type conversion and cleaning
    db_value, conversion_logs = try_type_conversion(spreadsheet_raw_value, value_type)
    # Remove dropdown analysis
    # dropdown_valid = None
    # if is_drop_down:
    #     allowed_values = lookup.get('allowed_values')
    #     if allowed_values is not None:
    #         dropdown_valid = db_value in allowed_values
    # Value match logic
    value_match_line = None
    if db_value == spreadsheet_raw_value:
        value_match_line = f"  {pad('value match')} : True"
    elif (
        (isinstance(spreadsheet_raw_value, (int, float, str)) and isinstance(db_value, (int, float, str)))
        and str(spreadsheet_raw_value) == str(db_value)
    ):
        value_match_line = f"  {pad('value match')} : True (type conversion: {type(spreadsheet_raw_value).__name__} → {type(db_value).__name__}, value preserved)"
    else:
        value_match_line = f"  {pad('value match')} : False"
    # Whitespace cleaning for audit display and warnings
    display_spreadsheet_raw_value = spreadsheet_raw_value.strip() if isinstance(spreadsheet_raw_value, str) else spreadsheet_raw_value
    display_db_value = db_value.strip() if isinstance(db_value, str) else db_value
    if isinstance(spreadsheet_raw_value, str) and spreadsheet_raw_value != display_spreadsheet_raw_value:
        field_lines.append(f"  whitespace warning     : spreadsheet_raw_value before strip: {json.dumps(spreadsheet_raw_value, default=json_serializer)} after strip: {json.dumps(display_spreadsheet_raw_value, default=json_serializer)}")
    if isinstance(db_value, str) and db_value != display_db_value:
        field_lines.append(f"  whitespace warning     : db_value before strip: {json.dumps(db_value, default=json_serializer)} after strip: {json.dumps(display_db_value, default=json_serializer)}")
    # Aligned output
    field_lines.append(f"{field} diagnostics:")
    field_lines.append(f"  {pad('data type')} : {getattr(value_type, '__name__', str(value_type)) if value_type else None}")
    field_lines.append(f"  {pad('is_drop_down')} : {is_drop_down}")
    field_lines.append(f"  {pad('label schema')} : {json.dumps(schema_label, default=json_serializer)}")
    field_lines.append(f"  {pad('label spreadsheet')} : {json.dumps(spreadsheet_label, default=json_serializer)}")
    field_lines.append(f"  {pad('label match')} : {label_match}")
    field_lines.append(f"  {pad('value spreadsheet raw')} : {json.dumps(display_spreadsheet_raw_value, default=json_serializer)}")
    field_lines.append(f"  {pad('value db')} : {json.dumps(display_db_value, default=json_serializer)}")
    field_lines.append(value_match_line)
    # Remove dropdown valid output
    # if is_drop_down:
    #     field_lines.append(f"  {pad('dropdown valid')} : {dropdown_valid}")
    if conversion_logs:
        field_lines.append(f"  {pad('associated logs')} : {conversion_logs}")
    return field_lines + [""]

# =========================
# Summary Section
# =========================
def summary_section(label_match_count: int, label_mismatch_count: int, value_match_count: int, value_mismatch_count: int) -> List[str]:
    """
    Generate the summary section for the audit log.
    Args:
        label_match_count: Number of fields with label match True.
        label_mismatch_count: Number of fields with label match False.
        value_match_count: Number of fields with value match True.
        value_mismatch_count: Number of fields with value match False.
    Returns:
        List of lines for the summary section.
    """
    return [
        "",
        "Summary:",
        f"  label match: {label_match_count} pass, {label_mismatch_count} fail",
        f"  value match: {value_match_count} pass, {value_mismatch_count} fail"
    ]

# =========================
# Main Audit Entry Point
# =========================
def generate_import_audit(
    file_path: Path,
    parse_result: Dict,
    schema_map: Dict,
    logs: Optional[List[str]] = None,
    route: str = ""
) -> str:
    """
    Generate a human-readable audit trail for an Excel import.

    Args:
        file_path: Path to the imported file.
        parse_result: Output of parse_xl_file (metadata, schemas, tab_contents).
        schema_map: Loaded schema map (from xl_parse.py).
        logs: List of log messages from the import process.
        route: Route or context for the import (for logging).

    Returns:
        The audit log as a string.
    """
    if logs is None:
        logs = []
    lines = format_header(file_path, route, parse_result)
    tab_name = 'Feedback Form'
    tab_schemas = parse_result.get('schemas', {})
    if tab_name not in tab_schemas:
        lines.append(f"Tab: {tab_name} not found in spreadsheet schemas.")
        return '\n'.join(lines)
    schema_version = tab_schemas[tab_name]
    if schema_version not in schema_map:
        lines.append(f"Schema version '{schema_version}' not found in schema_map.")
        return '\n'.join(lines)
    schema_dict = schema_map[schema_version]['schema']
    wb = openpyxl.load_workbook(file_path, data_only=True)
    if tab_name not in wb.sheetnames:
        lines.append(f"Tab: {tab_name} not found in Excel file.")
        return '\n'.join(lines)
    ws = wb[tab_name]
    lines.append(f"Tab: {tab_name} diagnostics:")
    label_match_count = 0
    label_mismatch_count = 0
    value_match_count = 0
    value_mismatch_count = 0
    for field, lookup in schema_dict.items():
        field_lines = field_diagnostics(field, lookup, ws, logs)
        # Count matches for summary
        for line in field_lines:
            if line.strip().startswith('label match'):
                if line.strip().endswith('True'):
                    label_match_count += 1
                elif line.strip().endswith('False'):
                    label_mismatch_count += 1
            if line.strip().startswith('value match'):
                if line.strip().endswith('True'):
                    value_match_count += 1
                elif line.strip().endswith('False'):
                    value_mismatch_count += 1
        lines.extend(field_lines)
    lines.extend(summary_section(label_match_count, label_mismatch_count, value_match_count, value_mismatch_count))
    return '\n'.join(lines) 