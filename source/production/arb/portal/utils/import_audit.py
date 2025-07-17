import datetime
import json
from pathlib import Path
from typing import Optional
from arb.utils.json import json_serializer
import openpyxl


def generate_import_audit(
    file_path: Path,
    parse_result: dict,
    schema_map: dict,
    logs: Optional[list[str]] = None,
    route: str = ""
) -> str:
    if logs is None:
        logs = []
    lines = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"Import of file named {file_path.name} began at {now}.")
    if route:
        lines.append(f"Route: {route}")
    lines.append("")
    # Metadata and schema
    meta = parse_result.get('metadata', {})
    schema_tab = parse_result.get('schemas', {})
    lines.append("the following information was extracted from the _json_schema tab:")
    lines.append(json.dumps(schema_tab, indent=2, default=json_serializer))
    lines.append("")
    lines.append("the following information was extracted from the _json_metadata tab:")
    lines.append(json.dumps(meta, indent=2, default=json_serializer))
    lines.append("")
    # Sector and schema
    sector = meta.get('sector') or meta.get('Sector')
    schema_name = None
    if schema_tab:
        schema_name = next(iter(schema_tab.values()), None)
    lines.append(f"the sector for this file is: {sector}")
    lines.append(f"the schema for this file is: {schema_name}")
    lines.append("")
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
    label_pad = 21
    label_match_count = 0
    label_mismatch_count = 0
    value_match_count = 0
    value_mismatch_count = 0
    for field, lookup in schema_dict.items():
        field_lines = []
        schema_label = lookup.get('label')
        label_address = lookup.get('label_address')
        value_address = lookup.get('value_address')
        value_type = lookup.get('value_type')
        is_drop_down = lookup.get('is_drop_down')
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
        if label_match is True:
            label_match_count += 1
        elif label_match is False:
            label_mismatch_count += 1
        spreadsheet_raw_value = None
        if value_address:
            try:
                cell = ws[value_address]
                if isinstance(cell, tuple):
                    cell = cell[0]
                spreadsheet_raw_value = cell.value
            except Exception:
                spreadsheet_raw_value = None
        db_value = spreadsheet_raw_value
        conversion_logs = []
        if spreadsheet_raw_value is not None:
            if value_type and not isinstance(spreadsheet_raw_value, value_type):
                if spreadsheet_raw_value == "":
                    db_value = None
                else:
                    try:
                        if value_type == datetime.datetime:
                            from arb.utils.date_and_time import excel_str_to_naive_datetime, is_datetime_naive
                            excel_val = spreadsheet_raw_value
                            if not isinstance(excel_val, str):
                                excel_val = str(excel_val)
                            local_datetime = excel_str_to_naive_datetime(excel_val)
                            if local_datetime and not is_datetime_naive(local_datetime):
                                conversion_logs.append(f"Date time {spreadsheet_raw_value} is not a naive datetime, skipping to avoid data corruption")
                                db_value = None
                            else:
                                db_value = local_datetime
                        else:
                            db_value = value_type(spreadsheet_raw_value)
                        conversion_logs.append(f"Type conversion successful. value is now <{db_value}> with type: <{type(db_value)}>")
                    except (ValueError, TypeError) as e:
                        conversion_logs.append(f"Type conversion failed: {e}. Resetting value to None.")
                        db_value = None
        dropdown_valid = None
        if is_drop_down:
            allowed_values = lookup.get('allowed_values')
            if allowed_values is not None:
                dropdown_valid = db_value in allowed_values
        value_match = (db_value == spreadsheet_raw_value)
        if value_match is True:
            value_match_count += 1
        elif value_match is False:
            value_mismatch_count += 1
        # Aligned output
        def pad(label):
            return label.ljust(label_pad)
        field_lines.append(f"{field} diagnostics:")
        field_lines.append(f"  {pad('data type')} : {getattr(value_type, '__name__', str(value_type)) if value_type else None}")
        field_lines.append(f"  {pad('is_drop_down')} : {is_drop_down}")
        field_lines.append(f"  {pad('label schema')} : {json.dumps(schema_label, default=json_serializer)}")
        field_lines.append(f"  {pad('label spreadsheet')} : {json.dumps(spreadsheet_label, default=json_serializer)}")
        field_lines.append(f"  {pad('label match')} : {label_match}")
        field_lines.append(f"  {pad('value spreadsheet raw')} : {json.dumps(spreadsheet_raw_value, default=json_serializer)}")
        field_lines.append(f"  {pad('value db')} : {json.dumps(db_value, default=json_serializer)}")
        field_lines.append(f"  {pad('value match')} : {value_match}")
        if is_drop_down:
            field_lines.append(f"  {pad('dropdown valid')} : {dropdown_valid}")
        if conversion_logs:
            field_lines.append(f"  {pad('associated logs')} : {conversion_logs}")
        lines.extend(field_lines)
        lines.append("")
    # Remove extra value addresses output
    # (do not output anything about extra_addresses)
    # Add summary
    lines.append("")
    lines.append(f"Summary:")
    lines.append(f"  label match: {label_match_count} pass, {label_mismatch_count} fail")
    lines.append(f"  value match: {value_match_count} pass, {value_mismatch_count} fail")
    return '\n'.join(lines) 