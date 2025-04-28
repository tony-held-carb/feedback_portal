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

from dateutil import parser


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


def iso8601_to_CA(iso_string: str, error_on_missing_tz: bool = True) -> datetime:
  """
  Parse an ISO 8601 string and convert it to a timezone-aware datetime
  object in California Pacific Time (America/Los_Angeles). Automatically
  handles Daylight Saving Time transitions.

  Args:
      iso_string (str): An ISO 8601-formatted datetime string.
                        Example: '2025-04-20T14:30:00+00:00'
      error_on_missing_tz (bool): If True, raises a ValueError when the input
                                  datetime string does not include timezone info.
                                  If False, assumes the input is in UTC and logs
                                  a warning.

  Returns:
      datetime: A timezone-aware datetime object in US/Pacific time.

  Raises:
      ValueError: If the input string has no timezone info and
                  error_on_missing_tz is True.
  """
  dt = datetime.fromisoformat(iso_string)

  if dt.tzinfo is None:
    if error_on_missing_tz:
      raise ValueError("The ISO string is missing timezone information.")
    else:
      warnings.warn(
        "ISO 8601 string is missing timezone info. Assuming UTC.",
        stacklevel=2
      )
      dt = dt.replace(tzinfo=ZoneInfo("UTC"))

  pacific_dt = dt.astimezone(ZoneInfo("America/Los_Angeles"))
  return pacific_dt


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

  dt = iso8601_to_CA("2025-04-20T10:30:00-07:00")
  print(dt)
  print(dt.tzinfo)

  dt = iso8601_to_utc_dt("2025-04-20T10:30:00-07:00")
  print(dt)
  print(dt.tzinfo)


if __name__ == '__main__':
  example_usage_01()
