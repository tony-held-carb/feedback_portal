
"""
Shared application-wide constants.
These should never change at runtime.
"""
from zoneinfo import ZoneInfo

# Dropdown values
PLEASE_SELECT: str = "Please Select"

# Timezone and datetime formats
UTC_TIME_ZONE = ZoneInfo("UTC")
CA_TIME_ZONE = ZoneInfo("America/Los_Angeles")
HTML_LOCAL_TIME_FORMAT = "%Y-%m-%dT%H:%M"

# GPS precision
GPS_RESOLUTION: int = 5

# Excel formatting schema locations
XL_NUMBER_OF_TABS_CELL = "$B$7"
XL_FORMATTING_SCHEMA_CELL = "$B$10"
XL_FIRST_TAB_NAME_CELL = "$A$10"

# Latitude/longitude bounds for California
MIN_LATITUDE = 32
MAX_LATITUDE = 42
MIN_LONGITUDE = -125
MAX_LONGITUDE = -114

# File upload default
DEFAULT_UPLOAD_FOLDER: str = "static/uploads"

__all__ = [
  "PLEASE_SELECT", "UTC_TIME_ZONE", "CA_TIME_ZONE", "HTML_LOCAL_TIME_FORMAT",
  "GPS_RESOLUTION", "XL_NUMBER_OF_TABS_CELL", "XL_FORMATTING_SCHEMA_CELL",
  "XL_FIRST_TAB_NAME_CELL", "MIN_LATITUDE", "MAX_LATITUDE",
  "MIN_LONGITUDE", "MAX_LONGITUDE", "DEFAULT_UPLOAD_FOLDER"
]
