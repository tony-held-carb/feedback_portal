"""
Hardcoded schema definitions and sample payloads for Excel template processing.

These were manually created by inspecting old_v01 and old_v02 versions of the Excel spreadsheets.
The new versioning systems uses the naming scheme v01, v02, etc (without the old_prefix).

Contents:
    - `default_value_types_v01_00`: field types for v01 based on old_v01 and old_v02 schemas
    - Sample payloads for oil & gas and landfill forms
    - `jinja_names_set`: manually compiled field names used in Jinja templates
    - Diagnostic comparison for field coverage (see `__main__`)
"""

import datetime

import arb.__get_logger as get_logger
from arb.utils.diagnostics import list_differences

logger, pp_log = get_logger.get_logger(__name__, __file__)

# -------------------------------------------------------------------------------------
# v01 schema field types based on legacy old_v01 and old_v02 excel schemas
# -------------------------------------------------------------------------------------

default_value_types_v01_00 = {
  "additional_activities": str,
  "additional_notes": str,
  "component_at_source": str,
  "component_other_description": str,
  "contact_email": str,
  "contact_name": str,
  "contact_phone": str,
  "emission_cause": str,
  "emission_cause_notes": str,
  "emission_cause_secondary": str,
  "emission_cause_tertiary": str,
  "emission_identified_flag_fk": str,
  "emission_location": str,
  "emission_location_notes": str,
  "emission_type_fk": str,
  "equipment_at_source": str,
  "equipment_other_description": str,
  "facility_name": str,
  "final_repair_concentration": float,
  "id_arb_eggrt": str,
  "id_arb_swis": str,
  "id_incidence": int,
  "id_message": str,
  "id_plume": int,
  "included_in_last_lmr": str,
  "included_in_last_lmr_description": str,
  "initial_leak_concentration": float,
  "initial_mitigation_plan": str,
  "inspection_timestamp": datetime.datetime,
  "instrument": str,
  "last_component_leak_monitoring_timestamp": datetime.datetime,
  "last_surface_monitoring_timestamp": datetime.datetime,
  "lat_carb": float,
  "lat_revised": float,
  "long_carb": float,
  "long_revised": float,
  "method21_date": datetime.datetime,
  "method21_performed": str,
  "method21_result": float,
  "mitigation_actions": str,
  "mitigation_timestamp": datetime.datetime,
  "observation_timestamp": datetime.datetime,
  "ogi_date": datetime.datetime,
  "ogi_performed": str,
  "ogi_result": float,
  "planned_for_next_lmr": str,
  "planned_for_next_lmr_description": str,
  "re_monitored_concentration": float,
  "re_monitored_timestamp": datetime.datetime,
  "repair_description": str,
  "repair_timestamp": datetime.datetime,
  "venting_description_1": str,
  "venting_description_2": str,
  "venting_exclusion": str,
}

# todo - see if these payloads still make sense
#        looks like every value is a string ... not sure if that should be changed

# -------------------------------------------------------------------------------------
# Sample payloads - oil and gas
# -------------------------------------------------------------------------------------

oil_and_gas_payload_01 = {

  "id_incidence": "4321",
  "id_plume": "1234",
  "observation_timestamp": "06/25/2024 00:00",
  "lat_carb": "35.3211",
  "long_carb": "-119.5808",
  "id_message": "123-001",
  "facility_name": "Example Facility Name",
  "id_arb_eggrt": "Example Cal e-GGRT ARB ID",
  "contact_name": "Example Contact Person Name",
  "contact_phone": "555-555-5555",
  "contact_email": "me@email.com",
}

oil_and_gas_payload_02 = {

  "id_incidence": "1000011",
  "id_plume": "1234",
  "observation_timestamp": "06/25/2024 00:00",
  "lat_carb": "35.3211",
  "long_carb": "-119.5808",
  "facility_name": "Facility Name",
  "id_arb_eggrt": "Cal e-GGRT ARB ID",
  "contact_name": "Contact Person Name",
  "contact_phone": "555-555-5555",
  "contact_email": "me@email.com",

  "venting_exclusion": "Please Select",
  "venting_description_1": "Q7 Answer.",

  "inspection_timestamp": "08/14/2023 00:00",
  "inspection_type": "Please Select",
  "found_source_type": "Please Select",
  "venting_description_2": "Q11 Answer.",
  "initial_mitigation_plan": "Q12 Answer.",

  "ogi_survey": "Please Select",
  "equipment_at_source": "Please Select",
  "equipment_other_description": "Q15 Answer.",
  "component_at_source": "Please Select",
  "component_other_description": "Q17 Answer.",
  "initial_method_21_timestamp": "08/13/2023 14:00",
  "initial_leak_concentration": "100",
  "repair_timestamp": "08/21/2023 16:00",
  "final_repair_concentration": "40",
  "repair_description": "Q22 Answer.",

  "additional_notes": "Q23 Answer.",
}

# -------------------------------------------------------------------------------------
# Sample payloads - landfill
# -------------------------------------------------------------------------------------

landfill_payload_01 = {
  "id_incidence": "153",
  "id_plume": "447",
  "observation_timestamp": "06/25/2024 00:00",
  "lat_carb": "35.3211",
  "long_carb": "-119.5808",
  "id_message": "200-002",

  "facility_name": "Example Facility Name",
  "id_arb_swis": "Example Cal SWIS ID",
  "contact_name": "Example Contact Person Name",
  "contact_phone": "555-555-5555",
  "contact_email": "me@email.com",
}

landfill_payload_02 = {
  "id_incidence": "153",
  "id_plume": "447",
  "observation_timestamp": "06/25/2024 00:00",
  "lat_carb": "35.3211",
  "long_carb": "-119.5808",
  "facility_name": "Facility Name",
  "id_arb_swis": "Cal e-GGRT ARB ID",
  "contact_name": "Contact Person Name",
  "contact_phone": "555-555-5555",
  "contact_email": "me@email.com",

  "inspection_timestamp": "08/14/2023 00:00",
  "instrument": "Q7 Answer.",
  "emission_identified_flag_fk": "Please Select",

  "initial_leak_concentration": "500",
  "lat_revised": "35.3211",
  "long_revised": "-119.5808",
  "emission_type_notes": "Q14 Answer.",
  "emission_location": "Gas Control Device/Control System Component",
  "emission_location_notes": "Q16 Answer.",
  "emission_cause": "Construction - Other",
  "emission_cause_secondary": "Offline Gas Collection Well(s)",
  "emission_cause_tertiary": "Construction - New Well Installation",
  "emission_cause_notes": "Q20 Answer.",
  "mitigation_actions": "Q21 Answer",
  "mitigation_timestamp": "12/15/2023 00:00",
  "re_monitored_concentration": "85",
  "most_recent_prior_inspection": "Not sure if this is a timestamp or a float?",
  "last_surface_monitoring_timestamp": "12/16/2023 00:00",
  "last_component_leak_monitoring_timestamp": "12/17/2023 00:00",
  "included_in_last_lmr": "No",
  "included_in_last_lmr_description": "Q26 Answer",
  "planned_for_next_lmr": "No",
  "planned_for_next_lmr_description": "Q28 Answer",
  "additional_notes": "Q31 Answer.",
}

# -------------------------------------------------------------------------------------
# Jinja schema field names (used for legacy template validation)
# -------------------------------------------------------------------------------------

jinja_names_set = {
  "additional_activities",
    "additional_notes",
    "component_at_source",
    "component_other_description",
    "contact_email",
    "contact_name",
    "contact_phone",
    "emission_cause",
    "emission_cause_notes",
    "emission_cause_secondary",
    "emission_cause_tertiary",
    "emission_identified_flag_fk",
    "emission_location",
    "emission_location_notes",
    "emission_type_fk",
    "equipment_at_source",
    "equipment_other_description",
    "facility_name",
    "final_repair_concentration",
    "id_arb_eggrt",
    "id_arb_swis",
    "id_incidence",
    "id_message",
    "id_plume",
    "included_in_last_lmr",
    "included_in_last_lmr_description",
    "initial_leak_concentration",
    "initial_mitigation_plan",
    "inspection_timestamp",
    "instrument",
    "last_component_leak_monitoring_timestamp",
    "last_surface_monitoring_timestamp",
    "lat_carb",
    "lat_revised",
    "long_carb",
    "long_revised",
    "method21_date",
    "method21_performed",
    "method21_result",
    "mitigation_actions",
    "mitigation_timestamp",
    "observation_timestamp",
    "ogi_date",
    "ogi_performed",
    "ogi_result",
    "planned_for_next_lmr",
    "planned_for_next_lmr_description",
    "re_monitored_concentration",
    "re_monitored_timestamp",
    "repair_description",
    "repair_timestamp",
    "venting_description_1",
    "venting_description_2",
    "venting_exclusion",
}

if __name__ == "__main__":
  default_names = list(default_value_types_v01_00.keys())
  jinja_names = list(jinja_names_set)

  in_default_value_types_v01_00_only, in_jinja_names_only = list_differences(
    default_value_types_v01_00, jinja_names,
    iterable_01_name="SQLAlchemy Model JSON",
    iterable_02_name="WTForm Fields",
    print_warning=False
  )
  print(f"{in_default_value_types_v01_00_only=}")
  print(f"{in_jinja_names_only=}")
