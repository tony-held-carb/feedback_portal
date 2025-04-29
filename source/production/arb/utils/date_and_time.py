import re
from collections.abc import Mapping
from datetime import datetime
from zoneinfo import ZoneInfo

from arb.__get_logger import get_logger

__version__ = "1.0.0"
logger, pp_log = get_logger(__name__, __file__)

UTC_TZ = ZoneInfo("UTC")
PACIFIC_TZ = ZoneInfo("America/Los_Angeles")


def str_to_datetime(datetime_str):
  """
  Convert a string to a datetime object, if possible.

  String should be in format (not all numbers required) of:
    datetime.datetime(2024, 11, 15, 14, 30, 45)

  Args:
    datetime_str (str): The string to convert to a datetime object

  Returns (None|datetime): A datetime object.

  Notes:
    - An example string produced by repr
        datetime_str = "datetime.datetime(2024, 11, 15, 14, 30, 45)"
  """
  # Extract the numbers using regex
  match = re.search(r"datetime\.datetime\(([\d, ]+)\)", datetime_str)
  if match:
    date_parts = map(int, match.group(1).split(", "))
    dt = datetime(*date_parts)
    # print(dt)  # Output: 2024-11-15 14:30:45
    return dt


def date_to_string(x, str_format="%Y-%m-%dT%H:%M"):
  """
  Convert a datetime.datetime object to a string if necessary.
  If x is None, None will be returned.

  Args:
    x (datetime.datetime|None): variable that may be a datetime.datetime object
    str_format (str): datetime format string

  Returns:
    y (str|None): datetime formatted string

  """
  if x is None:
    y = None
  elif isinstance(x, datetime):
    y = x.strftime(str_format)
  else:
    raise TypeError(f'x must be datetime.datetime or None. {x=}')
  # logger.debug(f"\n\t{x=}")
  # logger.debug(f"{x=}, {y=}")
  return y


def repr_datetime_to_string(datetime_string):
  """
  Convert a string created with repr of a datetime.datetime into a formated string.

  Args:
   datetime_string (str|None): string created with repr of a datetime.datetime object

  Returns:
    y (str|None): datetime formatted string

  """
  if datetime_string is None:
    y = None
  elif isinstance(datetime_string, str):
    pass
    y = str_to_datetime(datetime_string)
  else:
    raise TypeError(f'datetime_string must be a string or None {datetime_string=}, {type(datetime_string)=}')
  # logger.debug(f"\n\t{x=}")
  # logger.debug(f"{x=}, {y=}")
  return y


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


def datetime_to_ca_naive(dt: datetime,
                         assume_naive_is_utc: bool = False,
                         utc_strict: bool = True) -> datetime:
  """
  Converts a datetime to a naive datetime in the America/Los_Angeles timezone.

  Args:
      dt: A datetime object.  Can be naive or timezone-aware using ZoneInfo.
      assume_naive_is_utc: If True, and dt is naive, a warning will be logged and
        the naive datetime will be assumed to already be UTC (NOT PACIFIC).
        If False and dt is naive, an error will be raised.
      utc_strict: If True, raises an error if dt is not explicitly in ZoneInfo(UTC).
        Note if assume_naive_is_utc is True, naive datetime will not be affected by this flag.

  Returns:
      A naive datetime in Pacific Time with tzinfo=None.
  """
  if dt.tzinfo is None:
    if assume_naive_is_utc:
      logger.warning(f"datetime_to_ca_naive called with a naive datetime.  "
                     f"Assuming timezone is already UTC for {dt=}")
      dt = dt.replace(tzinfo=UTC_TZ)
    else:
      raise ValueError(f"datetime must be timezone-aware, or set assume_naive_is_utc=True.  {dt=}")

  if utc_strict and dt.tzinfo != UTC_TZ:
    raise ValueError("datetime tzinfo must be ZoneInfo UTC when utc_strict=True")

  dt_pacific = dt.astimezone(PACIFIC_TZ)
  return dt_pacific.replace(tzinfo=None)


def ca_naive_to_utc_datetime(dt: datetime) -> datetime:
  """
  Converts a naive datetime assumed to be in America/Los_Angeles time
  to a timezone-aware ZoneInfo UTC datetime. Raises error if already timezone-aware.

  Args:
      dt: A datetime object.

  Returns:
      A timezone-aware UTC datetime.

  Raises:
      ValueError: If the datetime is already timezone-aware.
  """
  if dt.tzinfo is None:
    return dt.replace(tzinfo=PACIFIC_TZ).astimezone(UTC_TZ)
  else:
    raise ValueError(f"Datetime already has timezone: {dt=!r}")


def convert_datetimes_to_ca_naive(data: object,
                                  assume_naive_is_utc: bool = False,
                                  utc_strict: bool = True) -> object:
  """
  Recursively converts all datetime objects found anywhere in a nested data structure
  (including dict keys, values, list elements, etc.) to naive Pacific Time.

  Args:
      data: A nested structure (dict, list, tuple, set, etc.) possibly containing datetimes.
      assume_naive_is_utc: If True, and dt is naive, a warning will be logged and
        the naive datetime will be assumed to already be UTC (NOT PACIFIC).
        If False and dt is naive, an error will be raised.
      utc_strict: If True, raises an error if dt is not explicitly in UTC.
        Note if assume_naive_is_utc is True, naive datetime will not be affected by this flag.

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
      ... }
      >>> convert_datetimes_to_ca_naive(nested)
      {
          datetime.datetime(2025, 4, 23, 8, 0): [
              {"created": datetime.datetime(2025, 4, 23, 11, 0)},
              (datetime.datetime(2025, 4, 23, 13, 0),)
          ]
      }
  """
  if isinstance(data, datetime):
    return datetime_to_ca_naive(data, assume_naive_is_utc=assume_naive_is_utc, utc_strict=utc_strict)
  elif isinstance(data, Mapping):
    return {
      convert_datetimes_to_ca_naive(k, assume_naive_is_utc, utc_strict):
        convert_datetimes_to_ca_naive(v, assume_naive_is_utc, utc_strict)
      for k, v in data.items()
    }
  elif isinstance(data, list):
    return [convert_datetimes_to_ca_naive(item, assume_naive_is_utc, utc_strict) for item in data]
  elif isinstance(data, tuple):
    return tuple(convert_datetimes_to_ca_naive(item, assume_naive_is_utc, utc_strict) for item in data)
  elif isinstance(data, set):
    return {convert_datetimes_to_ca_naive(item, assume_naive_is_utc, utc_strict) for item in data}
  else:
    return data


def convert_ca_naive_datetimes_to_utc(data: object) -> object:
  """
  Recursively converts all naive datetimes (assumed to be in America/Los_Angeles time)
  to UTC-aware datetime objects throughout a nested data structure.
  Raises an error if any datetime is already timezone-aware.

  Args:
      data: Any structure (dict, list, tuple, set, etc.) possibly containing naive datetimes.

  Returns:
      A new structure with all naive datetimes converted to UTC-aware datetime objects.

  Raises:
      ValueError: If any datetime has a timezone already set.

  Examples:
      >>> from datetime import datetime
      >>> convert_ca_naive_datetimes_to_utc(datetime(2025, 4, 23, 12, 0))
      datetime.datetime(2025, 4, 23, 19, 0, tzinfo=zoneinfo.ZoneInfo('UTC'))

      >>> convert_ca_naive_datetimes_to_utc({"ts": datetime(2025, 4, 23, 12, 0)})
      {'ts': datetime.datetime(2025, 4, 23, 19, 0, tzinfo=zoneinfo.ZoneInfo('UTC'))}
  """
  if isinstance(data, datetime):
    return ca_naive_to_utc_datetime(data)
  elif isinstance(data, Mapping):
    return {
      convert_ca_naive_datetimes_to_utc(k): convert_ca_naive_datetimes_to_utc(v)
      for k, v in data.items()
    }
  elif isinstance(data, list):
    return [convert_ca_naive_datetimes_to_utc(item) for item in data]
  elif isinstance(data, tuple):
    return tuple(convert_ca_naive_datetimes_to_utc(item) for item in data)
  elif isinstance(data, set):
    return {
      convert_ca_naive_datetimes_to_utc(item)
      for item in data
    }
  else:
    return data


from datetime import datetime
from dateutil import parser


def parse_unknown_datetime(date_str: str) -> datetime | None:
  """
  Attempts to parse a string into a datetime object using dateutil.parser.parse.

  Args:
      date_str (str): The input string that represents a date and/or time.

  Returns:
      datetime | None: The parsed datetime object if successful, otherwise None.

  Raises:
      ValueError: If the input cannot be parsed as a date and time.

  Example:
      >>> parse_unknown_datetime("2025-04-28T16:23:00Z")
      datetime.datetime(2025, 4, 28, 16, 23, tzinfo=tzutc())

      >>> parse_unknown_datetime("April 28, 2025 4:23 PM")
      datetime.datetime(2025, 4, 28, 16, 23)
  """
  if not date_str or not isinstance(date_str, str):
    return None

  try:
    return parser.parse(date_str)
  except (ValueError, TypeError):
    return None
