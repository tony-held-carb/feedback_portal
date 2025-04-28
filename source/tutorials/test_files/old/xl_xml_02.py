import os
import shutil
import xml.etree.ElementTree as ET
import zipfile


def modify_excel_cell(input_file, output_file, sheet_name, cell_ref, new_value):
  # Step 1: Extract the .xlsx file
  temp_dir = "temp_extracted"
  with zipfile.ZipFile(input_file, 'r') as zip_ref:
    zip_ref.extractall(temp_dir)

  # Step 2: Locate the sheet's XML
  workbook_path = os.path.join(temp_dir, "xl", "workbook.xml")
  sheets_path = os.path.join(temp_dir, "xl", "worksheets")
  sheet_id = None

  # Parse workbook.xml to find the sheet name
  workbook_tree = ET.parse(workbook_path)
  workbook_root = workbook_tree.getroot()
  namespaces = {"ns": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

  for sheet in workbook_root.findall("ns:sheets/ns:sheet", namespaces):
    if sheet.get("name") == sheet_name:
      sheet_id = sheet.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
      break

  if not sheet_id:
    shutil.rmtree(temp_dir)
    raise ValueError(f"Sheet '{sheet_name}' not found in workbook.")

  # Find the corresponding worksheet XML file
  sheet_file = os.path.join(sheets_path, f"sheet{sheet_id[-1]}.xml")

  # Step 3: Modify the cell value
  tree = ET.parse(sheet_file)
  root = tree.getroot()

  for cell in root.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c"):
    if cell.get("r") == cell_ref:
      # Update the cell value
      value = cell.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")
      print(f"{value=}")
      if value is None:
        value = ET.SubElement(cell, "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")
      value.text = str(new_value)
      break

  # Write back the modified sheet
  tree.write(sheet_file)

  # Step 4: Repackage the files into a new .xlsx
  with zipfile.ZipFile(output_file, 'w') as zip_ref:
    for foldername, subfolders, filenames in os.walk(temp_dir):
      for filename in filenames:
        file_path = os.path.join(foldername, filename)
        arcname = os.path.relpath(file_path, temp_dir)
        zip_ref.write(file_path, arcname)

  # Clean up the temporary directory
  shutil.rmtree(temp_dir)


# Example usage:
modify_excel_cell(
  input_file="test_input.xlsx",
  output_file="test_output.xlsx",
  sheet_name="my_sheet",
  cell_ref="A1",
  new_value="Modified Value"
)
