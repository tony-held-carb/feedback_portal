import datetime

import xlwings as xw


def modify_file(file_input, file_output, change_dicts):
  # Start a new workbook
  print(f"{change_dicts=}")
  with xw.App(visible=False) as app:  # Run Excel in the background
    wb = xw.Book(file_input)  # Open the file
    sheet_names = [sheet.name for sheet in wb.sheets]

    try:
      for change_dict in change_dicts:
        print(f"{change_dict=}")
        sheet_name = change_dict['sheet_name']

        if sheet_name not in sheet_names:
          print(f"Attempting to add {sheet_name=} to {wb.sheets=}")
          # Create a new sheet
          new_sheet = wb.sheets.add()
          new_sheet.name = sheet_name

        # Access the sheet
        sheet = wb.sheets[sheet_name]

        address_values = change_dict['cell_values'].items()
        print(f"{address_values=}")

        for address, value in address_values:
          print(f"{address=}, {value=}")
          sheet[address].value = value

        # Save the workbook as a new file
      wb.save(file_output)
      print(f"File saved as {file_output}")
    finally:
      # Close the workbook
      wb.close()


if __name__ == '__main__':
  file_input = "landfill_operator_feedback_with_formatting_v15.xlsx"  # Replace with the path to your file
  file_output = "test_output.xlsx"  # Path to save the modified file

  change_dicts = [
    {
      'sheet_name': 'my_sheet',
      'cell_values': {
        'C10': "Look at me, i'm C10",
        'D11': "Look at me, i'm D11",
      },
    },
    {
      'sheet_name': '_json_schema',
      'cell_values': {
        'B20': "Look at me, i'm B20",
        'B21': datetime.datetime.now(),
      },
    },
    {
      'sheet_name': 'Feedback Form',
      'cell_values': {
        'B26': "Modified location description",
        'C27': "I'm supposed to be invalid input",
        'B47': "Modified monitoring description",
      },
    },

  ]

  modify_file(file_input, file_output, change_dicts)

# todo - looks like you should make a copy first to avoid writing to the original ...
