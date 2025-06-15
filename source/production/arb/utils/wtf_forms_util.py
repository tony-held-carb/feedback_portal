"""
Functions and helper classes to support WTForms models.

Notes:
  * WTForm model classes should remain adjacent to Flask views (e.g., in `wtf_landfill.py`)
  * This module is for shared utilities, validators, and form-to-model conversion logic.
"""

import copy
import datetime
from decimal import Decimal
from typing import Callable

from flask_wtf import FlaskForm
from sqlalchemy.ext.automap import AutomapBase
from sqlalchemy.ext.declarative import DeclarativeMeta
from wtforms import SelectField, ValidationError
from wtforms.fields.core import Field
from wtforms.validators import InputRequired, Optional

from arb.__get_logger import get_logger
from arb.portal.json_update_util import apply_json_patch_and_log
from arb.utils.constants import PLEASE_SELECT
from arb.utils.diagnostics import get_changed_fields, list_differences
from arb.utils.json import deserialize_dict, make_dict_serializeable, safe_json_loads, wtform_types_and_values

__version__ = "1.0.0"

from arb.utils.sql_alchemy import load_model_json_column

logger, pp_log = get_logger()


def min_decimal_precision(min_digits: int) -> Callable:
  """
  Return a validator for WTForms DecimalField enforcing minimum decimal precision.

  Args:
    min_digits (int): Minimum number of digits required after the decimal.

  Returns:
    Callable: WTForms-compatible validator that raises ValidationError if decimal places are insufficient.

  Example:
    Input :
      field = DecimalField("Amount", validators=[min_decimal_precision(2)])
    Output:
      Raises ValidationError if fewer than 2 decimal places are entered
  """

  def _min_decimal_precision(form, field):
    logger.debug(f"_min_decimal_precision called with {form=}, {field=}")
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


def remove_validators(form: FlaskForm,
                      field_names: list[str],
                      validators_to_remove: list[type] | None = None) -> None:
  """
  Remove specified validators from selected WTForms fields.

  Args:
    form (FlaskForm): The WTForms form instance.
    field_names (list[str]): List of field names to examine and modify.
    validators_to_remove (list[type] | None): Validator classes to remove.
      Default to [InputRequired] if not provided.

  Notes:
    This modifies the validator list in-place and is useful when
    conditional field requirements apply.

  Example:
    Input :
      remove_validators(form, ["name", "email"], [InputRequired])
    Output:
      Removes InputRequired validators from 'name' and 'email' fields

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
                              optional_if_true: list[str] | None = None) -> None:
  """
  Conditionally switch validators on selected form fields based on a boolean test.

  If bool_test is True:
    - Fields in required_if_true become required (InputRequired).
    - Fields in optional_if_true become optional (Optional).

  If bool_test is False:
    - Fields in required_if_true become optional.
    - Fields in optional_if_true become required.

  Args:
    form (FlaskForm): The form to update.
    bool_test (bool): If True, required/optional fields are swapped accordingly.
    required_if_true (list[str]): Field names that become required when bool_test is True.
    optional_if_true (list[str] | None): Field names that become optional when bool_test is True.
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
                      old_validator: type,
                      new_validator: type) -> None:
  """
  Replace one validator type with another on a list of WTForms fields.

  Args:
    form (FlaskForm): WTForms form instance.
    field_names_to_change (list[str]): List of fields to alter.
    old_validator (type): Validator class to remove (e.g., Optional).
    new_validator (type): Validator class to add (e.g., InputRequired).

  Notes:
    - The replacement is done in-place on each field's `validators` list.
    - Useful for dynamically changing required status.

  Example:
    Input :
      change_validators(form, ["name"], Optional, InputRequired)
    Output:
      Replaces Optional with InputRequired on the 'name' field
  """
  field_names = get_wtforms_fields(form, include_csrf_token=False)
  for field_name in field_names:
    if field_name in field_names_to_change:
      validators = form[field_name].validators
      for i, validator in enumerate(validators):
        if isinstance(validator, old_validator):
          validators[i] = new_validator()


def wtf_count_errors(form: FlaskForm, log_errors: bool = False) -> dict[str, int]:
  """
  Count validation errors on a WTForm instance.

  Args:
    form (FlaskForm): The form to inspect.
    log_errors (bool): If True, log the form's errors using debug log level.

  Returns:
    dict[str, int]: Dictionary with error counts:
      - 'elements_with_errors': number of fields that had one or more errors
      - 'element_error_count': total number of field-level errors
      - 'wtf_form_error_count': number of form-level (non-field) errors
      - 'total_error_count': sum of all error types

  Notes:
    Ensure `form.validate_on_submit()` or `form.validate()` has been called first,
    or the error counts will be inaccurate.

  Example:
    Input :
      error_summary = wtf_count_errors(form)
    Output:
      error_summary["total_error_count"] → total number of errors found
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


def model_to_wtform(model: AutomapBase,
                    wtform: FlaskForm,
                    json_column: str = "misc_json") -> None:
  """
  Populate a WTForm from a SQLAlchemy model's JSON column.

  This function loads the model's JSON field (typically 'misc_json') and
  sets WTForms field `.data` and `.raw_data` accordingly. Required for correct rendering
  and validation of pre-filled forms.

  Args:
    model (AutomapBase): SQLAlchemy model instance containing a JSON column.
    wtform (FlaskForm): The WTForm instance to populate.
    json_column (str): The attribute name of the JSON column. Defaults to "misc_json".

  Raises:
    ValueError: If a datetime value cannot be parsed.
    TypeError: If the field type is unsupported.

  Notes:
    - Supports preloading DateTimeField and DecimalField types.
    - Converts ISO8601 UTC → localized Pacific time.
    - Ignores JSON fields that don’t map to WTForm fields.
  """
  model_json_dict = getattr(model, json_column)
  logger.debug(f"model_to_wtform called with model={model}, json={model_json_dict}")

  # # Ensure dict, not str
  # if isinstance(model_json_dict, str):
  #   try:
  #     model_json_dict = json.loads(model_json_dict)
  #     logger.debug(f"Parsed JSON string into dict.")
  #   except json.JSONDecodeError:
  #     logger.warning(f"Invalid JSON in model's '{json_column}' column.")
  #     model_json_dict = {}

  if isinstance(model_json_dict, str) or model_json_dict is None:
    model_json_dict = safe_json_loads(model_json_dict, context_label=f"model's '{json_column}' column")

  if model_json_dict is None:
    model_json_dict = {}

  model_id_incidence = getattr(model, "id_incidence", None)
  if "id_incidence" in model_json_dict and model_json_dict["id_incidence"] != model_id_incidence:
    logger.warning(f"[model_to_wtform] MISMATCH: model.id_incidence={model_id_incidence} "
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


def format_raw_data(field: Field, value) -> list[str]:
  """
  Convert a field value to a format suitable for WTForms `.raw_data`.

  Args:
    field (Field): A WTForms field instance (e.g., DecimalField, DateTimeField).
    value (str | int | float | Decimal | datetime.datetime | None): The field's data value.

  Returns:
    list[str]: List of string values to assign to `field.raw_data`.

  Raises:
    ValueError: If the value type is unsupported.

  Example:
    Input :
      format_raw_data(field, Decimal("10.5"))
    Output:
      ['10.5']
  """
  if value is None:
    return []
  elif isinstance(value, (str, int, float)):
    return [str(value)]
  elif isinstance(value, Decimal):
    return [str(float(value))]  # Cast to float before converting to string
  elif isinstance(value, datetime.datetime):
    return [value.isoformat()]
  else:
    raise ValueError(f"Unsupported type for raw_data: {type(value)} with value {value}")


def wtform_to_model(model: AutomapBase,
                    wtform: FlaskForm,
                    json_column: str = "misc_json",
                    user: str = "anonymous",
                    comments: str = "",
                    ignore_fields: list[str] | None = None,
                    type_matching_dict: dict[str, type] | None = None) -> None:
  """
  Extract data from a WTForm and update the model's JSON column. Logs all changes.

  Args:
    model (AutomapBase): SQLAlchemy model instance.
    wtform (FlaskForm): WTForm with typed Python values.
    json_column (str): JSON column name on the model.
    user (str): Username for logging purposes.
    comments (str): Optional comment for logging context.
    ignore_fields (list[str] | None): Fields to exclude from update.
    type_matching_dict (dict[str, type] | None): Optional override for type enforcement.

  Notes:
    - Use make_dict_serializable and get_changed_fields to compare values.
    - Delegates to apply_json_patch_and_log to persist and log changes.
  """
  ignore_fields = set(ignore_fields or [])

  payload_all = {
    field_name: getattr(wtform, field_name).data
    for field_name in get_wtforms_fields(wtform)
    if field_name not in ignore_fields
  }

  # Use manual overrides only — no type_map from form
  payload_all = make_dict_serializeable(payload_all, type_map=type_matching_dict, convert_time_to_ca=True)

  existing_json = load_model_json_column(model, json_column)
  # todo - shouldn't json already be serialized, not sure what the next line accomplishes
  existing_serialized = make_dict_serializeable(existing_json, type_map=type_matching_dict, convert_time_to_ca=True)

  payload_changes = get_changed_fields(payload_all, existing_serialized)
  if payload_changes:
    logger.info(f"wtform_to_model payload_changes: {payload_changes}")
    apply_json_patch_and_log(model, payload_changes, json_column, user=user, comments=comments)

  logger.info(f"wtform_to_model payload_all: {payload_all}")


def get_payloads(model: DeclarativeMeta,
                 wtform: FlaskForm,
                 ignore_fields: list[str] | None = None) -> tuple[dict, dict]:
  """
  DEPRECATED: Use `wtform_to_model()` instead.

  Extract all field values and changed values from a WTForm.

  Args:
    model (DeclarativeMeta): SQLAlchemy model with JSON column `misc_json`.
    wtform (FlaskForm): The form to extract values from.
    ignore_fields (list[str] | None): List of fields to skip during comparison.

  Returns:
    tuple[dict, dict]: Tuple of (payload_all, payload_changes)
      - payload_all: All form fields
      - payload_changes: Subset of fields with changed values vs. model

  Notes:
    - Performs a naive comparison (==) without deserializing types.
    - Use skip_empty_fields = True to suppress null-like values.
  """
  if ignore_fields is None:
    ignore_fields = []

  skip_empty_fields = False  # Yes: if you wish to skip blank fields from being updated when feasible

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

    if skip_empty_fields is True:
      # skipping empty strings if the model is "" or None
      if field_value == "":
        if model_value in [None, ""]:
          continue

      # Only persist "Please Select" if overwriting a meaningful value.
      if isinstance(field, SelectField) and field_value == PLEASE_SELECT:
        if model_value in [None, ""]:
          continue

    payload_all[form_field_name] = field_value

    # todo (depreciated) - object types are not being seen as equivalent (because they are serialized strings)
    #        need to update logic - check out prep_payload_for_json for uniform approach
    if model_value != field_value:
      payload_changes[form_field_name] = field_value

  return payload_all, payload_changes


def prep_payload_for_json(payload: dict,
                          type_matching_dict: dict[str, type] | None = None) -> dict:
  """
  Prepare a payload dictionary for JSON-safe serialization.

  Args:
    payload (dict): Key-value updates extracted from a WTForm or another source.
    type_matching_dict (dict[str, type] | None): Optional type coercion rules.
      e.g., {"id_incidence": int, "some_flag": bool}

  Returns:
    dict: Transformed version of the payload, suitable for use in a model's JSON field.

  Notes:
    - Applies datetime to ISO, Decimal to float
    - Respects "Please Select" for placeholders
    - Values in `type_matching_dict` are explicitly cast to the specified types
  """

  type_matching_dict = type_matching_dict or {"id_incidence": int}

  return make_dict_serializeable(payload,
                                 type_map=type_matching_dict,
                                 convert_time_to_ca=True)


def update_model_with_payload(model: DeclarativeMeta,
                              payload: dict,
                              json_field: str = "misc_json",
                              comment: str = "") -> None:
  """
  Apply a JSON-safe payload to a model's JSON column and mark it as changed.

  Args:
    model (DeclarativeMeta): SQLAlchemy model instance to update.
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

  apply_json_patch_and_log(
    model,
    json_field=json_field,
    updates=model_json,
    user="anonymous",
    comments=comment,
  )

  logger.debug(f"Model JSON updated: {getattr(model, json_field)=}")


def get_wtforms_fields(form: FlaskForm,
                       include_csrf_token: bool = False) -> list[str]:
  """
  Return the sorted field names associated with a WTForms form.

  Args:
    form (FlaskForm): The WTForms form instance.
    include_csrf_token (bool): If True, include 'csrf_token' in the result.

  Returns:
    list[str]: Alphabetically sorted list of field names in the form.

  Example:
    Input :
      get_wtforms_fields(form)
    Output:
      ['name', 'sector']
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
    form (FlaskForm): The form containing SelectField fields to be initialized.
    default (str | None): The value to assign to a field if its current value is None.
      If not provided, use the application's global placeholder (e.g., "Please Select").

  Returns:
    None

  Example:
    Input :
      initialize_drop_downs(form, default="Please Select")
    Output:
      Sets all SelectField fields to default if not initialized

  Notes:
    - Fields that already have a value (even a falsy one like an empty string) are not modified.
    - Only fields of type `SelectField` are affected.
    - This function is typically used after form construction but before rendering or validation.
  """
  if default is None:
    default = PLEASE_SELECT

  logger.debug(f"Initializing drop-downs...")
  for field in form:
    if isinstance(field, SelectField) and field.data is None:
      logger.debug(f"{field.name} set to default value: {default}")
      field.data = default


def build_choices(header: list[tuple[str, str, dict]], items: list[str]) -> list[tuple[str, str, dict]]:
  """
  Combine header and dynamic items into a list of triple-tuples for WTForms SelectFields.

  Args:
    header (list[tuple[str, str, dict]]): Static options to appear first in the dropdown.
    items (list[str]): Dynamic option values to convert into (value, label, {}) format.

  Returns:
    list[tuple[str, str, dict]]: Combined list of header and generated item tuples.

  Example:
    Input :
      build_choices(
        [("Please Select", "Please Select", {"disabled": True})],
        ["One", "Two"]
      )
    Output:
      [
        ("Please Select", "Please Select", {"disabled": True}),
        ("One", "One", {}),
        ("Two", "Two", {})
      ]
  """
  footer = [(item, item, {}) for item in items]
  return header + footer


def ensure_field_choice(field_name: str,
                        field,
                        choices: list[tuple[str, str] | tuple[str, str, dict]] | None = None) -> None:
  """
  Ensure a field’s current value is among its valid choices, or reset it to a placeholder.

  Args:
    field_name (str): Name of the WTForms field (for logging purposes).
    field (Field): WTForms-compatible field (typically a SelectField).
    choices (list[tuple[str, str]] | list[tuple[str, str, dict]] | None):
      Valid choices to enforce. If None, use the field's existing choices.

  Returns:
    None

  Notes:
  - If `choices` is provided, this function sets `field.choices` to the new list.
  - If `choices` is None, it uses the field's existing `.choices`. In either case,
    it validates that the current `field.data` is among the available options and
    resets it to "Please Select" if not.
  - Both `field.data` and `field.raw_data` are reset to keep form behavior consistent.
  - Each choice tuple should be in the form:
      - value, label
      - value, label, metadata_dict
      - Only the first element `value` is used for validation.
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
  Append validation errors for SelectFields left at default placeholder values.

  Args:
    form (FlaskForm): WTForm instance containing SelectFields.
    default (str | None): Placeholder value to treat as invalid (default: "Please Select").

  Returns:
    None

  Notes:
    - Typically used for GET-submitted forms where default values are not caught automatically.
    - Adds "This field is required." error to fields that are InputRequired but still at default.
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
  Validate a WTForm while skipping CSRF errors (useful for GET-submitted forms).

  Args:
    form (FlaskForm): The form to validate.
    extra_validators (dict | None): Optional per-field validators to apply.

  Returns:
    bool: True if the form is valid after removing CSRF errors, otherwise False.

  Notes:
    - This allows validation to succeed even when CSRF tokens are missing or invalid.
    - It logs before and after validation for debug purposes.
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


if __name__ == '__main__':
  pass
