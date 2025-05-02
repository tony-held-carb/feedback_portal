"""
The following are code that are no longer used, perhaps they are too outdated.
Rather than deleting, the code is moved here in case it becomes relevant again at some point.
"""


def create_html_select(table_name, table_as_list, key_field, display_field):
  """
  Given a list of dictionaries, where each dictionary represents a row of table_name, create
  a list of tuples suitable for an HTML selector where the element value is the key_field and the displayed
  value is the associated display_field.


  Args:
    table_name (str): lower-case sql table name
    table_as_list (list[dict]): list of dictionaries where each dictionary has the column name as the key and the value as the value
    key_field (str): name of the dictionary key that represents the select element's value
    display_field (str): name of the dictionary key that represents the select element's display

  Returns:
    tuple: A tuple containing the drop-down menu items and a reverse dictionary lookup.
      - drop_downs (list[tuple]): lookup dictionary of drop down key values for each table.
      - drop_downs_rev (dict): reverse lookup dictionary of drop down key values for each table
  """
  drop_downs = {}
  drop_downs_rev = {}
  entries = [(-1, 'Please Select', {'disabled': True})]
  entries_rev = {}
  for row in table_as_list:
    value = row[key_field]
    display = row[display_field]
    entries.append((value, display))
    entries_rev[display] = value

  drop_downs[table_name] = entries
  drop_downs_rev[table_name] = entries_rev

  return drop_downs, drop_downs_rev


def update_contingent_selectors(self):
  """
  Update the selector choices if they are contingent on other form values.
  """

  logger.debug(f"in update_contingent_selectors()")

  # emission_cause is contingent on emission_location
  # use the emission_cause_contingent_on_emission_location key to find the possible choices
  # for the emission_location based on the emission_cause
  emission_location = self.emission_location.data
  logger.debug(f"{emission_location=}")
  emission_cause_dict = Globals.drop_downs_contingent["emission_cause_contingent_on_emission_location"]
  logger.debug(f"{emission_cause_dict=}")
  choices = emission_cause_dict.get(emission_location, None)
  logger.debug(f"{choices=}")

  if choices is not None:
    # Primary cause
    header_1 = [
      ("Please Select", "Please Select", {"disabled": True}),
      ("Not applicable as no leak was detected", "Not applicable as no leak was detected", {}),
    ]
    footer_1 = [(c, c, {}) for c in choices]
    choices_1 = header_1 + footer_1
    logger.debug(f"{choices_1=}")

    self.emission_cause.choices = choices_1
    if self.emission_cause.data not in choices_1:
      logger.debug(f"{self.emission_cause.data=} not in {choices_1=}")
      self.emission_cause.data = "Please Select"

    # Secondary and tertiary causes
    header_2 = [
      ("Please Select", "Please Select", {"disabled": True}),
      ("Not applicable as no leak was detected", "Not applicable as no leak was detected", {}),
      ("Not applicable as no additional leak cause suspected", "Not applicable as no additional leak cause suspected", {}),
    ]
    footer_2 = [(c, c, {}) for c in choices]
    choices_2 = header_2 + footer_2
    choices_2 = header_2 + footer_2
    logger.debug(f"{choices_2=}")

    self.emission_cause_secondary.choices = choices_2
    if self.emission_cause_secondary.data not in choices_2:
      logger.debug(f"{self.emission_cause_secondary.data=} not in {choices_2=}")
      self.emission_cause_secondary.data = "Please Select"

    self.emission_cause_tertiary.choices = choices_2
    if self.emission_cause_tertiary.data not in choices_2:
      logger.debug(f"{self.emission_cause_tertiary.data=} not in {choices_2=}")
      self.emission_cause_tertiary.data = "Please Select"
