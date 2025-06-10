
class RequiredIfTruthy:
  """
  WTForms validator: Applies InputRequired or Optional based on another field's truthiness.

  If the referenced field is "truthy" (not in a falsy list), then this field is required.
  If it is "falsy", this field becomes optional.

  Args:
      other_field_name (str): Name of the field to check.
      message (str | None): Optional custom validation error message.
      other_field_invalid_values (list | None): Values considered falsy (defaults to standard empty/zero/null values).

  Example:
      class MyForm(FlaskForm):
          confirm = BooleanField()
          notes = StringField(validators=[RequiredIfTruthy("confirm")])
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
  WTForms validator: Dynamically switches between InputRequired and Optional.

  The validator behavior is conditional on another field’s truthiness.
  Depending on `mode`, this field becomes required or optional.

  Args:
      other_field_name (str): Name of the field to evaluate.
      falsy_values (list | None): Custom falsy value list (defaults to standard values).
      mode (str): Either 'required on truthy' or 'optional on truthy'.
      message (str | None): Optional validation error message.

  Raises:
      TypeError: If an invalid mode is provided.

  Example:
      class MyForm(FlaskForm):
          toggle = BooleanField()
          extra = StringField(validators=[IfTruthy("toggle", mode="required on truthy")])
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
