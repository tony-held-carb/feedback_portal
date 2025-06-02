"""
Functions and helper classes to support WTForms models.

Notes:
  * Best practice is to keep WTForm models in a separate file located next to the Flask app (e.g., app.py),
    and place helper routines in this utility module.

"""

import copy
import datetime
import json

from flask_wtf import FlaskForm
from wtforms import SelectField, ValidationError
from wtforms.fields import DateTimeField, DecimalField
from wtforms.validators import InputRequired, Optional

from arb.__get_logger import get_logger
from arb.portal.json_update_util import apply_json_patch_and_log
from arb.utils.constants import PLEASE_SELECT
from arb.utils.date_and_time import (
  datetime_to_ca_naive,
  iso8601_to_utc_dt
)
from arb.utils.diagnostics import list_differences
from arb.utils.json import make_dict_serializeable

__version__ = "1.0.0"

from arb.utils.json import deserialize_dict, make_dict_serializeable, wtform_types_and_values

logger, pp_log = get_logger()


def min_decimal_precision(min_digits: int):
  """
  Create a WTForms validator to ensure at least `min_digits` after the decimal point.

  Args:
      min_digits (int): Minimum number of decimal places required.

  Returns:
      Callable: A validator function to attach to a WTForms DecimalField.

  Example:
      >>> amount = DecimalField("Amount", validators=[
      ...     InputRequired(),
      ...     min_decimal_precision(2)
      ... ])
  """

  def _min_decimal_precision(form, field):
    if field.data is None:
      return

    try:
      value_str = str(field.data)
      if '.' in value_str:
        _, decimals = value_str.split('.')
        if len(decimals) < min_digits:
          raise ValidationError()
      elif min_digits > 0:
        raise ValidationError()
    except (ValueError, TypeError):
      raise ValidationError(
        f"Field must be a valid numeric value with at least {min_digits} decimal places."
      )

  return _min_decimal_precision


class RequiredIfTruthy:
  """
  WTForms validator: Makes a field required if another field is truthy.

  Notes:
      - Not currently in use.
      - Inspired by StackOverflow and WTForms documentation examples.

  Example:
      class MyForm(FlaskForm):
          other_field = StringField(...)
          my_field = StringField(validators=[RequiredIfTruthy('other_field')])
  """

  field_flags = ("requirediftruthy",)

  def __init__(self, other_field_name: str, message: str | None = None, other_field_invalid_values: list | None = None):
    self.other_field_name = other_field_name
    self.message = message
    if other_field_invalid_values is None:
      other_field_invalid_values = [False, [], {}, (), '', '0', '0.0', 0, 0.0]
    self.other_field_invalid_values = other_field_invalid_values
    logger.debug("RequiredIfTruthy initialized")

  def __call__(self, form, field):
    other_field = form[self.other_field_name]
    if other_field is None:
      raise Exception(f'No field named "{self.other_field_name}" in form')

    if other_field.data not in self.other_field_invalid_values:
      logger.debug("other_field is truthy → requiring this field")
      InputRequired(self.message).__call__(form, field)
    else:
      logger.debug("other_field is falsy → allowing this field to be optional")
      Optional(self.message).__call__(form, field)


class IfTruthy:
  """
  WTForms validator: Choose between InputRequired or Optional depending on truthiness of another field.

  Args:
      other_field_name (str): Name of the other WTForms field.
      falsy_values (list | None): List of values considered falsy.
      mode (str): One of 'required on truthy' or 'optional on truthy'.
      message (str | None): Validation error message to use.

  Raises:
      TypeError: If an unknown mode is provided.

  Example:
      class MyForm(FlaskForm):
          trigger = BooleanField(...)
          conditional = StringField(validators=[IfTruthy('trigger', mode='required on truthy')])
  """

  field_flags = ("iftruthy",)

  def __init__(self, other_field_name: str, falsy_values: list | None = None, mode: str = 'required on truthy', message: str | None = None):
    self.other_field_name = other_field_name
    if falsy_values is None:
      falsy_values = [False, [], {}, (), '', '0', '0.0', 0, 0.0]
    self.falsy_values = falsy_values

    if mode == 'required on truthy':
      self.validators = {'truthy': InputRequired, 'falsy': Optional}
    elif mode == 'optional on truthy':
      self.validators = {'truthy': Optional, 'falsy': InputRequired}
    else:
      raise TypeError(f"Unknown mode: {mode}")

    self.message = message

  def __call__(self, form, field):
    other_field = form[self.other_field_name]
    if other_field is None:
      raise Exception(f'No field named "{self.other_field_name}" in form')

    validator_class = self.validators['truthy'] if other_field.data not in self.falsy_values else self.validators['falsy']
    validator_class(self.message).__call__(form, field)


def remove_validators(form: FlaskForm, field_names: list[str], validators_to_remove: list | None = None) -> None:
  """
  Dynamically remove specific validators from WTForms fields.

  Args:
      form (FlaskForm): The WTForms form instance.
      field_names (list[str]): List of field names to modify.
      validators_to_remove (list | None): Validator classes to remove. Defaults to [InputRequired].

  Notes:
    - Useful when validator logic depends on user input or view context.
    - Not currently in use

  """
  if validators_to_remove is None:
    validators_to_remove = [InputRequired]

  fields = get_wtforms_fields(form, include_csrf_token=False)
  for field in fields:
    if field in field_names:
      validators = form[field].validators
      for validator in validators:
        for validator_to_remove in validators_to_remove:
          if isinstance(validator, validator_to_remove):
            # logger.debug(f"{type(validators)}, {validators=}, {validator=}")
            validators.remove(validator)


def change_validators_on_test(form: FlaskForm,
                              bool_test: bool,
                              required_if_true: list[str],
                              optional_if_true: list[str] | None = None
                              ) -> None:
  """
  Change validator associated with a wtf form based on a boolean test.

  If bool_test is True:
    Optional validators will be changed to InputRequired for each form element in required_if_true.
    InputRequired validators will be changed to Optional for each form element in optional_if_true.

  If bool_test is False:
    InputRequired validators will be changed to Optional for each form element in required_if_true.
    Optional validators will be changed to InputRequired for each form element in optional_if_true.
  Args:
    form (FlaskForm): wtform
    bool_test (bool): Condition to test for validation change
    required_if_true (list[str]): wtform elements that should be set to InputRequired if bool_test is True
                             or set to Optional if bool_test is False
    optional_if_true (list[str] | None): wtform elements that should be set to Optional if bool_test is True
                                  or set to InputRequired if bool_test is False
  """
  if optional_if_true is None:
    optional_if_true = []

  if bool_test:
    change_validators(form,
                      field_names_to_change=required_if_true,
                      old_validator=Optional,
                      new_validator=InputRequired,
                      )

    change_validators(form,
                      field_names_to_change=optional_if_true,
                      old_validator=InputRequired,
                      new_validator=Optional,
                      )
  else:
    change_validators(form,
                      field_names_to_change=required_if_true,
                      old_validator=InputRequired,
                      new_validator=Optional,
                      )

    change_validators(form,
                      field_names_to_change=optional_if_true,
                      old_validator=Optional,
                      new_validator=InputRequired,
                      )


def change_validators(form: FlaskForm,
                      field_names_to_change: list[str],
                      old_validator,
                      new_validator
                      ) -> None:
  """
  Replace one validator with another for a given set of form field_names.

  Args:
      form (FlaskForm): WTForms form instance.
      field_names_to_change (list[str]): List of field names to update.
      old_validator: Validator class to be removed (e.g., Optional).
      new_validator: Validator class to be added (e.g., InputRequired).

  Example:
      >>> change_validators(form, ["comment"], Optional, InputRequired)
  """
  field_names = get_wtforms_fields(form, include_csrf_token=False)
  for field_name in field_names:
    if field_name in field_names_to_change:
      validators = form[field_name].validators
      for i, validator in enumerate(validators):
        if isinstance(validator, old_validator):
          validators[i] = new_validator()


def wtf_count_errors(form: FlaskForm, log_errors: bool = False) -> dict:
  """
  Count errors on a WTForm.

  Args:
      form (FlaskForm): The form to inspect.
      log_errors (bool): If True, log all errors to debug log.

  Returns:
      dict: {
          'elements_with_errors': int,
          'element_error_count': int,
          'wtf_form_error_count': int,
          'total_error_count': int
      }

  Notes:
    * make sure form.validate_on_submit() is called first or the error information will be undefined
    * form level errors are for overall form integrity and not associated with a single field's validation

  Example:
      >>> errors = wtf_count_errors(form)
      >>> print(errors["total_error_count"])

  """
  error_count_dict = {
    'elements_with_errors': 0,
    'element_error_count': 0,
    'wtf_form_error_count': 0,
    'total_error_count': 0,
  }

  if log_errors:
    logger.debug(f"Form errors are: {form.errors}")

  for field, error_list in form.errors.items():
    if field is None:
      error_count_dict['wtf_form_error_count'] += len(error_list)
    else:
      error_count_dict['elements_with_errors'] += 1
      error_count_dict['element_error_count'] += len(error_list)

  error_count_dict['total_error_count'] = (
      error_count_dict['element_error_count'] +
      error_count_dict['wtf_form_error_count']
  )

  return error_count_dict


def model_to_wtform(model,
                    wtform: FlaskForm,
                    json_column: str = "misc_json") -> None:
  """
  Populate a WTForm from a SQLAlchemy model's JSON column.

  This function loads the model's JSON field (typically 'misc_json') and
  sets WTForms field `.data` and `.raw_data` accordingly. Required for correct rendering
  and validation of pre-filled forms.

  Args:
      model: SQLAlchemy model instance with a JSON column.
      wtform (FlaskForm): The WTForm instance to populate.
      json_column (str): The attribute name of the model's JSON column (default is "misc_json").

  Raises:
      ValueError: If a datetime field cannot be parsed correctly.
      TypeError: If an unsupported object type is passed.

  Notes:
      - Datetime strings are assumed to be in ISO8601 UTC format and converted to Pacific time.
      - Decimal fields are coerced to float.
      - Fields in the JSON but not in the form are ignored.
  """
  model_json_dict = getattr(model, json_column)
  logger.debug(f"model_to_wtform called with model={model}, json={model_json_dict}")

  # Ensure dict, not str
  if isinstance(model_json_dict, str):
    try:
      model_json_dict = json.loads(model_json_dict)
      logger.debug("Parsed JSON string into dict.")
    except json.JSONDecodeError:
      logger.warning(f"Invalid JSON in model's '{json_column}' column.")
      model_json_dict = {}

  if model_json_dict is None:
    model_json_dict = {}

  if "id_incidence" in model_json_dict and model_json_dict["id_incidence"] != model.id_incidence:
    logger.warning(f"[model_to_wtform] MISMATCH: model.id_incidence={model.id_incidence} "
                   f"!= misc_json['id_incidence']={model_json_dict['id_incidence']}")

  form_fields = get_wtforms_fields(wtform)
  model_fields = list(model_json_dict.keys())

  list_differences(
    model_fields, form_fields,
    iterable_01_name="SQLAlchemy Model JSON",
    iterable_02_name="WTForm Fields",
    print_warning=False
  )

  # Use utilities to get type map and convert model dict
  type_map, _ = wtform_types_and_values(wtform)
  parsed_dict = deserialize_dict(model_json_dict, type_map, convert_time_to_ca=True)

  for field_name in form_fields:
    field = getattr(wtform, field_name)
    model_value = parsed_dict.get(field_name)

    # Set field data and raw_data for proper rendering/validation
    field.data = model_value
    field.raw_data = format_raw_data(field, model_value)

    logger.debug(f"Set {field_name=}, data={field.data}, raw_data={field.raw_data}")


def format_raw_data(field, value) -> list[str]:
  """
  Generate WTForms-compatible raw_data from a Python value.

  This helper function is used to populate the `.raw_data` attribute
  of WTForms fields. This is critical for validation, especially when
  the form has not been submitted via POST but needs to render with
  default or pre-populated values.

  Args:
      field : A WTForms field object (e.g., StringField, DateTimeField).
      value : The value to be assigned to the field. Can be a string, number, or datetime.

  Returns:
      list[str]: A list with a single string element representing the value, as expected by WTForms.

  Raises:
      ValueError: If the value is of an unsupported type.

  Examples:
      >>> from wtforms.fields import DateTimeField, StringField
      >>> from datetime import datetime, timezone
      >>> field = DateTimeField()
      >>> dt = datetime(2025, 4, 22, 18, 30, tzinfo=timezone.utc)
      >>> format_raw_data(field, dt)
      ['2025-04-22T11:30:00']  # Converted to Pacific

      >>> format_raw_data(field, "hello")
      ['hello']

  Notes:
      - Datetime objects must be naive local times.
      - Floats, ints, and strings are stringified.
      - Complex or nested structures will raise an exception unless explicitly supported.
  """
  if value is None:
    return []

  if isinstance(value, str):
    return [value]

  elif isinstance(value, (int, float, complex)):
    return [str(value)]

  elif isinstance(value, datetime.datetime):
    if isinstance(field, DateTimeField):
      if value.tzinfo is None:
        return [value.strftime("%Y-%m-%dT%H:%M")]
      else:
        raise TypeError(f"Attempt to set a DateTimeField with non-naive datetime object {value=!r}")
    else:
      return [value.isoformat()]

  raise ValueError(f"Unsupported type for raw_data: {type(value)} with value {value}")


def wtform_to_model(model,
                    wtform: FlaskForm,
                    ignore_fields: list[str] | None = None) -> None:
  """
  Update a SQLAlchemy model’s JSON column using data from a WTForm.

  Args:
      model: SQLAlchemy model instance.
      wtform (FlaskForm): The form containing updated data.
      ignore_fields (list[str] | None): List of form field names to skip. Useful for disabled fields.

  Example:
      >>> wtform_to_model(model, form, ignore_fields=["id_incidence"])
  """
  if ignore_fields is None:
    ignore_fields = []

  payload_all, payload_changes = get_payloads(model, wtform, ignore_fields)
  logger.info(f"wtform_to_model payload_all: {payload_all}")
  logger.info(f"wtform_to_model payload_changes: {payload_changes}")

  update_model_with_payload(model, payload_changes)


def get_payloads(model,
                 wtform: FlaskForm,
                 ignore_fields: list[str] | None = None) -> tuple[dict, dict]:
  """
  Generate all values and changed values from a form for updating a model.

  Args:
      model: SQLAlchemy model instance with JSON field `misc_json`.
      wtform (FlaskForm): The form used to extract updated values.
      ignore_fields (list[str] | None): Fields to ignore.

  Returns:
      tuple[dict, dict]: (payload_all, payload_changes)
          - payload_all: all fields from the form
          - payload_changes: only changed fields vs. model JSON

  Notes:
      - Values are compared against existing model JSON to detect changes.
  """
  if ignore_fields is None:
    ignore_fields = []

  payload_all = {}
  payload_changes = {}

  model_json_dict = getattr(model, "misc_json") or {}
  logger.debug(f"{model_json_dict=}")

  model_field_names = list(model_json_dict.keys())
  form_field_names = get_wtforms_fields(wtform)

  list_differences(model_field_names,
                   form_field_names,
                   iterable_01_name="SQLAlchemy Model",
                   iterable_02_name="WTForm Fields",
                   print_warning=False,
                   )

  for form_field_name in form_field_names:
    field = getattr(wtform, form_field_name)
    field_value = field.data
    model_value = model_json_dict.get(form_field_name)

    if form_field_name in ignore_fields:
      continue

    # skipping empty strings if the model is "" or None
    if field_value == "":
      if model_value in [None, ""]:
        continue

    # Only persist "Please Select" if overwriting a meaningful value.
    if isinstance(field, SelectField) and field_value == PLEASE_SELECT:
      if model_value in [None, ""]:
        continue

    payload_all[form_field_name] = field_value

    # todo - object types are not being seen as equivalent (because they are serialized strings)
    #        need to update logic - check out prep_payload_for_json for uniform approach
    if model_value != field_value:
      payload_changes[form_field_name] = field_value

  return payload_all, payload_changes



def prep_payload_for_json(payload: dict,
                          type_matching_dict: dict = None) -> dict:
  """
  Prepare a payload dictionary for JSON serialization.

  Allows 'Please Select' to be stored as-is.

  Ensures:
    - datetime → ISO8601 UTC string
    - decimal.Decimal → float
    - Values in `type_matching_dict` are explicitly cast to the specified types

  Args:
      payload (dict): Dictionary of key/value updates for the model.
      type_matching_dict (dict): Optional mapping of key names to expected types,
                                 e.g., {"id_incidence": int, "some_flag": bool}

  Returns:
      dict: A transformed copy of the payload suitable for JSON serialization.
  """
  type_matching_dict = type_matching_dict or {"id_incidence": int}

  return make_dict_serializeable(payload,
                                 type_map=type_matching_dict,
                                 convert_time_to_ca=True)



def update_model_with_payload(model,
                              payload: dict,
                              json_field: str = "misc_json",
                              comment: str = "") -> None:
  """
  Apply a JSON-safe payload to a model's JSON column and mark it as changed.

  Args:
      model: SQLAlchemy model instance to update.
      payload (dict): Dictionary of updates to apply.
      json_field (str): Name of the model's JSON column (default is "misc_json").
      comment (str): Optional comment to include with update logging.

  Notes:
      - Calls `prep_payload_for_json` to ensure data integrity.
      - Uses `apply_json_patch_and_log` to track and log changes.
      - Deep-copies the existing JSON field to avoid side effects.
  """
  logger.debug(f"update_model_with_payload: {model=}, {payload=}")

  model_json = copy.deepcopy(getattr(model, json_field) or {})
  new_payload = prep_payload_for_json(payload)
  model_json.update(new_payload)

  # todo (future): Integrate real user once authentication is added
  apply_json_patch_and_log(
    model,
    json_field=json_field,
    updates=model_json,
    user="anonymous",
    comments=comment,
  )

  logger.debug(f"Model JSON updated: {getattr(model, json_field)=}")


def get_wtforms_fields(form: FlaskForm, include_csrf_token: bool = False) -> list[str]:
  """
  Return the sorted field names associated with a WTForms form.

  Args:
      form (FlaskForm): The WTForms form instance.
      include_csrf_token (bool): If True, include the 'csrf_token' field in the returned list.
          If False, 'csrf_token' will be excluded. Defaults to False.

  Returns:
      list[str]: A sorted list of field names present in the form.

  Example:
      >>> class SampleForm(FlaskForm):
      ...     name = StringField("Name")
      >>> form = SampleForm()
      >>> get_wtforms_fields(form)
      ['name']
  """
  field_names = [
    name for name in form.data
    if include_csrf_token or name != "csrf_token"
  ]
  field_names.sort()
  return field_names


def initialize_drop_downs(form: FlaskForm, default: str = None) -> None:
  """
  Set default values for uninitialized WTForms SelectFields.

  Args:
      form (FlaskForm): The form containing SelectField elements.
      default (str): Default value to assign if the field’s data is None.

  Example:
      >>> initialize_drop_downs(form, default="-- Choose One --")
  """
  if default is None:
    default = PLEASE_SELECT

  logger.debug("Initializing drop-downs...")
  for field in form:
    if isinstance(field, SelectField) and field.data is None:
      logger.debug(f"{field.name} set to default value: {default}")
      field.data = default


def build_choices(header: list[tuple[str, str, dict]], items: list[str]) -> list[tuple[str, str, dict]]:
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


def ensure_field_choice(field_name: str, field, choices: list[tuple[str, str] | tuple[str, str, dict]] | None = None) -> None:
  """
  Ensure that a WTForms field's current value is valid for its available choices.

  If `choices` is provided, this function sets `field.choices` to the new list.
  If `choices` is None, it uses the field's existing `.choices`. In either case,
  it validates that the current `field.data` is among the available options and
  resets it to "Please Select" if not.

  Both `field.data` and `field.raw_data` are reset to keep form behavior consistent.

  Args:
      field_name (str): The name of the field (used for logging).
      field: A WTForms-compatible field object (e.g., SelectField).
      choices (list[tuple[str, str]] | list[tuple[str, str, dict]] | None): Optional.
          New valid choices to apply to the field. If omitted, the current field.choices
          will be used. Each tuple should be:
            - (value, label), or
            - (value, label, metadata_dict)
          Only the first element (`value`) is used for validation.

  Example:
      >>> ensure_field_choice("sector", form.sector, [("oil", "Oil & Gas"), ("land", "Landfill")])
      >>> form.sector.choices
      [('oil', 'Oil & Gas'), ('land', 'Landfill')]

  Note:
      - Use this with SelectField or similar fields where `.choices` must be explicitly defined.
      - The reset value "Please Select" should match a placeholder value if one is used in your app.
  """
  if choices is None:
    # Use existing field choices if none are supplied
    choices = field.choices
  else:
    # Apply a new set of choices to the field
    field.choices = choices

  valid_values = {c[0] for c in choices}

  if field.data not in valid_values:
    logger.debug(f"{field_name}.data={field.data!r} not in valid options, resetting to '{PLEASE_SELECT}'")
    field.data = PLEASE_SELECT
    field.raw_data = [field.data]


def validate_selectors(form: FlaskForm, default: str = None) -> None:
  """
  Validate SelectFields submitted via GET where default values need to be considered invalid.

  This manually appends an error message for InputRequired fields set to the default placeholder.

  Args:
      form (FlaskForm): WTForm instance to validate.
      default (str): Placeholder/default value that should be considered invalid.

  Example:
      >>> validate_selectors(form)
  """
  if default is None:
    default = PLEASE_SELECT

  for field in form:
    if isinstance(field, SelectField):
      if field.data is None or field.data == default:
        for validator in field.validators:
          if isinstance(validator, InputRequired):
            msg = "This field is required."
            if msg not in field.errors:
              field.errors.append(msg)


def validate_no_csrf(form: FlaskForm, extra_validators: dict | None = None) -> bool:
  """
  Validate a form while skipping CSRF errors.

  This is useful for validating forms submitted via HTTP GET or forms
  rendered outside of standard POST workflows.

  Args:
      form (FlaskForm): The form to validate.
      extra_validators (dict | None): Additional validators for fields.

  Returns:
      bool: True if form is valid (excluding CSRF errors), False otherwise.

  Example:
      >>> if validate_no_csrf(form): handle_form()

  Notes:
    * This is useful in performing validation on a form created using the GET method,
    since the GET method will result in token failure issues.
  """
  logger.debug(f"validate_no_csrf() called:")
  form.validate(extra_validators=extra_validators)

  if form.errors and 'csrf_token' in form.errors:
    del form.errors['csrf_token']

  csrf_field = getattr(form, 'csrf_token', None)
  if csrf_field:
    if csrf_field.errors:
      if 'The CSRF token is missing.' in csrf_field.errors:
        csrf_field.errors.remove('The CSRF token is missing.')

  form_valid = not bool(form.errors)

  logger.debug(f"after validate_no_csrf() called: {form_valid=}, {form.errors=}")
  return form_valid


def run_diagnostics():
  """
  Run a suite of basic diagnostics to verify that the key utilities in `wtf_forms_util.py` function as expected.

  This diagnostic:
    - Creates a mock WTForm with required fields.
    - Applies validator modifications.
    - Transfers data between the form and a fake SQLAlchemy-like model.
    - Checks form error reporting.
    - Logs all actions for manual review.

  Notes:
      This test does not rely on an actual Flask app context or database.
      It is meant for standalone logic verification and logging demonstration.

  Example:
      >>> if __name__ == "__main__":
      ...     run_diagnostics()
  """

  class DummyModel:
    """Mock SQLAlchemy model with JSON-like attribute."""

    def __init__(self):
      self.misc_json = {
        "name": "Alice",
        "age": 30,
        "created_at": "2024-01-01T08:00:00Z"
      }

  class TestForm(FlaskForm):
    """Test WTForm."""
    name = SelectField('Name', choices=[(PLEASE_SELECT, PLEASE_SELECT), ("Alice", "Alice"), ("Bob", "Bob")],
                       validators=[InputRequired()])
    age = DecimalField('Age', validators=[InputRequired()])
    created_at = DateTimeField('Created At', format="%Y-%m-%dT%H:%M", validators=[InputRequired()])

  from werkzeug.datastructures import MultiDict

  logger.info("Running WTForms diagnostics...")

  form = TestForm(formdata=MultiDict({
    "name": "Alice",
    "age": "30.00",
    "created_at": "2024-01-01T00:00"
  }))

  model = DummyModel()

  # Ensure defaults work
  initialize_drop_downs(form)

  # Transfer model → form
  model_to_wtform(model, form)
  logger.info(f"Model → Form: name={form.name.data}, age={form.age.data}, created_at={form.created_at.data}")

  # Form → model (round-trip)
  wtform_to_model(model, form)
  logger.info(f"Updated model.misc_json: {model.misc_json}")

  # Count errors
  error_summary = wtf_count_errors(form, log_errors=True)
  logger.info(f"Error summary: {error_summary}")

  # Test validator manipulation
  logger.info("Testing change_validators...")
  change_validators(form, field_names_to_change=["age"], old_validator=InputRequired, new_validator=Optional)
  for field_name in ["name", "age", "created_at"]:
    logger.debug(f"{field_name} validators: {form[field_name].validators}")

  # Test selector validation (simulate bad input)
  form.name.data = PLEASE_SELECT
  validate_selectors(form)
  logger.info(f"Name field errors after selector validation: {form.name.errors}")

  # Test CSRF-less validation
  result = validate_no_csrf(form)
  logger.info(f"validate_no_csrf result: {result}, errors: {form.errors}")

  logger.info("WTForms diagnostics completed successfully.")

  if __name__ == '__main__':
    run_diagnostics()
