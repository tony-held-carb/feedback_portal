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

# --- Constants and Logger ---
def test_sector_constants_are_lists():
  assert isinstance(db_hardcoded.OIL_AND_GAS_SECTORS, list)
  assert isinstance(db_hardcoded.LANDFILL_SECTORS, list)


def test_logger_is_configured():
  assert hasattr(db_hardcoded, "logger")
  assert db_hardcoded.logger.name == "arb.portal.db_hardcoded"

# --- Canonical Transformation Logic ---
@pytest.mark.skip(reason="The transformation logic for dropdowns is delegated to arb.utils.web_html.update_selector_dict. Canonical logic is tested elsewhere.")
def test_selector_list_to_tuples_matches_canonical():
  pass 