"""
Date-times often work out of the box, by magic, but to standardize usage
across RSDAS, this file provides notes and guidance on how to use datetimes in
an unambiguous and uniform way.

Topic 1. Difference Between Naive and Timezone-Aware datetime Objects in Python
=======================================================================

Python's `datetime` objects come in two forms: **naive** and **timezone-aware**.

1. Naive datetime
-----------------
A naive datetime does not contain any timezone information. It represents
a timestamp without any reference to a specific location on Earth.

Example:
    >>> from datetime import datetime
    >>> naive_dt = datetime.now()
    >>> print(naive_dt.tzinfo)
    None

This makes the timestamp ambiguous — it could refer to local time, UTC,
or something else, depending on context.

2. Timezone-aware datetime
--------------------------
An aware datetime object includes explicit timezone information via its
`tzinfo` attribute. This allows Python to properly account for timezone
offsets, daylight saving time, and conversions between zones.

Example:
    >>> from datetime import datetime
    >>> from zoneinfo import ZoneInfo
    >>> aware_dt = datetime.now(ZoneInfo("America/Los_Angeles"))
    >>> print(aware_dt.tzinfo)
    America/Los_Angeles

With this context, the datetime becomes globally unambiguous.

Comparison and Arithmetic
-------------------------
Mixing naive and aware datetime objects in operations like comparisons
or subtraction will raise a `TypeError`, as Python cannot safely resolve
the ambiguity:

    >>> aware - naive
    TypeError: can't subtract offset-naive and offset-aware datetimes

Topic 2.  How `datetime.now()` Works in Python
====================================

`datetime.now()` returns the current local date and time based on the system clock
of the machine running the code.

By default, it returns a **naive** `datetime` object, meaning it includes the
date and time but **no timezone information** (`tzinfo` is `None`):

    >>> from datetime import datetime
    >>> dt = datetime.now()
    >>> print(dt)
    2025-04-20 14:00:00
    >>> print(dt.tzinfo)
    None

Timezone Awareness
------------------
Although the value is based on the computer’s configured local timezone,
the result is not timezone-aware unless explicitly specified.

To get a **timezone-aware** local time, use `datetime.now()` with a timezone:

    >>> from zoneinfo import ZoneInfo  # Python 3.9+
    >>> dt = datetime.now(ZoneInfo("America/Los_Angeles"))
    >>> print(dt)
    2025-04-20 14:00:00-07:00
    >>> print(dt.tzinfo)
    America/Los_Angeles

Summary of datetime now's characteristics

Function            | Timezone      | Aware/Naive
--------------------------------------------------
datetime.now()      | Local         | Naive
datetime.utcnow()   | UTC           | Naive
datetime.now(tz)    | Specified tz  | Aware

- `datetime.now()` returns the local system time.
- The result is naive by default (no `tzinfo`).
- Pass a timezone to `datetime.now(tz)` to get an aware datetime.

Topic 3. Best Practices
--------------
- Always prefer timezone-aware datetime objects for logging, APIs,
  scheduling, and cross-system operations.
- Use `datetime.now(tz)` or `datetime.fromisoformat(...).astimezone(tz)`
  for safe, localized time.
- Avoid naive datetimes unless you're 100% sure they won't cause ambiguity.

"""

import warnings
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import dateutil
import pytz
from dateutil import parser


def is_iso8601(string: str) -> bool:
  """Check if a string is a valid ISO 8601 datetime.

  This function uses `dateutil.parser.isoparse` to determine whether a given
  string is a valid ISO 8601 datetime. It returns `True` for valid ISO 8601 strings,
  and `False` otherwise.

  Args:
      string (str): The string to validate.

  Returns:
      bool: True if the string is a valid ISO 8601 datetime, False otherwise.

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


def iso8601_to_utc_dt(iso_string, error_on_missing_tz=True):
  """
  Parse an ISO 8601 string and return a timezone-aware datetime object in UTC.

  This function uses `dateutil.parser.isoparse()` for robust ISO 8601 parsing,
  including support for variations like 'Z' (UTC shorthand) and missing separators.

  Args:
      iso_string (str): An ISO 8601-formatted datetime string.
                        Examples:
                          - '2025-04-20T14:30:00+00:00'
                          - '2025-04-20T14:30:00Z'
                          - '2025-04-20 14:30:00'
      error_on_missing_tz (bool):
          If True, raises a ValueError when the string has no timezone info.
          If False, assumes the datetime is already in UTC and attaches UTC tzinfo.

  Returns:
      datetime: A timezone-aware datetime object in UTC.

  Raises:
      ValueError: If the input string is invalid or lacks timezone info and
                  `error_on_missing_tz` is True.
  """
  try:
    dt = parser.isoparse(iso_string)
  except (ValueError, TypeError) as e:
    raise ValueError(f"Invalid ISO 8601 datetime string: '{iso_string}'") from e

  if dt.tzinfo is None:
    if error_on_missing_tz:
      raise ValueError("The ISO 8601 string is missing timezone information.")

    print(f"ISO 8601 string `{iso_string}` is missing timezone info. Assuming it is UTC.")
    dt = dt.replace(tzinfo=ZoneInfo("UTC"))

  return dt.astimezone(ZoneInfo("UTC"))


from datetime import datetime
from zoneinfo import ZoneInfo


def to_pacific_time_str(dt: datetime) -> str:
  """Convert a timezone-aware datetime to Pacific Time and format it for use in an html datetime selector.

  This function converts a timezone-aware datetime object to the
  America/Los_Angeles timezone (Pacific Time), and returns it as a string
  formatted as "%Y-%m-%dT%H:%M".

  Args:
      dt (datetime): A timezone-aware datetime object.

  Returns:
      str: The datetime converted to Pacific Time, formatted as "YYYY-MM-DDTHH:MM".

  Raises:
      ValueError: If the input datetime is naive (missing timezone info).

  Examples:
      >>> from datetime import datetime, timezone
      >>> from zoneinfo import ZoneInfo
      >>> dt = datetime(2025, 4, 22, 18, 30, tzinfo=timezone.utc)
      >>> to_pacific_time_str(dt)
      '2025-04-22T11:30'

      >>> dt = datetime(2025, 7, 1, 18, 30, tzinfo=timezone.utc)
      >>> to_pacific_time_str(dt)
      '2025-07-01T11:30'  # Pacific Daylight Time (PDT) is UTC-7

      >>> naive_dt = datetime(2025, 4, 22, 18, 30)
      >>> to_pacific_time_str(naive_dt)
      Traceback (most recent call last):
          ...
      ValueError: Input datetime must be timezone-aware.
  """
  if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
    raise ValueError("Input datetime must be timezone-aware.")

  pacific = dt.astimezone(ZoneInfo("America/Los_Angeles"))
  return pacific.strftime("%Y-%m-%dT%H:%M")


def example_usage_01():
  """
  Examples usage and results of common datetime operations.
  """
  # get a datetime using now without specifying the timezone
  now_no_tz = datetime.now()
  dt_timezone = now_no_tz.tzinfo
  print("datetime.now() results if the timezone is not specified")
  print("Datetime:", now_no_tz)
  print("Timezone:", dt_timezone)

  # Get current time in UTC
  print("\ndatetime.now() results if the timezone is not specified as utc or LA,CA")
  now_utc = datetime.now(timezone.utc)
  now_la = datetime.now(ZoneInfo("America/Los_Angeles"))

  print(f"LA is currently 7 hours behind zulu.")
  print(f"{now_no_tz = }")
  print(f"{now_utc = }")
  print(f"{now_la  = }")

  # Format as ISO 8601 string
  now_no_tz_iso_string = now_no_tz.isoformat()
  utc_iso_string = now_utc.isoformat()
  la_iso_string = now_la.isoformat()

  print(f"\nISO 8601 format of both LA and UTC")
  print(f"Datetime now_no_tz   in UTC as a ISO 8601 string: {now_no_tz_iso_string}")
  print(f"Datetime now_utc     in UTC as a ISO 8601 string: {utc_iso_string}")
  print(f"Datetime la_string   in UTC as a ISO 8601 string: {la_iso_string}")

  # Format using strftime
  no_tz_formatted_string = now_no_tz.strftime("%Y-%m-%dT%H:%M:%S")
  utc_formatted_string = now_utc.strftime("%Y-%m-%dT%H:%M:%S")
  la_formatted_string = now_la.strftime("%Y-%m-%dT%H:%M:%S")

  print(f"\nUsing strftime to create a string from a datetime object results in different strings.")
  print(f"Datetime now_no_tz   as a strftime string: {no_tz_formatted_string}")
  print(f"Datetime now_utc     as a strftime string: {utc_formatted_string}")
  print(f"Datetime la_string   as a strftime string: {la_formatted_string}")

  string_time = "2025-04-20T10:30:00-07:00"
  dt = iso8601_to_utc_dt(string_time)
  print(f"\nstring_time    : {string_time}")
  print(f"strftime string: {now_no_tz.strftime('%Y-%m-%dT%H:%M:%S')}")
  print(f"{dt =}, { dt.tzinfo=}")

  # Get current time in UTC
  print("\nNaive (tzinfo=None) and various tzinfo datetime objects")
  date_time_1 = datetime.now()
  print(f"{date_time_1!r}")
  date_time_2 = datetime.now(timezone.utc)  # from datetime lib
  print(f"{date_time_2!r}")
  date_time_3 = datetime.now(ZoneInfo("UTC"))
  print(f"{date_time_3!r}")
  date_time_4 = datetime.now(pytz.UTC)
  print(f"{date_time_4!r}")
  date_time_5 = datetime.now(dateutil.tz.UTC)
  print(f"{date_time_5!r}")


def utc_to_pacific_naive(dt: datetime) -> datetime:
  """
  Convert a UTC-aware datetime to a naive datetime in Pacific Time.

  Args:
      dt (datetime): A timezone-aware datetime in UTC.

  Returns:
      datetime: A naive datetime object in Pacific time.

  Raises:
      ValueError: If input datetime is not timezone-aware or not in UTC.

  Example:
      >>> dt_utc = datetime(2025, 7, 1, 17, 0, tzinfo=ZoneInfo("UTC"))
      >>> utc_to_pacific_naive(dt_utc)
      datetime.datetime(2025, 7, 1, 10, 0)
  """
  if dt.tzinfo is None:
    raise ValueError("Input datetime must be timezone-aware.")
  if dt.tzinfo != ZoneInfo("UTC"):
    raise ValueError("Input datetime must be in UTC.")

  pacific_dt = dt.astimezone(ZoneInfo("America/Los_Angeles"))
  return pacific_dt.replace(tzinfo=None)


def pacific_naive_to_utc(dt: datetime) -> datetime:
  """
  Convert a naive datetime (assumed to be in Pacific Time) to a timezone-aware UTC datetime.

  Args:
      dt (datetime): A naive datetime that should be interpreted as Pacific Time.

  Returns:
      datetime: A UTC timezone-aware datetime.

  Raises:
      ValueError: If the input datetime is already timezone-aware.

  Example:
      >>> naive_local = datetime(2025, 7, 1, 10, 0)
      >>> pacific_naive_to_utc(naive_local)
      datetime.datetime(2025, 7, 1, 17, 0, tzinfo=ZoneInfo('UTC'))
  """
  if dt.tzinfo is not None:
    raise ValueError("Input datetime must be naive (no timezone info).")

  pacific_aware = dt.replace(tzinfo=ZoneInfo("America/Los_Angeles"))
  return pacific_aware.astimezone(ZoneInfo("UTC"))


def normalize_to_zoneinfo(dt: datetime) -> datetime:
  """
  Normalizes any timezone-aware datetime to use Python's built-in zoneinfo.ZoneInfo tzinfo.
  Naive datetimes are returned unchanged.

  This function is intended to ensure **consistent use of the ZoneInfo system**
  throughout your codebase, avoiding interoperability issues and subtle bugs
  caused by mixing tzinfo types like pytz or dateutil with ZoneInfo.

  Why normalize to ZoneInfo?
  --------------------------
  - Python 3.9+ includes zoneinfo as the modern and standard timezone library.
  - Mixing tzinfo implementations (e.g., pytz, dateutil, ZoneInfo) can lead to:
      * Inaccurate conversions around daylight saving time
      * Unexpected behavior when calling astimezone()
      * Errors due to pytz’s requirement for manual localization via localize()/normalize()

  Handling:
  ---------
  - If `dt` is naive (tzinfo is None), it's returned unchanged.
  - If already using zoneinfo, it's returned unchanged.
  - Otherwise, it attempts to find an equivalent zoneinfo ZoneInfo object by tzname.
  - If no match is found, it safely converts to the equivalent ZoneInfo object via UTC.

  Args:
      dt: A datetime object (naive or timezone-aware).

  Returns:
      A datetime with zoneinfo-based tzinfo (or unchanged if naive).

  Example:
      >>> import pytz
      >>> dt = pytz.timezone("US/Pacific").localize(datetime(2025, 4, 23, 15, 0))
      >>> normalize_to_zoneinfo(dt)
      datetime.datetime(2025, 4, 23, 15, 0, tzinfo=zoneinfo.ZoneInfo(key='America/Los_Angeles'))
  """
  if dt.tzinfo is None:
    # Naive datetime — we don't modify it; let the caller decide how to handle it
    return dt

  if isinstance(dt.tzinfo, ZoneInfo):
    # Already a ZoneInfo-based datetime — return as-is
    return dt

  # --- MIXED TZINFO HANDLING ---
  # Attempt to match the timezone by name (tzname might be 'UTC', 'EST', etc.)
  offset = dt.utcoffset()
  tzname = dt.tzname()

  try:
    zoneinfo_guess = ZoneInfo(tzname)
    # Validate that the offset also matches to ensure correctness
    if dt.astimezone(zoneinfo_guess).utcoffset() == offset:
      return dt.astimezone(zoneinfo_guess)
  except Exception:
    pass

  # If all else fails, round-trip through UTC to retain the exact instant
  # and convert to a ZoneInfo timezone with the same tzname (if valid)
  return dt.astimezone(ZoneInfo("UTC")).astimezone(ZoneInfo("UTC" if tzname == "UTC" else tzname))


# def ca_naive_to_utc_string(dt: datetime,
#                            strftime: str = "%Y-%m-%dT%H:%M") -> str:
#   """
#   Converts a naive datetime assumed to be in America/Los_Angeles time
#   to an equivalent UTC string.
#
#   Args:
#       dt: A datetime object.
#       strftime: a formatting string.
#
#   Returns:
#       A UTC string formatted by strftime.
#
#   Raises:
#       ValueError: If the datetime is already timezone-aware.
#   """
#   # .isoformat()
#   if dt.tzinfo is None:
#     return dt.replace(tzinfo=PACIFIC_TZ).astimezone(UTC_TZ)
#   else:
#     raise ValueError(f"Datetime already has timezone: {dt=}")


if __name__ == '__main__':
  example_usage_01()
