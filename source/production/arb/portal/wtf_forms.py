"""
Defines WTForms that can be used simplify HTML form creation and validation.

This module defines the forms that derive from FlaskForm.  General purpose
wt_forms functions are located in arb.utils.wtf_forms_util.py module.
"""
from flask_wtf import FlaskForm
from wtforms.fields import (DateTimeLocalField, DecimalField, EmailField, FloatField, IntegerField, SelectField, StringField, TextAreaField)
from wtforms.validators import (Email, InputRequired, Length, NumberRange, Optional, Regexp)

import arb.__get_logger as get_logger
from arb.portal.globals import Globals
from arb.utils.diagnostics import obj_diagnostics
from arb.utils.misc import replace_list_occurrences
from arb.utils.wtf_forms_util import change_validators_on_test, get_wtforms_fields, validate_selectors

from arb.portal.constants import GPS_RESOLUTION, PLEASE_SELECT, MIN_LATITUDE, MAX_LATITUDE, MIN_LONGITUDE, MAX_LONGITUDE

logger, pp_log = get_logger.get_logger(__name__, __file__)

DROPDOWN_DATE_FORMAT = "%Y-%m-%dT%H:%M"


class OGFeedback(FlaskForm):
  """
  Oil & Gas feedback form designed to be consistent with the O&G feedback spreadsheet.

  Notes:
  """

  msg = f"Latitudes must be blank or valid California number between {MIN_LATITUDE} and {MAX_LATITUDE}."
  latitude_validation = {"min": MIN_LATITUDE, "max": MAX_LATITUDE,
                         "message": msg}
  msg = f"Longitudes must be blank or valid California number between  {MIN_LONGITUDE} and {MAX_LONGITUDE}."
  longitude_validation = {"min": MIN_LONGITUDE, "max": MAX_LONGITUDE,
                          "message": msg}

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
    format=DROPDOWN_DATE_FORMAT,
  )

  label = "4.  Plume CARB Estimated Latitude"
  lat_carb = DecimalField(
    label=label,
    places=GPS_RESOLUTION,
    validators=[InputRequired(), NumberRange(**latitude_validation)],
  )

  label = "5.  Plume CARB Estimated Longitude"
  long_carb = DecimalField(
    label=label,
    places=GPS_RESOLUTION,
    validators=[InputRequired(), NumberRange(**longitude_validation)],
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
    format=DROPDOWN_DATE_FORMAT,
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
    format=DROPDOWN_DATE_FORMAT,
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
    format=DROPDOWN_DATE_FORMAT,
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
    # Dictionary to replace standard WTForm messages with alternative message
    error_message_replacement_dict = {"Not a valid float value.": "Not a valid numeric value."}

    ###################################################################################################
    # Add, Remove, or Modify validation at a field level here before the super is called (for example)
    ###################################################################################################
    self.determine_contingent_fields()

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
      if self.ogi_result.data != "Please Select":
        if self.ogi_result.data != "Not applicable as OGI was not performed":
          self.ogi_result.errors.append("Can't have an OGI result if OGI was not performed")

    if self.method21_performed.data == "No":
      if self.method21_date.data:
        self.method21_date.errors.append("Can't have an Method 21 inspection date if Method 21 was not performed")
      # print(f"{self.method21_result.data=}")
      if self.method21_result.data != "Please Select":
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
    form_fields = get_wtforms_fields(self)

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


class LandfillFeedback(FlaskForm):
  """
  Landfill feedback form designed to be consistent with the Landfill feedback spreadsheet.

  Notes:
  """

  msg = f"Latitudes must be blank or valid California number between {MIN_LATITUDE} and {MAX_LATITUDE}."
  latitude_validation = {"min": MIN_LATITUDE, "max": MAX_LATITUDE,
                         "message": msg}
  msg = f"Longitudes must be blank or valid California number between  {MIN_LONGITUDE} and {MAX_LONGITUDE}."
  longitude_validation = {"min": MIN_LONGITUDE, "max": MAX_LONGITUDE,
                          "message": msg}

  # Section 2
  # todo - likely have to change these to InputRequired(), Optional(), blank and removed
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

  label = "3.  Plume Observation Date"
  observation_timestamp = DateTimeLocalField(
    label=label,
    validators=[InputRequired()],
    format=DROPDOWN_DATE_FORMAT,
  )

  label = "4.  Plume Origin CARB Estimated Latitude"
  # I think lat/longs are failing because they were renamed ...

  lat_carb = DecimalField(
    label=label,
    places=GPS_RESOLUTION,
    # validators=[Optional(), NumberRange(**latitude_validation), min_decimal_precision(GPS_RESOLUTION)],
    validators=[Optional(), NumberRange(**latitude_validation)],
  )

  label = "5.  Plume Origin CARB Estimated Longitude"
  long_carb = DecimalField(
    label=label,
    places=GPS_RESOLUTION,
    # validators=[Optional(), NumberRange(**longitude_validation), min_decimal_precision(GPS_RESOLUTION)],
    validators=[Optional(), NumberRange(**longitude_validation)],
  )

  label = "6.  CARB Message ID"
  id_message = StringField(
    label=label,
    validators=[Optional()],
  )

  # Section 3
  label = "Q1.  Facility Name"
  facility_name = StringField(
    label=label,
    validators=[InputRequired()],
  )

  label = "Q2.  Facility SWIS ID"
  id_arb_swis = StringField(
    label=label,
    validators=[Optional()],
  )

  label = "Q3.  Contact Name"
  contact_name = StringField(
    label=label,
    validators=[InputRequired()],
  )
  # contact_phone = StringField(label="Contact Phone", validators=[InputRequired()])
  label = "Q4.  Contact Phone"
  message = "Invalid phone number. Phone number must be in format '(123) 456-7890' or '(123) 456-7890 x1234567'."
  contact_phone = StringField(
    label=label,
    validators=[InputRequired(),
                Regexp(regex=r"^\(\d{3}\) \d{3}-\d{4}( x\d{1,7})?$", message=message)
                ],
  )

  label = "Q5.  Contact Email"
  contact_email = EmailField(
    label=label,
    validators=[InputRequired(), Email()])

  # Section 4
  label = "Q6.  Date of owner/operator’s follow-up ground monitoring."
  inspection_timestamp = DateTimeLocalField(
    label=label,
    validators=[InputRequired(), ],
    format=DROPDOWN_DATE_FORMAT,
  )

  label = "Q7.  Instrument used to locate the leak (e.g., Fisher Scientific TVA2020; RKI Multigas Analyzer Eagle 2; TDL)."
  instrument = StringField(
    label=label,
    validators=[InputRequired()])

  label = "Q8.  Was a leak identified through prior knowledge or by follow-up monitoring after receipt of a CARB plume notice?"
  emission_identified_flag_fk = SelectField(
    label=label,
    choices=Globals.drop_downs["emission_identified_flag_fk"],
    validators=[InputRequired(), ],
  )

  label = (f"Q9.  If no leaks were found, please describe any events or activities that may have "
           f"contributed to the plume observed on the date provided in Section 2.")
  additional_activities = TextAreaField(
    label=label,
    validators=[Optional()],
  )

  # Section 5
  label = "Q10:  Maximum concentration of methane leak (in ppmv)."
  initial_leak_concentration = DecimalField(
    label=label,
    validators=[InputRequired()],
  )

  label = "Q11.  Please provide a revised latitude if the leak location differs from CARB's estimate in Section 2."
  lat_revised = DecimalField(
    label=label,
    places=GPS_RESOLUTION,
    # validators=[Optional(), NumberRange(**latitude_validation), min_decimal_precision(GPS_RESOLUTION)],
    validators=[Optional(), NumberRange(**latitude_validation)],
  )

  label = "Q12.  Please provide a revised longitude if the leak location differs from CARB's estimate in Section 2."
  long_revised = DecimalField(
    label=label,
    places=GPS_RESOLUTION,
    # validators=[Optional(), NumberRange(**longitude_validation), min_decimal_precision(GPS_RESOLUTION)],
    validators=[Optional(), NumberRange(**longitude_validation)],
  )

  label = "Q13:  Please select from the drop-down menu which option best matches the description of the leak."
  emission_type_fk = SelectField(
    label=label,
    choices=Globals.drop_downs["emission_type_fk"],
    validators=[InputRequired(), ],
  )

  label = "Q14.  Please select from the drop-down menu which option best describes the location of the leak."
  emission_location = SelectField(
    label=label,
    choices=Globals.drop_downs["emission_location"],
    validators=[InputRequired(), ],
  )

  label = (f"Q15.  Please provide a more detailed description of the leak location, "
           f"including grid ID number or component name, if applicable.")
  emission_location_notes = TextAreaField(
    label=label,
    validators=[],
  )

  label = "Q16.  Please select the most likely cause of the leak."
  emission_cause = SelectField(
    label=label,
    choices=Globals.drop_downs["emission_cause"],
    validators=[InputRequired(), ],
  )

  label = (f"Q17 (Optional).  Please select an alternative cause (only if suspected).  "
           f"This should not be the same as your Q16 response.")
  emission_cause_secondary = SelectField(
    label=label,
    choices=Globals.drop_downs["emission_cause_secondary"],
    validators=[Optional()],
  )

  label = (f"Q18 (Optional).  Please select an alternative cause (only if suspected).  "
           f"This should not be the same as your Q16 or Q17 responses.")
  emission_cause_tertiary = SelectField(
    label=label,
    choices=Globals.drop_downs["emission_cause_tertiary"],
    validators=[Optional()],
  )

  label = (f"Q19.  Please provide a more detailed description of the cause(s), "
           f"including the reason for and duration of any construction activity or downtime.")
  emission_cause_notes = TextAreaField(
    label=label,
    validators=[InputRequired()],
  )

  label = "Q20.  Describe any corrective actions taken."
  mitigation_actions = TextAreaField(
    label=label,
    validators=[InputRequired()],
  )

  label = "Q21.  Repair date."
  mitigation_timestamp = DateTimeLocalField(
    label=label,
    validators=[InputRequired()],
    format=DROPDOWN_DATE_FORMAT
  )

  label = "Q22.  Re-monitored date."
  re_monitored_timestamp = DateTimeLocalField(
    label=label,
    validators=[Optional()],
    format=DROPDOWN_DATE_FORMAT
  )

  label = "Q23.  Re-monitored methane concentration after repair (ppmv)."
  re_monitored_concentration = DecimalField(
    label=label,
    validators=[InputRequired()],
  )

  label = (f"Q24.  Was the leak location monitored in the most recent "
           f"prior quarterly/annual surface emissions or quarterly component leak monitoring event?")
  included_in_last_lmr = SelectField(
    label=label,
    choices=Globals.drop_downs["included_in_last_lmr"],
    validators=[InputRequired(), ],
  )

  label = "Q25.  If 'No' to Q24, please explain why the area was excluded from monitoring."
  included_in_last_lmr_description = TextAreaField(
    label=label,
    validators=[InputRequired()])

  label = "Q26.  Is this grid/component planned for inclusion in the next quarterly/annual leak monitoring?"
  planned_for_next_lmr = SelectField(
    label=label,
    choices=Globals.drop_downs["planned_for_next_lmr"],
    validators=[InputRequired(), ],
  )

  label = "Q27.  If 'No' to Q26, please state why the area will not be monitored."
  planned_for_next_lmr_description = TextAreaField(
    label=label,
    validators=[InputRequired()])

  label = "Q28.  Date of most recent surface emissions monitoring event (prior to this notification)."
  last_component_leak_monitoring_timestamp = DateTimeLocalField(
    label=label,
    validators=[InputRequired()],
    format=DROPDOWN_DATE_FORMAT
  )

  label = "Q29.  Date of most recent component leak monitoring event (prior to this notification)."
  last_surface_monitoring_timestamp = DateTimeLocalField(
    label=label,
    validators=[InputRequired()],
    format=DROPDOWN_DATE_FORMAT
  )

  label = "Q30. Additional notes or comments."
  additional_notes = TextAreaField(
    label=label,
    validators=[],
  )

  def update_contingent_selectors(self):
    """
    Update selector choices for emission causes based on the selected emission location.

    This method dynamically updates the primary, secondary, and tertiary emission cause fields
    based on the value of self.emission_location. It sets valid choices and resets any invalid
    selection to a safe default.

    Assumes:
        - self.emission_location, self.emission_cause,
          self.emission_cause_secondary, and self.emission_cause_tertiary
          are WTForms SelectField instances.
        - Globals.drop_downs_contingent contains a nested dict of contingent options.
    """
    logger.debug("Running update_contingent_selectors()")

    emission_location = self.emission_location.data
    logger.debug(f"Selected emission_location: {emission_location!r}")

    emission_cause_dict = Globals.drop_downs_contingent.get(
      "emission_cause_contingent_on_emission_location", {}
    )
    choices_raw = emission_cause_dict.get(emission_location, [])
    logger.debug(f"Available contingent causes: {choices_raw!r}")

    # Define headers
    primary_header = [
      ("Please Select", "Please Select", {"disabled": True}),
      ("Not applicable as no leak was detected", "Not applicable as no leak was detected", {}),
    ]
    secondary_tertiary_header = primary_header + [
      ("Not applicable as no additional leak cause suspected",
       "Not applicable as no additional leak cause suspected", {}),
    ]

    # Build full choices
    primary_choices = self._build_choices(primary_header, choices_raw)
    secondary_tertiary_choices = self._build_choices(secondary_tertiary_header, choices_raw)

    # Update each field
    self._update_selector("emission_cause", self.emission_cause, primary_choices)
    self._update_selector("emission_cause_secondary", self.emission_cause_secondary, secondary_tertiary_choices)
    self._update_selector("emission_cause_tertiary", self.emission_cause_tertiary, secondary_tertiary_choices)

  def _build_choices(self, header: list[tuple[str, str, dict]], items: list[str]) -> list[tuple[str, str, dict]]:
    """
    Combine header and choices into a list of triple tuples for WTForms.

    Args:
        header (list[tuple[str, str, dict]]): The static header items.
        items (list[str]): Dynamic items to append as (value, value, {}).

    Returns:
        list[tuple[str, str, dict]]: Combined list.
    """
    footer = [(item, item, {}) for item in items]
    return header + footer

  def _update_selector(self, field_name: str, field, choices: list[tuple[str, str, dict]]) -> None:
    """
    Update the field's choices and reset data if invalid.

    Args:
        field_name (str): The name of the field (for logging).
        field: The WTForms field to update.
        choices (list[tuple[str, str, dict]]): New valid choices.
    """
    field.choices = choices
    valid_values = {value for value, _, _ in choices}

    if field.data not in valid_values:
      logger.debug(f"{field_name}.data={field.data!r} not in valid options, resetting to 'Please Select'")
      field.data = "Please Select"
    # else:
    #   logger.debug(f"{field_name}.data={field.data!r} is valid")

  def validate(self, extra_validators=None):
    """
    Overriding validate to allow for form-level validation and inter-comparing fields.

    Args:
      extra_validators:

    """
    # Dictionary to replace standard WTForm messages with alternative message
    error_message_replacement_dict = {"Not a valid float value.": "Not a valid numeric value."}

    ###################################################################################################
    # Add, Remove, or Modify validation at a field level here before the super is called (for example)
    ###################################################################################################
    self.determine_contingent_fields()
    self.update_contingent_selectors()
    # todo - update contingent dropdowns

    ###################################################################################################
    # call the super to perform each fields individual validation (which saves to form.errors)
    # This will create the form.errors dictionary.  If there are form_errors they will be in the None key.
    # The form_errors will not affect if validate returns True/False, only the fields are considered.
    ###################################################################################################
    # logger.debug("in the validator before super")
    obj_diagnostics(self, message="in the validator before super")
    form_fields = get_wtforms_fields(self)

    for field_name in form_fields:
      field = getattr(self, field_name)
      logger.debug(f"field_name: {field_name}, {type(field.data)=}, {field.data=}, {type(field.raw_data)=}")

    super_return = super().validate(extra_validators=extra_validators)

    ###################################################################################################
    # Validating selectors explicitly ensures the same number of errors on GETS and POSTS for the same data
    ###################################################################################################
    validate_selectors(self, PLEASE_SELECT)

    ###################################################################################################
    # Perform any field level validation where one field is cross-referenced to another
    # The error will be associated with one of the fields
    ###################################################################################################

    if self.emission_identified_flag_fk.data == "No leak was detected":
      valid_options = ["Please Select",
                       "Not applicable as no leak was detected",
                       "Not applicable as no additional leak cause suspected",
                       ]
      if self.emission_type_fk.data not in valid_options:
        self.emission_type_fk.errors.append(f"Q8 and Q13 appear to be inconsistent")
      if self.emission_location.data not in valid_options:
        self.emission_location.errors.append(f"Q8 and Q14 appear to be inconsistent")
      if self.emission_cause.data not in valid_options:
        self.emission_cause.errors.append(f"Q8 and Q16 appear to be inconsistent")
      if self.emission_cause_secondary.data not in valid_options:
        self.emission_cause_secondary.errors.append(f"Q8 and Q17 appear to be inconsistent")
      if self.emission_cause_tertiary.data not in valid_options:
        self.emission_cause.errors.append(f"Q8 and Q18 appear to be inconsistent")

    # Q8 and Q13 should be coupled to Operator aware response
    elif self.emission_identified_flag_fk.data == "Operator was aware of the leak prior to receiving the CARB plume notification":
      valid_options = ["Please Select",
                       "Operator was aware of the leak prior to receiving the notification, and/or repairs were in progress on the date of the plume observation", ]
      if self.emission_type_fk.data not in valid_options:
        self.emission_type_fk.errors.append(f"Q8 and Q13 appear to be inconsistent")

    if self.emission_identified_flag_fk.data != "No leak was detected":
      invalid_options = ["Not applicable as no leak was detected", ]
      if self.emission_type_fk.data in invalid_options:
        self.emission_type_fk.errors.append(f"Q8 and Q13 appear to be inconsistent")
      if self.emission_location.data in invalid_options:
        self.emission_location.errors.append(f"Q8 and Q14 appear to be inconsistent")
      if self.emission_cause.data in invalid_options:
        self.emission_cause.errors.append(f"Q8 and Q16 appear to be inconsistent")
      if self.emission_cause_secondary.data in invalid_options:
        self.emission_cause_secondary.errors.append(f"Q8 and Q17 appear to be inconsistent")
      if self.emission_cause_tertiary.data in invalid_options:
        self.emission_cause_tertiary.errors.append(f"Q8 and Q18 appear to be inconsistent")

    if self.inspection_timestamp.data and self.mitigation_timestamp.data:
      if self.mitigation_timestamp.data < self.inspection_timestamp.data:
        self.mitigation_timestamp.errors.append(
          "Date of mitigation cannot be prior to initial site inspection.")

    # todo - add that 2nd and 3rd can be repeats
    ignore_repeats = ["Please Select",
                      "Not applicable as no leak was detected",
                      "Not applicable as no additional leak cause suspected",
                      ]

    if (self.emission_cause_secondary.data not in ignore_repeats and
        self.emission_cause_secondary.data in [self.emission_cause.data]):
      self.emission_cause_secondary.errors.append(f"Q17 appears to be a repeat")

    if (self.emission_cause_tertiary.data not in ignore_repeats and
        self.emission_cause_tertiary.data in [self.emission_cause.data, self.emission_cause_secondary.data]):
      self.emission_cause_secondary.errors.append(f"Q18 appears to be a repeat")

    # not sure if this test makes sense since they may have know about it prior to the plume (going to comment out)
    # if self.observation_timestamp.data and self.inspection_timestamp.data:
    #   if self.inspection_timestamp.data < self.observation_timestamp.data:
    #     self.inspection_timestamp.errors.append(
    #       "Date of inspection cannot be prior to date of initial plume observation.")

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
    form_fields = get_wtforms_fields(self)

    for field in form_fields:
      field_errors = getattr(self, field).errors
      replace_list_occurrences(field_errors, error_message_replacement_dict)

    ###################################################################################################
    # Current logic to determine if form is valid the error dict must be empty.
    # #Consider other approaches
    ###################################################################################################
    form_valid = not bool(self.errors)

    return form_valid

  def determine_contingent_fields(self) -> None:
    """
    Some fields change from Required to Optional (or vice versa), or are required if another field selected is 'other',
    This function updates all the contingent fields so they consistent with the input business logic.

    #Consider making validation more robust, for example, we may want to
    reorder so that the venting exclusion is last, (I tried this before, but it may break the biz logic)
    """
    # If a venting exclusion is claimed, then a venting description is required and many fields become optional
    required_if_emission_identified = [
      "additional_activities",
      "initial_leak_concentration",
      # "lat_revised",
      # "long_revised",
      "emission_type_fk",
      "emission_location",
      # "emission_location_notes",
      "emission_cause",
      # "emission_cause_secondary",
      # "emission_cause_tertiary",
      "emission_cause_notes",
      "mitigation_actions",
      "mitigation_timestamp",
      "re_monitored_timestamp",
      "re_monitored_concentration",
      "included_in_last_lmr",
      "included_in_last_lmr_description",
      "planned_for_next_lmr",
      "planned_for_next_lmr_description",
      "last_surface_monitoring_timestamp",
      "last_component_leak_monitoring_timestamp",
      "additional_notes",
    ]
    # todo - update logic for new selectors
    emission_identified_test = self.emission_identified_flag_fk.data != "No leak was detected"
    # print(f"{emission_identified_test=}")
    change_validators_on_test(self, emission_identified_test, required_if_emission_identified)

    if emission_identified_test:
      lmr_included_test = self.included_in_last_lmr.data == "No"
      logger.debug(f"\n\t{lmr_included_test=}")
      change_validators_on_test(self, lmr_included_test, ["included_in_last_lmr_description"])

      lmr_planned_test = self.planned_for_next_lmr.data == "No"
      logger.debug(
        f"\n\t{lmr_planned_test=}")
      change_validators_on_test(self, lmr_planned_test, ["planned_for_next_lmr_description"])
