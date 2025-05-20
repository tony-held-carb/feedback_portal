"""
This module groups hardcoded testing/example data
and related routines associated with the operator portal.

Notes:
"""
import datetime
from pathlib import Path

from arb.__get_logger import get_logger
from arb.utils.web_html import update_selector_dict
from arb.portal.constants import PLEASE_SELECT

logger, pp_log = get_logger()
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


def add_og_dummy_data(db, base, table_name) -> None:
  """
  Add dummy data to incidence table for diagnostics.
  This routine is likely outdated and is kept only as a template.

  Args:
    db (SQLAlchemy): SQLAlchemy database associated with a flask app
    base (DeclarativeMeta): SQLAlchemy declarative base
    table_name (str): database table name
  """
  from arb.utils.sql_alchemy import get_class_from_table_name
  logger.debug("Adding dummy oil and gas data to populate the database")
  table = get_class_from_table_name(base, table_name)
  col_name = "misc_json"

  offset = 2000000  # adjust so that you don't have a unique constraint issue

  for i in range(1, 10):
    id_incidence = i + offset
    id_plume = i + 100
    lat_arb = i + 50.
    long_arb = i + 75.
    observation_timestamp = datetime.datetime.now().replace(second=0, microsecond=0)

    facility_name = f"facility_{i}"
    contact_name = f"contact_name_{i}"
    contact_phone = f"(555) 555-5555x{i}"
    contact_email = f"my_email_{i}@server.com"
    sector = "Oil & Gas"
    sector_type = "Oil & Gas"

    json_data = {"id_incidence": id_incidence,
                 "id_plume": id_plume,
                 "lat_arb": lat_arb,
                 "long_arb": long_arb,
                 # "observation_timestamp": observation_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
                 "observation_timestamp": observation_timestamp,
                 "facility_name": facility_name,
                 "contact_name": contact_name,
                 "contact_phone": contact_phone,
                 "contact_email": contact_email,
                 "sector": sector,
                 "sector_type": sector_type,
                 }

    model = table(description="Dummy data created by add_og_dummy_data", **{col_name: json_data})

    logger.debug(f"Adding incidence with json dummy data: {json_data=}")

    db.session.add(model)
  db.session.commit()


def get_og_dummy_data():
  """
  Create a model with dummy data for debugging purposes.
  """

  json_data = {
    "id_incidence": 2001,
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


def get_landfill_dummy_data():
  """
  Create a model with dummy data for debugging purposes.
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
    "id_incidence": 2002,
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


def get_excel_dropdown_data():
  """
  Get a dict of tuples suitable for html select elements (keyed by html element name).

  Each tuple is 2 or 3 items in length with the format:
    (select value, select text, and an optional dictionary of additional html formatting)

  # todo - The new drop-downs are not context depended like they are in excel and the
           validate logic needs to be updated.
  Returns:
    drop_downs (list[tuple]): lookup dictionary of drop-down key values for each table.
  """
  # Oil & Gas
  drop_downs = {
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

  # keys to the contingent dropdowns follow the patter html_selector2_contingent_on_html_selector1
  # for instance, emission_cause_contingent_on_emission_location means that the choices for
  # emission_cause are based on a lookup of the value of emission_location

  drop_downs_contingent = {
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

  # Note, the drop_downs get "Please Select" prepended, but the drop_down_contingent content is not modified
  drop_downs = update_selector_dict(drop_downs)
  return drop_downs, drop_downs_contingent
