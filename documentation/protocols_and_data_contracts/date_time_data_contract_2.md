# Datetime Data Contract (Clean Version)

## Requirements

- **All datetimes stored in the database or JSON must be UTC-aware ISO 8601 strings.**
- **All datetimes received from forms must be naive (California local time).**
- **All conversions between local and UTC must use the official utility functions in `utils/date_and_time.py`.**

---

## Official Utility Functions (from `utils/date_and_time.py`)

### String ↔ Datetime Conversions

- **`iso_str_to_utc_datetime(iso_str: str, error_on_missing_tz: bool = True) -> datetime`**
  Convert an ISO 8601 string to a UTC-aware datetime object. Raises if missing timezone info unless overridden.

- **`utc_datetime_to_iso_str(utc_dt: datetime) -> str`**
  Convert a timezone-aware datetime to a UTC ISO 8601 string. Raises if input is naive.

### Form/HTML ↔ Datetime Conversions

- **`html_naive_str_to_utc_datetime(html_str: str) -> datetime | None`**
  Convert an HTML form datetime-local string (naive, California local) to a UTC-aware datetime.

- **`utc_datetime_to_html_naive_str(utc_dt: datetime) -> str`**
  Convert a UTC-aware datetime to a naive California local string for HTML form display.

### California Local (Naive) ↔ UTC Conversions

- **`ca_naive_datetime_to_utc_datetime(ca_naive_dt: datetime) -> datetime`**
  Convert a naive California local datetime to a UTC-aware datetime. Raises if input is not naive.

- **
  `utc_datetime_to_ca_naive_datetime(utc_dt: datetime, assume_naive_is_utc: bool = False, utc_strict: bool = True) -> datetime`
  **
  Convert a UTC-aware (or optionally naive) datetime to naive California local time. Raises if input is naive and not
  allowed, or not UTC when strict.

### Excel ↔ Datetime Conversions

- **`excel_str_to_naive_datetime(excel_str: str) -> datetime | None`**
  Parse a string from an Excel cell to a naive datetime object (no timezone).

- **`excel_naive_datetime_to_utc_datetime(excel_dt: datetime) -> datetime`**
  Convert a naive Excel datetime (assumed California local) to a UTC-aware datetime.

### Validation/Inspection

- **`is_datetime_naive(dt: datetime) -> bool`**
  Return True if a datetime is naive (lacks timezone info).

- **`is_datetime_utc(dt: datetime) -> bool`**
  Return True if the datetime is timezone-aware and in UTC.

### Bulk/Recursive Utilities

- **`bulk_utc_datetime_to_ca_naive_datetime(data: object, ...) -> object`**
  Recursively convert all UTC datetimes in a nested structure to naive California local.

- **`bulk_ca_naive_datetime_to_utc_datetime(data: object) -> object`**
  Recursively convert all naive California local datetimes in a nested structure to UTC-aware.

---

## Usage Examples

### Form Submission → DB Storage

```python
from arb.utils.date_and_time import ca_naive_datetime_to_utc_datetime, utc_datetime_to_iso_str

# User submits a naive local datetime from the form
local_dt = form.observation_timestamp.data  # naive, California local

# Convert to UTC-aware
db_utc_dt = ca_naive_datetime_to_utc_datetime(local_dt)

# Serialize for DB
db_value = utc_datetime_to_iso_str(db_utc_dt)
```

### DB Read → Form Population

```python
from arb.utils.date_and_time import iso_str_to_utc_datetime, utc_datetime_to_ca_naive_datetime

# Read ISO string from DB
db_value = row['observation_timestamp']

# Convert to UTC datetime
utc_dt = iso_str_to_utc_datetime(db_value)

# Convert to naive California local for form
local_dt = utc_datetime_to_ca_naive_datetime(utc_dt)
```

---

## See Also

- [utils/date_and_time.py](../../source/production/arb/utils/date_and_time.py)

---

**Note:**

- Do not copy or inline code from the utility module. Always use the latest version of the functions above to ensure
  contract compliance.
- If you need to add new datetime handling logic, add it to `utils/date_and_time.py` and update this contract as needed.
