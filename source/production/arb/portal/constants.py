"""
Shared application-wide constants.

These values are intended to remain immutable throughout the application's lifecycle.
They are used for:
  - Form field validation
  - Spreadsheet cell parsing
  - Geographic input bounds
  - Time zone-aware date formatting

Notes:
    * Constants are grouped semantically (e.g., GPS, datetime, spreadsheet).
    * Constants should be referenced from this module rather than redefined inline.
"""
from pathlib import Path
from zoneinfo import ZoneInfo

from arb.__get_logger import get_logger

# Initialize module-level logger
logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')

# -----------------------------------------------------------------------------
# UI Constants
# -----------------------------------------------------------------------------
PLEASE_SELECT = 'Please Select'

# -----------------------------------------------------------------------------
# Geographic Boundaries (California-specific)
# -----------------------------------------------------------------------------
MIN_LATITUDE = 32
MAX_LATITUDE = 42
MIN_LONGITUDE = -125
MAX_LONGITUDE = -114
GPS_RESOLUTION = 5
LATITUDE_VALIDATION = {"min": MIN_LATITUDE, "max": MAX_LATITUDE,
                       "message": f"Latitudes must be blank or valid California number between {MIN_LATITUDE} and {MAX_LATITUDE}."}

LONGITUDE_VALIDATION = {"min": MIN_LONGITUDE, "max": MAX_LONGITUDE,
                        "message": f"Longitudes must be blank or valid California number between {MIN_LONGITUDE} and {MAX_LONGITUDE}."}


# -----------------------------------------------------------------------------
# Time Zones and Datetime Formats
# -----------------------------------------------------------------------------
UTC_TIME_ZONE = ZoneInfo("UTC")
CA_TIME_ZONE = ZoneInfo("America/Los_Angeles")
"""
ZoneInfo: Time zone objects used for datetime conversions and formatting.

Use these to convert UTC-stored timestamps to California local time for display:

Example:
    >>> from datetime import datetime
    >>> dt_utc = datetime.now(UTC_TIME_ZONE)
    >>> dt_pacific = dt_utc.astimezone(CA_TIME_ZONE)
"""

HTML_LOCAL_TIME_FORMAT = "%Y-%m-%dT%H:%M"
"""
str: Format string compatible with HTML <input type="datetime-local">.

Example:
    >>> from datetime import datetime
    >>> datetime.now().strftime(HTML_LOCAL_TIME_FORMAT)
    '2025-05-05T14:30'
"""

DATETIME_WITH_SECONDS = "%Y_%m_%d_%H_%M_%S"
"""
str: Format string for filename-safe datetime representation (includes seconds).

Example:
    >>> from datetime import datetime
    >>> datetime.now().strftime(DATETIME_WITH_SECONDS)
    '2025_05_05_14_30_22'
"""


# -----------------------------------------------------------------------------
# Module Diagnostics (Optional)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
  print("Running diagnostics for constants.py...\n")

  print(f"PLEASE_SELECT = {PLEASE_SELECT}")
  print(f"LATITUDE range = ({MIN_LATITUDE}, {MAX_LATITUDE})")
  print(f"LONGITUDE range = ({MIN_LONGITUDE}, {MAX_LONGITUDE})")
  print(f"GPS_RESOLUTION = {GPS_RESOLUTION} digits")
  print(f"UTC_TIME_ZONE = {UTC_TIME_ZONE}")
  print(f"CA_TIME_ZONE = {CA_TIME_ZONE}")
  print(f"HTML_LOCAL_TIME_FORMAT = {HTML_LOCAL_TIME_FORMAT}")
  print(f"DATETIME_WITH_SECONDS = {DATETIME_WITH_SECONDS}")

  from datetime import datetime

  now = datetime.now(UTC_TIME_ZONE)
  print(f"\nCurrent UTC datetime: {now.strftime(DATETIME_WITH_SECONDS)}")
  print(f"Formatted for HTML input: {now.astimezone(CA_TIME_ZONE).strftime(HTML_LOCAL_TIME_FORMAT)}")

  print("\nDiagnostics complete.")
