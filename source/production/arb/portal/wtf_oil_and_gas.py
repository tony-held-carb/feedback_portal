"""
Defines a WTForm that can be used to simplify HTML form creation and validation
for Oil and Gas feedback workflows.

This module defines forms derived from FlaskForm. They are used in conjunction
with templates to render sector-specific feedback forms with conditional logic
and validators based on user inputs.

General-purpose WTForms utilities are located in:
    arb.utils.wtf_forms_util.py

Form classes:
    - OGFeedback: Oil and Gas sector form with contingent dropdowns, dynamic
      validation rules, and optional monitoring logic.

Each form includes:
    - Rich WTForms field definitions
    - Conditional validators depending on other fields
    - Custom validate() methods
    - Dynamic dropdown logic through determine_contingent_fields()
"""
from pathlib import Path

from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, DecimalField, EmailField, FloatField, IntegerField, SelectField, StringField, TextAreaField
from wtforms.validators import Email, InputRequired, Length, NumberRange, Optional, Regexp

from arb.__get_logger import get_logger
from arb.portal.constants import GPS_RESOLUTION, HTML_LOCAL_TIME_FORMAT, LATITUDE_VALIDATION, LONGITUDE_VALIDATION, PLEASE_SELECT
from arb.portal.globals import Globals
from arb.utils.misc import replace_list_occurrences
from arb.utils.wtf_forms_util import change_validators_on_test, ensure_field_choice, get_wtforms_fields, validate_selectors

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


class OGFeedback(FlaskForm):
  """
  Oil & Gas feedback form designed to be consistent with the O&G feedback spreadsheet.

  Notes:
  """

  # venting through inspection (not through the 95669.1(b)(1) exclusion)
  venting_responses = [
    "Venting-construction/maintenance",
    "Venting-routine",
  ]

  # These are considered leaks that require mitigation
  unintentional_leak = [
    "Unintentional-leak",
    "Unintentional-non-component",
  ]

  # Section 3
  label = "1.  Incidence/Emission ID"
  id_incidence = IntegerField(
    label=label,
    validators=[InputRequired(), NumberRange(min=1, message="Emission ID must be a positive integer")],
  )  # REFERENCES incidences (id_incidence)

  label = "2.  Plume ID(s)"
  id_plume = IntegerField(
    label=label,
    validators=[InputRequired(), NumberRange(min=1, message="Plume ID must be a positive integer")],
  )  # REFERENCES plumes (id_plume)

  label = "3.  Plume Observation Timestamp(s)"
  observation_timestamp = DateTimeLocalField(
    label=label,
    validators=[InputRequired()],
    format=HTML_LOCAL_TIME_FORMAT,
  )

  label = "4.  Plume CARB Estimated Latitude"
  lat_carb = DecimalField(
    label=label,
    places=GPS_RESOLUTION,
    validators=[InputRequired(), NumberRange(**LATITUDE_VALIDATION)],
  )

  label = "5.  Plume CARB Estimated Longitude"
  long_carb = DecimalField(
    label=label,
    places=GPS_RESOLUTION,
    validators=[InputRequired(), NumberRange(**LONGITUDE_VALIDATION)],
  )

  label = "6.  CARB Message ID"
  id_message = StringField(
    label=label,
    validators=[Optional()],
  )

  # Section 4
  label = "Q1.  Facility Name"
  facility_name = StringField(
    label=label,
    validators=[InputRequired()],
  )

  label = "Q2.  Facility's Cal e-GGRT ARB ID (if known)"
  id_arb_eggrt = StringField(
    label=label,
    validators=[Optional()],
  )

  label = "Q3.  Contact Name"
  contact_name = StringField(
    label=label,
    validators=[InputRequired()],
  )
  # contact_phone = StringField(label="Contact Phone", validators=[InputRequired()])
  label = "Q4.  Contact Phone Number"
  message = "Invalid phone number. Phone number must be in format '(123) 456-7890' or '(123) 456-7890 x1234567'."
  contact_phone = StringField(
    label=label,
    validators=[InputRequired(),
                Regexp(regex=r"^\(\d{3}\) \d{3}-\d{4}( x\d{1,7})?$", message=message)
                ],
  )

  label = "Q5.  Contact Email Address"
  contact_email = EmailField(
    label=label,
    validators=[InputRequired(), Email()],
  )

  # Section 5
  label = (f"Q6.  Was the plume a result of activity-based venting that is being reported "
           f"per section 95669.1(b)(1) of the Oil and Gas Methane Regulation?")
  venting_exclusion = SelectField(
    label=label,
    choices=Globals.drop_downs["venting_exclusion"],
    validators=[InputRequired()],
  )

  label = (f"Q7.  If you answered 'Yes' to Q6, please provide a brief summary of the source of the venting "
           f"defined by Regulation 95669.1(b)(1) and why the venting occurred.")
  message = "If provided, a description must be at least 30 characters."
  venting_description_1 = TextAreaField(
    label=label,
    validators=[InputRequired(),
                Length(min=30, message=message)],
  )

  # Section 6
  label = "Q8. Was an OGI inspection performed?"
  ogi_performed = SelectField(
    label=label,
    choices=Globals.drop_downs["ogi_performed"],
    validators=[InputRequired()],
  )

  label = "Q9.  If you answered 'Yes' to Q8, what date and time was the OGI inspection performed?"
  ogi_date = DateTimeLocalField(
    label=label,
    validators=[InputRequired()],
    format=HTML_LOCAL_TIME_FORMAT,
  )

  label = "Q10. If you answered 'Yes' to Q8, what type of source was found using OGI?"
  ogi_result = SelectField(
    label=label,
    choices=Globals.drop_downs["ogi_result"],
    validators=[InputRequired()],
  )

  label = "Q11.  Was a Method 21 inspection performed?"
  method21_performed = SelectField(
    label=label,
    choices=Globals.drop_downs["method21_performed"],
    validators=[InputRequired()],
  )

  label = "Q12.  If you answered 'Yes' to Q11, what date and time was the Method 21 inspection performed?"
  method21_date = DateTimeLocalField(
    label=label,
    validators=[InputRequired()],
    format=HTML_LOCAL_TIME_FORMAT,
  )

  label = "Q13. If you answered 'Yes' to Q11, what type of source was found using Method 21?"
  method21_result = SelectField(
    label=label,
    choices=Globals.drop_downs["method21_result"],
    validators=[InputRequired()],
  )

  label = "Q14. If you answered 'Yes' to Q11, what was the initial leak concentration in ppmv (if applicable)?"
  initial_leak_concentration = FloatField(
    label=label,
    validators=[InputRequired()],
  )

  label = (f"Q15.  If you answered 'Venting' to Q10 or Q13, please provide a brief summary of the source "
           f"of the venting discovered during the ground inspection and why the venting occurred.")
  venting_description_2 = TextAreaField(
    label=label,
    validators=[InputRequired()],
  )

  label = (f"Q16.  If you answered a 'Unintentional-leak' or 'Unintentional-non-component' to Q10 or Q13, "
           f"please provide a description of your initial mitigation plan.")
  initial_mitigation_plan = TextAreaField(
    label=label,
    validators=[InputRequired()],
  )

  # Section 7
  label = f"Q17.  What type of equipment is at the source of the emissions?"
  equipment_at_source = SelectField(
    label=label,
    choices=Globals.drop_downs["equipment_at_source"],
    validators=[InputRequired(), ],
  )

  label = "Q18.  If you answered 'Other' for Q17, please provide an additional description of the equipment."
  equipment_other_description = TextAreaField(
    label=label,
    validators=[InputRequired()],
  )

  label = f"Q19.  If your source is a component, what type of component is at the source of the emissions?"
  component_at_source = SelectField(
    label=label,
    choices=Globals.drop_downs["component_at_source"],
    validators=[],
  )

  label = "Q20.  If you answered 'Other' for Q19, please provide an additional description of the component."
  component_other_description = TextAreaField(
    label=label, validators=[InputRequired()],
  )

  label = f"Q21.  Repair/mitigation completion date & time (if applicable)."
  repair_timestamp = DateTimeLocalField(
    label=label,
    validators=[InputRequired()],
    format=HTML_LOCAL_TIME_FORMAT,
  )

  label = f"Q22.  Final repair concentration in ppmv (if applicable)."
  final_repair_concentration = FloatField(
    label=label,
    validators=[InputRequired()],
  )

  label = f"Q23.  Repair/Mitigation actions taken (if applicable)."
  repair_description = StringField(
    label=label,
    validators=[InputRequired()],
  )

  # Section 8
  label = f"Q24. Additional notes or comments."
  additional_notes = TextAreaField(
    label=label,
    validators=[],
  )

  def update_contingent_selectors(self):
    pass

  def validate(self, extra_validators=None):
    """
    Overriding validate to allow for form-level validation and inter-comparing fields.

    Args:
      extra_validators:

    """
    logger.debug(f"validate() called.")
    form_fields = get_wtforms_fields(self)

    # Dictionary to replace standard WTForm messages with alternative message
    error_message_replacement_dict = {"Not a valid float value.": "Not a valid numeric value."}

    ###################################################################################################
    # Add, Remove, or Modify validation at a field level here before the super is called (for example)
    ###################################################################################################
    self.determine_contingent_fields()

    ###################################################################################################
    # Set selectors with values not in their choices list to "Please Select"
    ###################################################################################################
    for field_name in form_fields:
      field = getattr(self, field_name)
      logger.debug(f"field_name: {field_name}, {type(field.data)=}, {field.data=}, {type(field.raw_data)=}")
      if isinstance(field, SelectField):
        ensure_field_choice(field_name, field)

    ###################################################################################################
    # call the super to perform each fields individual validation (which saves to form.errors)
    # This will create the form.errors dictionary.  If there are form_errors they will be in the None key.
    # The form_errors will not affect if validate returns True/False, only the fields are considered.
    ###################################################################################################
    # logger.debug("in the validator before super")
    super_return = super().validate(extra_validators=extra_validators)

    ###################################################################################################
    # Validating selectors explicitly ensures the same number of errors on GETS and POSTS for the same data
    ###################################################################################################
    validate_selectors(self, PLEASE_SELECT)

    ###################################################################################################
    # Perform any field level validation where one field is cross-referenced to another
    # The error will be associated with one of the fields
    ###################################################################################################
    if self.observation_timestamp.data and self.ogi_date.data:
      if self.observation_timestamp.data > self.ogi_date.data:
        self.ogi_date.errors.append(
          "Initial OGI timestamp must be after the plume observation timestamp")

    if self.observation_timestamp.data and self.method21_date.data:
      if self.observation_timestamp.data > self.method21_date.data:
        self.method21_date.errors.append(
          "Initial Method 21 timestamp must be after the plume observation timestamp")

    if self.observation_timestamp.data and self.repair_timestamp.data:
      if self.observation_timestamp.data > self.repair_timestamp.data:
        self.method21_date.errors.append(
          "Repair timestamp must be after the plume observation timestamp")

    if self.venting_exclusion and self.ogi_result.data:
      if self.venting_exclusion.data == "Yes":
        if self.ogi_result.data in ["Unintentional-leak"]:
          self.ogi_result.errors.append("If you claim a venting exclusion, you can't also have a leak detected with OGI.")

    if self.venting_exclusion and self.method21_result.data:
      if self.venting_exclusion.data == "Yes":
        if self.method21_result.data in ["Unintentional-leak"]:
          self.method21_result.errors.append("If you claim a venting exclusion, you can't also have a leak detected with Method 21.")

    if self.ogi_result.data in self.unintentional_leak:
      if self.method21_performed.data != "Yes":
        self.method21_performed.errors.append("If a leak was detected via OGI, Method 21 must be performed.")

    if self.ogi_performed.data == "No":
      if self.ogi_date.data:
        self.ogi_date.errors.append("Can't have an OGI inspection date if OGI was not performed")
      # print(f"{self.ogi_result.data=}")
      if self.ogi_result.data != PLEASE_SELECT:
        if self.ogi_result.data != "Not applicable as OGI was not performed":
          self.ogi_result.errors.append("Can't have an OGI result if OGI was not performed")

    if self.method21_performed.data == "No":
      if self.method21_date.data:
        self.method21_date.errors.append("Can't have an Method 21 inspection date if Method 21 was not performed")
      # print(f"{self.method21_result.data=}")
      if self.method21_result.data != PLEASE_SELECT:
        if self.method21_result.data != "Not applicable as Method 21 was not performed":
          self.method21_result.errors.append("Can't have an Method 21 result if Method 21 was not performed")

    # todo (consider) - you could also remove the option for not applicable rather than the following two tests
    if self.ogi_performed.data == "Yes":
      if self.ogi_result.data == "Not applicable as OGI was not performed":
        self.ogi_result.errors.append("Invalid response given your Q8 answer")

    if self.method21_performed.data == "Yes":
      if self.method21_result.data == "Not applicable as Method 21 was not performed":
        self.method21_result.errors.append("Invalid response given your Q11 answer")

    ###################################################################################################
    # perform any form level validation and append it to the form_errors property
    # This may not be useful, but if you want to have form level errors appear at the top of the error
    # header, put the logic here.
    ###################################################################################################
    # self.form_errors.append("I'm a form level error #1")
    # self.form_errors.append("I'm a form level error #2")

    ###################################################################################################
    # Search and replace the error messages associated with input fields to a custom message
    # For instance, the default 'float' error is changed because a typical user will not know what a
    # float value is (they will be more comfortable with the word 'numeric')
    ###################################################################################################
    for field in form_fields:
      field_errors = getattr(self, field).errors
      replace_list_occurrences(field_errors, error_message_replacement_dict)

    ###################################################################################################
    # Current logic to determine if form is valid the error dict must be empty.
    # #Consider other approaches
    ###################################################################################################
    form_valid = not bool(self.errors)

    logger.debug(f"after validate(): {self.errors=}")
    return form_valid

  def determine_contingent_fields(self) -> None:
    """
    Some fields change from Required to Optional (or vice versa), or are required if another field selected is 'other',
    This function updates all the contingent fields so they consistent with the input business logic.

    #Consider making validation more robust, for example, we may want to
    reorder so that the venting exclusion is last, (I tried this before, but it may break the biz logic)
    """

    # logger.debug(f"In determine_contingent_fields()")

    # If a venting exclusion is claimed, then a venting description is required and many fields become optional
    required_if_venting_exclusion = ["venting_description_1", ]
    optional_if_venting_exclusion = [
      "ogi_performed",
      "ogi_date",
      "ogi_result",
      "method21_performed",
      "method21_date",
      "method21_result",
      "initial_leak_concentration",
      "venting_description_2",
      "initial_mitigation_plan",
      "equipment_at_source",
      "equipment_other_description",
      "component_at_source",
      "component_other_description",
      "repair_timestamp",
      "final_repair_concentration",
      "repair_description",
      "additional_notes",
    ]
    venting_exclusion_test = self.venting_exclusion.data == "Yes"
    # logger.debug(f"\n\t{venting_exclusion_test=}, {self.venting_exclusion_test.data=}")
    change_validators_on_test(self, venting_exclusion_test, required_if_venting_exclusion, optional_if_venting_exclusion)

    required_if_ogi_performed = [
      "ogi_date",
      "ogi_result",
    ]
    ogi_test = self.ogi_performed.data == "Yes"
    change_validators_on_test(self, ogi_test, required_if_ogi_performed)

    required_if_method21_performed = [
      "method21_date",
      "method21_result",
      "initial_leak_concentration",
    ]
    method21_test = self.method21_performed.data == "Yes"
    change_validators_on_test(self, method21_test, required_if_method21_performed)

    required_if_venting_on_inspection = [
      "venting_description_2",
    ]
    venting2_test = False
    if self.ogi_result.data in self.venting_responses or self.method21_result.data in self.venting_responses:
      venting2_test = True
    change_validators_on_test(self, venting2_test, required_if_venting_on_inspection)

    required_if_unintentional = [
      "initial_mitigation_plan",
      "equipment_at_source",
      "repair_timestamp",
      "final_repair_concentration",
      "repair_description",
    ]
    unintentional_test = False
    if self.ogi_result.data in self.unintentional_leak or self.method21_result.data in self.unintentional_leak:
      unintentional_test = True
    change_validators_on_test(self, unintentional_test, required_if_unintentional)

    required_if_equipment_other = [
      "equipment_other_description",
    ]
    equipment_other_test = self.equipment_at_source.data == "Other"
    change_validators_on_test(self, equipment_other_test, required_if_equipment_other)

    required_if_component_other = [
      "component_other_description",
    ]
    component_other_test = self.component_at_source.data == "Other"
    change_validators_on_test(self, component_other_test, required_if_component_other)
