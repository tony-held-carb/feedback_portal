"""
Hardcoded testing data and dropdown lookup values for the ARB Methane Feedback Portal.

This module provides:
  - Dummy incidence records for Oil & Gas and Landfill sectors
  - Lookup values for HTML dropdowns (independent and contingent)
  - Shared test values for local debugging or spreadsheet seeding

Args:
  None

Returns:
  None

Attributes:
  logger (logging.Logger): Logger instance for this module.
  OIL_AND_GAS_SECTORS (list[str]): Oil & Gas sector names for dropdowns.
  LANDFILL_SECTORS (list[str]): Landfill sector names for dropdowns.
  _drop_downs (dict): Canonical dropdown data for forms. Do not mutate at runtime.
  _drop_downs_contingent (dict): Canonical contingent dropdown data for forms. Do not mutate at runtime.

Examples:
  from arb.portal.db_hardcoded import get_og_dummy_form_data
  data = get_og_dummy_form_data()
  print(data["sector"])
  # Output: 'Oil & Gas'

Notes:
  - Intended for use during development and offline diagnostics.
  - Not suitable for production database seeding.
  - The logger emits a debug message when this file is loaded.
  - The dropdown transformation logic in get_excel_dropdown_data is imported from arb.utils.web_html.update_selector_dict to ensure consistency with the canonical implementation.
"""

import copy
import datetime
import logging
from pathlib import Path

# from arb.utils.web_html import update_selector_dict
# from arb.utils.date_and_time import utc_datetime_to_iso_str

logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')

# Sector classification constants
OIL_AND_GAS_SECTORS = [
  "Industrial - Other",
  "Industrial: Other",
  "Industrial: Oil & Gas",
  "Industrial: Power Generation",
  "Oil and Gas",
  "Oil & Gas",
]

LANDFILL_SECTORS = [
  "Agriculture: Dairy (Enteric Fermentation or Manure Management)",
  "Agriculture: Dairy Digester",
  "Agriculture: Other",
  "Anaerobic Digester",
  "Compost",
  "Landfill",
  "Landfills",
  "Livestock",
  "Recycling & Waste: Compost",
  "Recycling & Waste: Anaerobic Digester",
  "Recycling & Waste: Landfills",
  "Recycling & Waste: Other",
]

# _drop_downs: Human-readable canonical dropdown data. Do not alter at runtime.
_drop_downs = {
  "venting_exclusion": [
    "Yes",
    "No",
  ],
  "ogi_performed": [
    "Yes",
    "No",
  ],
  "ogi_result": [
    "Not applicable as OGI was not performed",
    "No source found",
    "Unintentional-leak",
    "Unintentional-non-component",
    "Venting-construction/maintenance",
    "Venting-routine",
  ],
  "method21_performed": [
    "Yes",
    "No",
  ],
  "method21_result": [
    "Not applicable as Method 21 was not performed",
    "No source found",
    "Unintentional-below leak threshold",
    "Unintentional-leak",
    "Unintentional-non-component",
    "Venting-construction/maintenance",
    "Venting-routine",
  ],
  "equipment_at_source": [
    "Centrifugal Natural Gas Compressor",
    "Continuous High Bleed Natural Gas-actuated Pneumatic Device",
    "Continuous Low Bleed Natural Gas-actuated Pneumatic Device",
    "Intermittent Bleed Natural Gas-actuated Pneumatic Device",
    "Natural Gas-actuated Pneumatic Pump",
    "Pressure Separator",
    "Reciprocating Natural Gas Compressor",
    "Separator",
    "Tank",
    "Open Well Casing Vent",
    "Piping",
    "Well",
    "Other",
  ],
  "component_at_source": [
    "Valve",
    "Connector",
    "Flange",
    "Fitting - pressure meter/gauge",
    "Fitting - not pressure meter/gauge",
    "Open-ended line",
    "Plug",
    "Pressure relief device",
    "Stuffing box",
    "Other",
  ],

  # Landfill
  "emission_identified_flag_fk": [
    "Operator was aware of the leak prior to receiving the CARB plume notification",
    "Operator detected a leak during follow-up monitoring after receipt of the CARB plume notification",
    "No leak was detected",
  ],
  "emission_type_fk": [
    "Not applicable as no leak was detected",
    "Operator was aware of the leak prior to receiving the notification, and/or repairs were in progress on the date of the plume observation",
    "An unintentional leak  (i.e., the operator was not aware of, and could be repaired if discovered)",
    "An intentional or allowable vent (i.e., the operator was aware of, and/or would not repair)",
    "Due to a temporary activity (i.e., would be resolved without corrective action when the activity is complete)",
  ],
  "emission_location": [
    "Not applicable as no leak was detected",
    "Gas Collection System Component (e.g., blower, well, valve, port)",
    "Gas Control Device/Control System Component",
    "Landfill Surface: Daily Cover",
    "Landfill Surface: Final Cover",
    "Landfill Surface: Intermediate Cover",
    "Leachate Management System",
    "Working Face (area where active filling was being conducted at the time of detection)",
  ],
  "emission_cause": [
    "Not applicable as no leak was detected",
    "Collection system downtime",
    "Construction - New Well Installation",
    "Construction - Well Raising or Horizontal Extension",
    "Cover integrity",
    "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
    "Cracked/Broken Seal",
    "Damaged component",
    "Insufficient vacuum",
    "Offline Gas Collection Well(s)",
    "Other",
    "Uncontrolled Area (no gas collection infrastructure)",
  ],
  "emission_cause_secondary": [
    "Not applicable as no leak was detected",
    "Not applicable as no additional leak cause suspected",
    "Collection system downtime",
    "Construction - New Well Installation",
    "Construction - Well Raising or Horizontal Extension",
    "Cover integrity",
    "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
    "Cracked/Broken Seal",
    "Damaged component",
    "Insufficient vacuum",
    "Offline Gas Collection Well(s)",
    "Other",
    "Uncontrolled Area (no gas collection infrastructure)",
  ],
  "emission_cause_tertiary": [
    "Not applicable as no leak was detected",
    "Not applicable as no additional leak cause suspected",
    "Collection system downtime",
    "Construction - New Well Installation",
    "Construction - Well Raising or Horizontal Extension",
    "Cover integrity",
    "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
    "Cracked/Broken Seal",
    "Damaged component",
    "Insufficient vacuum",
    "Offline Gas Collection Well(s)",
    "Other",
    "Uncontrolled Area (no gas collection infrastructure)",
  ],

  "included_in_last_lmr": [
    "Yes",
    "No",
  ],
  "planned_for_next_lmr": [
    "Yes",
    "No",
  ],
}

# _drop_downs_contingent: Human-readable canonical contingent dropdown data. Do not alter at runtime.
# keys to the contingent dropdowns follow the patter html_selector2_contingent_on_html_selector1
# for instance, emission_cause_contingent_on_emission_location means that the choices for
# emission_cause are based on a lookup of the emission_location

_drop_downs_contingent = {
  "emission_cause_contingent_on_emission_location": {
    "Gas Collection System Component (e.g., blower, well, valve, port)": [
      "Construction - New Well Installation",
      "Construction - Well Raising or Horizontal Extension",
      "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
      "Damaged component",
      "Insufficient vacuum",
      "Offline Gas Collection Well(s)",
      "Other",
    ],
    "Gas Control Device/Control System Component": [
      "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
      "Damaged component",
      "Other",
    ],
    "Landfill Surface: Daily Cover": [
      "Collection system downtime",
      "Construction - New Well Installation",
      "Construction - Well Raising or Horizontal Extension",
      "Cover integrity",
      "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
      "Cracked/Broken Seal",
      "Damaged component",
      "Insufficient vacuum",
      "Offline Gas Collection Well(s)",
      "Other",
      "Uncontrolled Area (no gas collection infrastructure)",
    ],
    "Landfill Surface: Intermediate Cover": [
      "Collection system downtime",
      "Construction - New Well Installation",
      "Cover integrity",
      "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
      "Cracked/Broken Seal",
      "Damaged component",
      "Insufficient vacuum",
      "Offline Gas Collection Well(s)",
      "Other",
      "Uncontrolled Area (no gas collection infrastructure)",
    ],
    "Landfill Surface: Final Cover": [
      "Collection system downtime",
      "Construction - New Well Installation",
      "Construction - Well Raising or Horizontal Extension",
      "Cover integrity",
      "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
      "Cracked/Broken Seal",
      "Damaged component",
      "Insufficient vacuum",
      "Offline Gas Collection Well(s)",
      "Other",
      "Uncontrolled Area (no gas collection infrastructure)",
    ],
    "Leachate Management System": [
      "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
      "Damaged component",
      "Offline Gas Collection Well(s)",
      "Other",
    ],
    "Working Face (area where active filling was being conducted at the time of detection)": [
      "Construction - New Well Installation",
      "Construction - Well Raising or Horizontal Extension",
      "Cover-related Construction (Excavation/ Exposed Operations/ Re-grading)",
      "Offline Gas Collection Well(s)",
      "Other",
      "Uncontrolled Area (no gas collection infrastructure)",
    ],
  },
}


def get_og_dummy_form_data() -> dict:
  """
  Generate dummy Oil & Gas form data as a dictionary.

  Args:
    None

  Returns:
    dict: Pre-filled key/value pairs simulating user input from the HTML form.

  Examples:
    data = get_og_dummy_form_data()
    print(data["sector"])
    # Output: 'Oil & Gas'

  Notes:
    - Datetime fields are naive (California local), matching what a user would submit.
    - This data is NOT contract-compliant for direct DB storage; it must be converted to UTC-aware ISO 8601 strings before being saved to the database.
  """

  json_data = {
    "id_incidence": 1002050,
    "id_plume": 1001,
    "observation_timestamp": datetime.datetime.now().replace(second=0, microsecond=0),
    "lat_carb": 100.05,
    "long_carb": 100.06,
    "id_message": "id_message response",
    "facility_name": "facility_name response",
    "id_arb_eggrt": "1001",
    "contact_name": "contact_name response",
    "contact_phone": f"(555) 555-5555",
    "contact_email": "my_email@email.com",
    # "venting_exclusion": PLEASE_SELECT,
    "venting_description_1": "venting_description_1 response",
    # "ogi_performed": PLEASE_SELECT,
    "ogi_date": datetime.datetime.now().replace(second=0, microsecond=0),
    # "ogi_result": PLEASE_SELECT,
    # "method21_performed": PLEASE_SELECT,
    "method21_date": datetime.datetime.now().replace(second=0, microsecond=0),
    # "method21_result": PLEASE_SELECT,
    "initial_leak_concentration": 1004,
    "venting_description_2": "venting_description_2 response",
    "initial_mitigation_plan": "initial_mitigation_plan response",
    # "equipment_at_source": PLEASE_SELECT,
    "equipment_other_description": "equipment_other_description response",
    # "component_at_source": PLEASE_SELECT,
    "component_other_description": "component_other_description response",
    "repair_timestamp": datetime.datetime.now().replace(second=0, microsecond=0),
    "final_repair_concentration": 101.05,
    "repair_description": "repair_description response",
    "additional_notes": "additional_notes response",

    "sector": "Oil & Gas",
    "sector_type": "Oil & Gas",
  }

  return json_data


def get_landfill_dummy_form_data() -> dict:
  """
  Generate dummy Landfill form data as a dictionary.

  Args:
    None

  Returns:
    dict: Pre-filled key/value pairs simulating user input from the HTML form.

  Examples:
    data = get_landfill_dummy_form_data()
    print(data["sector"])
    # Output: 'Landfill'

  Notes:
    - Datetime fields are naive (California local), matching what a user would submit.
    - This data is NOT contract-compliant for direct DB storage; it must be converted to UTC-aware ISO 8601 strings before being saved to the database.
  """
  logger.debug(f"in landfill_dummy_data()")

  json_data = {
    "additional_activities": "additional_activities",
    "additional_notes": "additional_notes",
    "contact_email": "my_email@email.com",
    "contact_name": "contact_name",
    "contact_phone": f"(555) 555-5555",
    # "emission_cause": PLEASE_SELECT,
    "emission_cause_notes": "emission_cause_notes",
    # "emission_cause_secondary": PLEASE_SELECT,
    # "emission_cause_tertiary": PLEASE_SELECT,
    # "emission_identified_flag_fk": PLEASE_SELECT,
    # "emission_location": PLEASE_SELECT,
    "emission_location_notes": "emission_location_notes",
    # "emission_type_fk": PLEASE_SELECT,
    "facility_name": "facility_name",
    "id_arb_swis": "id_arb_swis",
    "id_incidence": 1002030,
    "id_message": "id_message",
    "id_plume": 1002,
    # "included_in_last_lmr": PLEASE_SELECT,
    "included_in_last_lmr_description": "included_in_last_lmr_description",
    "initial_leak_concentration": 1002.5,
    "inspection_timestamp": datetime.datetime.now().replace(second=0, microsecond=0),
    "instrument": "instrument",
    "last_component_leak_monitoring_timestamp": datetime.datetime.now().replace(second=0, microsecond=0),
    "last_surface_monitoring_timestamp": datetime.datetime.now().replace(second=0, microsecond=0),
    "lat_carb": 102.5,
    "lat_revised": 103.5,
    "long_carb": 104.5,
    "long_revised": 105.5,
    "mitigation_actions": "mitigation_actions",
    "mitigation_timestamp": datetime.datetime.now().replace(second=0, microsecond=0),
    "observation_timestamp": datetime.datetime.now().replace(second=0, microsecond=0),
    # "planned_for_next_lmr": PLEASE_SELECT,
    "planned_for_next_lmr_description": "planned_for_next_lmr_description",
    "re_monitored_concentration": 1002.5,
    "re_monitored_timestamp": datetime.datetime.now().replace(second=0, microsecond=0),

    "sector": "Landfill",
    "sector_type": "Landfill",
  }
  return json_data


def get_excel_dropdown_data() -> tuple[dict, dict]:
  """
  Return transformed dropdown lookup values for use in HTML form rendering.

  Returns:
    tuple:
      - dict[str, list[tuple[str, str] | tuple[str, str, dict[str, Any]]]]: Independent dropdowns keyed by HTML field name, with each value as a tuple suitable for form rendering.
      - dict[str, dict[str, list[str | Any]]]: Contingent dropdowns dependent on parent field values, as deep copies of the module-level canonical data.

  Examples:
    drop_downs, contingent = get_excel_dropdown_data()
    print(list(drop_downs.keys()))
    # Output: [ ... field names ... ]

  Notes:
    - The module-level variables _drop_downs and _drop_downs_contingent contain the canonical, human-readable dropdown data as found in Excel templates and business logic.
    - This function returns a deep copy of _drop_downs, transformed using arb.utils.web_html.update_selector_dict, which applies the canonical (value, label) tuple structure and prepends a disabled 'Please Select' option.
    - The contingent dropdowns (_drop_downs_contingent) are returned as a deep copy, unmodified.
    - The transformation logic is always imported from the canonical implementation to ensure consistency and maintainability.
    - NOT COVERED BY UNIT TESTS: This function is not directly covered by unit tests because the transformation logic is delegated to arb.utils.web_html.update_selector_dict, which is tested elsewhere and imported inside the function. Change with caution. See documentation/docstring_update_for_testing.md for details.
  """
  drop_downs = copy.deepcopy(_drop_downs)
  drop_downs_contingent = copy.deepcopy(_drop_downs_contingent)

  from arb.utils.web_html import update_selector_dict

  drop_downs = update_selector_dict(drop_downs)

  return drop_downs, drop_downs_contingent
