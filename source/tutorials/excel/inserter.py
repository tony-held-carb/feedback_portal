import zipfile

import jinja2

fillFields = {
  'facilityName': 'Hacks Inc.',
  'contactName': 'Robert Tables',
  'contactPhone': '(555) 123-1337',
  'contactEmail': 'bobby.tables@dropdb.com',
  'incidenceId': '123',
  'plumeId': '456',
  'coordinates': '-123.45678,39.12345',
  # 'dateObserved': '2025-02-29 12:34',
  'dateObserved': 'Pizza',
  'drop_down_01': "I'm drop down 01!",
}

xlsx = zipfile.ZipFile('landfill_template.xlsx', 'r')
new_xlsx = zipfile.ZipFile(f"landfill_template_{fillFields['incidenceId']}.xlsx", 'w')

for filename in xlsx.namelist():
  contents = xlsx.open(filename).read()
  if filename == 'xl/sharedStrings.xml':  # Seems to be the only file that needs string replacement, so I don't run it on the others
    contents = jinja2.Template(contents.decode('utf-8')).render(fillFields)
  new_xlsx.writestr(filename, contents)

xlsx.close()
new_xlsx.close()
