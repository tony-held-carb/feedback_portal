"""
Hardcoded test/example data and dropdown configurations
for the Operator Feedback Portal.

Includes:
  - Oil & Gas dummy JSON submissions
  - Landfill dummy JSON submissions
  - HTML <select> dropdown options and dependent dropdowns

Notes:
  - These functions are for development/test only.
  - Dropdown values are used for validation and rendering in forms.
"""

import datetime

import arb.__get_logger as get_logger

logger, pp_log = get_logger.get_logger(__name__, __file__)


def add_og_dummy_data(db, base, table_name: str) -> None:
  """
  Add dummy Oil & Gas data to the database for diagnostics or dev setup.

  Args:
      db (SQLAlchemy): SQLAlchemy instance.
      base (DeclarativeMeta): SQLAlchemy automapped base or declarative base.
      table_name (str): Name of the target table to populate.

  Returns:
      None

  Notes:
      Adjust the `offset` to avoid unique constraint violations when reusing this.
      This routine assumes the table has a JSON column named `misc_json`.

  Example:
      >>> add_og_dummy_data(db, base, "incidence")
  """
  from arb.utils.sql_alchemy import get_class_from_table_name
  table = get_class_from_table_name(base, table_name)
  col_name = "misc_json"
  offset = 2_000_000

  logger.debug("Adding dummy oil and gas data to populate the database")

  for i in range(1, 10):
    json_data = {
      "id_incidence": i + offset,
      "id_plume": i + 100,
      "lat_arb": i + 50.0,
      "long_arb": i + 75.0,
      "observation_timestamp": datetime.datetime.now(),
      "facility_name": f"facility_{i}",
      "contact_name": f"contact_name_{i}",
      "contact_phone": f"(555) 555-5555x{i}",
      "contact_email": f"my_email_{i}@server.com",
      "sector": "Oil & Gas",
      "sector_type": "Oil & Gas",
    }

    model = table(description="Dummy data created by add_og_dummy_data", **{col_name: json_data})
    logger.debug(f"Adding incidence with json dummy data: {json_data=}")
    db.session.add(model)

  db.session.commit()


def get_og_dummy_data() -> dict:
  """
  Return a full dummy Oil & Gas report payload.

  Returns:
      dict: Simulated JSON payload mimicking a real OG user submission.

  Example:
      >>> data = get_og_dummy_data()
      >>> print(data["facility_name"])
      'facility_name response'
  """
  now = datetime.datetime.now()
  return {
    "id_incidence": 1001,
    "id_plume": 1001,
    "observation_timestamp": now,
    "lat_carb": 100.05,
    "long_carb": 100.06,
    "id_message": "id_message response",
    "facility_name": "facility_name response",
    "id_arb_eggrt": 1001,
    "contact_name": "contact_name response",
    "contact_phone": "(555) 555-5555",
    "contact_email": "my_email@email.com",
    "venting_exclusion": "Please Select",
    "venting_description_1": "venting_description_1 response",
    "ogi_performed": "Please Select",
    "ogi_date": now,
    "ogi_result": "Please Select",
    "method21_performed": "Please Select",
    "method21_date": now,
    "method21_result": "Please Select",
    "initial_leak_concentration": 1004,
    "venting_description_2": "venting_description_2 response",
    "initial_mitigation_plan": "initial_mitigation_plan response",
    "equipment_at_source": "Please Select",
    "equipment_other_description": "equipment_other_description response",
    "component_at_source": "Please Select",
    "component_other_description": "component_other_description response",
    "repair_timestamp": now,
    "final_repair_concentration": 101.05,
    "repair_description": "repair_description response",
    "additional_notes": "additional_notes response",
    "sector": "Oil & Gas",
    "sector_type": "Oil & Gas",
  }


def get_landfill_dummy_data() -> dict:
  """
  Return a full dummy Landfill report payload.

  Returns:
      dict: Simulated JSON payload for Landfill form data.

  Example:
      >>> data = get_landfill_dummy_data()
      >>> print(data["sector_type"])
      'Landfill'
  """
  logger.debug("Generating landfill dummy data")
  now = datetime.datetime.now()
  return {
    "additional_activities": "additional_activities",
    "additional_notes": "additional_notes",
    "contact_email": "my_email@email.com",
    "contact_name": "contact_name",
    "contact_phone": "(555) 555-5555",
    "emission_cause": "Please Select",
    "emission_cause_notes": "emission_cause_notes",
    "emission_cause_secondary": "Please Select",
    "emission_cause_tertiary": "Please Select",
    "emission_identified_flag_fk": "Please Select",
    "emission_location": "Please Select",
    "emission_location_notes": "emission_location_notes",
    "emission_type_fk": "Please Select",
    "facility_name": "facility_name",
    "id_arb_swis": "id_arb_swis",
    "id_message": "id_message",
    "id_plume": 1002,
    "included_in_last_lmr": "Please Select",
    "included_in_last_lmr_description": "included_in_last_lmr_description",
    "initial_leak_concentration": 1002.5,
    "inspection_timestamp": now,
    "instrument": "instrument",
    "last_component_leak_monitoring_timestamp": now,
    "last_surface_monitoring_timestamp": now,
    "lat_carb": 102.5,
    "lat_revised": 103.5,
    "long_carb": 104.5,
    "long_revised": 105.5,
    "mitigation_actions": "mitigation_actions",
    "mitigation_timestamp": now,
    "observation_timestamp": now,
    "planned_for_next_lmr": "Please Select",
    "planned_for_next_lmr_description": "planned_for_next_lmr_description",
    "re_monitored_concentration": 1002.5,
    "re_monitored_timestamp": now,
    "sector": "Landfill",
    "sector_type": "Landfill",
  }


def run_diagnostics() -> None:
  """
  Run diagnostics to verify the structure and integrity of dummy payloads and dropdown data.

  This function checks:
      - Basic keys and field expectations in Oil & Gas and Landfill dummy data
      - That dropdowns include key select fields with the 'Please Select' placeholder
      - That contingent dropdowns exist and are properly structured

  Example:
      >>> run_diagnostics()
      ✓ Oil & Gas dummy payload valid
      ✓ Landfill dummy payload valid
      ✓ Excel dropdowns valid
      ✓ Contingent dropdown mappings valid
      ✓ All diagnostics passed.

  Raises:
      AssertionError: If any validation fails.
  """
  print("\n=== Running diagnostics on dummy_data.py ===")

  # Validate Oil & Gas dummy structure
  og = get_og_dummy_data()
  assert og.get("sector") == "Oil & Gas", "OG payload missing or has incorrect sector"
  assert "facility_name" in og, "OG payload missing facility_name"
  assert isinstance(og.get("observation_timestamp"), datetime.datetime), "OG timestamp invalid"
  print("✓ Oil & Gas dummy payload valid")

  # Validate Landfill dummy structure
  landfill = get_landfill_dummy_data()
  assert landfill.get("sector") == "Landfill", "Landfill payload missing or has incorrect sector"
  assert "facility_name" in landfill, "Landfill payload missing facility_name"
  assert isinstance(landfill.get("inspection_timestamp"), datetime.datetime), "Landfill timestamp invalid"
  print("✓ Landfill dummy payload valid")

  # Validate dropdown structure
  dropdowns, contingent = get_excel_dropdown_data()

  required_keys = ["ogi_performed", "emission_location"]
  for key in required_keys:
    assert key in dropdowns, f"Missing key in dropdowns: {key}"
    assert dropdowns[key][0] == "Please Select", f"First item for '{key}' should be 'Please Select'"

  print("✓ Excel dropdowns valid")

  # Validate contingent dropdown structure
  assert "emission_cause_contingent_on_emission_location" in contingent, "Missing contingent dropdown key"
  mapping = contingent["emission_cause_contingent_on_emission_location"]
  assert isinstance(mapping, dict), "Contingent dropdown should be a dict"

  test_key = next(iter(mapping))
  assert isinstance(mapping[test_key], list), "Contingent dropdown mapping should contain lists"
  assert mapping[test_key], "Contingent dropdown mapping list is empty"

  print("✓ Contingent dropdown mappings valid")

  print("✓ All diagnostics passed.\n")


if __name__ == "__main__":
  run_diagnostics()
