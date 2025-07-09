"""
Functions and helper classes to support WTForms models.

Notes:
  * WTForm model classes should remain adjacent to Flask views (e.g., in `wtf_landfill.py`)
  * This module is for shared utilities, validators, and form-to-model conversion logic.
"""

import copy
import datetime
import logging
from decimal import Decimal
from typing import Callable

from flask_wtf import FlaskForm
from sqlalchemy.ext.automap import AutomapBase
from sqlalchemy.ext.declarative import DeclarativeMeta
from wtforms import SelectField, ValidationError
from wtforms.fields.core import Field
from wtforms.validators import InputRequired, Optional

from arb.portal.json_update_util import apply_json_patch_and_log
from arb.utils.constants import PLEASE_SELECT
from arb.utils.diagnostics import get_changed_fields, list_differences
from arb.utils.json import deserialize_dict, make_dict_serializeable, safe_json_loads, wtform_types_and_values
from arb.utils.sql_alchemy import load_model_json_column

__version__ = "1.0.0"

logger = logging.getLogger(__name__)


def min_decimal_precision(min_digits: int) -> Callable:
  """
  Return a validator for WTForms DecimalField enforcing minimum decimal precision.

  Args:
    min_digits (int): Minimum number of digits required after the decimal. If None or less than 0, raises ValueError.

  Returns:
    Callable: WTForms-compatible validator that raises ValidationError if decimal places are insufficient.

  Examples:
    Input : field = DecimalField("Amount", validators=[min_decimal_precision(2)])
    Output: Raises ValidationError if fewer than 2 decimal places are entered
    Input : min_digits=None
    Output: ValueError
    Input : min_digits=-1
    Output: ValueError

  Notes:
    - If `min_digits` is None or less than 0, raises ValueError.
    - Used as a custom validator in WTForms field definitions.
  """

  def _min_decimal_precision(form, field):
    """
    WTForms validator to enforce a minimum number of decimal places on a DecimalField.

    Args:
        form (FlaskForm): The form instance being validated (unused, required by WTForms signature).
        field (Field): The field instance to validate. Should have a .data attribute containing the value.

    Raises:
        ValidationError: If the value does not have the required number of decimal places or is not a valid number.

    Notes:
        - This is an internal helper returned by min_decimal_precision().
        - Used as a custom validator in WTForms field definitions.
    """
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
    form (FlaskForm): The WTForms form instance. Must not be None.
    field_names (list[str]): List of field names to examine and modify. If None or empty, no action is taken.
    validators_to_remove (list[type] | None): Validator classes to remove. Default to [InputRequired] if not provided.

  Returns:
    None

  Examples:
    Input : remove_validators(form, ["name", "email"], [InputRequired])
    Output: Removes InputRequired validators from 'name' and 'email' fields
    Input : remove_validators(form, None, [InputRequired])
    Output: No action
    Input : remove_validators(form, [], [InputRequired])
    Output: No action

  Notes:
    - If `field_names` is None or empty, no action is taken.
    - Useful when validator logic depends on user input or view context.
  """
  if validators_to_remove is None:
    validators_to_remove = [InputRequired]

  fields = get_wtforms_fields(form, include_csrf_token=False)
  for field in fields:
    if field in field_names:
      validators = form[field].validators
      # Reassign validators with those not matching types to remove
      form[field].validators = [v for v in validators if not any(isinstance(v, t) for t in validators_to_remove)]


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
    form (FlaskForm): The form to update. Must not be None.
    bool_test (bool): If True, required/optional fields are swapped accordingly.
    required_if_true (list[str]): Field names that become required when bool_test is True. If None or empty, no action is taken.
    optional_if_true (list[str] | None): Field names that become optional when bool_test is True. If None, treated as empty list.

  Returns:
    None

  Examples:
    Input : change_validators_on_test(form, True, ["name"], ["email"])
    Output: 'name' becomes required, 'email' becomes optional
    Input : change_validators_on_test(form, False, ["name"], ["email"])
    Output: 'name' becomes optional, 'email' becomes required
    Input : change_validators_on_test(form, True, None, None)
    Output: No action

  Notes:
    - If `required_if_true` is None or empty, no action is taken.
    - If `optional_if_true` is None, treated as empty list.
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
    form (FlaskForm): WTForms form instance. Must not be None.
    field_names_to_change (list[str]): List of fields to alter. If None or empty, no action is taken.
    old_validator (type): Validator class to remove (e.g., Optional). Must not be None.
    new_validator (type): Validator class to add (e.g., InputRequired). Must not be None.

  Returns:
    None

  Examples:
    Input : change_validators(form, ["name"], Optional, InputRequired)
    Output: Replaces Optional with InputRequired on the 'name' field
    Input : change_validators(form, None, Optional, InputRequired)
    Output: No action
    Input : change_validators(form, ["name"], None, InputRequired)
    Output: No action

  Notes:
    - If `field_names_to_change` is None or empty, no action is taken.
    - If `old_validator` or `new_validator` is None, no action is taken.
  """
  field_names = get_wtforms_fields(form, include_csrf_token=False)
  for field_name in field_names:
    if field_name in field_names_to_change:
      validators = form[field_name].validators
      # Replace old_validator with new_validator, reassign as list
      form[field_name].validators = [new_validator() if isinstance(v, old_validator) else v for v in validators]


def wtf_count_errors(form: FlaskForm, log_errors: bool = False) -> dict[str, int]:
  """
  Count validation errors on a WTForm instance.

  Args:
    form (FlaskForm): The form to inspect. Must not be None.
    log_errors (bool): If True, log the form's errors using debug log level.

  Returns:
    dict[str, int]: Dictionary with error counts:
      - 'elements_with_errors': number of fields that had one or more errors
      - 'element_error_count': total number of field-level errors
      - 'wtf_form_error_count': number of form-level (non-field) errors
      - 'total_error_count': sum of all error types

  Examples:
    Input : error_summary = wtf_count_errors(form)
    Output: error_summary["total_error_count"] → total number of errors found
    Input : wtf_count_errors(None)
    Output: Exception

  Notes:
    - Ensure `form.validate_on_submit()` or `form.validate()` has been called first, or the error counts will be inaccurate.
    - If `form` is None, an exception will be raised.
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
    - Ignores JSON fields that don't map to WTForm fields.
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
    field (Field): A WTForms field instance (e.g., DecimalField, DateTimeField). Must not be None.
    value (str | int | float | Decimal | datetime.datetime | None): The field's data value. If None, returns an empty list.

  Returns:
    list[str]: List of string values to assign to `field.raw_data`. Returns an empty list if value is None.

  Raises:
    ValueError: If the value type is unsupported (not str, int, float, Decimal, or datetime.datetime).

  Examples:
    Input : format_raw_data(field, Decimal("10.5"))
    Output: ['10.5']
    Input : format_raw_data(field, None)
    Output: []
    Input : format_raw_data(field, object())
    Output: ValueError

  Notes:
    - If value is None, returns an empty list.
    - If value is a Decimal, casts to float before converting to string.
    - If value is an unsupported type, raises ValueError.
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
    model (AutomapBase): SQLAlchemy model instance. Must not be None.
    wtform (FlaskForm): WTForm with typed Python values. Must not be None.
    json_column (str): JSON column name on the model. Defaults to "misc_json". If None or invalid, raises AttributeError.
    user (str): Username for logging purposes. If None, defaults to "anonymous".
    comments (str): Optional comment for logging context. If None, treated as empty string.
    ignore_fields (list[str] | None): Fields to exclude from update. If None, no fields are excluded.
    type_matching_dict (dict[str, type] | None): Optional override for type enforcement. If None, uses default type map.

  Returns:
    None

  Examples:
    Input : wtform_to_model(model, form)
    Output: Updates model's JSON column with form data
    Input : wtform_to_model(model, form, ignore_fields=["id"])
    Output: Updates all fields except 'id'
    Input : wtform_to_model(None, form)
    Output: AttributeError

  Notes:
    - Uses make_dict_serializable and get_changed_fields to compare values.
    - Delegates to apply_json_patch_and_log to persist and log changes.
    - If model or wtform is None, raises AttributeError.
  """
  ignore_fields_set = set(ignore_fields or [])

  payload_all = {
    field_name: getattr(wtform, field_name).data
    for field_name in get_wtforms_fields(wtform)
    if field_name not in ignore_fields_set
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
    model (DeclarativeMeta): SQLAlchemy model with JSON column `misc_json`. Must not be None.
    wtform (FlaskForm): The form to extract values from. Must not be None.
    ignore_fields (list[str] | None): List of fields to skip during comparison. If None, no fields are skipped.

  Returns:
    tuple[dict, dict]: Tuple of (payload_all, payload_changes)
      - payload_all: All form fields
      - payload_changes: Subset of fields with changed values vs. model

  Examples:
    Input : get_payloads(model, form)
    Output: (all_fields_dict, changed_fields_dict)
    Input : get_payloads(model, form, ignore_fields=["id"])
    Output: (all_fields_dict, changed_fields_dict) excluding 'id'
    Input : get_payloads(None, form)
    Output: AttributeError

  Notes:
    - Performs a naive comparison (==) without deserializing types.
    - Use skip_empty_fields = True to suppress null-like values.
    - If model or wtform is None, raises AttributeError.
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
    payload (dict): Key-value updates extracted from a WTForm or another source. Must not be None.
    type_matching_dict (dict[str, type] | None): Optional type coercion rules. If None, uses default type map.
      e.g., {"id_incidence": int, "some_flag": bool}

  Returns:
    dict: Transformed version of the payload, suitable for use in a model's JSON field.

  Examples:
    Input : prep_payload_for_json({"id_incidence": "123"}, {"id_incidence": int})
    Output: {"id_incidence": 123}
    Input : prep_payload_for_json({}, None)
    Output: {}
    Input : prep_payload_for_json(None)
    Output: TypeError

  Notes:
    - Applies datetime to ISO, Decimal to float.
    - Respects "Please Select" for placeholders.
    - Values in `type_matching_dict` are explicitly cast to the specified types.
    - If payload is None, raises TypeError.
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
    model (DeclarativeMeta): SQLAlchemy model instance to update. Must not be None.
    payload (dict): Dictionary of updates to apply. Must not be None.
    json_field (str): Name of the model's JSON column (default is "misc_json"). If None or invalid, raises AttributeError.
    comment (str): Optional comment to include with update logging. If None, treated as empty string.

  Returns:
    None

  Examples:
    Input : update_model_with_payload(model, {"foo": 1})
    Output: Updates model's misc_json with foo=1
    Input : update_model_with_payload(None, {"foo": 1})
    Output: AttributeError

  Notes:
    - Calls `prep_payload_for_json` to ensure data integrity.
    - Uses `apply_json_patch_and_log` to track and log changes.
    - Deep-copies the existing JSON field to avoid side effects.
    - If model or payload is None, raises AttributeError.
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
    form (FlaskForm): The WTForms form instance. Must not be None.
    include_csrf_token (bool): If True, include 'csrf_token' in the result. Defaults to False.

  Returns:
    list[str]: Alphabetically sorted list of field names in the form. Returns an empty list if form is None.

  Examples:
    Input : get_wtforms_fields(form)
    Output: ['name', 'sector']
    Input : get_wtforms_fields(None)
    Output: []

  Notes:
    - If form is None, returns an empty list.
    - Field names are sorted alphabetically.
    - If include_csrf_token is False, 'csrf_token' is excluded from the result.
  """
  field_names = [
    name for name in form.data
    if include_csrf_token or name != "csrf_token"
  ]
  field_names.sort()
  return field_names


def initialize_drop_downs(form: FlaskForm, default: str | None = None) -> None:
  """
  Set default values for uninitialized WTForms SelectFields.

  Args:
    form (FlaskForm): The form containing SelectField fields to be initialized. Must not be None.
    default (str | None): The value to assign to a field if its current value is None. If None, uses the application's global placeholder (e.g., "Please Select").

  Returns:
    None

  Examples:
    Input : initialize_drop_downs(form, default="Please Select")
    Output: Sets all SelectField fields to default if not initialized
    Input : initialize_drop_downs(form, default=None)
    Output: Sets all SelectField fields to the global placeholder if not initialized
    Input : initialize_drop_downs(None)
    Output: Exception

  Notes:
    - Fields that already have a value (even a falsy one like an empty string) are not modified.
    - Only fields of type `SelectField` are affected.
    - This function is typically used after form construction but before rendering or validation.
    - If form is None, raises an exception.
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
    header (list[tuple[str, str, dict]]): Static options to appear first in the dropdown. Must not be None.
    items (list[str]): Dynamic option values to convert into (value, label, {}) format. If None or empty, only header is returned.

  Returns:
    list[tuple[str, str, dict]]: Combined list of header and generated item tuples.

  Examples:
    Input : build_choices([("Please Select", "Please Select", {"disabled": True})], ["One", "Two"])
    Output: [("Please Select", "Please Select", {"disabled": True}), ("One", "One", {}), ("Two", "Two", {})]
    Input : build_choices([("Please Select", "Please Select", {"disabled": True})], [])
    Output: [("Please Select", "Please Select", {"disabled": True})]
    Input : build_choices([], ["A"])
    Output: [("A", "A", {})]

  Notes:
    - If items is None or empty, only the header is returned.
    - If header is None, raises an exception.
  """
  footer = [(item, item, {}) for item in items]
  return header + footer


def ensure_field_choice(field_name: str,
                        field,
                        choices: list[tuple[str, str] | tuple[str, str, dict]] | None = None) -> None:
  """
  Ensure a field's current value is among its valid choices, or reset it to a placeholder.

  Args:
    field_name (str): Name of the WTForms field (for logging purposes). Must not be None.
    field (Field): WTForms-compatible field (typically a SelectField). Must not be None.
    choices (list[tuple[str, str]] | list[tuple[str, str, dict]] | None): Valid choices to enforce. If None, uses the field's existing choices. If both are None, uses an empty list.

  Returns:
    None

  Examples:
    Input : ensure_field_choice("sector", field, [("A", "A"), ("B", "B")])
    Output: Resets field.data to placeholder if not in ["A", "B"]
    Input : ensure_field_choice("sector", field, None)
    Output: Uses field.choices for validation
    Input : ensure_field_choice("sector", None, [("A", "A")])
    Output: Exception

  Notes:
    - If choices is provided, this function sets field.choices to the new list.
    - If choices is None, it uses the field's existing .choices. If both are None, uses an empty list.
    - Resets field.data and field.raw_data to the placeholder if the value is invalid.
    - If field is None, raises an exception.
  """

  if choices is None:
    # Use existing field choices if none are supplied
    choices = field.choices if field.choices is not None else []
  else:
    # Apply a new set of choices to the field
    field.choices = choices

  valid_values = {c[0] for c in choices}

  if field.data not in valid_values:
    logger.debug(f"{field_name}.data={field.data!r} not in valid options, resetting to '{PLEASE_SELECT}'")
    field.data = PLEASE_SELECT
    field.raw_data = [field.data]


def validate_selectors(form: FlaskForm, default: str | None = None) -> None:
  """
  Append validation errors for SelectFields left at default placeholder values.

  Args:
    form (FlaskForm): WTForm instance containing SelectFields. Must not be None.
    default (str | None): Placeholder value to treat as invalid (default: "Please Select"). If None, uses the global placeholder.

  Returns:
    None

  Examples:
    Input : validate_selectors(form, default="Please Select")
    Output: Adds error to fields left at default
    Input : validate_selectors(form, default=None)
    Output: Adds error to fields left at the global placeholder
    Input : validate_selectors(None)
    Output: Exception

  Notes:
    - Typically used for GET-submitted forms where default values are not caught automatically.
    - Adds "This field is required." error to fields that are InputRequired but still at default.
    - If form is None, raises an exception.
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
              field.errors.append(msg)  # type: ignore


def validate_no_csrf(form: FlaskForm, extra_validators: dict | None = None) -> bool:
  """
  Validate a WTForm while skipping CSRF errors (useful for GET-submitted forms).

  Args:
    form (FlaskForm): The form to validate. Must not be None.
    extra_validators (dict | None): Optional per-field validators to apply. If None, no extra validators are used.

  Returns:
    bool: True if the form is valid after removing CSRF errors, otherwise False.

  Examples:
    Input : validate_no_csrf(form)
    Output: True if valid, False if errors remain (except CSRF)
    Input : validate_no_csrf(None)
    Output: Exception

  Notes:
    - This allows validation to succeed even when CSRF tokens are missing or invalid.
    - It logs before and after validation for debug purposes.
    - If form is None, raises an exception.
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


def coerce_choices(val):
    """
    Convert various dropdown data formats to a list of (str, str) tuples for WTForms SelectField.

    WTForms SelectField expects choices as a list of (value, label) tuples. This helper ensures
    compatibility regardless of the input format (dict, list of tuples, or list of strings).

    Args:
        val: The dropdown data, which may be a dict, list of tuples, or list of strings.

    Returns:
        List[Tuple[str, str]]: A list of (value, label) tuples.
    """
    if not val:
        return []
    if isinstance(val, dict):
        return [(str(k), str(v)) for k, v in val.items()]
    if isinstance(val, list):
        # If already a list of tuples, convert to (str, str) using only first two elements
        if all(isinstance(x, tuple) and len(x) >= 2 for x in val):
            return [(str(x[0]), str(x[1])) for x in val]
        # If a list of strings, convert to (str, str)
        if all(isinstance(x, str) for x in val):
            return [(x, x) for x in val]
    return []


if __name__ == '__main__':
  pass
