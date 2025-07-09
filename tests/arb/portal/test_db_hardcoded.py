import pytest
import arb.portal.db_hardcoded as db_hardcoded
from unittest.mock import patch
import datetime

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

def test_get_excel_dropdown_data_returns_tuple():
  result = db_hardcoded.get_excel_dropdown_data()
  assert isinstance(result, tuple)
  assert len(result) == 2
  assert isinstance(result[0], dict)
  assert isinstance(result[1], dict)

def test_sector_constants_are_lists():
  assert isinstance(db_hardcoded.OIL_AND_GAS_SECTORS, list)
  assert isinstance(db_hardcoded.LANDFILL_SECTORS, list) 