import xlwings as xw


def modify_file(file_input, file_output):
  # Start a new workbook
  with xw.App(visible=False) as app:  # Run Excel in the background
    wb = xw.Book(file_input)  # Open the file
    try:
      # Access the sheet
      sheet = wb.sheets['my_sheet']  # Replace 'my_sheet' with your sheet name

      # Modify cells
      sheet['C10'].value = "Look at me, i'm C10"
      sheet['D11'].value = "Look at me, i'm D11"

      # Save the workbook as a new file
      wb.save(file_output)
      print(f"File saved as {file_output}")
    finally:
      # Close the workbook
      wb.close()


if __name__ == '__main__':
  # Open the existing Excel file
  # file_input = "test_input.xlsx"  # Replace with the path to your file
  # file_input = "og_operator_feedback_with_formatting_v11_in.xlsx"  # Replace with the path to your file
  file_input = "landfill_operator_feedback_with_formatting_v15.xlsx"  # Replace with the path to your file

  file_output = "test_output.xlsx"  # Path to save the modified file

  modify_file(file_input, file_output)
