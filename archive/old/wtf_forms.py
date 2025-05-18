"""
Defines WTForms that can be used to simplify HTML form creation and validation
for the Oil & Gas and Landfill feedback workflows.

This module defines forms derived from FlaskForm. They are used in conjunction
with templates to render sector-specific feedback forms with conditional logic
and validators based on user inputs.

General-purpose WTForms utilities are located in:
    arb.utils.wtf_forms_util.py

Form classes:
    - OGFeedback: Oil & Gas sector form with conditional validation for venting,
      OGI/Method 21 logic, and equipment/component descriptions.
    - LandfillFeedback: Landfill sector form with contingent dropdowns, dynamic
      validation rules, and optional monitoring logic.

Each form includes:
    - Rich WTForms field definitions
    - Conditional validators depending on other fields
    - Custom validate() methods
    - Dynamic dropdown logic through determine_contingent_fields()

"""

from pathlib import Path

from arb.__get_logger import get_logger

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


