"""
Datetime parsing and timezone utilities for ISO 8601, UTC/Pacific conversion, and recursive datetime transformation in nested structures.

Features:
- ISO 8601 validation and parsing (via `dateutil`)
- Conversion between UTC and naive Pacific time (Los Angeles)
- HTML and Excel datetime contract-compliant conversions
- Recursive datetime transformations within nested dicts/lists/sets/tuples

Timezone policy:
- `UTC_TZ` and `PACIFIC_TZ` are globally defined using `zoneinfo.ZoneInfo`
- Naive timestamps are only assumed to be UTC if explicitly configured via arguments
"""
import logging
from collections.abc import Mapping
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo
from dateutil import parser
__version__ = "1.0.0"
logger = logging.getLogger(__name__)

UTC_TZ = ZoneInfo("UTC")
PACIFIC_TZ = ZoneInfo("America/Los_Angeles")

# --- Core Contract Functions ---

# -- String to Datetime Conversion Functions --

def iso_str_to_utc_datetime(iso_str: str, error_on_missing_tz: bool = True) -> datetime:
    """
    Convert an ISO 8601 string to a UTC-aware datetime object.

    Args:
        iso_str (str): ISO 8601-formatted datetime string.
        error_on_missing_tz (bool): If True, raise if no timezone info is present.

    Returns:
        datetime: UTC-aware datetime object.

    Raises:
        ValueError: If the string is invalid or lacks timezone info (when required).

    Examples:
        iso_str_to_utc_datetime("2025-04-20T14:30:00+00:00")
        iso_str_to_utc_datetime("2025-04-20T14:30:00Z")
        iso_str_to_utc_datetime("2025-04-20 14:30:00", error_on_missing_tz=False)
    """
    try:
        dt = parser.isoparse(iso_str)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid ISO 8601 datetime string: '{iso_str}'") from e
    if dt.tzinfo is None:
        if error_on_missing_tz:
            raise ValueError("Missing timezone info in ISO 8601 string.")
        logger.warning(f"Assuming UTC for naive ISO string: {iso_str}")
        dt = dt.replace(tzinfo=UTC_TZ)
    return dt.astimezone(UTC_TZ)

def excel_str_to_naive_datetime(excel_str: str) -> datetime | None:
    """
    Parse a string from an Excel cell to a naive datetime object (no timezone).

    Args:
        excel_str (str): Excel cell value to parse.

    Returns:
        datetime | None: Parsed naive datetime, or None if unparseable.

    Notes:
        - Only used if openpyxl did not already parse the cell as a datetime.
        - Returns None if the string is empty, not a string, or unparseable.
    """
    if not isinstance(excel_str, str) or not excel_str:
        return None
    try:
        return parser.parse(excel_str)
    except (ValueError, TypeError):
        return None

def html_naive_str_to_utc_datetime(html_str: str) -> datetime | None:
    """
    Convert an HTML form datetime-local string (naive, California local) to a UTC-aware datetime.

    Args:
        html_str (str): HTML datetime-local input value (e.g., "2025-01-15T14:30").

    Returns:
        datetime | None: UTC-aware datetime, or None if input is empty.

    Examples:
        html_naive_str_to_utc_datetime("2025-01-15T14:30")
    """
    if not html_str:
        return None
    ca_naive_dt = datetime.fromisoformat(html_str)
    return ca_naive_datetime_to_utc_datetime(ca_naive_dt)

def ca_naive_datetime_to_utc_datetime(ca_naive_dt: datetime) -> datetime:
    """
    Convert a naive California local datetime to a UTC-aware datetime.

    Args:
        ca_naive_dt (datetime): Naive datetime (assumed Pacific Time).

    Returns:
        datetime: UTC-aware datetime.

    Raises:
        ValueError: If input is not naive.
    """
    if ca_naive_dt.tzinfo is not None:
        raise ValueError(f"Expected naive datetime, got {ca_naive_dt!r}")
    return ca_naive_dt.replace(tzinfo=PACIFIC_TZ).astimezone(UTC_TZ)

def utc_datetime_to_ca_naive_datetime(utc_dt: datetime, assume_naive_is_utc: bool = False, utc_strict: bool = True) -> datetime:
    """
    Convert a UTC-aware (or optionally naive) datetime to naive California local time.

    Args:
        utc_dt (datetime): The datetime to convert.
        assume_naive_is_utc (bool): If True, treat naive input as UTC.
        utc_strict (bool): If True, require input to be UTC.

    Returns:
        datetime: Naive California local datetime.

    Raises:
        ValueError: If input is naive and assume_naive_is_utc is False, or if UTC check fails.
    """
    dt = utc_dt
    if dt.tzinfo is None:
        if assume_naive_is_utc:
            logger.warning(f"Assuming UTC for naive datetime.")
            dt = dt.replace(tzinfo=UTC_TZ)
        else:
            raise ValueError("Naive datetime provided without assume_naive_is_utc=True")
    elif utc_strict and dt.tzinfo != UTC_TZ:
        raise ValueError("datetime must be UTC when utc_strict=True")
    return dt.astimezone(PACIFIC_TZ).replace(tzinfo=None)

def utc_datetime_to_iso_str(utc_dt: datetime) -> str:
    """
    Convert a timezone-aware datetime to a UTC ISO 8601 string.

    Args:
        utc_dt (datetime): Timezone-aware datetime.

    Returns:
        str: UTC ISO 8601 string.

    Raises:
        ValueError: If input is naive.
    """
    if utc_dt.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware")
    return utc_dt.astimezone(UTC_TZ).isoformat()

def utc_datetime_to_html_naive_str(utc_dt: datetime) -> str:
    """
    Convert a UTC-aware datetime to a naive California local string for HTML form display.

    Args:
        utc_dt (datetime): UTC-aware datetime.

    Returns:
        str: California local datetime string (e.g., "2025-01-15T14:30").

    Raises:
        ValueError: If input is naive or not UTC.
    """
    if utc_dt.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware")
    if utc_dt.tzinfo != UTC_TZ:
        raise ValueError("Datetime must be UTC")
    return utc_datetime_to_ca_naive_datetime(utc_dt, utc_strict=True).strftime("%Y-%m-%dT%H:%M")

def is_datetime_naive(dt: datetime) -> bool:
    """
    Return True if a datetime is naive (lacks timezone info).

    A datetime is considered naive if:
      - dt.tzinfo is None: No timezone information is attached.
      - OR dt.tzinfo.utcoffset(dt) is None: tzinfo is set, but it returns None for this datetime (per Python's datetime docs, this means the datetime is treated as naive).
    This covers both cases described in the Python datetime documentation.
    Args:
        dt (datetime): Datetime to check.
    Returns:
        bool: True if naive, False otherwise.
    """
    if dt is None:
        # None is not a datetime, so treat as not naive (or could raise error)
        return False
    if dt.tzinfo is None:
        # No timezone info attached: definitely naive
        return True
    if dt.tzinfo.utcoffset(dt) is None:
        # tzinfo is set, but utcoffset returns None: still considered naive
        return True
    # Otherwise, datetime is timezone-aware
    return False

def is_datetime_utc(dt: datetime) -> bool:
    """
    Return True if the datetime is timezone-aware and in UTC.

    This check uses dt.tzinfo.utcoffset(dt) == timedelta(0) because:
      - There are multiple ways a datetime can be marked as UTC (e.g., datetime.timezone.utc, zoneinfo.ZoneInfo("UTC"), pytz.UTC, custom tzinfo, etc.).
      - Comparing tzinfo objects directly (e.g., dt.tzinfo == timezone.utc) is not reliable across all libraries and implementations.
      - The UTC offset is always zero for UTC, regardless of the tzinfo class, so this test is robust and works for all compliant tzinfo implementations.
    Args:
        dt (datetime): Datetime to check.
    Returns:
        bool: True if dt is timezone-aware and in UTC, False otherwise.
    """
    if dt is None:
        return False
    if dt.tzinfo is None:
        return False
    # UTC offset must be zero for UTC, regardless of tzinfo implementation
    return dt.tzinfo.utcoffset(dt) == timedelta(0)

def excel_naive_datetime_to_utc_datetime(excel_dt: datetime) -> datetime:
    """
    Convert a naive Excel datetime (assumed California local) to a UTC-aware datetime.

    Args:
        excel_dt (datetime): Naive datetime from Excel.

    Returns:
        datetime: UTC-aware datetime.

    Raises:
        ValueError: If input is already timezone-aware.
    """
    if excel_dt.tzinfo is not None:
        raise ValueError("Excel datetime should be naive (no timezone)")
    return ca_naive_datetime_to_utc_datetime(excel_dt)

def utc_iso_str_to_ca_str(iso_str: str) -> str:
    """
    Convert a UTC ISO string to a California local time string for display.

    Args:
        iso_str (str): UTC ISO 8601 string.

    Returns:
        str: California local time string for display (e.g., "2025-01-15T14:30").
    """
    if not iso_str:
        return ""
    try:
        utc_dt = iso_str_to_utc_datetime(iso_str)
        return utc_datetime_to_html_naive_str(utc_dt)
    except Exception:
        return iso_str  # fallback: show as-is if parsing fails

# --- Bulk/Recursive Conversion Utilities ---

def bulk_utc_datetime_to_ca_naive_datetime(data: object, assume_naive_is_utc: bool = False, utc_strict: bool = True) -> object:
    """
    Recursively convert all UTC-aware datetimes in a nested structure to naive California local datetimes.

    Args:
        data (object): Structure containing datetimes (dict, list, etc.).
        assume_naive_is_utc (bool): Whether to treat naive datetimes as UTC.
        utc_strict (bool): Whether to enforce UTC input.

    Returns:
        object: Structure with all datetimes converted to naive California local.
    """
    if isinstance(data, datetime):
        return utc_datetime_to_ca_naive_datetime(data, assume_naive_is_utc, utc_strict)
    elif isinstance(data, Mapping):
        return {
            bulk_utc_datetime_to_ca_naive_datetime(k, assume_naive_is_utc, utc_strict):
                bulk_utc_datetime_to_ca_naive_datetime(v, assume_naive_is_utc, utc_strict)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [bulk_utc_datetime_to_ca_naive_datetime(i, assume_naive_is_utc, utc_strict) for i in data]
    elif isinstance(data, tuple):
        return tuple(bulk_utc_datetime_to_ca_naive_datetime(i, assume_naive_is_utc, utc_strict) for i in data)
    elif isinstance(data, set):
        return {bulk_utc_datetime_to_ca_naive_datetime(i, assume_naive_is_utc, utc_strict) for i in data}
    return data

def bulk_ca_naive_datetime_to_utc_datetime(data: object) -> object:
    """
    Recursively convert all naive California local datetimes in a nested structure to UTC-aware datetimes.

    Args:
        data (object): Structure containing datetimes (dict, list, etc.).

    Returns:
        object: Structure with all datetimes converted to UTC-aware datetimes.
    """
    if isinstance(data, datetime):
        return ca_naive_datetime_to_utc_datetime(data)
    elif isinstance(data, Mapping):
        return {bulk_ca_naive_datetime_to_utc_datetime(k): bulk_ca_naive_datetime_to_utc_datetime(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [bulk_ca_naive_datetime_to_utc_datetime(i) for i in data]
    elif isinstance(data, tuple):
        return tuple(bulk_ca_naive_datetime_to_utc_datetime(i) for i in data)
    elif isinstance(data, set):
        return {bulk_ca_naive_datetime_to_utc_datetime(i) for i in data}
    return data


if __name__ == "__main__":
  print("In main of date_and_time.py")
