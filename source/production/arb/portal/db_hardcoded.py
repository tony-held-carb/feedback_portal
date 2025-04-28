"""
This module groups hardcoded testing/example data
and related routines associated with the operator portal.

Notes:
"""
import datetime
from zoneinfo import ZoneInfo

import arb.__get_logger as get_logger
from arb.utils.web_html import update_selector_dict

logger, pp_log = get_logger.get_logger(__name__, __file__)

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
    observation_timestamp = datetime.datetime.now()

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
    "additional_notes": "additional_notes",
    "component_other_description": "component_other_description",
    "contact_email": "my_email@email.com",
    "contact_name": "contact_name",
    "contact_phone": f"(555) 555-5555",
    # "equipment_at_source": 2,
    "equipment_other_description": "equipment_other_description",
    "facility_name": "facility_name",
    "final_repair_concentration": 101,
    # "found_source_type": 2,
    "id_arb_eggrt": 1001,
    # "id_incidence": 1002,
    "id_plume": 1003,
    "initial_leak_concentration": 1004,
    "initial_method_21_timestamp": datetime.datetime.now(),
    "initial_mitigation_plan": "initial_mitigation_plan",
    "inspection_timestamp": datetime.datetime.now(),
    # "inspection_type": 2,
    "notification_timestamp": datetime.datetime.now(),
    "observation_timestamp": datetime.datetime.now(),
    # "ogi_survey": 2,
    # "repair_description": 2,
    "repair_timestamp": datetime.datetime.now(),
    "venting_description_1": "venting_description_1",
    "venting_description_2": "venting_description_2",
    # "venting_exclusion": 2,
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
    "facility_name": "facility_name",
    "additional_notes": "additional_notes",
    "component_other_description": "component_other_description",
    "contact_email": "my_email@email.com",
    "contact_name": "contact_name",
    "contact_phone": f"(555) 555-5555",
    "sector": "Landfill",
    "sector_type": "Landfill",
    "id_plume": 1234,
    "observation_timestamp": datetime.datetime.now() - datetime.timedelta(days=5),
    "inspection_timestamp": datetime.datetime.now() - datetime.timedelta(days=4),
    "mitigation_timestamp": datetime.datetime.now() - datetime.timedelta(days=6),
    "last_surface_monitoring_timestamp": datetime.datetime.now() - datetime.timedelta(days=2),
    "last_component_leak_monitoring_timestamp": datetime.datetime.now() - datetime.timedelta(days=1),
  }
  return json_data


def get_excel_dropdown_data():
  """
  Get a dict of tuples suitable for html select elements (keyed by html element name).

  Each tuple is 2 or 3 items in length with the format:
    (select value, select text, and an optional dictionary of additional html formatting)

  # todo - The new drop downs are not context depended like they are in excel and the
           validate logic needs to be updated.
  Returns:
    drop_downs (list[tuple]): lookup dictionary of drop down key values for each table.
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

  drop_downs = update_selector_dict(drop_downs)
  return drop_downs
