"""
Landfill feedback form definition for the ARB Feedback Portal (WTForms).

This module defines the `LandfillFeedback` class, a comprehensive WTForms-based
HTML form for collecting information on methane emission inspections and responses
at landfill sites. The form is organized into multiple logical sections and includes
dynamic dropdown behavior, conditional validation, and cross-field logic.

Key Features:
-------------
- Uses `FlaskForm` as a base and is rendered using Bootstrap-compatible templates.
- Dropdowns support conditional dependencies using `Globals.drop_downs_contingent`.
- Validators are programmatically adjusted to enforce or relax constraints based on user input.
- Supports optional "Other" fields that are only required when triggered.
- Final validation is managed via a custom `validate()` override.

Example Usage:
--------------
  form = LandfillFeedback()
  form.process(request.form)

  if form.validate_on_submit():
    # Process and store form data
    save_landfill_feedback(form.data)

Notes:
------
- The `update_contingent_selectors()` method updates selector/contingent choices.
- The `determine_contingent_fields()` method enforces dynamic field-level validation.
- Intended for use with the `landfill_incidence_update` route and similar flows.
- General-purpose WTForms utilities are located in:
    arb.utils.wtf_forms_util.py
"""

from pathlib import Path

from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, DecimalField, EmailField, IntegerField, SelectField, StringField, TextAreaField
from wtforms.validators import Email, InputRequired, NumberRange, Optional, Regexp

from arb.__get_logger import get_logger
from arb.portal.constants import GPS_RESOLUTION, HTML_LOCAL_TIME_FORMAT, LATITUDE_VALIDATION, LONGITUDE_VALIDATION, PLEASE_SELECT
from arb.portal.globals import Globals
from arb.utils.diagnostics import obj_diagnostics
from arb.utils.misc import replace_list_occurrences
from arb.utils.wtf_forms_util import build_choices, change_validators_on_test, ensure_field_choice, get_wtforms_fields, validate_selectors

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


class LandfillFeedback(FlaskForm):
  """
  WTForms form class for collecting landfill feedback data.

  Captures user-submitted information about methane emissions,
  inspections, corrective actions, and contact details related to
  landfill facility operations.

  Notes:
    - Some fields are conditionally validated depending on selections.
    - The form dynamically updates contingent dropdowns using
      `update_contingent_selectors()`.
    - Final validation is enforced in the `validate()` method.
  """

  # Section 2
  # todo - likely have to change these to InputRequired(), Optional(), blank and removed
  # label = "1.  Incidence/Emission ID"
  id_incidence = IntegerField(
    "Incidence/Emission ID",
    validators=[Optional()],
    render_kw={"readonly": True}
  )

  label = "2.  Plume ID(s)"
  id_plume = IntegerField(
    label=label,
    validators=[InputRequired(), NumberRange(min=1, message="Plume ID must be a positive integer")],
  )  # REFERENCES plumes (id_plume)

  label = "3.  Plume Observation Date"
  observation_timestamp = DateTimeLocalField(
    label=label,
    validators=[InputRequired()],
    format=HTML_LOCAL_TIME_FORMAT,
  )

  label = "4.  Plume Origin CARB Estimated Latitude"
  # I think lat/longs are failing because they were renamed ...

  lat_carb = DecimalField(
    label=label,
    places=GPS_RESOLUTION,
    # validators=[Optional(), NumberRange(**LATITUDE_VALIDATION), min_decimal_precision(GPS_RESOLUTION)],
    validators=[Optional(), NumberRange(**LATITUDE_VALIDATION)],
  )

  label = "5.  Plume Origin CARB Estimated Longitude"
  long_carb = DecimalField(
    label=label,
    places=GPS_RESOLUTION,
    # validators=[Optional(), NumberRange(**LONGITUDE_VALIDATION), min_decimal_precision(GPS_RESOLUTION)],
    validators=[Optional(), NumberRange(**LONGITUDE_VALIDATION)],
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
    format=HTML_LOCAL_TIME_FORMAT,
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
    # validators=[Optional(), NumberRange(**LATITUDE_VALIDATION), min_decimal_precision(GPS_RESOLUTION)],
    validators=[Optional(), NumberRange(**LATITUDE_VALIDATION)],
  )

  label = "Q12.  Please provide a revised longitude if the leak location differs from CARB's estimate in Section 2."
  long_revised = DecimalField(
    label=label,
    places=GPS_RESOLUTION,
    # validators=[Optional(), NumberRange(**LONGITUDE_VALIDATION), min_decimal_precision(GPS_RESOLUTION)],
    validators=[Optional(), NumberRange(**LONGITUDE_VALIDATION)],
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
    format=HTML_LOCAL_TIME_FORMAT
  )

  label = "Q22.  Re-monitored date."
  re_monitored_timestamp = DateTimeLocalField(
    label=label,
    validators=[Optional()],
    format=HTML_LOCAL_TIME_FORMAT
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
    format=HTML_LOCAL_TIME_FORMAT
  )

  label = "Q29.  Date of most recent component leak monitoring event (prior to this notification)."
  last_surface_monitoring_timestamp = DateTimeLocalField(
    label=label,
    validators=[InputRequired()],
    format=HTML_LOCAL_TIME_FORMAT
  )

  label = "Q30. Additional notes or comments."
  additional_notes = TextAreaField(
    label=label,
    validators=[],
  )

  label = "1. CARB internal notes"
  carb_notes = TextAreaField(
    label=label,
    validators=[],
  )

  def update_contingent_selectors(self) -> None:
    """
    Update contingent dropdown field choices based on current field selections.

    This method looks up selector/contingent relationships defined in
    `Globals.drop_downs_contingent` and dynamically modifies the `choices`
    for child fields when a selector field has a known dependency.

    This method dynamically updates the primary, secondary, and tertiary
    emission cause fields based on the value of `self.emission_location`. It
    ensures valid dropdown options and clears invalid selections.

    Assumes:
      - `self.emission_location`, `self.emission_cause`,
        `self.emission_cause_secondary`, and `self.emission_cause_tertiary`
        are all `SelectField` instances.
      - `Globals.drop_downs_contingent` contains a nested dictionary of
        location-contingent dropdown options.

    Returns:
      None
    """
    # todo - update contingent dropdowns?

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
      (PLEASE_SELECT, PLEASE_SELECT, {"disabled": True}),
      ("Not applicable as no leak was detected",
       "Not applicable as no leak was detected", {}),
    ]
    secondary_tertiary_header = primary_header + [
      ("Not applicable as no additional leak cause suspected",
       "Not applicable as no additional leak cause suspected", {}),
    ]

    # Build full choices
    primary_choices = build_choices(primary_header, choices_raw)
    secondary_tertiary_choices = build_choices(secondary_tertiary_header, choices_raw)

    # Update each field's choices
    self.emission_cause.choices = primary_choices
    self.emission_cause_secondary.choices = secondary_tertiary_choices
    self.emission_cause_tertiary.choices = secondary_tertiary_choices

  def validate(self, extra_validators=None) -> bool:
    """
    Override WTForms default validation with custom cross-field logic.

    Ensures required fields are conditionally enforced based on upstream
    values, including:
      - Facility activity selections imply required contingent selections
      - If "Other" is chosen, corresponding text input must be filled
      - If leak is confirmed, additional emission details are required

    Returns:
      bool: True if form is valid, False otherwise.

    Notes:
      - Calls `determine_contingent_fields()` before validation to
        ensure field validators are correct.
      - Uses built-in `super().validate()` after adjusting validators.
    """

    logger.debug(f"validate() called.")
    form_fields = get_wtforms_fields(self)

    # Dictionary to replace standard WTForm messages with an alternative message
    error_message_replacement_dict = {"Not a valid float value.": "Not a valid numeric value."}

    ###################################################################################################
    # Add, Remove, or Modify validation at a field level here before the super is called (for example)
    ###################################################################################################
    self.determine_contingent_fields()
    self.update_contingent_selectors()

    ###################################################################################################
    # Set selectors with values not in their choices list to "Please Select"
    ###################################################################################################
    for field_name in form_fields:
      field = getattr(self, field_name)
      logger.debug(f"field_name: {field_name}, {type(field.data)=}, {field.data=}, {type(field.raw_data)=}")
      if isinstance(field, SelectField):
        ensure_field_choice(field_name, field)

    ###################################################################################################
    # call the super to perform each field's individual validation (which saves to form.errors)
    # This will create the form.errors dictionary.  If there are form_errors they will be in the None key.
    # The form_errors will not affect if validate returns True/False, only the fields are considered.
    ###################################################################################################
    # logger.debug("in the validator before super")
    obj_diagnostics(self, message="in the validator before super")

    super_return = super().validate(extra_validators=extra_validators)

    ###################################################################################################
    # Validating selectors explicitly ensures the same number of errors on GETS and POSTS for the same data
    ###################################################################################################
    validate_selectors(self, PLEASE_SELECT)

    ###################################################################################################
    # Perform any field level validation where one field is cross-referenced to another
    # The error will be associated with one of the fields
    ###################################################################################################
    # todo - move field level validation to separate function

    if self.emission_identified_flag_fk.data == "No leak was detected":
      valid_options = [PLEASE_SELECT,
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

    # Q8 and Q13 should be coupled to Operator-aware response
    elif self.emission_identified_flag_fk.data == "Operator was aware of the leak prior to receiving the CARB plume notification":
      valid_options = [PLEASE_SELECT,
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

    # todo - add that 2nd and 3rd can't be repeats
    ignore_repeats = [PLEASE_SELECT,
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
    for field in form_fields:
      field_errors = getattr(self, field).errors
      replace_list_occurrences(field_errors, error_message_replacement_dict)

    ###################################################################################################
    # Current logic to determine if form is valid the error dict must be empty.
    # #Consider other approaches
    ###################################################################################################
    form_valid = not bool(self.errors)

    return form_valid

  def determine_contingent_fields(self):
    """
    Add or remove field validators depending on contingent dropdown selections.

    Some dropdown options imply that no further input is needed (e.g.,
    selecting "No leak was detected" disables required validation on
    follow-up questions). This function clears or restores validators
    accordingly.

    These fields toggle between required and optional depending on related
    field values (e.g., dropdowns that are set to "Other", or location-dependent fields).
    Some validation rules involve mutually exclusive or fallback logic.

    Notes:
      - This function should be called before validation to sync requirements.
      - May need to re-order exclusions (e.g., venting) for edge cases.
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
      logger.debug(f"{lmr_included_test=}")
      change_validators_on_test(self, lmr_included_test, ["included_in_last_lmr_description"])

      lmr_planned_test = self.planned_for_next_lmr.data == "No"
      logger.debug(
        f"{lmr_planned_test=}")
      change_validators_on_test(self, lmr_planned_test, ["planned_for_next_lmr_description"])
