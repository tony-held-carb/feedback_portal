import hashlib
import re
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


# =========================
# XML Parsing Helpers
# =========================
def parse_shared_strings(xml: str) -> List[str]:
  """Parse sharedStrings.xml and return a list of strings."""
  root = ET.fromstring(xml)
  strings = []
  for si in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
    t = si.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
    if t is not None:
      strings.append(t.text or "")
    else:
      ts = si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
      strings.append(''.join([x.text or '' for x in ts]))
  return strings


def parse_styles(xml: str) -> Dict[int, Dict[str, str]]:
  """Parse styles.xml and return a dict of style index -> formatting dict."""
  root = ET.fromstring(xml)
  numFmts = {}
  for numFmt in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}numFmt'):
    numFmts[numFmt.attrib['numFmtId']] = numFmt.attrib['formatCode']
  fonts = []
  for font in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}font'):
    font_dict = {}
    for child in font:
      font_dict[child.tag.split('}')[-1]] = child.attrib.get('val', child.text)
    fonts.append(font_dict)
  fills = []
  for fill in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}fill'):
    fill_dict = {}
    for child in fill:
      fill_dict[child.tag.split('}')[-1]] = child.attrib.get('val', child.text)
    fills.append(fill_dict)
  borders = []
  for border in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}border'):
    border_dict = {}
    for child in border:
      border_dict[child.tag.split('}')[-1]] = child.attrib.get('val', child.text)
    borders.append(border_dict)
  cellXfs = []
  for xf in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}xf'):
    cellXfs.append(xf.attrib)
  styles = {}
  for idx, xf in enumerate(cellXfs):
    style = {}
    if 'numFmtId' in xf:
      style['numFmt'] = numFmts.get(xf['numFmtId'], xf['numFmtId'])
    if 'fontId' in xf:
      try:
        style['font'] = fonts[int(xf['fontId'])]
      except Exception:
        style['font'] = {}
    if 'fillId' in xf:
      try:
        style['fill'] = fills[int(xf['fillId'])]
      except Exception:
        style['fill'] = {}
    if 'borderId' in xf:
      try:
        style['border'] = borders[int(xf['borderId'])]
      except Exception:
        style['border'] = {}
    style['xf'] = xf
    styles[idx] = style
  return styles


def parse_sheet(xml: str, shared_strings: List[str], styles: Dict[int, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
  """Parse a worksheet XML and return a dict: cell address -> {value, formula, style, ...}"""
  root = ET.fromstring(xml)
  ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
  cells = {}
  for c in root.findall('.//main:c', ns):
    addr = c.attrib['r']
    cell = {}
    v = c.find('main:v', ns)
    f = c.find('main:f', ns)
    t = c.attrib.get('t', None)
    s = c.attrib.get('s', None)
    if t == 's' and v is not None:
      idx = int(v.text)
      cell['value'] = shared_strings[idx] if idx < len(shared_strings) else ''
    elif v is not None:
      cell['value'] = v.text
    else:
      cell['value'] = ''
    if f is not None:
      cell['formula'] = f.text
    # Only attempt style lookup if s is a string and is a valid integer
    if isinstance(s, str):
      s_stripped = s.strip()
      if s_stripped and s_stripped.isdigit():
        style_idx = int(s_stripped)
        cell['style'] = styles.get(style_idx, {})
    cells[addr] = cell
  return cells


def parse_comments(zipf: zipfile.ZipFile, sheet_file: str) -> Dict[str, str]:
  """Parse comments for a given sheet if present."""
  comments = {}
  # Try to find the comments file for this sheet
  base = sheet_file.split('/')[-1].replace('.xml', '')
  comments_file = f'xl/comments{base[5:]}.xml'  # e.g., sheet1 -> comments1
  if comments_file in zipf.namelist():
    root = ET.fromstring(zipf.read(comments_file).decode('utf-8'))
    for comment in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}comment'):
      ref = comment.attrib['ref']
      text = ''.join(
        [t.text or '' for t in comment.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')])
      comments[ref] = text
  return comments


def parse_data_validations(sheet_xml: str) -> Dict[str, str]:
  """Parse data validations (dropdowns) for a sheet."""
  root = ET.fromstring(sheet_xml)
  ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
  validations = {}
  for dv in root.findall('.//main:dataValidation', ns):
    sqref = dv.attrib.get('sqref', '')
    formula1 = dv.find('main:formula1', ns)
    formula2 = dv.find('main:formula2', ns)
    val_str = f"type={dv.attrib.get('type', '')}, formula1={formula1.text if formula1 is not None else ''}, formula2={formula2.text if formula2 is not None else ''}"
    for cell in sqref.split():
      validations[cell] = val_str
  return validations


def parse_hyperlinks(sheet_xml: str) -> Dict[str, str]:
  """Parse hyperlinks for a sheet."""
  root = ET.fromstring(sheet_xml)
  ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
  links = {}
  for hl in root.findall('.//main:hyperlink', ns):
    ref = hl.attrib.get('ref', '')
    target = hl.attrib.get('display', hl.attrib.get('location', hl.attrib.get('tooltip', '')))
    links[ref] = target
  return links


def get_sheet_names(zipf: zipfile.ZipFile) -> List[str]:
  return [f for f in zipf.namelist() if re.match(r'xl/worksheets/sheet[0-9]+.xml', f)]


def parse_workbook(zipf: zipfile.ZipFile) -> Dict[str, Dict[str, Dict[str, str]]]:
  shared_strings = []
  styles = {}
  if 'xl/sharedStrings.xml' in zipf.namelist():
    shared_strings = parse_shared_strings(zipf.read('xl/sharedStrings.xml').decode('utf-8'))
  if 'xl/styles.xml' in zipf.namelist():
    styles = parse_styles(zipf.read('xl/styles.xml').decode('utf-8'))
  sheets = {}
  for sheet_file in get_sheet_names(zipf):
    sheet_name = sheet_file.split('/')[-1].replace('.xml', '')
    sheet_xml = zipf.read(sheet_file).decode('utf-8')
    cells = parse_sheet(sheet_xml, shared_strings, styles)
    comments = parse_comments(zipf, sheet_file)
    validations = parse_data_validations(sheet_xml)
    hyperlinks = parse_hyperlinks(sheet_xml)
    # Merge all info into each cell
    for addr in set(list(cells.keys()) + list(comments.keys()) + list(validations.keys()) + list(hyperlinks.keys())):
      if addr not in cells:
        cells[addr] = {}
      if addr in comments:
        cells[addr]['comment'] = comments[addr]
      if addr in validations:
        cells[addr]['validation'] = validations[addr]
      if addr in hyperlinks:
        cells[addr]['hyperlink'] = hyperlinks[addr]
    sheets[sheet_name] = cells
  return sheets


def excel_range_from_addresses(addresses: List[str]) -> str:
  """
  Convert a list of Excel cell addresses to a range notation.

  Only works for addresses in the same row or same column.

  Args:
      addresses (List[str]): List of Excel cell addresses (e.g., ['A1', 'A2', 'A3']).

  Returns:
      str: Excel range notation (e.g., 'A1:A3') or comma-separated addresses if not consecutive.

  Examples:
      Input : ['A1', 'A2', 'A3']
      Output: 'A1:A3'
      Input : ['A1', 'B1', 'C1']
      Output: 'A1:C1'
      Input : ['A1', 'C3', 'B2']
      Output: 'A1,C3,B2'
  """
  # Only works for addresses in the same row or same column
  if not addresses:
    return ''
  if len(addresses) == 1:
    return addresses[0]
  # Split into columns and rows
  cols = [re.match(r'([A-Z]+)', addr).group(1) for addr in addresses]
  rows = [int(re.match(r'[A-Z]+([0-9]+)', addr).group(1)) for addr in addresses]
  if all(c == cols[0] for c in cols):
    # Same column, consecutive rows
    return f"{cols[0]}{min(rows)}:{cols[0]}{max(rows)}"
  if all(r == rows[0] for r in rows):
    # Same row, consecutive columns
    col_nums = [col_to_num(c) for c in cols]
    min_col = num_to_col(min(col_nums))
    max_col = num_to_col(max(col_nums))
    return f"{min_col}{rows[0]}:{max_col}{rows[0]}"
  # Otherwise, just join with commas
  return ','.join(addresses)


def col_to_num(col: str) -> int:
  """
  Convert Excel column letter to column number.

  Args:
      col (str): Excel column letter (e.g., 'A', 'B', 'AA').

  Returns:
      int: Column number (1-based).

  Examples:
      Input : 'A'
      Output: 1
      Input : 'B'
      Output: 2
      Input : 'AA'
      Output: 27
  """
  num = 0
  for c in col:
    num = num * 26 + (ord(c) - ord('A') + 1)
  return num


def num_to_col(num: int) -> str:
  """
  Convert column number to Excel column letter.

  Args:
      num (int): Column number (1-based).

  Returns:
      str: Excel column letter (e.g., 'A', 'B', 'AA').

  Examples:
      Input : 1
      Output: 'A'
      Input : 2
      Output: 'B'
      Input : 27
      Output: 'AA'
  """
  col = ''
  while num > 0:
    num, rem = divmod(num - 1, 26)
    col = chr(rem + ord('A')) + col
  return col


def canonicalize_font(font: Dict[str, Any]) -> Optional[Tuple[str, str, Any, Any, Any, Any, Any, Any, Any]]:
  """
  Canonicalize font properties for comparison.

  Args:
      font (Dict[str, Any]): Font dictionary from Excel styles.

  Returns:
      Optional[Tuple[str, str, Any, Any, Any, Any, Any, Any, Any]]: Canonicalized font tuple or None if not a dict.

  Examples:
      Input : {'name': 'Arial', 'sz': 12, 'bold': True}
      Output: ('arial', '12', None, None, None, True, None, None, None)
  """
  if not isinstance(font, dict):
    return None
  return (
    font.get('name', '').lower() if font.get('name') else '',
    str(font.get('sz', '')).strip(),
    font.get('color', None),
    font.get('family', None),
    font.get('scheme', None),
    font.get('bold', None),
    font.get('italic', None),
    font.get('underline', None),
    font.get('strike', None),
  )


def canonicalize_fill(fill: Dict[str, Any]) -> Optional[Tuple[Any, Any, Any]]:
  """
  Canonicalize fill properties for comparison.

  Args:
      fill (Dict[str, Any]): Fill dictionary from Excel styles.

  Returns:
      Optional[Tuple[Any, Any, Any]]: Canonicalized fill tuple or None if not a dict.

  Examples:
      Input : {'patternType': 'solid', 'fgColor': {'rgb': 'FF0000'}}
      Output: ('solid', {'rgb': 'FF0000'}, None)
  """
  if not isinstance(fill, dict):
    return None
  return (
    fill.get('patternType', None),
    fill.get('fgColor', None),
    fill.get('bgColor', None),
  )


def canonicalize_border(border: Dict[str, Any]) -> Optional[Tuple[Tuple[str, Any], ...]]:
  """
  Canonicalize border properties for comparison.

  Args:
      border (Dict[str, Any]): Border dictionary from Excel styles.

  Returns:
      Optional[Tuple[Tuple[str, Any], ...]]: Canonicalized border tuple or None if not a dict.

  Examples:
      Input : {'left': {'style': 'thin'}, 'right': {'style': 'thin'}}
      Output: (('left', {'style': 'thin'}), ('right', {'style': 'thin'}))
  """
  if not isinstance(border, dict):
    return None
  return tuple(sorted(border.items()))


def build_font_map(styles: Dict[str, Any]) -> Dict[int, Optional[Tuple[str, str, Any, Any, Any, Any, Any, Any, Any]]]:
  """
  Build a mapping of font indices to canonicalized font properties.

  Args:
      styles (Dict[str, Any]): Excel styles dictionary.

  Returns:
      Dict[int, Optional[Tuple[str, str, Any, Any, Any, Any, Any, Any, Any]]]: Mapping of font index to canonicalized font.

  Examples:
      Input : {'fonts': [{'name': 'Arial', 'sz': 12}, {'name': 'Times', 'sz': 10}]}
      Output: {0: ('arial', '12', None, ...), 1: ('times', '10', None, ...)}
  """
  font_map = {}
  fonts = styles.get('fonts', []) if styles else []
  for idx, font in enumerate(fonts):
    font_map[idx] = canonicalize_font(font)
  return font_map


def compare_workbooks(wb1: Dict[str, Dict[str, Dict[str, str]]], wb2: Dict[str, Dict[str, Dict[str, str]]],
                      verbosity: str = 'significant_only', suppress_trivial_details: bool = True, styles1=None,
                      styles2=None) -> List[str]:
  output = []
  warnings = []
  # Check style table alignment if provided
  if styles1 is not None and styles2 is not None:
    for key in ['fonts', 'fills', 'borders']:
      list1 = styles1.get(key, [])
      list2 = styles2.get(key, [])
      if len(list1) != len(list2):
        warnings.append(
          f"WARNING: Number of {key} definitions differ between files (A: {len(list1)}, B: {len(list2)}). Style table misalignment may cause false positives.")
      elif any(list1[i] != list2[i] for i in range(len(list1))):
        warnings.append(
          f"WARNING: {key} definitions differ in order or content between files. Style table misalignment may cause false positives.")
  summary = {
    'value': 0,
    'formula': 0,
    'style': 0,
    'style_trivial': 0,
    'style_significant': 0,
    'comment': 0,
    'validation': 0,
    'hyperlink': 0,
    'cells_compared': 0,
    'sheets_compared': 0,
  }
  style_subdiffs = {}
  trivial_type_counts = {}  # New: count trivial diffs by type
  sheets1 = set(wb1.keys())
  sheets2 = set(wb2.keys())
  only_in_a = sorted(sheets1 - sheets2)
  only_in_b = sorted(sheets2 - sheets1)
  in_both = sorted(sheets1 & sheets2)
  if only_in_a:
    output.append("[Sheets only in A]")
    for name in only_in_a:
      output.append(f"  {name}")
  if only_in_b:
    output.append("[Sheets only in B]")
    for name in only_in_b:
      output.append(f"  {name}")
  font_map1 = build_font_map(styles1)
  font_map2 = build_font_map(styles2)
  fills1 = [canonicalize_fill(f) for f in (styles1.get('fills', []) if styles1 else [])]
  fills2 = [canonicalize_fill(f) for f in (styles2.get('fills', []) if styles2 else [])]
  borders1 = [canonicalize_border(b) for b in (styles1.get('borders', []) if styles1 else [])]
  borders2 = [canonicalize_border(b) for b in (styles2.get('borders', []) if styles2 else [])]
  default_font_tuple = ('calibri', '11', None, None, None, None, None, None, None)  # Excel default
  default_fill_tuple = (None, None, None)
  default_border_tuple = ()
  for sheet in in_both:
    summary['sheets_compared'] += 1
    output.append(f"\n=== Sheet: {sheet} ===")
    cells1 = wb1[sheet]
    cells2 = wb2[sheet]
    all_addrs = sorted(set(cells1.keys()) | set(cells2.keys()), key=lambda x: (int(re.sub(r'[^0-9]', '', x) or 0), x))
    trivial_buffer = []
    last_trivial = None

    def flush_trivial_buffer():
      nonlocal trivial_buffer, last_trivial
      if not trivial_buffer:
        return
      addrs = [addr for addr, _ in trivial_buffer]
      msg = trivial_buffer[0][1]
      # Count by type for summary
      for line in msg.split('\n'):
        m = re.match(r'\s*([a-zA-Z0-9_.]+):', line)
        if m:
          key = m.group(1)
          trivial_type_counts[key] = trivial_type_counts.get(key, 0) + len(addrs)
      if not suppress_trivial_details:
        range_str = excel_range_from_addresses(addrs)
        output.append(f"  {range_str}: Style differs [trivial]\n{msg}")
      trivial_buffer.clear()
      last_trivial = None

    for addr in all_addrs:
      summary['cells_compared'] += 1
      c1 = cells1.get(addr, {})
      c2 = cells2.get(addr, {})
      # Value
      if c1.get('value', '') != c2.get('value', ''):
        flush_trivial_buffer()
        summary['value'] += 1
        output.append(
          f"  {addr}: Value differs [significant]\n    A: {c1.get('value', '')}\n    B: {c2.get('value', '')}")
      # Formula
      if c1.get('formula', '') != c2.get('formula', ''):
        flush_trivial_buffer()
        summary['formula'] += 1
        output.append(
          f"  {addr}: Formula differs [significant]\n    A: {c1.get('formula', '')}\n    B: {c2.get('formula', '')}")
      # Style (compare sub-features)
      s1 = c1.get('style', {}) if isinstance(c1.get('style', {}), dict) else {}
      s2 = c2.get('style', {}) if isinstance(c2.get('style', {}), dict) else {}
      xf1 = s1.get('xf', {}) if isinstance(s1.get('xf', {}), dict) else {}
      xf2 = s2.get('xf', {}) if isinstance(s2.get('xf', {}), dict) else {}
      font_tuple1 = default_font_tuple
      font_tuple2 = default_font_tuple
      font_idx1 = xf1.get('fontId')
      font_idx2 = xf2.get('fontId')
      try:
        if font_idx1 is not None and str(font_idx1).isdigit():
          font_tuple1 = font_map1.get(int(font_idx1), default_font_tuple)
      except Exception:
        pass
      try:
        if font_idx2 is not None and str(font_idx2).isdigit():
          font_tuple2 = font_map2.get(int(font_idx2), default_font_tuple)
      except Exception:
        pass
      # Compare font tuples for significance
      style_diff_significant = False
      subdiffs = []
      trivial_subdiffs = []
      if font_tuple1 != font_tuple2:
        subdiffs.append(f"    font: A={font_tuple1} | B={font_tuple2}")
        style_diff_significant = True
      # Compare fill tuples for significance
      fill_tuple1 = default_fill_tuple
      fill_tuple2 = default_fill_tuple
      fill_idx1 = xf1.get('fillId')
      fill_idx2 = xf2.get('fillId')
      try:
        if fill_idx1 is not None and str(fill_idx1).isdigit():
          fill_tuple1 = fills1[int(fill_idx1)] if int(fill_idx1) < len(fills1) else default_fill_tuple
      except Exception:
        pass
      try:
        if fill_idx2 is not None and str(fill_idx2).isdigit():
          fill_tuple2 = fills2[int(fill_idx2)] if int(fill_idx2) < len(fills2) else default_fill_tuple
      except Exception:
        pass
      if fill_tuple1 != fill_tuple2:
        subdiffs.append(f"    fill: A={fill_tuple1} | B={fill_tuple2}")
        style_diff_significant = True
      # Compare border tuples for significance
      border_tuple1 = default_border_tuple
      border_tuple2 = default_border_tuple
      border_idx1 = xf1.get('borderId')
      border_idx2 = xf2.get('borderId')
      try:
        if border_idx1 is not None and str(border_idx1).isdigit():
          border_tuple1 = borders1[int(border_idx1)] if int(border_idx1) < len(borders1) else default_border_tuple
      except Exception:
        pass
      try:
        if border_idx2 is not None and str(border_idx2).isdigit():
          border_tuple2 = borders2[int(border_idx2)] if int(border_idx2) < len(borders2) else default_border_tuple
      except Exception:
        pass
      if border_tuple1 != border_tuple2:
        subdiffs.append(f"    border: A={border_tuple1} | B={border_tuple2}")
        style_diff_significant = True

      if style_diff_significant and subdiffs:
        flush_trivial_buffer()
        summary['style'] += 1
        summary['style_significant'] += 1
        if verbosity in ('all', 'significant_only'):
          output.append(f"  {addr}: Style differs [significant]\n" + '\n'.join(subdiffs))
      elif style_diff_significant and not subdiffs:
        # Fallback: treat as trivial if no subdiffs found
        trivial_subdiffs.append("    (No sub-feature difference detected)")
        last_trivial = '\n'.join(trivial_subdiffs)
        trivial_buffer.append((addr, last_trivial))
        summary['style'] += 1
        summary['style_trivial'] += 1
      elif trivial_subdiffs:
        last_trivial = '\n'.join(trivial_subdiffs)
        trivial_buffer.append((addr, last_trivial))
        summary['style'] += 1
        summary['style_trivial'] += 1
      else:
        flush_trivial_buffer()
      # Comment
      if c1.get('comment', '') != c2.get('comment', ''):
        flush_trivial_buffer()
        summary['comment'] += 1
        output.append(
          f"  {addr}: Comment differs [significant]\n    A: {c1.get('comment', '')}\n    B: {c2.get('comment', '')}")
      # Data validation
      if c1.get('validation', '') != c2.get('validation', ''):
        flush_trivial_buffer()
        summary['validation'] += 1
        output.append(
          f"  {addr}: Data validation differs [significant]\n    A: {c1.get('validation', '')}\n    B: {c2.get('validation', '')}")
      # Hyperlink
      if c1.get('hyperlink', '') != c2.get('hyperlink', ''):
        flush_trivial_buffer()
        summary['hyperlink'] += 1
        output.append(
          f"  {addr}: Hyperlink differs [significant]\n    A: {c1.get('hyperlink', '')}\n    B: {c2.get('hyperlink', '')}")
    flush_trivial_buffer()
  # Add summary at the top
  summary_lines = [
    "\n=== SUMMARY ===",
    f"Sheets compared: {summary['sheets_compared']}",
    f"Cells compared: {summary['cells_compared']}",
    f"Value differences: {summary['value']}",
    f"Formula differences: {summary['formula']}",
    f"Style differences: {summary['style']} (significant: {summary['style_significant']}, trivial: {summary['style_trivial']})",
    f"  (by sub-feature): " + ', '.join(
      [f"{k}: {v}" for k, v in sorted(style_subdiffs.items())]) if style_subdiffs else "  (by sub-feature): None",
    f"  (trivial by type): " + ', '.join(
      [f"{k}: {v}" for k, v in
       sorted(trivial_type_counts.items())]) if trivial_type_counts else "  (trivial by type): None",
    f"Comment differences: {summary['comment']}",
    f"Data validation differences: {summary['validation']}",
    f"Hyperlink differences: {summary['hyperlink']}",
    "================\n"
  ]
  return summary_lines + output


def compute_sha256(path: Path) -> str:
  with open(path, "rb") as f:
    return hashlib.sha256(f.read()).hexdigest()


def compare_xlsx_files(file_a: Path, file_b: Path, log_to_file: bool = True) -> List[str]:
  output = [f"Comparing:\n  A: {file_a.name}\n  B: {file_b.name}\n"]
  hash_a = compute_sha256(file_a)
  hash_b = compute_sha256(file_b)
  output.append("SHA-256 Hashes:")
  output.append(f"  A: {hash_a}")
  output.append(f"  B: {hash_b}")
  if hash_a == hash_b:
    output.append("\u2714 Files are identical at the binary level.\n")
    return output
  output.append("\u2192 Hashes differ; comparing content...\n")
  with zipfile.ZipFile(file_a, 'r') as za, zipfile.ZipFile(file_b, 'r') as zb:
    wb1 = parse_workbook(za)
    wb2 = parse_workbook(zb)
    output.extend(compare_workbooks(wb1, wb2))
  if log_to_file:
    now = datetime.now()
    out_path = Path(f"comparison_cellwise_at_{now.strftime('%Y%m%d_%H%M%S')}.txt")
    print(f"Creating comparison file: {out_path}")
    with open(out_path, "w", encoding="utf-8") as f:
      for line in output:
        f.write(line + "\n")
  return output


if __name__ == "__main__":
  # Example usage: update these paths as needed
  file_a = Path(
    r"D:/local/cursor/feedback_portal/diagnostics/dairy_digester_operator_feedback_v006_for_review_local.xlsx")
  file_b = Path(
    r"D:/local/cursor/feedback_portal/diagnostics/dairy_digester_operator_feedback_v006_for_review_sharepoint.xlsx")
  compare_xlsx_files(file_a, file_b, log_to_file=True)

# Notes:
# - This script parses and compares cell values, formulas, formatting, comments, data validation, and hyperlinks for each cell.
# - It mimics the structure of excel_compare.py, but works directly at the XML level for full fidelity.
# - Sheet and workbook-level metadata comparison can be added similarly by parsing the relevant XML files.
# - Extend parse_styles and parse_sheet to handle more formatting, protection, and advanced features as needed.
