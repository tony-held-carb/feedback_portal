"""
Defines WTForms that can be used simplify HTML form creation and validation.

This module defines the forms that derive from FlaskForm.  General purpose
wt_forms functions are located in arb.utils.wtf_forms_util.py module.
"""
from flask_wtf import FlaskForm
from wtforms.fields import (DateTimeLocalField, DecimalField, EmailField, FloatField, IntegerField, SelectField, StringField, TextAreaField)
from wtforms.validators import (DataRequired, Email, InputRequired, Length, NumberRange, Optional, Regexp)

import arb.__get_logger as get_logger
from arb.portal.globals import Globals
from arb.utils.diagnostics import obj_diagnostics
from arb.utils.misc import replace_list_occurrences
from arb.utils.wtf_forms_util import change_validators_on_test, get_wtforms_fields, validate_selectors

logger, pp_log = get_logger.get_logger(__name__, __file__)

DROPDOWN_DATE_FORMAT = "%Y-%m-%dT%H:%M"


class OGFeedback(FlaskForm):
  """
  Oil & Gas feedback form designed to be consistent with the O&G feedback spreadsheet.

  Notes:
  """

  msg = f"Latitudes must be blank or valid California number between {Globals.MIN_LATITUDE} and {Globals.MAX_LATITUDE}."
  latitude_validation = {"min": Globals.MIN_LATITUDE, "max": Globals.MAX_LATITUDE,
                         "message": msg}
  msg = f"Longitudes must be blank or valid California number between  {Globals.MIN_LONGITUDE} and {Globals.MAX_LONGITUDE}."
  longitude_validation = {"min": Globals.MIN_LONGITUDE, "max": Globals.MAX_LONGITUDE,
                          "message": msg}

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
  lat_arb = DecimalField(
    label=label,
    places=Globals.GPS_RESOLUTION,
    validators=[Optional(), NumberRange(**latitude_validation)],
  )

  label = "5.  Plume CARB Estimated Longitude"
  long_arb = DecimalField(
    label=label,
    places=Globals.GPS_RESOLUTION,
    validators=[Optional(), NumberRange(**longitude_validation)],
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
    validators=[DataRequired(),
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
    validators=[],
    format=DROPDOWN_DATE_FORMAT,
  )

  label = "Q10. If you answered 'Yes' to Q8, what type of source was found using OGI?"
  ogi_result = SelectField(
    label=label,
    choices=Globals.drop_downs["ogi_result"],
    validators=[],
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
    validators=[],
    format=DROPDOWN_DATE_FORMAT,
  )

  label = "Q13. If you answered 'Yes' to Q11, what type of source was found using Method 21?"
  method21_result = SelectField(
    label=label,
    choices=Globals.drop_downs["method21_result"],
    validators=[],
  )

  label = "Q14. If you answered 'Yes' to Q11, what was the initial leak concentration in ppmv (if applicable)?"
  initial_leak_concentration = FloatField(
    label=label,
    validators=[],
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
    validators=[InputRequired(), ],
  )

  label = "Q20.  If you answered 'Other' for Q19, please provide an additional description of the component."
  component_other_description = TextAreaField(
    label=label, validators=[],
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
    validate_selectors(self, Globals.PLEASE_SELECT)

    ###################################################################################################
    # Perform any field level validation where one field is cross-referenced to another
    # The error will be associated with one of the fields
    ###################################################################################################
    # todo - likely need to update these to new OGI/Method 21 options, just commenting out now because
    # the change in drop down approaches may muddle things ...

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
        if self.ogi_result.data in "Unintentional-leak":
          self.ogi_result.errors.append("If you claim a venting exclusion, you can't also have a leak detected with OGI.")

    if self.venting_exclusion and self.method21_result.data:
      if self.venting_exclusion.data == "Yes":
        if self.method21_result.data in "Unintentional-leak":
          self.method21_result.errors.append("If you claim a venting exclusion, you can't also have a leak detected with Method 21.")

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
      "method21_performed",
    ]
    venting_exclusion = self.venting_exclusion.data == "Yes"
    # logger.debug(f"\n\t{venting_exclusion=}, {self.venting_exclusion.data=}")
    change_validators_on_test(self, venting_exclusion, required_if_venting_exclusion, optional_if_venting_exclusion)

    required_if_ogi_performed = [
      "ogi_date",
      "ogi_result",
    ]
    ogi_required = self.ogi_performed.data == "Yes"
    change_validators_on_test(self, ogi_required, required_if_ogi_performed)

    required_if_method21_performed = [
      "method21_date",
      "method21_result",
      "initial_leak_concentration",
    ]
    ogi_required = self.method21_performed.data == "Yes"
    change_validators_on_test(self, ogi_required, required_if_method21_performed)

    required_if_venting_on_inspection = [
      "venting_description_2",
    ]
    venting_responses = [
      "Venting-construction/maintenance",
      "Venting-routine",
    ]
    venting2_required = False
    if self.ogi_result.data in venting_responses or self.method21_result.data in venting_responses:
      venting2_required = True
    change_validators_on_test(self, venting2_required, required_if_venting_on_inspection)

    required_if_unintentional = [
      "initial_mitigation_plan",
      "equipment_at_source",
    ]
    unintentional_responses = [
      "Unintentional-leak",
      "Unintentional-non-component",
    ]
    unintentional_required = False
    if self.ogi_result.data in unintentional_responses or self.method21_result.data in unintentional_responses:
      unintentional_required = True
    change_validators_on_test(self, unintentional_required, required_if_unintentional)

    required_if_equipment_other = [
      "equipment_other_description",
    ]
    equipment_other_required = self.equipment_at_source.data == "Other"
    change_validators_on_test(self, equipment_other_required, required_if_equipment_other)

    required_if_component_other = [
      "component_other_description",
    ]
    component_other_required = self.component_at_source.data == "Other"
    change_validators_on_test(self, component_other_required, required_if_component_other)

    # todo - return here to complete oil & gas validation ... go to the bottom of form



class LandfillFeedback(FlaskForm):
  """
  Landfill feedback form designed to be consistent with the Landfill feedback spreadsheet.

  Notes:
  """

  msg = f"Latitudes must be blank or valid California number between {Globals.MIN_LATITUDE} and {Globals.MAX_LATITUDE}."
  latitude_validation = {"min": Globals.MIN_LATITUDE, "max": Globals.MAX_LATITUDE,
                         "message": msg}
  msg = f"Longitudes must be blank or valid California number between  {Globals.MIN_LONGITUDE} and {Globals.MAX_LONGITUDE}."
  longitude_validation = {"min": Globals.MIN_LONGITUDE, "max": Globals.MAX_LONGITUDE,
                          "message": msg}

  # Section 2
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
  lat_arb = DecimalField(
    label=label,
    places=Globals.GPS_RESOLUTION,
    # validators=[Optional(), NumberRange(**latitude_validation), min_decimal_precision(Globals.GPS_RESOLUTION)],
    validators=[Optional(), NumberRange(**latitude_validation)],
  )

  label = "5.  Plume Origin CARB Estimated Longitude"
  long_arb = DecimalField(
    label=label,
    places=Globals.GPS_RESOLUTION,
    # validators=[Optional(), NumberRange(**longitude_validation), min_decimal_precision(Globals.GPS_RESOLUTION)],
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
    validators=[DataRequired(),
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
    places=Globals.GPS_RESOLUTION,
    # validators=[Optional(), NumberRange(**latitude_validation), min_decimal_precision(Globals.GPS_RESOLUTION)],
    validators=[Optional(), NumberRange(**latitude_validation)],
  )

  label = "Q12.  Please provide a revised longitude if the leak location differs from CARB's estimate in Section 2."
  long_revised = DecimalField(
    label=label,
    places=Globals.GPS_RESOLUTION,
    # validators=[Optional(), NumberRange(**longitude_validation), min_decimal_precision(Globals.GPS_RESOLUTION)],
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
    validate_selectors(self, Globals.PLEASE_SELECT)

    ###################################################################################################
    # Perform any field level validation where one field is cross-referenced to another
    # The error will be associated with one of the fields
    ###################################################################################################
    # todo - update with new html selectors
    # emission_identified = self.emission_identified_flag_fk.data == Globals.drop_downs_rev["emission_identified_flag_fk"]["Yes"]
    #
    # emission_type_not_found = self.emission_type_fk.data == Globals.drop_downs_rev["emission_type_fk"]["Not found"]
    #
    # if self.emission_identified_flag_fk.data in [Globals.drop_downs_rev["emission_identified_flag_fk"]["Please Select"]]:
    #   pass
    # elif self.emission_identified_flag_fk.data in [Globals.drop_downs_rev["emission_identified_flag_fk"]["Yes"]]:
    #   if self.emission_type_fk.data in [Globals.drop_downs_rev["emission_type_fk"]["Not found"]]:
    #     msg = ("Answer inconsistency.  You answered 'Yes' to 'Was an emission source identified by follow-up monitoring?' "
    #            "yet selected 'Not found' for the emission type.")
    #     self.emission_type_fk.errors.append(msg)
    # elif self.emission_identified_flag_fk.data in [Globals.drop_downs_rev["emission_identified_flag_fk"]["No"]]:
    #   if self.emission_type_fk.data not in [Globals.drop_downs_rev["emission_type_fk"]["Not found"]]:
    #     msg = ("Answer inconsistency.  You answered 'No' to 'Was an emission source identified by follow-up monitoring?' "
    #            "yet did not select 'Not found' for the emission type.")
    #     self.emission_type_fk.errors.append(msg)

    if self.observation_timestamp.data and self.inspection_timestamp.data:
      if self.inspection_timestamp.data < self.observation_timestamp.data:
        self.inspection_timestamp.errors.append(
          "Date of inspection cannot be prior to date of initial plume observation.")

    if self.inspection_timestamp.data and self.mitigation_timestamp.data:
      if self.mitigation_timestamp.data < self.inspection_timestamp.data:
        self.mitigation_timestamp.errors.append(
          "Date of mitigation cannot be prior to initial site inspection.")

    # The last_surface_monitoring_timestamp and last_component_leak_monitoring_timestamp are
    # no longer required to be after the initial site inspection.

    # if self.last_surface_monitoring_timestamp.data and self.inspection_timestamp.data:
    #   if self.last_surface_monitoring_timestamp.data < self.inspection_timestamp.data:
    #     self.last_surface_monitoring_timestamp.errors.append(
    #       "Date of last surface emissions monitoring cannot be prior to initial site inspection.")
    #
    # if self.last_component_leak_monitoring_timestamp.data and self.inspection_timestamp.data:
    #   if self.last_component_leak_monitoring_timestamp.data < self.inspection_timestamp.data:
    #     self.last_component_leak_monitoring_timestamp.errors.append(
    #       "Date of last component leak monitoring cannot be prior to initial site inspection.")

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
      "initial_leak_concentration",
      # "lat_revised",
      # "long_revised",
      "emission_type_fk",
      "emission_type_notes",
      "emission_location",
      # "emission_location_notes",
      "emission_cause",
      # "emission_cause_secondary",
      # "emission_cause_tertiary",
      "emission_cause_notes",
      "mitigation_actions",
      "mitigation_timestamp",
      "re_monitored_concentration",
      "most_recent_prior_inspection",
      "last_surface_monitoring_timestamp",
      "last_component_leak_monitoring_timestamp",
      "included_in_last_lmr",
      "included_in_last_lmr_description",
      "planned_for_next_lmr",
      "planned_for_next_lmr_description",
    ]
    # todo - update logic for new selectors
    # emission_identified_value = self.emission_identified_flag_fk.data
    # emission_identified_yes = Globals.drop_downs_rev["emission_identified_flag_fk"]["Yes"]
    # emission_identified = emission_identified_value == emission_identified_yes
    # logger.debug(
    #   f"\n\t{emission_identified=}, {emission_identified_value=}, {emission_identified_yes=}")
    # change_validators_on_test(self, emission_identified, required_if_emission_identified)

    lmr_test = self.included_in_last_lmr.data == "No"
    logger.debug(f"\n\t{lmr_test=}")
    change_validators_on_test(self, lmr_test, ["included_in_last_lmr_description"])

    lmr_test = self.planned_for_next_lmr.data == "No"
    logger.debug(
      f"\n\t{lmr_test=}")
    change_validators_on_test(self, lmr_test, ["planned_for_next_lmr_description"])
