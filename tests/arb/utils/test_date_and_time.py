"""
Unit tests for date_and_time.py

Coverage philosophy:
- All normal and common edge cases for datetime parsing, conversion, and validation are well covered.
- Error handling for invalid, empty, and naive/aware datetime inputs is tested.
- Bulk/recursive utilities are lightly tested, as they are not currently used in production workflows.
- DST transitions, leap years, and other rare corner cases are not exhaustively tested, but can be added if these scenarios become relevant.

This suite provides strong confidence for current usage and can be expanded as new requirements or edge cases arise.
"""
import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from arb.utils import date_and_time as dtmod

UTC_TZ = ZoneInfo("UTC")
PACIFIC_TZ = ZoneInfo("America/Los_Angeles")

# --- iso_str_to_utc_datetime ---
def test_iso_str_to_utc_datetime_valid():
    assert dtmod.iso_str_to_utc_datetime("2025-04-20T14:30:00+00:00") == datetime(2025, 4, 20, 14, 30, tzinfo=UTC_TZ)
    assert dtmod.iso_str_to_utc_datetime("2025-04-20T14:30:00Z") == datetime(2025, 4, 20, 14, 30, tzinfo=UTC_TZ)

def test_iso_str_to_utc_datetime_missing_tz_error():
    with pytest.raises(ValueError):
        dtmod.iso_str_to_utc_datetime("2025-04-20 14:30:00")

def test_iso_str_to_utc_datetime_missing_tz_assume_utc():
    result = dtmod.iso_str_to_utc_datetime("2025-04-20 14:30:00", error_on_missing_tz=False)
    assert result == datetime(2025, 4, 20, 14, 30, tzinfo=UTC_TZ)

def test_iso_str_to_utc_datetime_empty():
    with pytest.raises(ValueError):
        dtmod.iso_str_to_utc_datetime("")

def test_iso_str_to_utc_datetime_invalid():
    with pytest.raises(ValueError):
        dtmod.iso_str_to_utc_datetime("not a date")

# --- excel_str_to_naive_datetime ---
def test_excel_str_to_naive_datetime_valid():
    result = dtmod.excel_str_to_naive_datetime("2025-04-20 14:30:00")
    assert isinstance(result, datetime)
    assert result.year == 2025

def test_excel_str_to_naive_datetime_empty_invalid():
    assert dtmod.excel_str_to_naive_datetime("") is None
    assert dtmod.excel_str_to_naive_datetime("not a date") is None

# --- html_naive_str_to_utc_datetime ---
def test_html_naive_str_to_utc_datetime_valid():
    result = dtmod.html_naive_str_to_utc_datetime("2025-01-15T14:30")
    assert isinstance(result, datetime)
    assert result.tzinfo == UTC_TZ

def test_html_naive_str_to_utc_datetime_empty():
    assert dtmod.html_naive_str_to_utc_datetime("") is None

# --- ca_naive_datetime_to_utc_datetime ---
def test_ca_naive_datetime_to_utc_datetime_valid():
    naive = datetime(2025, 1, 15, 14, 30)
    result = dtmod.ca_naive_datetime_to_utc_datetime(naive)
    assert result.tzinfo == UTC_TZ

def test_ca_naive_datetime_to_utc_datetime_aware():
    aware = datetime(2025, 1, 15, 14, 30, tzinfo=UTC_TZ)
    with pytest.raises(ValueError):
        dtmod.ca_naive_datetime_to_utc_datetime(aware)

# --- utc_datetime_to_ca_naive_datetime ---
def test_utc_datetime_to_ca_naive_datetime_utc():
    utc_dt = datetime(2025, 1, 15, 22, 30, tzinfo=UTC_TZ)
    result = dtmod.utc_datetime_to_ca_naive_datetime(utc_dt)
    assert result.tzinfo is None

def test_utc_datetime_to_ca_naive_datetime_naive_flag():
    naive = datetime(2025, 1, 15, 22, 30)
    result = dtmod.utc_datetime_to_ca_naive_datetime(naive, assume_naive_is_utc=True)
    assert result.tzinfo is None

def test_utc_datetime_to_ca_naive_datetime_naive_error():
    naive = datetime(2025, 1, 15, 22, 30)
    with pytest.raises(ValueError):
        dtmod.utc_datetime_to_ca_naive_datetime(naive)

def test_utc_datetime_to_ca_naive_datetime_non_utc_error():
    pacific = datetime(2025, 1, 15, 14, 30, tzinfo=PACIFIC_TZ)
    with pytest.raises(ValueError):
        dtmod.utc_datetime_to_ca_naive_datetime(pacific, utc_strict=True)

# --- utc_datetime_to_iso_str ---
def test_utc_datetime_to_iso_str_valid():
    utc_dt = datetime(2025, 1, 15, 22, 30, tzinfo=UTC_TZ)
    result = dtmod.utc_datetime_to_iso_str(utc_dt)
    assert result.startswith("2025-01-15T22:30:00")

def test_utc_datetime_to_iso_str_naive():
    naive = datetime(2025, 1, 15, 22, 30)
    with pytest.raises(ValueError):
        dtmod.utc_datetime_to_iso_str(naive)

# --- utc_datetime_to_html_naive_str ---
def test_utc_datetime_to_html_naive_str_valid():
    utc_dt = datetime(2025, 1, 15, 22, 30, tzinfo=UTC_TZ)
    result = dtmod.utc_datetime_to_html_naive_str(utc_dt)
    assert result == "2025-01-15T14:30"

def test_utc_datetime_to_html_naive_str_naive():
    naive = datetime(2025, 1, 15, 22, 30)
    with pytest.raises(ValueError):
        dtmod.utc_datetime_to_html_naive_str(naive)

def test_utc_datetime_to_html_naive_str_non_utc():
    pacific = datetime(2025, 1, 15, 14, 30, tzinfo=PACIFIC_TZ)
    with pytest.raises(ValueError):
        dtmod.utc_datetime_to_html_naive_str(pacific)

# --- is_datetime_naive ---
def test_is_datetime_naive_cases():
    assert dtmod.is_datetime_naive(datetime(2025, 1, 15, 14, 30)) is True
    assert dtmod.is_datetime_naive(datetime(2025, 1, 15, 14, 30, tzinfo=UTC_TZ)) is False
    # None is not a valid datetime, so skip passing None

# --- is_datetime_utc ---
def test_is_datetime_utc_cases():
    assert dtmod.is_datetime_utc(datetime(2025, 1, 15, 14, 30, tzinfo=UTC_TZ)) is True
    assert dtmod.is_datetime_utc(datetime(2025, 1, 15, 14, 30, tzinfo=PACIFIC_TZ)) is False
    assert dtmod.is_datetime_utc(datetime(2025, 1, 15, 14, 30)) is False
    # None is not a valid datetime, so skip passing None

# --- excel_naive_datetime_to_utc_datetime ---
def test_excel_naive_datetime_to_utc_datetime_valid():
    naive = datetime(2025, 1, 15, 14, 30)
    result = dtmod.excel_naive_datetime_to_utc_datetime(naive)
    assert result.tzinfo == UTC_TZ

def test_excel_naive_datetime_to_utc_datetime_aware():
    aware = datetime(2025, 1, 15, 14, 30, tzinfo=UTC_TZ)
    with pytest.raises(ValueError):
        dtmod.excel_naive_datetime_to_utc_datetime(aware)

# --- utc_iso_str_to_ca_str ---
def test_utc_iso_str_to_ca_str_valid():
    result = dtmod.utc_iso_str_to_ca_str("2025-01-15T22:30:00+00:00")
    assert result == "2025-01-15T14:30"

def test_utc_iso_str_to_ca_str_empty():
    assert dtmod.utc_iso_str_to_ca_str("") == ""

def test_utc_iso_str_to_ca_str_invalid():
    assert dtmod.utc_iso_str_to_ca_str("not a date") == "not a date"

# --- bulk_utc_datetime_to_ca_naive_datetime ---
def test_bulk_utc_datetime_to_ca_naive_datetime_dict():
    data = {"dt": datetime(2025, 1, 15, 22, 30, tzinfo=UTC_TZ)}
    result = dtmod.bulk_utc_datetime_to_ca_naive_datetime(data)
    assert isinstance(result, dict)
    assert isinstance(result["dt"], datetime)
    assert result["dt"].tzinfo is None

def test_bulk_utc_datetime_to_ca_naive_datetime_list():
    data = [datetime(2025, 1, 15, 22, 30, tzinfo=UTC_TZ)]
    result = dtmod.bulk_utc_datetime_to_ca_naive_datetime(data)
    assert isinstance(result, list)
    assert isinstance(result[0], datetime)
    assert result[0].tzinfo is None

def test_bulk_utc_datetime_to_ca_naive_datetime_non_datetime():
    assert dtmod.bulk_utc_datetime_to_ca_naive_datetime(123) == 123

# --- bulk_ca_naive_datetime_to_utc_datetime ---
def test_bulk_ca_naive_datetime_to_utc_datetime_dict():
    data = {"dt": datetime(2025, 1, 15, 14, 30)}
    result = dtmod.bulk_ca_naive_datetime_to_utc_datetime(data)
    assert isinstance(result, dict)
    assert isinstance(result["dt"], datetime)
    assert result["dt"].tzinfo == UTC_TZ

def test_bulk_ca_naive_datetime_to_utc_datetime_list():
    data = [datetime(2025, 1, 15, 14, 30)]
    result = dtmod.bulk_ca_naive_datetime_to_utc_datetime(data)
    assert isinstance(result, list)
    assert isinstance(result[0], datetime)
    assert result[0].tzinfo == UTC_TZ

def test_bulk_ca_naive_datetime_to_utc_datetime_non_datetime():
    assert dtmod.bulk_ca_naive_datetime_to_utc_datetime(123) == 123 