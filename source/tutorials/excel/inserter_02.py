"""
Used to learn best practices on updating excel files using Steve's jinja approach.

This code is not maintained.  See excel for current source.
"""

import logging
import pathlib
import pprint

# from production.rsdas_utils.excel.excel import update_xlsx
# from production.rsdas_utils.json.json_utils import json_save_with_meta

logger = logging.getLogger(__name__)

# hard coded schema data

# oil and gas blank
oil_and_gas_payload_blank = {
  "id_incidence": "",
  "id_plume": "",
  "observation_timestamp": "",
  "lat_carb": "",
  "long_carb": "",
  "notification_timestamp": "",

  "facility_name": "",
  "id_arb_eggrt": "",
  "contact_name": "",
  "contact_phone": "",
  "contact_email": "",

  "venting_exclusion": "Please Select",
  "venting_description_1": "",

  "inspection_timestamp": "",
  "inspection_type": "Please Select",
  "found_source_type": "Please Select",
  "venting_description_2": "",
  "initial_mitigation_plan": "",

  "ogi_survey": "Please Select",
  "equipment_at_source": "Please Select",
  "equipment_other_description": "",
  "component_at_source": "Please Select",
  "component_other_description": "",
  "initial_method_21_timestamp": "",
  "initial_leak_concentration": "",
  "repair_timestamp": "",
  "final_repair_concentration": "",
  "repair_description": "",

  "additional_notes": "",
}

# oil and gas example
oil_and_gas_payload_01 = {

  "id_incidence": "1000011",
  "id_plume": "1234",
  "observation_timestamp": "06/25/2024 00:00",
  "lat_carb": "35.3211",
  "long_carb": "-119.5808",
  "notification_timestamp": "06/27/2024 00:00",

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

# landfill blank
landfill_payload_blank = {
  "id_incidence": "",
  "id_plume": "",
  "observation_timestamp": "",
  "lat_carb": "",
  "long_carb": "",
  "notification_timestamp": "",

  "facility_name": "",
  "id_arb_eggrt": "",
  "contact_name": "",
  "contact_phone": "",
  "contact_email": "",

  "inspection_timestamp": "",
  "instrument": "",
  "emission_identified_flag_fk": "Please Select",

  "initial_leak_concentration": "",
  "lat_revised": "",
  "long_revised": "",
  "emission_type_fk": "Please Select",
  "emission_type_notes": "",
  "emission_location": "Please Select",
  "emission_location_notes": "",
  "emission_cause": "Please Select",
  "emission_cause_secondary": "Please Select",
  "emission_cause_tertiary": "Please Select",
  "emission_cause_notes": "",

  "mitigation_actions": "",
  "mitigation_timestamp": "",
  "re_monitored_concentration": "",
  "most_recent_prior_inspection": "",
  "last_surface_monitoring_timestamp": "",
  "last_component_leak_monitoring_timestamp": "",
  "included_in_last_lmr": "Please Select",
  "included_in_last_lmr_description": "",
  "planned_for_next_lmr": "Please Select",
  "planned_for_next_lmr_description": "",

  "additional_notes": "",
}

# landfill example
landfill_payload_01 = {
  "id_incidence": "153",
  "id_plume": "447",
  "observation_timestamp": "06/25/2024 00:00",
  "lat_carb": "35.3211",
  "long_carb": "-119.5808",
  "notification_timestamp": "06/27/2024 00:00",

  "facility_name": "Facility Name",
  "id_arb_eggrt": "Cal e-GGRT ARB ID",
  "contact_name": "Contact Person Name",
  "contact_phone": "555-555-5555",
  "contact_email": "me@email.com",

  "inspection_timestamp": "08/14/2023 00:00",
  "instrument": "Q7 Answer.",
  "emission_identified_flag_fk": "Please Select",

  "initial_leak_concentration": "500",
  "lat_revised": "35.3211",
  "long_revised": "-119.5808",
  "emission_type_fk": "Not found",
  "emission_type_notes": "Q13 Answer.",
  "emission_location": "Gas Control Device/Control System Component",
  "emission_location_notes": "Q15 Answer.",
  "emission_cause": "Construction - Other",
  "emission_cause_secondary": "Offline Gas Collection Well(s)",
  "emission_cause_tertiary": "Construction - New Well Installation",
  "emission_cause_notes": "Q19 Answer.",

  "mitigation_actions": "Q20 Answer",
  "mitigation_timestamp": "12/15/2023 00:00",
  "re_monitored_concentration": "85",
  "most_recent_prior_inspection": "Not sure if this is a timestamp or a float?",
  "last_surface_monitoring_timestamp": "12/16/2023 00:00",
  "last_component_leak_monitoring_timestamp": "12/17/2023 00:00",
  "included_in_last_lmr": "No",
  "included_in_last_lmr_description": "Q27 Answer",
  "planned_for_next_lmr": "No",
  "planned_for_next_lmr_description": "Q29 Answer",

  "additional_notes": "Q30 Answer.",
}

payloads = {
  "oil_and_gas_payload_blank": oil_and_gas_payload_blank,
  "oil_and_gas_payload_v01": oil_and_gas_payload_01,
  "landfill_payload_blank": landfill_payload_blank,
  "landfill_payload_01": landfill_payload_01,
}


# def get_blank_template(version="oil_and_gas_v02"):
#   """
#   Return a dictionary of replacement values for a blank template.
#   Args:
#     version (str): The version of the template.
#
#   Returns (dict): A dictionary containing the replacement values.
#
#   Notes:
#     - A blank template will have empty strings for all values
#       except for drop down fields which will be initialized to 'Please Select'
#   """
#   xl_formats = {"oil_and_gas_v01": None,
#                 "oil_and_gas_v03": oil_and_gas_payload_blank,
#                 "landfill_v01": None,
#                 "landfill_v03": landfill_payload_blank}
#
#   return xl_formats[version]


def update_xlsx_example_01():
  """
  Example usage of update_xlsx_file on landfill template.
  """
  xls_dir_path = pathlib.Path("//portal/feedback_forms/current_versions")
  xls_input = xls_dir_path / "landfill_operator_feedback_with_formatting_v34_jinja_.xlsx"
  xls_output = xls_input.with_stem(xls_input.stem + "_out1")
  variable_dict = payloads["landfill_payload_blank"]

  update_xlsx(xls_input, xls_output, variable_dict)


def update_xlsx_example_02():
  """
  Example usage of update_xlsx_file on landfill template.
  """
  xls_dir_path = pathlib.Path("//portal/feedback_forms/current_versions")
  xls_input = xls_dir_path / "landfill_operator_feedback_with_formatting_v26.xlsx"
  xls_output = xls_input.with_stem(xls_input.stem + "_out2")
  variable_dict = payloads["landfill_payload_blank"]

  changes = payloads["landfill_payload_01"]

  variable_dict.update(changes)
  update_xlsx(xls_input, xls_output, variable_dict)


def update_xlsx_example_03():
  """
  Example usage of update_xlsx_file on oil & gas templates.
  """
  xls_dir_path = pathlib.Path("//portal/feedback_forms/current_versions")
  xls_input = xls_dir_path / "og_operator_feedback_with_formatting_v24.xlsx"
  xls_output = xls_input.with_stem(xls_input.stem + "_out1")
  variable_dict = payloads["landfill_payload_blank"]

  update_xlsx(xls_input, xls_output, variable_dict)


def update_xlsx_example_04():
  """
  Example usage of update_xlsx_file on oil & gas templates.
  """
  xls_dir_path = pathlib.Path("//portal/feedback_forms/current_versions")
  xls_input = xls_dir_path / "og_operator_feedback_with_formatting_v24.xlsx"
  xls_output = xls_input.with_stem(xls_input.stem + "_out2")
  variable_dict = payloads["landfill_payload_blank"]

  changes = payloads["oil_and_gas_payload_01"]

  variable_dict.update(changes)
  update_xlsx(xls_input, xls_output, variable_dict)


def create_payload(payload,
                   file_name,
                   schema_version,
                   metadata=None):
  """
  Create payload with schema version

  Args:
    payload:
    file_name:
    schema_version:

  """
  # Convert and write JSON object to file
  if metadata is None:
    metadata = {}

  metadata["schema_version"] = schema_version
  metadata["payload description"] = "Test of Excel jinja templating system"

  logger.debug(f"Creating JSON file: {file_name} with metadata: {metadata}")

  json_save_with_meta(file_name,
                      data=payload,
                      metadata=metadata,
                      )


def create_payloads():
  """
  Create example payloads.
  """
  create_payload(oil_and_gas_payload_01,
                 "oil_and_gas_v03_payload_01.json",
                 "oil_and_gas_v03")

  create_payload(landfill_payload_01,
                 "landfill_v03_payload_01.json",
                 "landfill_v03")


if __name__ == "__main__":
  logging.basicConfig(filename='excel_tutorial_01.log',
                      encoding='utf-8',
                      level=logging.DEBUG,
                      format='+%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s | %(filename)s | %(lineno)d | %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S',
                      )
  pp = pprint.PrettyPrinter(indent=4, sort_dicts=False)

  # create_payload(landfill_payload_01, "landfill_payload_01.json", schema_version="landfill_v03")
  # create_payload(oil_and_gas_payload_01, "oil_and_gas_payload_v01.json", schema_version="oil_and_gas_v03")

  # get this working and then party :)
  # update_xlsx_example_01()
  # update_xlsx_example_02()
  # update_xlsx_example_03()
  # update_xlsx_example_04()

  create_payloads()
