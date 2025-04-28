import os
import shutil
import xml.etree.ElementTree as ET
import zipfile


def modify_excel_cell(input_file, output_file, sheet_name, cell_reference, new_value):
  # Extract the Excel file contents
  with zipfile.ZipFile(input_file, 'r') as z:
    temp_dir = './temp_excel'
    z.extractall(temp_dir)

  # Path to the sheet XML file
  sheet_file = f'{temp_dir}/xl/worksheets/{sheet_name}.xml'
  if not os.path.exists(sheet_file):
    raise FileNotFoundError(f"Sheet '{sheet_name}' not found in the Excel file.")

  # Parse the sheet XML
  tree = ET.parse(sheet_file)
  root = tree.getroot()

  # Define namespaces
  ns = {'': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
  ET.register_namespace('', ns[''])

  # Find the cell
  cell = root.find(f".//c[@r='{cell_reference}']", ns)
  print(f"{cell=}")
  if cell is None:
    raise ValueError(f"Cell '{cell_reference}' not found in sheet '{sheet_name}'.")

  # Update the cell value
  value_element = cell.find('v', ns)
  print(f"{value_element=}")
  print(f"{dir(value_element)=}")
  if value_element is not None:
    print(f"Original value of {cell_reference}: {value_element.text}")
    value_element.text = new_value
  else:
    print(f"Original value of {cell_reference}: None (empty cell)")
    ET.SubElement(cell, 'v').text = new_value

  # Write the modified XML back to the sheet file
  tree.write(sheet_file)

  # Recreate the Excel file with the updated XML
  with zipfile.ZipFile(output_file, 'w') as z:
    for root, _, files in os.walk(temp_dir):
      for file in files:
        file_path = os.path.join(root, file)
        arcname = os.path.relpath(file_path, temp_dir)
        z.write(file_path, arcname)

  # Cleanup the temporary directory
  shutil.rmtree(temp_dir)


# Example usage
input_excel = 'test_input.xlsx'
output_excel = 'test_output.xlsx'
sheet_name = 'sheet1'  # Replace with your sheet name
cell_to_modify = 'B2'
new_value = '42'

modify_excel_cell(input_excel, output_excel, sheet_name, cell_to_modify, new_value)
