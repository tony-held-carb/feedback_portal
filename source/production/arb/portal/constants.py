"""
Shared application-wide constants for the ARB Methane Feedback Portal.

These constants are designed to be immutable and centrally maintained.
They support consistent behavior and validation across:

  - Web form defaults and placeholders
  - Geospatial input validation
  - Spreadsheet cell parsing
  - Time zone-aware datetime formatting
  - Filename-safe timestamp generation

Structure:
  - UI Constants
  - Geographic Boundaries (California-specific)
  - Time Zones and Datetime Formats
  - Module Self-Test

Notes:
  - Constants should always be imported from this module instead of redefined.
  - Time zone constants use `zoneinfo.ZoneInfo` and are safe for use with
    timezone-aware datetime objects.
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
PLEASE_SELECT = "Please Select"
"""str: Placeholder value used for dropdowns where no selection is made."""

# -----------------------------------------------------------------------------
# Geographic Boundaries (California-specific)
# -----------------------------------------------------------------------------
MIN_LATITUDE = 32.0
"""float: Minimum possible CA latitude."""
MAX_LATITUDE = 42.0
"""float: Maximum possible CA latitude."""
MIN_LONGITUDE = -125.0
"""float: Minimum possible CA longitude."""
MAX_LONGITUDE = -114.0
"""float: Maximum possible CA longitude."""
GPS_RESOLUTION = 5
"""int: Desired decimal precision for GPS values."""

LATITUDE_VALIDATION = {"min": MIN_LATITUDE, "max": MAX_LATITUDE,
                       "message": f"Latitudes must be blank or valid California number between {MIN_LATITUDE} and {MAX_LATITUDE}."}
"""dict: Latitude validation schema for WTForms or other validators."""

LONGITUDE_VALIDATION = {"min": MIN_LONGITUDE, "max": MAX_LONGITUDE,
                        "message": f"Longitudes must be blank or valid California number between {MIN_LONGITUDE} and {MAX_LONGITUDE}."}
"""dict: Longitude validation schema for WTForms or other validators."""

# -----------------------------------------------------------------------------
# Time Zones and Datetime Formats
# -----------------------------------------------------------------------------
UTC_TIME_ZONE = ZoneInfo("UTC")
"""ZoneInfo: UTC (Zulu) timezone."""
CA_TIME_ZONE = ZoneInfo("America/Los_Angeles")
"""ZoneInfo: Timezone objects used for datetime conversion and formatting."""

HTML_LOCAL_TIME_FORMAT = "%Y-%m-%dT%H:%M"
"""str: HTML5-compatible format string for <input type="datetime-local">."""

DATETIME_WITH_SECONDS = "%Y_%m_%d_%H_%M_%S"
"""str: Filename-safe datetime string format (includes seconds)."""

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
