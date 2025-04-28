import os
import xml.etree.ElementTree as ET
import zipfile

# Build the XML
root = ET.Element("worksheet", xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main")
sheet_data = ET.SubElement(root, "sheetData")
row = ET.SubElement(sheet_data, "row", r="1")
cell = ET.SubElement(row, "c", r="A1", t="inlineStr")
value = ET.SubElement(cell, "is")
ET.SubElement(value, "t").text = "Hello, World!"

# Save the XML to a file
tree = ET.ElementTree(root)
os.makedirs("xl/worksheets", exist_ok=True)
tree.write("xl/worksheets/sheet1.xml", encoding="utf-8", xml_declaration=True)

# Create the .xlsx archive
with zipfile.ZipFile("output.xlsx", "w") as z:
  z.write("xl/worksheets/sheet1.xml", arcname="xl/worksheets/sheet1.xml")
