"""
Functions and helper classes to support WTForms models.

Notes:
  * Best practices to have the wtform models in a separate file in the same directory as the
  flask app (app.py) and have the helper routines in this file in a utils directory.

"""

import datetime
import decimal
import json
from typing import Any

from flask_wtf import FlaskForm
from sqlalchemy.orm.attributes import flag_modified
from wtforms import SelectField, ValidationError
from wtforms.fields import DateTimeField
from wtforms.validators import InputRequired, Optional

import arb.__get_logger as get_logger
from arb.utils.date_and_time import ca_naive_to_utc_datetime, datetime_to_ca_naive, iso8601_to_utc_dt
from arb.utils.diagnostics import list_differences
from arb.utils.sql_alchemy import get_sa_column_types, get_sa_fields

__version__ = "1.0.0"
logger, pp_log = get_logger.get_logger(__name__, __file__)

HTML_LOCAL_TIME_FORMAT = "%Y-%m-%dT%H:%M"


def min_decimal_precision(min_digits):
  """
  WTForms Validator to ensure that float values have required precision.

  Example Usage:
    amount = DecimalField('Amount', validators=[
                          DataRequired(),
                          min_decimal_precision(2)  # Ensure at least 2 decimal places
                          ])

  Args:
    min_digits (int): minimum number of decimal places required to ensure precision
  """

  def _min_decimal_precision(form, field):
    # Check if the field data is a valid number
    if field.data is None:
      return

    try:
      # Convert to string for easier precision check
      value_str = str(field.data)
      # Split on the decimal point
      if '.' in value_str:
        _, decimals = value_str.split('.')
        if len(decimals) < min_digits:
          raise ValidationError()
      else:
        # If there is no decimal point, precision is zero
        if min_digits > 0:
          raise ValidationError()
    except (ValueError, TypeError):
      raise ValidationError(f"Field must be a valid numeric value with at least {min_digits} decimal places.")

  return _min_decimal_precision


class RequiredIfTruthy:
  """
  Validator which makes a field required if another field is set and has a truthy value.
  Sources:
    - https://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms
    - https://wtforms.readthedocs.io/en/2.3.x/validators/
    - https://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms

  Notes:
    - Not currently in use
  """
  field_flags = ("requirediftruthy",)

  def __init__(self, other_field_name, message=None, other_field_invalid_values=None):
    self.other_field_name = other_field_name
    self.message = message
    # the other field must have a value not in other_field_invalid_values to be considered valid
    if other_field_invalid_values is None:
      other_field_invalid_values = [False, [], {}, (), '', '0', '0.0', 0, 0.0]
    self.other_field_invalid_values = other_field_invalid_values
    logger.debug(f"In __init__()")

  def __call__(self, form, field):
    # logger.debug(f"in __call__, {form=}, {field=}")
    # logger.debug(f"{self.other_field_name=}, {self.message}, {field=}")
    other_field = form[self.other_field_name]
    # logger.debug(f"{type(other_field.data)=}, {other_field.data=}")
    if other_field is None:
      raise Exception('no field named "%s" in form' % self.other_field_name)
    if other_field.data not in self.other_field_invalid_values:
      logger.debug('data required')
      InputRequired(self.message).__call__(form, field)
    else:
      logger.debug('data not required')
      Optional(self.message).__call__(form, field)


class IfTruthy:
  """
  Validator which makes a validator required/optional based on the value in another field.

  Sources:
    - https://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms
    - https://wtforms.readthedocs.io/en/2.3.x/validators/
    - https://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms

  Notes:
    - Not currently in use
  """
  field_flags = ("iftruthy",)

  def __init__(self, other_field_name, falsy_values=None, mode='required on truthy', message=None):
    """
    Have a field's validator be InputRequired or Optional based on the truthiness of the data in another field.

    if mode='required on truthy' and the other field is truthy, then validator is InputRequired
    if mode='required on truthy' and the other field is falsy, then validator is Optional
    if mode='optional on truthy' and the other field is truthy, then validator is Optional
    if mode='optional on truthy' and the other field is falsy, then validator is InputRequired

    Args:
      other_field_name (str): name of the other field that this validator is contingent upon
      falsy_values (list): values that are considered false for the other field
      mode (str): ('required on truthy'|'optional on truthy')
        determines which validator is used on truthy
      message (str): message passed to validator

    Notes:
      1) the other field's truthiness is determined if it is not in the falsy_value list

    Examples:

    """
    # logger.debug(f"In IfTruthy __init__")

    self.other_field_name = other_field_name
    # the other field must have a value not in other_field_invalid_values to be considered valid
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
    # logger.debug(f"in __call__, {form=}, {field=}")
    # logger.debug(f"{self.other_field_name=}, {self.falsy_values=}, {self.validators=}, {self.message}")
    other_field = form[self.other_field_name]
    # logger.debug(f"{type(other_field.data)=}, {other_field.data=}")
    if other_field is None:
      raise Exception('no field named "%s" in form' % self.other_field_name)
    if other_field.data not in self.falsy_values:
      # the other field is truthy
      self.validators['truthy'](self.message).__call__(form, field)
    else:
      self.validators['falsy'](self.message).__call__(form, field)


def remove_validators(form, field_names, validators_to_remove=None) -> None:
  """
  Dynamically remove validators from wtform fields.

  Args:
    form (FlaskForm): wtform
    field_names (list(str)): fields to remove validators from
    validators_to_remove (list): list validators you wish to remove

  Notes:
    - Validators are in a field dict named kwargs
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


def change_validators_on_test(form, bool_test, required_if_true, optional_if_true=None) -> None:
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
    required_if_true (list): wtform elements that should be set to InputRequired if bool_test is True
                             or set to Optional if bool_test is False
    optional_if_true (list|None): wtform elements that should be set to Optional if bool_test is True
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


def change_validators(form,
                      field_names_to_change,
                      old_validator=InputRequired,
                      new_validator=Optional) -> None:
  """
  For each element in a form, replace one type of validator for another in the element's validation list.

  Args:
    form (FlaskForm): wtform
    field_names_to_change (list(str)): form fields to change from the old_validator to the new_validator
    old_validator (InputRequired | Optional): Validator type to remove from an element's validation list.
    new_validator (InputRequired | Optional): Validator type to add from an element's validation list.

  Notes:

  """
  # logger.debug(f"\n\tin change_validators")
  # logger.debug(f"{field_names=}")
  # logger.debug(f"{old_validator=}")
  # logger.debug(f"{new_validator=}")
  fields = get_wtforms_fields(form, include_csrf_token=False)
  for field in fields:
    if field in field_names_to_change:
      validators = form[field].validators
      # logger.debug(f"{field} old {validators=}")
      for i, validator in enumerate(validators):
        # logger.debug(i, validator)
        if isinstance(validator, old_validator):
          # logger.debug(i, validator, validators[i])
          # logger.debug(f"Changing validator in field: {field} from {old_validator} to {new_validator}")
          validators[i] = new_validator()
      # logger.debug(f"{field} new {validators=}")


def wtf_count_errors(form, log_errors=False):
  """
  Count the number of elements with errors and the total number of errors in the wtform form.

  Args:
    form (FlaskForm):
    log_errors (bool): True if you want errors to be logged

  Returns (dict): dictionary with keys 'elements_with_errors' & 'element_error_count'

  Notes:
    * make sure form.validate_on_submit() is called first or the error information will be undefined
    * form level errors are for overall form integrity and not associated with a single field's validation

  """
  error_count_dict = {
    'elements_with_errors': 0,
    'element_error_count': 0,
    'wtf_form_error_count': 0,
    'total_error_count': 0, }

  if log_errors is True:
    logger.debug(f"Form errors are: {form.errors}")

  for field, error_list in form.errors.items():
    # form level errors are stored in the None key
    if field is None:
      error_count_dict['wtf_form_error_count'] = len(error_list)
    else:
      error_count_dict['elements_with_errors'] += 1
      error_count_dict['element_error_count'] += len(error_list)

  error_count_dict['total_error_count'] = error_count_dict['element_error_count'] + error_count_dict['wtf_form_error_count']

  return error_count_dict


def model_to_wtform(model: Any, wtform: FlaskForm, json_column: str = 'misc_json') -> None:
  """
  Populate a WTForm based on values from a SQLAlchemy model's JSON column.

  This function reads data from a model's JSON column and attempts to populate
  corresponding fields in a WTForm. model keys are matched to field names.

  Key's that are in the model but not in the wtform will be ignored.

  If a field is of type DateTimeField, then the model value must be a string in
  UTC ISO8601 format.

  This function also sets the WTForms `raw_data` attribute to ensure that validation
  works correctly when the form is rendered but not submitted via POST.

  Args:
      model (Any): A SQLAlchemy model instance containing a dynamic JSON column.
      wtform (FlaskForm): An instance of a Flask-WTF form.
      json_column (str): Name of the model attribute that stores JSON data (default: "misc_json").

  Raises:
      ValueError: If a value's type is unsupported for conversion into WTForms raw_data.

  Example:
      >>> class MyModel:
      ...     misc_json = '{"created_at": "2025-04-22T18:30:00Z", "name": "Test"}'
      >>> form = MyForm()  # with fields `created_at`, `name`
      >>> model_to_wtform(MyModel(), form)
      >>> print(form.created_at.data)  # datetime object in UTC
      >>> print(form.created_at.raw_data)  # ['2025-04-22T11:30:00'] in Pacific Time

  Limitations:
      - Assumes flat JSON structure (no nesting).
      - Assumes datetime fields are ISO8601 strings in UTC.
      - Does not support lists or custom field types unless manually extended.
  """
  # todo - lots of changes, need to review closely once the wtform_to_model works

  model_json_dict = getattr(model, json_column)
  logger.debug(f"model_to_wtform called with model: {model}, json: {model_json_dict}")

  # Parse string JSON if necessary
  if isinstance(model_json_dict, str):
    try:
      model_json_dict = json.loads(model_json_dict)
      logger.debug(f"Parsed JSON string into dict: {model_json_dict}")
    except json.JSONDecodeError:
      logger.warning(f"Invalid JSON in model's '{json_column}' column.")
      model_json_dict = {}

  if model_json_dict is None:
    model_json_dict = {}

  form_fields = get_wtforms_fields(wtform)
  model_fields = list(model_json_dict.keys())

  list_differences(
    model_fields, form_fields,
    iterable_01_name="SQLAlchemy Model JSON",
    iterable_02_name="WTForm Fields",
    print_warning=False
  )

  for attr_name in model_fields:
    if attr_name not in form_fields:
      continue

    attr_value = model_json_dict.get(attr_name)
    field = getattr(wtform, attr_name)

    if isinstance(field, DateTimeField):
      if attr_value is None:
        pass
      elif isinstance(attr_value, str):
        attr_value = iso8601_to_utc_dt(attr_value)
        attr_value = datetime_to_ca_naive(attr_value)
      else:
        raise ValueError(f"database field can't be converted to datetime: {attr_value=}")

    # Set field data and raw_data for proper rendering/validation
    field.data = attr_value
    field.raw_data = format_raw_data(field, attr_value)

    # todo (consider) update contingent fields here?

    logger.debug(f"Set {attr_name=} with data={field.data}, raw_data={field.raw_data}")


def format_raw_data(field: Any, value: Any) -> list[str]:
  """
  Generate WTForms-compatible raw_data from a Python value.

  This helper function is used to populate the `.raw_data` attribute
  of WTForms fields. This is critical for validation, especially when
  the form has not been submitted via POST but needs to render with
  default or pre-populated values.

  Args:
      field (Any): A WTForms field object (e.g., StringField, DateTimeField).
      value (Any): The value to be assigned to the field. Can be a string, number, or datetime.

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


def wtform_to_model(model, wtform, ignore_fields=None) -> None:
  """
  Update a SQLAlchemy model based on wtform contents

  Args:
    model (db.Model): SQLAlchemy model
    wtform (FlaskForm): form
    ignore_fields (list[str]): fields not considered in model update (likely because they are disabled in html form)

  Notes:

  """
  if ignore_fields is None:
    ignore_fields = []

  # obj_diagnostics(model, "in wtform_to_model")

  payload_all, payload_changes = get_payloads(model, wtform, ignore_fields)
  logger.info(f"wtform_to_model payload_all: {payload_all}")
  logger.info(f"wtform_to_model payload_changes: {payload_changes}")

  update_model_with_payload(model, payload_changes)


def get_payloads(model, wtform, ignore_fields=None) -> (dict, dict):
  """
  Create a dictionary payload_changes for a SQLAlchemy model based on wtform contents.

  Args:
    model (db.Model): SQLAlchemy model
    wtform (FlaskForm): form
    ignore_fields (list[str]): fields not considered in model update (likely because they are disabled in html form)

  Returns:
    tuple: A tuple containing payload_all, payload_changes.
      - payload_all (dict): all key, values associated with model.
      - payload_changes (dict): subset of payload_all were values will change.

  Notes:

  """
  if ignore_fields is None:
    ignore_fields = []

  payload_all = {}
  payload_changes = {}
  # obj_diagnostics(model, "in get_payload()")

  model_json_dict = getattr(model, 'misc_json')
  if model_json_dict is None:
    model_json_dict = {}
  logger.debug(f"{model_json_dict=}")

  if model_json_dict:
    model_fields = model_json_dict.keys()
  else:
    model_fields = {}
  # logger.debug(f"{model_fields=}")

  form_fields = get_wtforms_fields(wtform)
  # logger.debug(f"{form_fields=}")

  list_differences(model_fields,
                   form_fields,
                   iterable_01_name="SQLAlchemy Model",
                   iterable_02_name="WTForm Fields",
                   print_warning=False,
                   )

  for attr_name in form_fields:
    attr_value = getattr(wtform, attr_name).data
    # logger.debug(f"{attr_name} {type(attr_value)}:\n\t {attr_value}")

    if ignore_fields is None or attr_name not in ignore_fields:
      # logger.debug(f"Setting {attr_name} to {attr_value}")
      existing_value = model_json_dict.get(attr_name, None)
      payload_all[attr_name] = attr_value

      if existing_value != attr_value:
        payload_changes[attr_name] = attr_value

  return payload_all, payload_changes


def update_model_with_payload(model, payload, json_field='misc_json') -> None:
  """
  Create a dictionary payload for a SQLAlchemy model based on wtform contents

  Args:
    model (db.Model): SQLAlchemy model
    payload (dict): key value pairs to update in model
    json_field (str): Name of db column that stores json data

  Notes:
    - Current implementation updates fields in the json dictionary, but does not delete fields that do not change.


  """
  logger.debug(f"\n\t{type(model)=}, {model=}, {payload=}")
  model_fields = get_sa_fields(model)
  column_info = get_sa_column_types(model)
  logger.debug(f"\n\t{column_info=}")
  # logger.debug(f"{model_fields=}")

  # todo (consider), currently this routine only updates the key value pairs in the json field
  #   and does not update the db columns that contain this duplicate data.
  #   Likely it would be best not to have data duplication, so either the columns
  #   should be updated in the db, or some other not duplicative approach be explored.
  model_json_dict = getattr(model, json_field)
  if model_json_dict is None:
    model_json_dict = {}

  # todo (consider) current implementation loops through payload.items() and casts certain elements
  #   based on hard coded element names.  Perhaps a more generalized approach or a json serializer should be considered
  # json_str = dict_to_json_str(payload)
  # logger.debug(f"{json_str=}")
  # model_json_dict = json_str

  for key, value in payload.items():
    if isinstance(value, datetime.datetime):
      logger.debug(f"Attempting to cast local datetime to utc string")
      value = ca_naive_to_utc_datetime(value).isoformat()
      logger.debug(f"New Value <{value}> is of type {type(value)}")
    if isinstance(value, decimal.Decimal):
      logger.debug(f"Attempting to cast decimal to float")
      value = float(value)
      logger.debug(f"New Value <{value}> is of type {type(value)}")
    # todo (consider) - hack to get types correct, replace with a more robust approach
    if key == 'id_incidence':
      if value is not None:
        value = int(value)
    elif key in ['lat_arb', 'long_arb']:
      if value is not None:
        value = float(value)

    model_json_dict[key] = value

  setattr(model, json_field, model_json_dict)
  # model.misc_json = model_json_dict

  logger.debug(f"After the setattr, the model json data is now: {getattr(model, json_field)=}")

  # flag the json field as updated so the changes persist, if you don't flag it,
  # SQLAlchemy won't update the model
  flag_modified(model, json_field)


def get_wtforms_fields(form, include_csrf_token=False):
  """
  Return the sorted field names of wtforms elements.

  Args:
    form (FlaskForm): wtform
    include_csrf_token (bool): if True, include CSRF token in field list
  Returns (list): field names associated with a wtforms form.

  """
  form_fields = []
  for field_name in form.data:
    if field_name != 'csrf_token' or include_csrf_token is True:
      form_fields.append(field_name)
  form_fields.sort()

  return form_fields


def initialize_drop_downs(form, default="Please Select") -> None:
  """
  Initialize all the selector fields in a form that have not been specified (i.e. they are None)
  to a default value.

  Args:
    form (FlaskForm): wtform
    default (str): default value for selector element

  """
  logger.debug(f"in initialize_drop_downs()")
  for field in form:
    if isinstance(field, SelectField):
      logger.debug(f"Initializing {field.name}.  {field.data=}")
      if field.data is None:
        logger.debug(f"{field.name} set to {default =}")
        field.data = default


def validate_selectors(form, default="Please Select") -> None:
  """
  Ensure that selectors are properly on method='get' validated by adding errors to inputRequired selectors that are set to
  default/disabled values

  Args:
    form (FlaskForm): wtform
    default (str): default value for selector element
  """
  for field in form:
    if isinstance(field, SelectField):
      if field.data is None or field.data == default:
        for validator in field.validators:
          if isinstance(validator, InputRequired):
            msg = 'This field is required.'
            if msg not in field.errors:
              field.errors.append(msg)


def validate_no_csrf(form, extra_validators=None):
  """
  Validate the form without considering errors from the csrf token.

  Args:
    form (FlaskForm): wtform
    extra_validators (dict|None): See https://wtforms.readthedocs.io/en/3.2.x/forms/#wtforms.form.Form.validate

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
