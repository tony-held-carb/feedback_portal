import os
import shutil
import zipfile

# Define file paths
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
# Assume "tab_1" corresponds to "sheet1.xml"
sheet_path = os.path.join(temp_dir, "xl", "worksheets", "sheet1.xml")

# Read the sheet XML content
with open(sheet_path, 'r', encoding='utf-8') as file:
  sheet_data = file.read()

# Modify the value of cell C3 from D6 to D7
# Look for the cell tag corresponding to C3, e.g., <c r="C3"><v>D6</v></c>
print(f"\n{sheet_data}")
sheet_data = sheet_data.replace('<c r="C3"><v>D6</v></c>', '<c r="C3"><v>D7</v></c>')
print(f"\n{sheet_data}")

# Write the updated sheet XML content back
with open(sheet_path, 'w', encoding='utf-8') as file:
  file.write(sheet_data)

# Step 3: Recreate the ZIP file as a new Excel file
with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
  for folder_name, subfolders, filenames in os.walk(temp_dir):
    for filename in filenames:
      file_path = os.path.join(folder_name, filename)
      arcname = os.path.relpath(file_path, temp_dir)
      zip_ref.write(file_path, arcname)

# Clean up the temporary directory
shutil.rmtree(temp_dir)

print(f"Modified Excel file saved as {output_file}")
