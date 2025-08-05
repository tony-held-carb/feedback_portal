import pytest

try:
  import arb.portal.db_hardcoded as db_hardcoded
except ModuleNotFoundError:
  # If running as a script, ensure PYTHONPATH includes the project root
  import sys, os

  sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
  import arb.portal.db_hardcoded as db_hardcoded
import datetime
import copy


# NOTE: Some edge cases or error conditions in get_excel_dropdown_data may not be fully covered by unit tests,
# as the transformation logic is delegated to arb.utils.web_html.update_selector_dict. This ensures canonical
# behavior but means that any bugs or changes in the canonical function are not directly tested here.
# See documentation/docstring_update_for_testing.md for details and rationale.

# --- Dummy Data Tests ---
def test_get_og_dummy_form_data_keys():
  data = db_hardcoded.get_og_dummy_form_data()
  assert isinstance(data, dict)
  assert "sector" in data and data["sector"] == "Oil & Gas"
  assert "observation_timestamp" in data
  assert isinstance(data["observation_timestamp"], datetime.datetime)


def test_get_landfill_dummy_form_data_keys():
  data = db_hardcoded.get_landfill_dummy_form_data()
  assert isinstance(data, dict)
  assert "sector" in data and data["sector"] == "Landfill"
  assert "inspection_timestamp" in data
  assert isinstance(data["inspection_timestamp"], datetime.datetime)


# --- Enhanced Dummy Data Testing ---
def test_get_og_dummy_form_data_completeness():
  """Test that all expected Oil & Gas fields are present and have correct types."""
  data = db_hardcoded.get_og_dummy_form_data()

  # Required fields that should always be present
  expected_fields = {
    "id_incidence": int,
    "id_plume": int,
    "observation_timestamp": datetime.datetime,
    "lat_carb": float,
    "long_carb": float,
    "id_message": str,
    "facility_name": str,
    "id_arb_eggrt": str,
    "contact_name": str,
    "contact_phone": str,
    "contact_email": str,
    "venting_description_1": str,
    "ogi_date": datetime.datetime,
    "method21_date": datetime.datetime,
    "initial_leak_concentration": int,
    "venting_description_2": str,
    "initial_mitigation_plan": str,
    "equipment_other_description": str,
    "component_other_description": str,
    "repair_timestamp": datetime.datetime,
    "final_repair_concentration": float,
    "repair_description": str,
    "additional_notes": str,
    "sector": str,
    "sector_type": str,
  }

  for field, expected_type in expected_fields.items():
    assert field in data, f"Missing field: {field}"
    assert isinstance(data[field], expected_type), f"Field {field} has wrong type: {type(data[field])}"


def test_get_landfill_dummy_form_data_completeness():
  """Test that all expected Landfill fields are present and have correct types."""
  data = db_hardcoded.get_landfill_dummy_form_data()

  # Required fields that should always be present
  expected_fields = {
    "additional_activities": str,
    "additional_notes": str,
    "contact_email": str,
    "contact_name": str,
    "contact_phone": str,
    "emission_cause_notes": str,
    "facility_name": str,
    "id_arb_swis": str,
    "id_incidence": int,
    "id_message": str,
    "id_plume": int,
    "included_in_last_lmr_description": str,
    "initial_leak_concentration": float,
    "inspection_timestamp": datetime.datetime,
    "instrument": str,
    "last_component_leak_monitoring_timestamp": datetime.datetime,
    "last_surface_monitoring_timestamp": datetime.datetime,
    "lat_carb": float,
    "lat_revised": float,
    "long_carb": float,
    "long_revised": float,
    "mitigation_actions": str,
    "mitigation_timestamp": datetime.datetime,
    "observation_timestamp": datetime.datetime,
    "planned_for_next_lmr_description": str,
    "re_monitored_concentration": float,
    "re_monitored_timestamp": datetime.datetime,
    "sector": str,
    "sector_type": str,
  }

  for field, expected_type in expected_fields.items():
    assert field in data, f"Missing field: {field}"
    assert isinstance(data[field], expected_type), f"Field {field} has wrong type: {type(data[field])}"


def test_dummy_data_datetime_consistency():
  """Test that datetime fields in dummy data are consistent and naive (local time)."""
  og_data = db_hardcoded.get_og_dummy_form_data()
  landfill_data = db_hardcoded.get_landfill_dummy_form_data()

  # Check that datetime fields are naive (no timezone info)
  datetime_fields_og = ["observation_timestamp", "ogi_date", "method21_date", "repair_timestamp"]
  datetime_fields_landfill = ["inspection_timestamp", "last_component_leak_monitoring_timestamp",
                              "last_surface_monitoring_timestamp", "mitigation_timestamp",
                              "observation_timestamp", "re_monitored_timestamp"]

  for field in datetime_fields_og:
    dt = og_data[field]
    assert dt.tzinfo is None, f"OG field {field} should be naive datetime"
    assert dt.second == 0, f"OG field {field} should have seconds=0"
    assert dt.microsecond == 0, f"OG field {field} should have microseconds=0"

  for field in datetime_fields_landfill:
    dt = landfill_data[field]
    assert dt.tzinfo is None, f"Landfill field {field} should be naive datetime"
    assert dt.second == 0, f"Landfill field {field} should have seconds=0"
    assert dt.microsecond == 0, f"Landfill field {field} should have microseconds=0"


def test_dummy_data_sector_consistency():
  """Test that sector information is consistent across dummy data."""
  og_data = db_hardcoded.get_og_dummy_form_data()
  landfill_data = db_hardcoded.get_landfill_dummy_form_data()

  assert og_data["sector"] == "Oil & Gas"
  assert og_data["sector_type"] == "Oil & Gas"
  assert landfill_data["sector"] == "Landfill"
  assert landfill_data["sector_type"] == "Landfill"


# Note: The dummy data may use in-range or out-of-range values depending on current testing needs.
# Do not assert specific value ranges here. Range validation is tested in the WTForms/form validation tests.

# --- Dropdown Data Structure Tests ---
def test_module_level_dropdowns_are_dicts():
  assert isinstance(db_hardcoded._drop_downs, dict)
  assert isinstance(db_hardcoded._drop_downs_contingent, dict)


def test_get_excel_dropdown_data_returns_tuple_and_dicts():
  drop_downs, contingent = db_hardcoded.get_excel_dropdown_data()
  assert isinstance(drop_downs, dict)
  assert isinstance(contingent, dict)
  assert isinstance(drop_downs.get("venting_exclusion"), list)


def test_get_excel_dropdown_data_please_select_present():
  drop_downs, _ = db_hardcoded.get_excel_dropdown_data()
  for key, values in drop_downs.items():
    assert isinstance(values, list)
    if values:
      first = values[0]
      assert isinstance(first, tuple)
      assert "Please Select" in first[0]
      assert isinstance(first[-1], dict) and first[-1].get("disabled") is True


def test_get_excel_dropdown_data_tuple_structure():
  drop_downs, _ = db_hardcoded.get_excel_dropdown_data()
  for key, values in drop_downs.items():
    for tup in values:
      assert isinstance(tup, tuple)
      assert len(tup) in (2, 3)
      assert isinstance(tup[0], str)
      assert isinstance(tup[1], str)


def test_get_excel_dropdown_data_deepcopy_immutability():
  drop_downs, contingent = db_hardcoded.get_excel_dropdown_data()
  orig = copy.deepcopy(db_hardcoded._drop_downs)
  drop_downs["venting_exclusion"].append(("NEW", "NEW"))
  assert db_hardcoded._drop_downs == orig
  contingent["emission_cause_contingent_on_emission_location"]["Other"] = ["NEW"]
  assert db_hardcoded._drop_downs_contingent != contingent


def test_empty_dropdown_edge_case():
  # Simulate an empty dropdown in the module variable
  orig = db_hardcoded._drop_downs.get("venting_exclusion")
  if orig is not None:
    db_hardcoded._drop_downs["venting_exclusion"] = []
    drop_downs, _ = db_hardcoded.get_excel_dropdown_data()
    assert drop_downs["venting_exclusion"][0][0] == "Please Select"
    db_hardcoded._drop_downs["venting_exclusion"] = orig  # restore


def test_contingent_dropdown_structure():
  _, contingent = db_hardcoded.get_excel_dropdown_data()
  for key, val in contingent.items():
    assert isinstance(val, dict)
    for subkey, subval in val.items():
      assert isinstance(subval, list)


# --- Enhanced Dropdown Testing ---
def test_all_expected_dropdown_keys_present():
  """Test that all expected dropdown keys are present in the transformed data."""
  drop_downs, _ = db_hardcoded.get_excel_dropdown_data()

  expected_keys = {
    "venting_exclusion", "ogi_performed", "ogi_result", "method21_performed",
    "method21_result", "equipment_at_source", "component_at_source",
    "emission_identified_flag_fk", "emission_type_fk", "emission_location",
    "emission_cause", "emission_cause_secondary", "emission_cause_tertiary",
    "included_in_last_lmr", "planned_for_next_lmr"
  }

  for key in expected_keys:
    assert key in drop_downs, f"Missing dropdown key: {key}"


def test_dropdown_values_not_empty():
  """Test that all dropdowns contain values (not just the Please Select option)."""
  drop_downs, _ = db_hardcoded.get_excel_dropdown_data()

  for key, values in drop_downs.items():
    assert len(values) > 1, f"Dropdown {key} should have more than just 'Please Select'"
    # Check that there are actual options beyond the Please Select
    actual_options = [v for v in values if "Please Select" not in v[0]]
    assert len(actual_options) > 0, f"Dropdown {key} has no actual options"


def test_contingent_dropdown_completeness():
  """Test that contingent dropdowns have all expected parent-child relationships."""
  _, contingent = db_hardcoded.get_excel_dropdown_data()

  # Test the main contingent relationship
  assert "emission_cause_contingent_on_emission_location" in contingent

  contingent_data = contingent["emission_cause_contingent_on_emission_location"]
  expected_parents = {
    "Gas Collection System Component (e.g., blower, well, valve, port)",
    "Gas Control Device/Control System Component",
    "Landfill Surface: Daily Cover",
    "Landfill Surface: Intermediate Cover",
    "Landfill Surface: Final Cover",
    "Leachate Management System",
    "Working Face (area where active filling was being conducted at the time of detection)"
  }

  for parent in expected_parents:
    assert parent in contingent_data, f"Missing parent option: {parent}"
    assert isinstance(contingent_data[parent], list), f"Parent {parent} should have list of options"
    assert len(contingent_data[parent]) > 0, f"Parent {parent} has no child options"


def test_dropdown_data_consistency():
  """Test that dropdown data is consistent between original and transformed versions."""
  drop_downs, _ = db_hardcoded.get_excel_dropdown_data()

  # Test that the original data is preserved in the transformed version
  for key, original_values in db_hardcoded._drop_downs.items():
    if key in drop_downs:
      transformed_values = drop_downs[key]
      # Skip the first "Please Select" option
      actual_transformed = [v[0] for v in transformed_values[1:]]
      assert actual_transformed == original_values, f"Values for {key} don't match"


# --- Constants and Logger ---
def test_sector_constants_are_lists():
  assert isinstance(db_hardcoded.OIL_AND_GAS_SECTORS, list)
  assert isinstance(db_hardcoded.LANDFILL_SECTORS, list)


def test_logger_is_configured():
  assert hasattr(db_hardcoded, "logger")
  assert db_hardcoded.logger.name == "arb.portal.db_hardcoded"


def test_sector_constants_content():
  """Test that sector constants contain expected values."""
  oil_gas_sectors = db_hardcoded.OIL_AND_GAS_SECTORS
  landfill_sectors = db_hardcoded.LANDFILL_SECTORS

  # Test that lists are not empty
  assert len(oil_gas_sectors) > 0
  assert len(landfill_sectors) > 0

  # Test that all values are strings
  for sector in oil_gas_sectors:
    assert isinstance(sector, str)
  for sector in landfill_sectors:
    assert isinstance(sector, str)

  # Test for specific expected values
  assert "Oil & Gas" in oil_gas_sectors
  assert "Landfill" in landfill_sectors


# --- Canonical Transformation Logic ---
@pytest.mark.skip(
  reason="The transformation logic for dropdowns is delegated to arb.utils.web_html.update_selector_dict. Canonical logic is tested elsewhere.")
def test_selector_list_to_tuples_matches_canonical():
  pass
