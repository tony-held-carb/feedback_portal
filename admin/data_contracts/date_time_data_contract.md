# DateTime Data Contract

**Version:** 1.0.0  
**Effective Date:** 2025-01-XX  
**Scope:** ARB Feedback Portal - All datetime handling across the application

## Overview

This document establishes a formal contract for how datetime values are handled throughout the ARB Feedback Portal application. The goal is to ensure consistency, prevent timezone-related bugs, and provide clear guidelines for developers working with datetime data.

## Core Principles

1. **UTC as the Single Source of Truth**: All datetime storage and internal processing uses UTC
2. **Timezone Awareness**: Python datetime objects must always be timezone-aware
3. **Late Localization**: Conversion to California local time happens as late as possible in the presentation layer
4. **Early UTC Conversion**: External datetime inputs are converted to UTC as early as possible
5. **Explicit Formatting**: All datetime serialization uses explicit, standardized formats

## Data Contract Specifications

### 1. Storage Format (Files, JSON, Database Text Fields)

**Contract:** All datetime values stored in text format MUST use UTC ISO 8601 format with timezone information.

**Format:** `YYYY-MM-DDTHH:MM:SS.SSSSSS+00:00` or `YYYY-MM-DDTHH:MM:SS.SSSSSSZ`

**Examples:**
```json
{
  "observation_timestamp": "2025-01-15T14:30:00.000000+00:00",
  "created_timestamp": "2025-01-15T22:45:30.123456Z",
  "repair_timestamp": "2025-01-16T03:15:45.000000+00:00"
}
```

**Implementation Requirements:**
- JSON serialization must use `datetime.isoformat()` with timezone info
- Database text fields must store UTC ISO format
- File exports must use UTC ISO format
- No exceptions for "local time" storage

### 2. Python Internal Representation

**Contract:** All Python datetime objects MUST be timezone-aware and represent UTC time.

**Valid Examples:**
```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# ✅ Correct - UTC timezone aware
utc_now = datetime.now(timezone.utc)
utc_from_iso = datetime.fromisoformat("2025-01-15T14:30:00+00:00")
utc_from_zoneinfo = datetime.now(ZoneInfo("UTC"))

# ❌ Invalid - Naive datetime
naive_dt = datetime.now()  # BANNED

# ❌ Invalid - Non-UTC timezone
pacific_dt = datetime.now(ZoneInfo("America/Los_Angeles"))  # Only for display
```

**Implementation Requirements:**
- Use `datetime.now(timezone.utc)` instead of `datetime.now()`
- Always specify timezone when creating datetime objects
- Validate timezone awareness in critical functions
- Use type hints: `datetime` (timezone-aware only)

### 3. HTML Form Presentation

**Contract:** HTML forms display datetime values in California local time (PST/PDT) without timezone information.

**Format:** `YYYY-MM-DDTHH:MM` (HTML datetime-local input format)

**Conversion Rules:**
- **Input to Display**: UTC → California Local (PST/PDT)
- **Display to Storage**: California Local → UTC
- **Conversion Timing**: As late as possible in form rendering, as early as possible in form processing

**Implementation Examples:**
```python
# Form display (UTC → California Local)
def format_for_html_form(utc_datetime: datetime) -> str:
    """Convert UTC datetime to California local for HTML form display."""
    if not utc_datetime.tzinfo:
        raise ValueError("Datetime must be timezone-aware")
    
    california_tz = ZoneInfo("America/Los_Angeles")
    local_dt = utc_datetime.astimezone(california_tz)
    return local_dt.strftime("%Y-%m-%dT%H:%M")

# Form processing (California Local → UTC)
def html_naive_str_to_utc_datetime(local_datetime_str: str) -> datetime:
    """Convert California local datetime string to UTC."""
    california_tz = ZoneInfo("America/Los_Angeles")
    local_dt = datetime.fromisoformat(local_datetime_str)
    local_dt = local_dt.replace(tzinfo=california_tz)
    return local_dt.astimezone(timezone.utc)
```

### 4. Excel File Input

**Contract:** Datetime values in Excel files are assumed to be California local time and must be converted to UTC immediately upon reading.

**Assumptions:**
- Excel files contain California local time (PST/PDT)
- No timezone information is stored in Excel
- Conversion happens during file parsing, not later

**Implementation Requirements:**
```python
def excel_naive_datetime_to_utc_datetime(excel_datetime: datetime) -> datetime:
    """Convert Excel datetime (assumed California local) to UTC."""
    if excel_datetime.tzinfo is not None:
        raise ValueError("Excel datetime should be naive (no timezone)")
    
    california_tz = ZoneInfo("America/Los_Angeles")
    local_dt = excel_datetime.replace(tzinfo=california_tz)
    return local_dt.astimezone(timezone.utc)
```

### 5. HTML Form Input

**Contract:** Datetime values from HTML forms are assumed to be California local time and must be converted to UTC immediately upon processing.

**Processing Flow:**
1. HTML form submits California local datetime string
2. Parse string as California local datetime
3. Convert to UTC immediately
4. Store as UTC in database/JSON

**Implementation:**
```python
def process_form_datetime(form_value: str) -> datetime:
    """Process datetime from HTML form (California local → UTC)."""
    if not form_value:
        return None
    
    # Parse as California local
    california_tz = ZoneInfo("America/Los_Angeles")
    local_dt = datetime.fromisoformat(form_value)
    local_dt = local_dt.replace(tzinfo=california_tz)
    
    # Convert to UTC
    return local_dt.astimezone(timezone.utc)
```

## Implementation Guidelines

### Utility Functions

Create centralized utility functions in `arb/utils/date_and_time.py`:

```python
class DateTimeContract:
    """Centralized datetime handling following the data contract."""
    
    CALIFORNIA_TZ = ZoneInfo("America/Los_Angeles")
    
    @staticmethod
    def utc_datetime_to_iso_str(dt: datetime) -> str:
        """Convert timezone-aware datetime to UTC ISO string."""
        if not dt.tzinfo:
            raise ValueError("Datetime must be timezone-aware")
        return dt.astimezone(timezone.utc).isoformat()
    
    @staticmethod
    def from_utc_iso(iso_string: str) -> datetime:
        """Parse UTC ISO string to timezone-aware datetime."""
        dt = datetime.fromisoformat(iso_string)
        if not dt.tzinfo:
            raise ValueError("ISO string must include timezone information")
        return dt.astimezone(timezone.utc)
    
    @staticmethod
    def to_california_local(utc_dt: datetime) -> datetime:
        """Convert UTC datetime to California local."""
        if not utc_dt.tzinfo:
            raise ValueError("Input datetime must be timezone-aware")
        return utc_dt.astimezone(DateTimeContract.CALIFORNIA_TZ)
    
    @staticmethod
    def from_california_local(local_dt: datetime) -> datetime:
        """Convert California local datetime to UTC."""
        if local_dt.tzinfo is None:
            local_dt = local_dt.replace(tzinfo=DateTimeContract.CALIFORNIA_TZ)
        return local_dt.astimezone(timezone.utc)
    
    @staticmethod
    def utc_datetime_to_html_naive_str(utc_dt: datetime) -> str:
        """
        Format UTC datetime for HTML datetime-local input.
        """
        if not utc_dt.tzinfo:
            raise ValueError("Datetime must be timezone-aware")
        if utc_dt.tzinfo != timezone.utc:
            raise ValueError("Datetime must be UTC")
        local_dt = utc_dt.astimezone(DateTimeContract.CALIFORNIA_TZ)
        return local_dt.strftime("%Y-%m-%dT%H:%M")
    
    @staticmethod
    def html_naive_str_to_utc_datetime(form_value: str) -> datetime:
        """Parse HTML form datetime (California local) to UTC."""
        if not form_value:
            return None
        local_dt = datetime.fromisoformat(form_value)
        return DateTimeContract.from_california_local(local_dt)
```

### Validation Functions

```python
def validate_datetime_contract(dt: datetime, context: str) -> None:
    """Validate datetime follows the contract."""
    if dt is None:
        return
    
    if not dt.tzinfo:
        raise ValueError(f"Datetime in {context} must be timezone-aware")
    
    # Ensure it's UTC
    if dt.tzinfo != timezone.utc:
        raise ValueError(f"Datetime in {context} must be UTC, got {dt.tzinfo}")
```

### Migration Strategy

1. **Phase 1**: Update utility functions to enforce contract
2. **Phase 2**: Add validation to critical data paths
3. **Phase 3**: Migrate existing data to UTC format
4. **Phase 4**: Add automated testing for contract compliance

## Testing Requirements

### Unit Tests

```python
def test_datetime_contract_compliance():
    """Test that all datetime operations follow the contract."""
    
    # Test UTC storage
    utc_dt = datetime.now(timezone.utc)
    iso_string = DateTimeContract.utc_datetime_to_iso_str(utc_dt)
    assert "+00:00" in iso_string or iso_string.endswith("Z")
    
    # Test HTML form conversion
    form_value = DateTimeContract.utc_datetime_to_html_naive_str(utc_dt)
    parsed_dt = DateTimeContract.html_naive_str_to_utc_datetime(form_value)
    assert parsed_dt.tzinfo == timezone.utc
    
    # Test validation
    with pytest.raises(ValueError):
        validate_datetime_contract(datetime.now(), "test")  # Naive datetime
```

### Integration Tests

```python
def test_form_datetime_roundtrip():
    """Test complete datetime roundtrip through forms."""
    # Create UTC datetime
    original_utc = datetime.now(timezone.utc)
    
    # Convert to form display
    form_value = DateTimeContract.utc_datetime_to_html_naive_str(original_utc)
    
    # Parse from form submission
    parsed_utc = DateTimeContract.html_naive_str_to_utc_datetime(form_value)
    
    # Should be equivalent (within reasonable tolerance)
    assert abs((original_utc - parsed_utc).total_seconds()) < 60
```