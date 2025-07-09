"""
Shared constants for ARB Feedback Portal utility modules.

  These constants are intended to remain immutable and serve as application-wide
  placeholders or configuration defaults for UI and utility logic.

  Notes:
    - Constants should not be modified at runtime.
    - Used across multiple modules for consistency.

  - PLEASE_SELECT: Placeholder value for dropdown selectors to indicate a required user selection.
"""

# -----------------------------------------------------------------------------
# UI Constants
# -----------------------------------------------------------------------------
PLEASE_SELECT = "Please Select"
"""str: Placeholder value used in dropdown selectors to indicate a required user selection.

  Examples:
    Input : Used as the default value in a dropdown menu.
    Output: Dropdown displays 'Please Select' as the initial option.

  Notes:
    - Should be compared using equality (==), not identity (is).
    - Do not modify this value at runtime.
"""
