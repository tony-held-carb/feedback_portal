"""
WTForms-based upload form for the ARB Feedback Portal.

Defines a minimal form used to upload Excel files via the web interface.
Typically used in the `/upload` route.

Fields:
--------
- file: Accepts `.xls` or `.xlsx` files only.
- submit: Triggers form submission.

Notes:
------
- Leverages Flask-WTF integration with Bootstrap-compatible rendering.
- Additional validation for file size or filename may be added externally.
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

  Fields:
    file (FileField): Upload field for selecting a `.xls` or `.xlsx` file.
    submit (SubmitField): Form button to initiate upload.

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
