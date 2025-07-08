"""
WTForms-based upload form for the ARB Feedback Portal.

Defines a minimal form used to upload Excel files via the web interface.
Typically used in the `/upload` route.

Args:
  None

Returns:
  None

Attributes:
  UploadForm (type): WTForms form class for file uploads.
  logger (logging.Logger): Logger instance for this module.

Examples:
  form = UploadForm()
  if form.validate_on_submit():
    # handle file upload
    pass

Notes:
  - Leverages Flask-WTF integration with Bootstrap-compatible rendering.
  - Additional validation for file size or filename may be added externally.
  - The logger emits a debug message when this file is loaded.
"""

import logging

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired

logger = logging.getLogger(__name__)


class UploadForm(FlaskForm):
  """
  WTForm for uploading Excel or JSON files via the ARB Feedback Portal.

  Attributes:
    file (FileField): Upload field for selecting a `.xls` or `.xlsx` file.
    submit (SubmitField): Form button to initiate upload.

  Examples:
    form = UploadForm()
    if form.validate_on_submit():
      # handle file upload
      pass

  Notes:
    - Uses Flask-WTF and integrates with Bootstrap templates.
    - File extension restrictions enforced via `FileAllowed`.
    - Form is rendered in the Upload UI at `/upload`.
  """

  file = FileField(
    "Choose Excel File",
    validators=[DataRequired(), FileAllowed(['xls', 'xlsx'], 'Excel files only!')]
  )
  submit = SubmitField("Upload")
