import glob
import os
import xml.etree.ElementTree as ET

import xlrd
from xlsxwriter import Workbook


def excel_to_xml_no_openpyxl(workbook_path, output_dir):
  # Open the workbook
  workbook = xlrd.open_workbook(workbook_path)

  # Ensure output directory exists
  os.makedirs(output_dir, exist_ok=True)

  for sheet in workbook.sheets():
    # Create an XML root element for the sheet
    root = ET.Element("worksheet")
    root.set("name", sheet.name)

    for row_idx in range(sheet.nrows):
      row_element = ET.SubElement(root, "row", index=str(row_idx))
      for col_idx, cell in enumerate(sheet.row(row_idx)):
        cell_element = ET.SubElement(row_element, "cell", index=str(col_idx))
        cell_element.text = str(cell.value)

    # Write the XML to a file
    tree = ET.ElementTree(root)
    xml_file_path = os.path.join(output_dir, f"{sheet.name}.xml")
    tree.write(xml_file_path, encoding="utf-8", xml_declaration=True)
    print(f"Saved: {xml_file_path}")


def xml_to_excel_no_openpyxl(xml_dir, output_file):
  # Create a new workbook
  workbook = Workbook(output_file)

  # Get all XML files from the directory
  xml_files = glob.glob(os.path.join(xml_dir, "*.xml"))

  for xml_file in xml_files:
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()
    sheet_name = root.attrib["name"]

    # Add a worksheet
    worksheet = workbook.add_worksheet(sheet_name)

    for row_element in root.findall("row"):
      row_index = int(row_element.attrib["index"])
      for cell_element in row_element.findall("cell"):
        col_index = int(cell_element.attrib["index"])
        value = cell_element.text
        worksheet.write(row_index, col_index, value)

  workbook.close()
  print(f"Workbook saved as: {output_file}")


if __name__ == '__main__':
  # Example Usage
  excel_to_xml_no_openpyxl("test_input.xlsx", "xml_output")
  # Example Usage
  xml_to_excel_no_openpyxl("xml_output", "test_output.xlsx")
