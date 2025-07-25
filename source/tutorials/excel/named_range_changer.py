# Based on https://chatgpt.com/share/6754be1a-cd50-800b-9373-3d4c95fa41a6

import os
import shutil
import zipfile

# Paths for the input and output Excel files
input_file = "worksheet_1.xlsx"
output_file = "worksheet_2.xlsx"

# Create a temporary directory to extract the files
temp_dir = "temp_excel"
if os.path.exists(temp_dir):
  shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

# Step 1: Extract the Excel file
with zipfile.ZipFile(input_file, 'r') as zip_ref:
  zip_ref.extractall(temp_dir)

# Step 2: Modify the `sheet1.xml` file to change the value of C3
sheet_path = os.path.join(temp_dir, "xl", "worksheets", "sheet1.xml")
with open(sheet_path, 'r', encoding='utf-8') as file:
  sheet_data = file.read()

# Update the value in cell C3 from D6 to D7
sheet_data = sheet_data.replace('<c r="C3"><v>D6</v></c>', '<c r="C3"><v>D7</v></c>')

# Save the modified XML back
with open(sheet_path, 'w', encoding='utf-8') as file:
  file.write(sheet_data)

# Step 3: Recreate the .xlsx file
with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
  for folder_name, subfolders, filenames in os.walk(temp_dir):
    for filename in filenames:
      file_path = os.path.join(folder_name, filename)
      arcname = os.path.relpath(file_path, temp_dir)
      zip_ref.write(file_path, arcname)

# Clean up temporary files
shutil.rmtree(temp_dir)

print(f"Modified Excel file saved as {output_file}")
