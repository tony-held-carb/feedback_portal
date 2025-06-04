# arb/portal/wtf_upload.py

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired


class UploadForm(FlaskForm):
  """
  WTForm for uploading Excel or JSON files via the portal.

  Fields:
    file (FileField): Upload field for selecting a local file.
    submit (SubmitField): Button to submit the form.

  Notes:
    - Validations may be added to restrict file extensions or size.
    - This form is typically rendered in the Upload page template.
  """
  file = FileField(
    "Choose Excel File",
    validators=[DataRequired(), FileAllowed(['xls', 'xlsx'], 'Excel files only!')]
  )
  submit = SubmitField("Upload")
