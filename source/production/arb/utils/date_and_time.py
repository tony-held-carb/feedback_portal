"""
Datetime parsing and timezone utilities for ISO 8601, UTC/Pacific conversion,
repr-format recovery, and recursive datetime transformation in nested structures.

Features:
- ISO 8601 validation and parsing (via `dateutil`)
- Conversion between UTC and naive Pacific time (Los Angeles)
- Safe handling of repr-formatted datetime strings (e.g., "datetime.datetime(...)")
- Recursive datetime transformations within nested dicts/lists/sets/tuples

Timezone policy:
- `UTC_TZ` and `PACIFIC_TZ` are globally defined using `zoneinfo.ZoneInfo`
- Naive timestamps are only assumed to be UTC if explicitly configured via arguments
"""
import re
import logging
from collections.abc import Mapping
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from dateutil import parser
__version__ = "1.0.0"
logger = logging.getLogger(__name__)

UTC_TZ = ZoneInfo("UTC")
PACIFIC_TZ = ZoneInfo("America/Los_Angeles")


def str_to_datetime(datetime_str: str) -> datetime | None:
  """
  Convert a `repr()`-formatted string into a datetime object.

  Args:
      datetime_str (str): Example: "datetime.datetime(2024, 11, 15, 14, 30, 45)"

  Returns:
      datetime | None: Parsed datetime object if matched; otherwise, None.

  Notes:
      This reverses `repr(datetime)` stringification for debugging recovery.
  """
  match = re.search(r"datetime\.datetime\(([^)]+)\)", datetime_str)
  if match:
    date_parts = list(map(int, match.group(1).split(", ")))
    return datetime(*date_parts)
  return None


def date_to_string(dt: datetime | None, str_format: str = "%Y-%m-%dT%H:%M") -> str | None:
  """
  Convert a datetime object to a formatted string.

  Args:
      dt (datetime | None): A datetime object or None.
      str_format (str): Format string used with `strftime`.

  Returns:
      str | None: The formatted string if input is not None; otherwise, None.

  Raises:
      TypeError: If `x` is not a datetime object.
  """

  if dt is None:
    return None
  if not isinstance(dt, datetime):
    raise TypeError(f'x must be datetime.datetime or None. {dt=}')
  return dt.strftime(str_format)


def repr_datetime_to_string(datetime_string: str | None) -> str | None:
  """
  Convert a repr-formatted datetime string into an ISO 8601 string.

  Args:
      datetime_string (str | None): A string in the format "datetime.datetime(...)"

  Returns:
      str | None: ISO 8601 string or None if parsing fails or input is None.
  """
  if datetime_string is None:
    return None
  dt = str_to_datetime(datetime_string)
  return dt.isoformat() if dt else None


def is_iso8601(string: str) -> bool:
  """
  Determine whether a string is a valid ISO 8601 datetime.

  Args:
      string (str): The string to validate.

  Returns:
      bool: True if the string conforms to ISO 8601 datetime format, False otherwise.

  Notes:
      - Uses `dateutil.parser.isoparse` for strict ISO 8601 parsing.
      - ISO 8601 requires a full date (YYYY-MM-DD) at minimum. Time-only strings are invalid.
      - This does not validate durations, ordinal dates, or week dates.

  Examples:
      Valid cases (returns True):
          - "2024-12-31"
          - "2024-12-31T23:59:59"
          - "2024-12-31T23:59:59Z"             # UTC/Zulu time
          - "2024-12-31T23:59:59+00:00"        # Timezone offset
          - "2024-12-31T23:59:59.123456"       # Microsecond precision
          - "2024-12-31T23:59:59.123+02:00"    # Fractional seconds with TZ

      Invalid cases (returns False):
          - "12/31/2024"            # US-style date format
          - "2024-31-12"            # Invalid format (day and month swapped)
          - "2024"                  # Year only, not a complete date or datetime
          - "P1Y2M"                 # ISO 8601 duration, not a datetime
          - "Just some text"        # Clearly not a date
          - "2024-12-31 23:59:59"   # Space instead of 'T' (technically invalid ISO 8601)

          # Time-only values — invalid because ISO 8601 requires at least a full date
          - "23:59"                 # Just time (no date)
          - "23:59:59"              # Time only, still invalid
          - "T23:59:59Z"            # Prefixed with 'T' but still no date
          - "23:59:59+00:00"        # Time with timezone, but missing a date
          - "T23:59:59.123456"      # Microsecond time, still not valid without date

  Notes:
      - ISO 8601 datetimes require at least a full date (YYYY-MM-DD). Time-only strings are not valid by themselves.
      - This does not validate ISO 8601 durations, ordinal dates, or week dates.
      - This routine strictly uses `dateutil.parser.isoparse`, which rejects incomplete formats like time-only values.
  """
  try:
    parser.isoparse(string)
    return True
  except ValueError:
    return False


def iso8601_to_utc_dt(iso_string: str, error_on_missing_tz: bool = True) -> datetime:
  """
  Parse an ISO 8601 string and return a timezone-aware datetime object in UTC.

  This function uses `dateutil.parser.isoparse()` for robust ISO 8601 parsing,
  including support for variations like 'Z' (UTC shorthand) and missing separators.

  Args:
      iso_string: An ISO 8601-formatted datetime string.
      error_on_missing_tz: If True, raises a ValueError when the string has no timezone info.

  Returns:
      A timezone-aware datetime object in UTC.

  Raises:
      ValueError: If the input string is invalid or lacks timezone info and
                  `error_on_missing_tz` is True.

  Examples:
      Input : "2025-04-20T14:30:00+00:00"
      Output: datetime.datetime(2025, 4, 20, 14, 30, tzinfo=ZoneInfo("UTC"))

      Input : "2025-04-20T14:30:00Z"
      Output: datetime.datetime(2025, 4, 20, 14, 30, tzinfo=ZoneInfo("UTC"))

      Input : "2025-04-20 14:30:00", error_on_missing_tz=False
      Output: datetime.datetime(2025, 4, 20, 14, 30, tzinfo=ZoneInfo("UTC"))
  """
  try:
    dt = parser.isoparse(iso_string)
  except (ValueError, TypeError) as e:
    raise ValueError(f"Invalid ISO 8601 datetime string: '{iso_string}'") from e

  if dt.tzinfo is None:
    if error_on_missing_tz:
      raise ValueError("Missing timezone info in ISO 8601 string.")
    logger.warning(f"Assuming UTC for naive ISO string: {iso_string}")
    dt = dt.replace(tzinfo=UTC_TZ)

  return dt.astimezone(UTC_TZ)


def datetime_to_ca_naive(dt: datetime,
                         assume_naive_is_utc: bool = False,
                         utc_strict: bool = True) -> datetime:
  """
  Convert a datetime (UTC or naive) to naive Pacific Time.

  Args:
      dt (datetime): The datetime to convert.
      assume_naive_is_utc (bool): If True, interpret naive datetime as UTC.
      utc_strict (bool): If True, raise an error unless datetime is explicitly UTC.

  Returns:
      datetime: A naive Pacific Time datetime.

  Raises:
      ValueError: If datetime is naive and `assume_naive_is_utc` is False,
                  or if UTC check fails under `utc_strict`.
  """
  if dt.tzinfo is None:
    if assume_naive_is_utc:
      logger.warning(f"Assuming UTC for naive datetime.")
      dt = dt.replace(tzinfo=UTC_TZ)
    else:
      raise ValueError("Naive datetime provided without assume_naive_is_utc=True")
  elif utc_strict and dt.tzinfo != UTC_TZ:
    raise ValueError("datetime must be UTC when utc_strict=True")

  return dt.astimezone(PACIFIC_TZ).replace(tzinfo=None)


def ca_naive_to_utc_datetime(dt: datetime) -> datetime:
  """
  Convert a naive Pacific Time datetime to a UTC-aware datetime.

  Args:
      dt (datetime): A naive datetime.

  Returns:
      datetime: A UTC-aware datetime.

  Raises:
      ValueError: If the input is not naive (i.e., has timezone info).
  """
  if dt.tzinfo is not None:
    raise ValueError(f"Expected naive datetime, got {dt!r}")
  return dt.replace(tzinfo=PACIFIC_TZ).astimezone(UTC_TZ)


def convert_datetimes_to_ca_naive(data: object, assume_naive_is_utc: bool = False, utc_strict: bool = True) -> object:
  """
  Recursively convert all datetime objects in a nested structure to naive Pacific Time.

  Args:
      data (object): A structure that may include datetime values (dict, list, etc.).
      assume_naive_is_utc (bool): Whether to treat naive datetimes as UTC.
      utc_strict (bool): Whether to enforce that input datetimes be explicitly UTC.

  Returns:
      object: A structure of the same shape, with datetime values converted to naive Pacific.

  Examples:
      Input :
        {
          datetime(2025, 4, 23, 15, 0, tzinfo=ZoneInfo("UTC")): [
            {"created": datetime(2025, 4, 23, 18, 0)},
            (datetime(2025, 4, 23, 20, 0, tzinfo=ZoneInfo("UTC")),)
          ]
        }

      Output:
        {
          datetime.datetime(2025, 4, 23, 8, 0): [
            {"created": datetime.datetime(2025, 4, 23, 11, 0)},
            (datetime.datetime(2025, 4, 23, 13, 0),)
          ]
        }
  """
  if isinstance(data, datetime):
    return datetime_to_ca_naive(data, assume_naive_is_utc, utc_strict)
  elif isinstance(data, Mapping):
    return {
      convert_datetimes_to_ca_naive(k, assume_naive_is_utc, utc_strict):
        convert_datetimes_to_ca_naive(v, assume_naive_is_utc, utc_strict)
      for k, v in data.items()
    }
  elif isinstance(data, list):
    return [convert_datetimes_to_ca_naive(i, assume_naive_is_utc, utc_strict) for i in data]
  elif isinstance(data, tuple):
    return tuple(convert_datetimes_to_ca_naive(i, assume_naive_is_utc, utc_strict) for i in data)
  elif isinstance(data, set):
    return {convert_datetimes_to_ca_naive(i, assume_naive_is_utc, utc_strict) for i in data}
  return data


def convert_ca_naive_datetimes_to_utc(data: object) -> object:
  """
  Recursively convert all naive Pacific Time datetimes in a nested structure to UTC-aware datetimes.

  Args:
      data (object): A nested structure (e.g., dict, list, tuple).

  Returns:
      object: The same structure with datetime values converted to UTC-aware format.
  """
  if isinstance(data, datetime):
    return ca_naive_to_utc_datetime(data)
  elif isinstance(data, Mapping):
    return {convert_ca_naive_datetimes_to_utc(k): convert_ca_naive_datetimes_to_utc(v) for k, v in data.items()}
  elif isinstance(data, list):
    return [convert_ca_naive_datetimes_to_utc(i) for i in data]
  elif isinstance(data, tuple):
    return tuple(convert_ca_naive_datetimes_to_utc(i) for i in data)
  elif isinstance(data, set):
    return {convert_ca_naive_datetimes_to_utc(i) for i in data}
  return data


def parse_unknown_datetime(date_str: str) -> datetime | None:
  """
  Attempt to parse an arbitrary string into a datetime using `dateutil.parser.parse()`.

  Args:
      date_str (str): A date or datetime string in an unknown format.

  Returns:
      datetime | None: Parsed datetime object if successful; otherwise, None.

  Raises:
      None: Gracefully handles errors internally.

  Notes:
      - This method is lenient and accepts a wide range of human-readable formats.
      - Returns None if the string is empty, not a string, or unparseable.
  """

  if not isinstance(date_str, str) or not date_str:
    return None
  try:
    return parser.parse(date_str)
  except (ValueError, TypeError):
    return None


def is_datetime_naive(dt: datetime) -> bool:
  """
  Check whether a datetime object is naive (lacks timezone info).

  Args:
      dt (datetime): A datetime instance.

  Returns:
      bool: True if the datetime is naive (tzinfo is None or utcoffset is None); False otherwise.

  Examples:
      Input : datetime.now()
      Output: True

      Input : datetime.now(tz=ZoneInfo("UTC"))
      Output: False
  """
  return dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None


def normalize_value(val: Any) -> str:
  """
  Normalize a value for string-based diffing or comparison.

  Args:
    val (Any): The input value to normalize.

  Returns:
    str: Normalized value as a string, suitable for comparisons and display.

  Notes:
    - None and empty strings ("") are treated identically, returning "".
      This ensures fields that were previously None but now filled with an empty string
      (or vice versa) are not falsely flagged as changed.
    - Naive datetime values are assumed to be in California time and converted to UTC.
    - All other types are stringified using `str(val)`.

  Example:
    normalize_value(None)                → ""
    normalize_value("")                  → ""
    normalize_value(datetime(...))      → "2025-06-17T15:30:00+00:00"
    normalize_value(42)                 → "42"
  """
  if val is None or val == "":
    return ""
  if isinstance(val, datetime):
    if is_datetime_naive(val):
      val = ca_naive_to_utc_datetime(val)
    return val.isoformat()
  return str(val)


def run_diagnostics() -> None:
  """
  Run a series of diagnostic operations to verify the correctness of datetime utilities.

  Demonstrates:
      - ISO 8601 parsing to UTC
      - Conversion to naive Pacific time
      - Round-trip UTC conversion
      - Recursive conversion in nested data structures

  Returns:
      None
  """
  from pprint import pprint
  print("Running diagnostics on datetime utilities...\n")

  sample_iso = "2025-05-05T10:00:00Z"
  dt = iso8601_to_utc_dt(sample_iso)
  print("Parsed ISO 8601 to UTC:", dt)

  naive_pacific = datetime_to_ca_naive(dt)
  print("Converted to naive Pacific:", naive_pacific)

  round_trip = ca_naive_to_utc_datetime(naive_pacific)
  print("Round-trip back to UTC:", round_trip)

  nested_data = {
    dt: [
      {"created": dt},
      (dt,)
    ]
  }

  pacific_data = convert_datetimes_to_ca_naive(nested_data)
  print("\nConverted nested UTC datetimes to Pacific:")
  pprint(pacific_data)

  restored = convert_ca_naive_datetimes_to_utc(pacific_data)
  print("\nRestored nested Pacific datetimes to UTC:")
  pprint(restored)


if __name__ == "__main__":
  run_diagnostics()
