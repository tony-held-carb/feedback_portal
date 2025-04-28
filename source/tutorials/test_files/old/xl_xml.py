import os
import shutil
import xml.etree.ElementTree as ET
import zipfile

# Paths for the input and output files
# input_file = "og_operator_feedback_with_formatting_v11_in.xlsx"
# output_file = "og_operator_feedback_with_formatting_v11_out.xlsx"

input_file = "test_input.xlsx"
output_file = "test_output.xlsx"

# Step 1: Extract the Excel file (as a zip archive)
with zipfile.ZipFile(input_file, 'r') as zip_ref:
  extracted_dir = "extracted_excel"
  zip_ref.extractall(extracted_dir)

# Step 2: Locate and modify the XML for the desired sheet (e.g., sheet1.xml)
sheet_path = os.path.join(extracted_dir, "xl", "worksheets", "sheet1.xml")
tree = ET.parse(sheet_path)
root = tree.getroot()

# Namespaces used in Excel XML files
namespaces = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

# Find and modify the cell value (e.g., cell A1)
for cell in root.findall(".//ns:c[@r='A1']", namespaces):
  value = cell.find("ns:v", namespaces)
  # if value is not None:
  #     value.text = "New Value"  # Update the cell value
  #     print(f"Modified cell A1 to: {value.text}")

# Save the modified XML
tree.write(sheet_path)

# Step 3: Repackage the files into a new .xlsx file
shutil.make_archive("temp_excel", 'zip', extracted_dir)
shutil.move("temp_excel.zip", output_file)

# Cleanup temporary files
shutil.rmtree(extracted_dir)

print(f"Modified Excel file saved as {output_file}")
