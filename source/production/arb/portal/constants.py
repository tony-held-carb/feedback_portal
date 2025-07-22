"""
  Shared application-wide constants for the ARB Methane Feedback Portal.

  These constants are designed to be immutable and centrally maintained.
  They support consistent behavior and validation across:
    - Web form defaults and placeholders
    - Geospatial input validation
    - Spreadsheet cell parsing
    - Time zone-aware datetime formatting
    - Filename-safe timestamp generation

  Args:
    None

  Returns:
    None

  Attributes:
    PLEASE_SELECT (str): Placeholder value for dropdowns where no selection is made.
    MIN_LATITUDE (float): Minimum possible CA latitude.
    MAX_LATITUDE (float): Maximum possible CA latitude.
    MIN_LONGITUDE (float): Minimum possible CA longitude.
    MAX_LONGITUDE (float): Maximum possible CA longitude.
    GPS_RESOLUTION (int): Desired decimal precision for GPS values.
    LATITUDE_VALIDATION (dict): Latitude validation schema for WTForms or other validators.
    LONGITUDE_VALIDATION (dict): Longitude validation schema for WTForms or other validators.
    UTC_TIME_ZONE (ZoneInfo): UTC (Zulu) timezone.
    CA_TIME_ZONE (ZoneInfo): California timezone for datetime conversion and formatting.
    HTML_LOCAL_TIME_FORMAT (str): HTML5-compatible format string for <input type="datetime-local">.
    DATETIME_WITH_SECONDS (str): Filename-safe datetime string format (includes seconds).
    logger (logging.Logger): Logger instance for this module.

  Examples:
    from arb.portal.constants import PLEASE_SELECT, MIN_LATITUDE
    print(PLEASE_SELECT)
    # Output: 'Please Select'

  Notes:
    - Constants should always be imported from this module instead of redefined.
    - Time zone constants use `zoneinfo.ZoneInfo` and are safe for use with timezone-aware datetime objects.
    - The logger emits a debug message when this file is loaded.
    - Run this file directly to execute diagnostics on the constants.
"""

import logging
from pathlib import Path
from zoneinfo import ZoneInfo

# Initialize module-level logger
logger = logging.getLogger(__name__)
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')

# -----------------------------------------------------------------------------
# UI Constants
# -----------------------------------------------------------------------------
PLEASE_SELECT = "Please Select"
"""str: Placeholder value used for dropdowns where no selection is made.

  Examples:
    Input : Used as the default value in a dropdown menu.
    Output: Dropdown displays 'Please Select' as the initial option.

  Notes:
    - Should be compared using equality (==), not identity (is).
    - Do not modify this value at runtime.
"""

# -----------------------------------------------------------------------------
# Geographic Boundaries (California-specific)
# -----------------------------------------------------------------------------
MIN_LATITUDE = 32.0
"""float: Minimum possible CA latitude.

  Examples:
    Input : User enters a latitude value.
    Output: Value must be >= 32.0 to be valid for California.

  Notes:
    - Used for geospatial validation.
    - Do not modify at runtime.
"""
MAX_LATITUDE = 42.0
"""float: Maximum possible CA latitude.

  Examples:
    Input : User enters a latitude value.
    Output: Value must be <= 42.0 to be valid for California.

  Notes:
    - Used for geospatial validation.
    - Do not modify at runtime.
"""
MIN_LONGITUDE = -125.0
"""float: Minimum possible CA longitude.

  Examples:
    Input : User enters a longitude value.
    Output: Value must be >= -125.0 to be valid for California.

  Notes:
    - Used for geospatial validation.
    - Do not modify at runtime.
"""
MAX_LONGITUDE = -114.0
"""float: Maximum possible CA longitude.

  Examples:
    Input : User enters a longitude value.
    Output: Value must be <= -114.0 to be valid for California.

  Notes:
    - Used for geospatial validation.
    - Do not modify at runtime.
"""
GPS_RESOLUTION = 5
"""int: Desired decimal precision for GPS values.

  Examples:
    Input : GPS value is rounded for display or storage.
    Output: Value is rounded to 5 decimal places.

  Notes:
    - Used for formatting and validation.
    - Do not modify at runtime.
"""
LATITUDE_VALIDATION = {"min": MIN_LATITUDE, "max": MAX_LATITUDE,
                       "message": f"Latitudes must be blank or valid California number between {MIN_LATITUDE} and {MAX_LATITUDE}."}
"""dict: Latitude validation schema for WTForms or other validators.

  Examples:
    Input : Used in a WTForms validator for latitude fields.
    Output: Ensures latitude is within valid CA range.

  Notes:
    - Used for form and API validation.
    - Do not modify at runtime.
"""
LONGITUDE_VALIDATION = {"min": MIN_LONGITUDE, "max": MAX_LONGITUDE,
                        "message": f"Longitudes must be blank or valid California number between {MIN_LONGITUDE} and {MAX_LONGITUDE}."}
"""dict: Longitude validation schema for WTForms or other validators.

  Examples:
    Input : Used in a WTForms validator for longitude fields.
    Output: Ensures longitude is within valid CA range.

  Notes:
    - Used for form and API validation.
    - Do not modify at runtime.
"""

# -----------------------------------------------------------------------------
# Time Zones and Datetime Formats
# -----------------------------------------------------------------------------
UTC_TIME_ZONE = ZoneInfo("UTC")
"""ZoneInfo: UTC (Zulu) timezone.

  Examples:
    Input : Used to create timezone-aware datetime objects.
    Output: Datetime is set to UTC.

  Notes:
    - Use with datetime objects for consistent time handling.
    - Do not modify at runtime.
"""
CA_TIME_ZONE = ZoneInfo("America/Los_Angeles")
"""ZoneInfo: California timezone for datetime conversion and formatting.

  Examples:
    Input : Used to convert UTC datetime to local time.
    Output: Datetime is converted to America/Los_Angeles timezone.

  Notes:
    - Use with datetime objects for local time handling.
    - Do not modify at runtime.
"""
HTML_LOCAL_TIME_FORMAT = "%Y-%m-%dT%H:%M"
"""str: HTML5-compatible format string for <input type="datetime-local">.

  Examples:
    Input : Used to format a datetime for an HTML input field.
    Output: String formatted as 'YYYY-MM-DDTHH:MM'.

  Notes:
    - Use for HTML5 datetime-local input fields.
    - Do not modify at runtime.
"""
DATETIME_WITH_SECONDS = "%Y_%m_%d_%H_%M_%S"
"""str: Filename-safe datetime string format (includes seconds).

  Examples:
    Input : Used to format a datetime for a filename.
    Output: String formatted as 'YYYY_MM_DD_HH_MM_SS'.

  Notes:
    - Use for filenames and logs.
    - Do not modify at runtime.
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
