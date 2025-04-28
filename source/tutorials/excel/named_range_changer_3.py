import os
import shutil
import zipfile

# Define paths for the input and output Excel files
input_file = "worksheet_1.xlsx"
output_file = "worksheet_2.xlsx"
temp_dir = "temp_excel"

# Ensure a clean temporary directory
if os.path.exists(temp_dir):
  shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

# Step 1: Extract the Excel file contents
with zipfile.ZipFile(input_file, 'r') as zip_ref:
  zip_ref.extractall(temp_dir)

# Step 2: Locate and modify the worksheet XML for "tab_1"
# Assuming "tab_1" corresponds to "sheet1.xml"
sheet_path = os.path.join(temp_dir, "xl", "worksheets", "sheet1.xml")

# Read the XML content of the sheet
with open(sheet_path, 'r', encoding='utf-8') as file:
  sheet_data = file.read()

# Modify the value in cell C3
# Assume the cell has a structure like: <c r="C3"><v>Option_2</v></c>
sheet_data = sheet_data.replace('<c r="C3"><v>Drop_Down_Value_D6</v></c>', '<c r="C3"><v>Option_3</v></c>')

# Write the updated XML content back to the file
with open(sheet_path, 'w', encoding='utf-8') as file:
  file.write(sheet_data)

# Step 3: Recreate the Excel file with the modified content
with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
  for folder_name, subfolders, filenames in os.walk(temp_dir):
    for filename in filenames:
      file_path = os.path.join(folder_name, filename)
      arcname = os.path.relpath(file_path, temp_dir)
      zip_ref.write(file_path, arcname)

# Clean up the temporary directory
shutil.rmtree(temp_dir)

print(f"Modified Excel file saved as {output_file}")
