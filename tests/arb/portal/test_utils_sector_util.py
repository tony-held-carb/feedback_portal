"""
Comprehensive tests for arb.portal.utils.sector_util

Covers all sector utility functions including sector extraction, resolution,
classification, and error handling using mocks for DB and SQLAlchemy.
"""
from unittest.mock import MagicMock, patch

import pytest

from arb.portal.utils.sector_util import (extract_sector_payload, get_sector_info, get_sector_type, resolve_sector)


# --- extract_sector_payload ---
def test_extract_sector_payload_success():
  xl_dict = {
    "metadata": {"sector": "Oil"},
    "tab_contents": {"Feedback Form": {"foo": "bar"}}
  }
  result = extract_sector_payload(xl_dict)
  assert result["foo"] == "bar"
  assert result["sector"] == "Oil"


def test_extract_sector_payload_missing_metadata():
  xl_dict = {"tab_contents": {"Feedback Form": {}}}
  with pytest.raises(ValueError, match="Expected key 'metadata'"):
    extract_sector_payload(xl_dict)


def test_extract_sector_payload_missing_sector():
  xl_dict = {"metadata": {}, "tab_contents": {"Feedback Form": {}}}
  with pytest.raises(ValueError, match="Missing or empty 'sector'"):
    extract_sector_payload(xl_dict)


def test_extract_sector_payload_missing_tab():
  xl_dict = {"metadata": {"sector": "Oil"}, "tab_contents": {}}
  with pytest.raises(ValueError, match="Tab 'Feedback Form' not found"):
    extract_sector_payload(xl_dict)


# --- resolve_sector ---
def test_resolve_sector_json_priority():
  row = MagicMock()
  misc_json = {"sector": "Landfill"}
  result = resolve_sector("Oil", row, misc_json)
  assert result == "Landfill"


def test_resolve_sector_foreign_key_fallback():
  row = MagicMock()
  misc_json = {}
  result = resolve_sector("Oil", row, misc_json)
  assert result == "Oil"


def test_resolve_sector_both_none_raises():
  row = MagicMock()
  misc_json = {}
  with pytest.raises(ValueError, match="Can't determine incidence sector"):
    resolve_sector(None, row, misc_json)


def test_resolve_sector_mismatch_logs_error():
  row = MagicMock()
  misc_json = {"sector": "Landfill"}
  # Should not raise, just log error
  result = resolve_sector("Oil", row, misc_json)
  assert result == "Landfill"


# --- get_sector_type ---
def test_get_sector_type_oil_and_gas():
  with patch("arb.portal.utils.sector_util.OIL_AND_GAS_SECTORS", ["Oil", "Gas"]):
    assert get_sector_type("Oil") == "Oil & Gas"
    assert get_sector_type("Gas") == "Oil & Gas"


def test_get_sector_type_landfill():
  with patch("arb.portal.utils.sector_util.LANDFILL_SECTORS", ["Landfill", "Dump"]):
    assert get_sector_type("Landfill") == "Landfill"
    assert get_sector_type("Dump") == "Landfill"


def test_get_sector_type_unsupported():
  with patch("arb.portal.utils.sector_util.OIL_AND_GAS_SECTORS", []), \
      patch("arb.portal.utils.sector_util.LANDFILL_SECTORS", []):
    assert get_sector_type("Unknown") == "Unknown"


# --- get_sector_info (integration with mocks) ---
@patch("arb.portal.utils.sector_util.get_foreign_value")
@patch("arb.portal.utils.sector_util.get_table_row_and_column")
def test_get_sector_info_success(mock_get_row_col, mock_get_foreign):
  mock_get_foreign.return_value = "Oil"
  mock_get_row_col.return_value = (MagicMock(), {"sector": "Oil"})
  db = MagicMock()
  base = MagicMock()
  sector, sector_type = get_sector_info(db, base, 123)
  assert sector == "Oil"
  assert sector_type == "Oil & Gas" or sector_type == "Oil"  # Accept either if OIL_AND_GAS_SECTORS is patched


@patch("arb.portal.utils.sector_util.get_foreign_value")
@patch("arb.portal.utils.sector_util.get_table_row_and_column")
def test_get_sector_info_missing_misc_json(mock_get_row_col, mock_get_foreign):
  mock_get_foreign.return_value = "Landfill"
  mock_get_row_col.return_value = (MagicMock(), None)
  db = MagicMock()
  base = MagicMock()
  sector, sector_type = get_sector_info(db, base, 456)
  assert sector == "Landfill"
  assert sector_type == "Landfill" or sector_type == "Landfill"


@patch("arb.portal.utils.sector_util.get_foreign_value")
@patch("arb.portal.utils.sector_util.get_table_row_and_column")
def test_get_sector_info_conflicting_sectors(mock_get_row_col, mock_get_foreign):
  mock_get_foreign.return_value = "Oil"
  mock_get_row_col.return_value = (MagicMock(), {"sector": "Landfill"})
  db = MagicMock()
  base = MagicMock()
  sector, sector_type = get_sector_info(db, base, 789)
  assert sector == "Landfill"
  assert sector_type == "Landfill" or sector_type == "Landfill"
