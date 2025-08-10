Thoughts on refactoring xl_dict and related files.

- Key Files
  - arb.utils.excel.xl_parse.parse_xl_file()
    - Purpose: Core Excel parsing engine that converts Excel files to Python dictionaries using schema mapping and field extraction
    - Calls: extract_tabs()
  - arb.utils.excel.xl_parse.extract_tabs()
    - Purpose: Extract data from the data tabs that are enumerated in the schema tab.

- Analysis
  - parse_xl_file & extract_tabs are a little ugly and rely on a schema map dict that is a little ugy too but a lower priorty
  -

