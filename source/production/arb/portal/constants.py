"""
Shared application-wide constants.
These should never change at runtime.
"""
from zoneinfo import ZoneInfo

import arb.__get_logger as get_logger

logger, pp_log = get_logger.get_logger(__name__, __file__)


GPS_RESOLUTION = 5  # decimal digits required of users for GPS lat/long data

PLEASE_SELECT = 'Please Select'  # select element value for disabled 'Please Select' option

# Formatting schema for spreadsheet parsing
# XL_NUMBER_OF_TABS_CELL = "$B$7" - Not sure if still in use
# XL_FORMATTING_SCHEMA_CELL = "$B$10" - Not sure if still in use
# XL_FIRST_TAB_NAME_CELL = "$A$10"

# California lat longs should be between 32° 30' N to 42° N and 114° 8' W to 124° 24' W
MIN_LATITUDE = 32
MAX_LATITUDE = 42
MIN_LONGITUDE = -125
MAX_LONGITUDE = -114

# Datetime/timezone information
UTC_TIME_ZONE = ZoneInfo("UTC")
CA_TIME_ZONE = ZoneInfo("America/Los_Angeles")
HTML_LOCAL_TIME_FORMAT = "%Y-%m-%dT%H:%M"
DATETIME_WITH_SECONDS = "%Y_%m_%d_%H_%M_%S"
