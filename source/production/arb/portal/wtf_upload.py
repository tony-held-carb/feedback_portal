# arb/portal/wtf_upload.py

from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class UploadForm(FlaskForm):
    file = FileField(
        "Choose Excel File",
        validators=[DataRequired(), FileAllowed(['xls', 'xlsx'], 'Excel files only!')]
    )
    submit = SubmitField("Upload")
