"""
Datetime parsing and timezone utilities for ISO 8601, UTC/Pacific conversion,
repr-format recovery, and recursive datetime transformation in nested structures.

Supports:
- ISO 8601 validation and parsing
- `repr(datetime)` string recovery
- UTC ⇆ Pacific conversions with configurable behavior
- Recursive conversion across nested data structures
"""

import re
from collections.abc import Mapping
from datetime import datetime
from zoneinfo import ZoneInfo

from dateutil import parser

from arb.__get_logger import get_logger

__version__ = "1.0.0"
logger, pp_log = get_logger(__name__, log_to_console=__file__)

UTC_TZ = ZoneInfo("UTC")
PACIFIC_TZ = ZoneInfo("America/Los_Angeles")


def str_to_datetime(datetime_str: str) -> datetime | None:
  """
  Convert a string in repr-style format into a datetime object.

  Args:
      datetime_str (str): Example: "datetime.datetime(2024, 11, 15, 14, 30, 45)"

  Returns:
      datetime | None: Parsed datetime, or None if the pattern doesn't match.

  Notes:
      This is useful for reversing repr()-based serialization of datetime objects.
  """
  match = re.search(r"datetime\.datetime\(([^)]+)\)", datetime_str)
  if match:
    date_parts = list(map(int, match.group(1).split(", ")))
    return datetime(*date_parts)
  return None


def date_to_string(x: datetime, str_format: str = "%Y-%m-%dT%H:%M") -> str | None:
  """
  Convert a datetime object to a string, using the specified format.

  Args:
      x (datetime | None): A datetime object or None.
      str_format (str): Format string passed to strftime.

  Returns:
      str | None: Formatted string or None.
  """
  if x is None:
    return None
  if not isinstance(x, datetime):
    raise TypeError(f'x must be datetime.datetime or None. {x=}')
  return x.strftime(str_format)


def repr_datetime_to_string(datetime_string: str) -> str | None:
  """
  Convert a string created with repr(datetime) into ISO-style formatted string.

  Args:
      datetime_string (str | None): repr-formatted datetime string.

  Returns:
      str | None: ISO-style string or None.
  """
  if datetime_string is None:
    return None
  dt = str_to_datetime(datetime_string)
  return dt.isoformat() if dt else None


def is_iso8601(string: str) -> bool:
  """
  Check if a string is a valid ISO 8601 datetime.

  Args:
      string: The string to validate.

  Returns:
      True if the string is a valid ISO 8601 datetime, False otherwise.

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
      >>> iso8601_to_utc_dt("2025-04-20T14:30:00+00:00")
      datetime.datetime(2025, 4, 20, 14, 30, tzinfo=zoneinfo.ZoneInfo("UTC"))

      >>> iso8601_to_utc_dt("2025-04-20T14:30:00Z")
      datetime.datetime(2025, 4, 20, 14, 30, tzinfo=zoneinfo.ZoneInfo("UTC"))

      >>> iso8601_to_utc_dt("2025-04-20 14:30:00", error_on_missing_tz=False)
      datetime.datetime(2025, 4, 20, 14, 30, tzinfo=zoneinfo.ZoneInfo("UTC"))
      >>> iso8601_to_utc_dt("2025-04-20T14:30:00Z")
      datetime.datetime(2025, 4, 20, 14, 30, tzinfo=zoneinfo.ZoneInfo('UTC'))
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


def datetime_to_ca_naive(dt: datetime, assume_naive_is_utc: bool = False, utc_strict: bool = True) -> datetime:
  """
  Converts a datetime to a naive datetime in the America/Los_Angeles timezone.

  Args:
      dt: A datetime object. Can be naive or timezone-aware using ZoneInfo.
      assume_naive_is_utc: If True, and dt is naive, it will be assumed to be UTC.
      utc_strict: If True, raises an error if dt is not explicitly in ZoneInfo(UTC).

  Returns:
      A naive datetime in Pacific Time with tzinfo=None.

  Examples:
      >>> dt = datetime(2025, 5, 5, 12, 0, tzinfo=ZoneInfo("UTC"))
      >>> datetime_to_ca_naive(dt)
      datetime.datetime(2025, 5, 5, 5, 0)

      >>> dt = datetime(2025, 5, 5, 12, 0)
      >>> datetime_to_ca_naive(dt, assume_naive_is_utc=True)
      datetime.datetime(2025, 5, 5, 5, 0)
  """
  if dt.tzinfo is None:
    if assume_naive_is_utc:
      logger.warning("Assuming UTC for naive datetime.")
      dt = dt.replace(tzinfo=UTC_TZ)
    else:
      raise ValueError("Naive datetime provided without assume_naive_is_utc=True")
  elif utc_strict and dt.tzinfo != UTC_TZ:
    raise ValueError("datetime must be UTC when utc_strict=True")

  return dt.astimezone(PACIFIC_TZ).replace(tzinfo=None)


def ca_naive_to_utc_datetime(dt: datetime) -> datetime:
  """
  Convert naive Pacific datetime to UTC-aware datetime.

  Args:
      dt: Naive datetime.

  Returns:
      UTC-aware datetime.

  Raises:
      ValueError: If datetime is already timezone-aware.
  """
  if dt.tzinfo is not None:
    raise ValueError(f"Expected naive datetime, got {dt!r}")
  return dt.replace(tzinfo=PACIFIC_TZ).astimezone(UTC_TZ)


def convert_datetimes_to_ca_naive(data: object, assume_naive_is_utc: bool = False, utc_strict: bool = True) -> object:
  """
  Recursively converts all datetime objects found anywhere in a nested data structure
  (including dict keys, values, list elements, etc.) to naive Pacific Time.

  Args:
      data: A nested structure (dict, list, tuple, set, etc.) possibly containing datetimes.
      assume_naive_is_utc: If True, and dt is naive, it is assumed to already be UTC.
      utc_strict: If True, raises an error if dt is not explicitly in UTC.

  Returns:
      A new structure with all datetime objects converted to naive Pacific Time.

  Examples:
      >>> from datetime import datetime
      >>> from zoneinfo import ZoneInfo
      >>> nested = {
      ...     datetime(2025, 4, 23, 15, 0, tzinfo=ZoneInfo("UTC")): [
      ...         {"created": datetime(2025, 4, 23, 18, 0)},
      ...         (datetime(2025, 4, 23, 20, 0, tzinfo=ZoneInfo("UTC")),)
      ...     ]
      >>> convert_datetimes_to_ca_naive(nested)
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
  Recursively convert naive Pacific datetime objects to UTC-aware ones.

  Args:
      data: Arbitrary nested structure.

  Returns:
      Data with UTC datetimes.
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
  Try parsing any string into a datetime using dateutil.

  Args:
      date_str: Input date/time string.

  Returns:
      Parsed datetime or None.

  Examples:
      >>> parse_unknown_datetime("2025-04-28T16:23:00Z")
      datetime.datetime(2025, 4, 28, 16, 23, tzinfo=tzutc())
  """
  if not isinstance(date_str, str) or not date_str:
    return None
  try:
    return parser.parse(date_str)
  except (ValueError, TypeError):
    return None


def run_diagnostics():
  """
  Run basic diagnostics on datetime utilities for correctness.
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
