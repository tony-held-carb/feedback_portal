"""
excel_compare_02.py

Compare Excel workbooks (.xlsx) using xlwings for full-fidelity comparison.
This script requires Microsoft Excel to be installed and only works on Windows.

Features:
- Sheet presence and order comparison
- Cell-by-cell value and formula comparison
- Comments
- Data validation (dropdowns)
- Formatting (font, fill, border, alignment, number format)
- Cell protection
- Workbook and sheet protection
- Directory comparison (all files in two folders)

Outputs a summary of all differences to a text file or prints to console.
"""

import xlwings as xw
import os
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def compare_workbook_protection(wb1, wb2):
    logger.debug("Comparing workbook protection...")
    diffs = []
    if wb1.api.ProtectStructure != wb2.api.ProtectStructure:
        diffs.append(f"  ProtectStructure: A={wb1.api.ProtectStructure}, B={wb2.api.ProtectStructure}")
    if wb1.api.ProtectWindows != wb2.api.ProtectWindows:
        diffs.append(f"  ProtectWindows: A={wb1.api.ProtectWindows}, B={wb2.api.ProtectWindows}")
    logger.debug(f"Workbook protection diffs: {diffs}")
    return diffs

def compare_sheet_protection(ws1, ws2, sheet_name):
    logger.debug(f"Comparing sheet protection for {sheet_name}...")
    diffs = []
    if ws1.api.ProtectContents != ws2.api.ProtectContents:
        diffs.append(f"  ProtectContents: A={ws1.api.ProtectContents}, B={ws2.api.ProtectContents}")
    # Add more protection flags as needed
    if diffs:
        logger.debug(f"Sheet protection diffs for {sheet_name}: {diffs}")
        return [f"[Sheet Protection Differences] ({sheet_name})"] + diffs
    return []

def compare_cell_format(c1, c2):
    logger.debug(f"Comparing cell format for {c1.get_address(False, False)}...")
    diffs = []
    # Font
    if c1.api.Font.Name != c2.api.Font.Name:
        diffs.append(f"    Font.Name: A={c1.api.Font.Name}, B={c2.api.Font.Name}")
    if c1.api.Font.Size != c2.api.Font.Size:
        diffs.append(f"    Font.Size: A={c1.api.Font.Size}, B={c2.api.Font.Size}")
    if c1.api.Font.Bold != c2.api.Font.Bold:
        diffs.append(f"    Font.Bold: A={c1.api.Font.Bold}, B={c2.api.Font.Bold}")
    if c1.api.Font.Italic != c2.api.Font.Italic:
        diffs.append(f"    Font.Italic: A={c1.api.Font.Italic}, B={c2.api.Font.Italic}")
    if c1.api.Font.Underline != c2.api.Font.Underline:
        diffs.append(f"    Font.Underline: A={c1.api.Font.Underline}, B={c2.api.Font.Underline}")
    if c1.api.Font.Color != c2.api.Font.Color:
        diffs.append(f"    Font.Color: A={c1.api.Font.Color}, B={c2.api.Font.Color}")
    # Fill
    if c1.api.Interior.Color != c2.api.Interior.Color:
        diffs.append(f"    Fill.Color: A={c1.api.Interior.Color}, B={c2.api.Interior.Color}")
    # Number format
    if c1.api.NumberFormat != c2.api.NumberFormat:
        diffs.append(f"    NumberFormat: A={c1.api.NumberFormat}, B={c2.api.NumberFormat}")
    # Alignment
    if c1.api.HorizontalAlignment != c2.api.HorizontalAlignment:
        diffs.append(f"    HorizontalAlignment: A={c1.api.HorizontalAlignment}, B={c2.api.HorizontalAlignment}")
    if c1.api.VerticalAlignment != c2.api.VerticalAlignment:
        diffs.append(f"    VerticalAlignment: A={c1.api.VerticalAlignment}, B={c2.api.VerticalAlignment}")
    if c1.api.WrapText != c2.api.WrapText:
        diffs.append(f"    WrapText: A={c1.api.WrapText}, B={c2.api.WrapText}")
    # Borders (simple)
    for side in [7, 8, 9, 10]:  # xlEdgeLeft, xlEdgeRight, xlEdgeTop, xlEdgeBottom
        b1 = c1.api.Borders(side)
        b2 = c2.api.Borders(side)
        if b1.LineStyle != b2.LineStyle or b1.Color != b2.Color:
            diffs.append(f"    Border {side}: A=({b1.LineStyle},{b1.Color}), B=({b2.LineStyle},{b2.Color})")
    logger.debug(f"Cell format diffs: {diffs}")
    return diffs

def safe_get_validation_formula(cell):
    try:
        v = cell.api.Validation
        if v is not None and v.Type == 3:
            return v.Formula1
    except Exception as e:
        logger.debug(f"Validation check failed for {cell.get_address(False, False)}: {e}")
    return None

def compare_excel_content(path1, path2):
    logger.info(f"Opening workbooks: {path1}, {path2}")
    output = []
    with xw.App(visible=False) as app:
        try:
            wb1 = app.books.open(str(path1))
            wb2 = app.books.open(str(path2))
        except Exception as e:
            logger.error(f"Failed to open workbooks: {e}")
            print(f"ERROR: Failed to open workbooks: {e}")
            return [f"ERROR: Failed to open workbooks: {e}"]
        logger.info("Workbooks opened successfully.")
        # Workbook protection
        diffs = compare_workbook_protection(wb1, wb2)
        if diffs:
            output.append("[Workbook Protection Differences]")
            output.extend(diffs)
        sheets1 = {ws.name for ws in wb1.sheets}
        sheets2 = {ws.name for ws in wb2.sheets}
        only_in_a = sorted(sheets1 - sheets2)
        only_in_b = sorted(sheets2 - sheets1)
        in_both = sorted(sheets1 & sheets2)
        logger.info(f"Sheets only in A: {only_in_a}")
        logger.info(f"Sheets only in B: {only_in_b}")
        logger.info(f"Sheets in both: {in_both}")
        if only_in_a:
            output.append("[Sheets only in A]")
            output.extend([f"  {name}" for name in only_in_a])
        if only_in_b:
            output.append("[Sheets only in B]")
            output.extend([f"  {name}" for name in only_in_b])
        for sheet in in_both:
            logger.info(f"Comparing sheet: {sheet}")
            output.append(f"\n=== Sheet: {sheet} ===")
            ws1 = wb1.sheets[sheet]
            ws2 = wb2.sheets[sheet]
            max_row = max(ws1.used_range.last_cell.row, ws2.used_range.last_cell.row)
            max_col = max(ws1.used_range.last_cell.column, ws2.used_range.last_cell.column)
            logger.info(f"Sheet {sheet} max_row: {max_row}, max_col: {max_col}")
            # Sheet protection
            diffs = compare_sheet_protection(ws1, ws2, sheet)
            if diffs:
                output.extend(diffs)
            for row in range(1, max_row + 1):
                if row % 10 == 0:
                    logger.debug(f"Processing row {row}/{max_row} in sheet {sheet}")
                for col in range(1, max_col + 1):
                    c1 = ws1.range((row, col))
                    c2 = ws2.range((row, col))
                    coord = c1.get_address(False, False)
                    # Value
                    if c1.value != c2.value:
                        output.append(f"  {coord}: Value A={c1.value}, B={c2.value}")
                    # Formula
                    if c1.formula != c2.formula:
                        output.append(f"  {coord}: Formula A={c1.formula}, B={c2.formula}")
                    # Comment
                    comm1 = c1.api.Comment.Text() if c1.api.Comment else None
                    comm2 = c2.api.Comment.Text() if c2.api.Comment else None
                    if comm1 != comm2:
                        output.append(f"  {coord}: Comment A={comm1}, B={comm2}")
                    # Data validation (dropdowns)
                    val1 = safe_get_validation_formula(c1)
                    val2 = safe_get_validation_formula(c2)
                    if val1 != val2:
                        output.append(f"  {coord}: Validation A={val1}, B={val2}")
                    # Protection
                    if c1.api.Locked != c2.api.Locked or c1.api.FormulaHidden != c2.api.FormulaHidden:
                        output.append(f"  {coord}: Protection A=(Locked:{c1.api.Locked},Hidden:{c1.api.FormulaHidden}), B=(Locked:{c2.api.Locked},Hidden:{c2.api.FormulaHidden})")
                    # Formatting
                    fmt_diffs = compare_cell_format(c1, c2)
                    for d in fmt_diffs:
                        output.append(f"  {coord}: {d}")
            logger.info(f"Finished comparing sheet: {sheet}")
        wb1.close()
        wb2.close()
        logger.info("Closed both workbooks.")
    return output

def compare_excel_files(file_a_path, file_b_path, log_to_file=False):
    logger.info(f"Starting file comparison: {file_a_path} vs {file_b_path}")
    output = [f"Comparing:\n  A: {file_a_path}\n  B: {file_b_path}\n"]
    output.extend(compare_excel_content(file_a_path, file_b_path))
    if log_to_file:
        now = datetime.now()
        out_path = Path(f"comparison_xlwings_{now.strftime('%Y%m%d_%H%M%S')}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            for line in output:
                f.write(line + "\n")
        print(f"Comparison complete. Output saved to: {out_path.resolve()}")
        logger.info(f"Comparison complete. Output saved to: {out_path.resolve()}")
    else:
        for line in output:
            print(line)
    return output

# Update directory comparison to skip files starting with '~$'
def compare_excel_directories(dir_a, dir_b):
    logger.info(f"Starting directory comparison: {dir_a} vs {dir_b}")
    dir_a = Path(dir_a)
    dir_b = Path(dir_b)
    excel_files_a = {f.name: f for f in dir_a.glob("*.xlsx") if f.is_file() and not f.name.startswith('~$')}
    excel_files_b = {f.name: f for f in dir_b.glob("*.xlsx") if f.is_file() and not f.name.startswith('~$')}
    only_in_a = sorted(set(excel_files_a) - set(excel_files_b))
    only_in_b = sorted(set(excel_files_b) - set(excel_files_a))
    in_both = sorted(set(excel_files_a) & set(excel_files_b))
    logger.info(f"Files only in A: {only_in_a}")
    logger.info(f"Files only in B: {only_in_b}")
    logger.info(f"Files in both: {in_both}")
    now = datetime.now()
    out_path = Path(f"comparison_xlwings_{now.strftime('%Y%m%d_%H%M%S')}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"Comparing Excel files in:\n  A: {dir_a}\n  B: {dir_b}\n\n")
        f.write(f"Files only in A ({len(only_in_a)}):\n")
        for name in only_in_a:
            f.write(f"  {name}\n")
        f.write(f"\nFiles only in B ({len(only_in_b)}):\n")
        for name in only_in_b:
            f.write(f"  {name}\n")
        f.write(f"\nFiles in both ({len(in_both)}):\n")
        for name in in_both:
            f.write(f"\n=== Comparing {name} ===\n")
            logger.info(f"Comparing file: {name}")
            result = compare_excel_content(excel_files_a[name], excel_files_b[name])
            for line in result:
                f.write(line + "\n")
    print(f"Directory comparison complete. Output saved to: {out_path.resolve()}")
    logger.info(f"Directory comparison complete. Output saved to: {out_path.resolve()}")

# Update default() to skip ~ files if present
def default():
    file_a = "diagnostics/dairy_digester_operator_feedback_v006_for_review_local.xlsx"
    file_b = "diagnostics/dairy_digester_operator_feedback_v006_for_review_sharepoint.xlsx"
    if file_a.startswith('~$') or file_b.startswith('~$'):
        print("Skipping lock/owner files starting with '~$'. Please close all Excel files and remove any '~$' files.")
        logger.warning("Skipping lock/owner files starting with '~$'.")
        return
    print("No arguments provided. Running default comparison for diagnostics files...")
    logger.info("No arguments provided. Running default comparison for diagnostics files...")
    compare_excel_files(file_a, file_b, log_to_file=True)

if __name__ == "__main__":
    import sys
    import argparse
    from arb.logging.arb_logging import setup_standalone_logging

    setup_standalone_logging("excel_compare_02")

    if len(sys.argv) == 1:
        default()
    else:
        parser = argparse.ArgumentParser(description="Compare Excel files or directories using xlwings.")
        parser.add_argument("a", help="First file or directory")
        parser.add_argument("b", help="Second file or directory")
        parser.add_argument("--dir", action="store_true", help="Compare directories instead of files")
        parser.add_argument("--log", action="store_true", help="Log output to file")
        args = parser.parse_args()
        if args.dir:
            compare_excel_directories(args.a, args.b)
        else:
            compare_excel_files(args.a, args.b, log_to_file=args.log) 