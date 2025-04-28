import glob
import os
import xml.etree.ElementTree as ET

from xlsx2csv import Xlsx2csv
from xlsxwriter import Workbook


def extract_xlsx_to_xml(workbook_path, output_dir):
  # Ensure output directory exists
  os.makedirs(output_dir, exist_ok=True)

  # Use Xlsx2csv to parse the workbook
  csv_converter = Xlsx2csv(workbook_path, outputencoding="utf-8")
  sheets = csv_converter.workbook.sheets

  for sheet_index, sheet in enumerate(sheets):
    sheet_name = sheet["name"]

    # Create XML root for the worksheet
    root = ET.Element("worksheet")
    root.set("name", sheet_name)

    # Process rows for this sheet
    csv_converter.convert(os.path.join(output_dir, "temp.csv"), sheetid=sheet_index + 1)
    with open(os.path.join(output_dir, "temp.csv"), "r", encoding="utf-8") as f:
      for row_index, line in enumerate(f):
        row = ET.SubElement(root, "row", index=str(row_index))
        for col_index, cell in enumerate(line.strip().split(",")):
          cell_elem = ET.SubElement(row, "cell", index=str(col_index))
          cell_elem.text = cell.strip()

    # Save XML file
    tree = ET.ElementTree(root)
    xml_file_path = os.path.join(output_dir, f"{sheet_name}.xml")
    tree.write(xml_file_path, encoding="utf-8", xml_declaration=True)
    print(f"Saved: {xml_file_path}")

  # Cleanup temp file
  os.remove(os.path.join(output_dir, "temp.csv"))


def recreate_xlsx_from_xml(xml_dir, output_workbook):
  # Create a new workbook
  workbook = Workbook(output_workbook)

  # List all XML files in the directory
  xml_files = glob.glob(os.path.join(xml_dir, "*.xml"))

  for xml_file in xml_files:
    # Parse XML
    tree = ET.parse(xml_file)
    root = tree.getroot()
    sheet_name = root.get("name")

    # Add a worksheet
    worksheet = workbook.add_worksheet(sheet_name[:31])  # Sheet names must be <= 31 chars

    # Process rows and cells
    for row_elem in root.findall("row"):
      row_index = int(row_elem.get("index"))
      for cell_elem in row_elem.findall("cell"):
        col_index = int(cell_elem.get("index"))
        value = cell_elem.text
        worksheet.write(row_index, col_index, value)

  workbook.close()
  print(f"Workbook saved as: {output_workbook}")


if __name__ == "__main__":
  # Example Usage
  # extract_xlsx_to_xml("test_input.xlsx", "xml_output")
  extract_xlsx_to_xml("og_operator_feedback_with_formatting_v11_in.xlsx", "xml_output")
  recreate_xlsx_from_xml("xml_output", "test_output.xlsx")
