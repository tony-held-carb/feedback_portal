from pathlib import Path

from flask import Response, redirect, render_template, request, url_for
from sqlalchemy.ext.automap import AutomapBase

from arb.__get_logger import get_logger
from arb.portal.constants import PLEASE_SELECT
from arb.portal.extensions import db
from arb.utils.sql_alchemy import add_commit_and_log_model, sa_model_diagnostics, sa_model_to_dict
from arb.utils.wtf_forms_util import initialize_drop_downs, model_to_wtform, validate_no_csrf, wtf_count_errors, wtform_to_model

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def incidence_prep(model_row: AutomapBase,
                   crud_type: str,
                   sector_type: str,
                   default_dropdown: str) -> str | Response:
  """
  Generate the context and render the HTML template for a feedback record.

  Populates WTForms fields from the model and applies validation logic
  depending on the request method (GET/POST). Integrates conditional
  dropdown resets, CSRF-less validation, and feedback record persistence.

  Args:
    model_row (AutomapBase): SQLAlchemy AutomapBase.
    crud_type (str): 'create' or 'update'.
    sector_type (str): 'Oil & Gas' or 'Landfill'.
    default_dropdown (str): Value used to fill in blank selects.

  Returns:
    str: Rendered HTML from the appropriate feedback template.

  Raises:
    ValueError: If the sector type is invalid.
  """
  # The imports below can't be moved to the top of the file because they require Globals to be initialized
  # prior to first use (Globals.load_drop_downs(app, db)).
  from arb.portal.wtf_landfill import LandfillFeedback
  from arb.portal.wtf_oil_and_gas import OGFeedback

  logger.debug(f"incidence_prep() called with {crud_type=}, {sector_type=}")
  sa_model_diagnostics(model_row)

  if default_dropdown is None:
    default_dropdown = PLEASE_SELECT

  if sector_type == "Oil & Gas":
    logger.debug(f"({sector_type=}) will use an Oil & Gas Feedback Form")
    wtf_form = OGFeedback()
    template_file = 'feedback_oil_and_gas.html'
  elif sector_type == "Landfill":
    logger.debug(f"({sector_type=}) will use a Landfill Feedback Form")
    wtf_form = LandfillFeedback()
    template_file = 'feedback_landfill.html'
  else:
    raise ValueError(f"Unknown sector type: '{sector_type}'.")

  if request.method == 'GET':
    # Populate wtform from model data
    model_to_wtform(model_row, wtf_form)
    # todo - maybe put update contingencies here?
    # obj_diagnostics(wtf_form, message="wtf_form in incidence_prep() after model_to_wtform")

    # For GET requests for row creation, don't validate and error_count_dict will be all zeros
    # For GET requests for row update, validate (except for the csrf token that is only present for a POST)
    if crud_type == 'update':
      validate_no_csrf(wtf_form, extra_validators=None)

  # todo - trying to make sure invalid drop-downs become "Please Select"
  #        may want to look into using validate_no_csrf or initialize_drop_downs (or combo)

  # Set all select elements that are a default value (None) to "Please Select" value
  initialize_drop_downs(wtf_form, default=default_dropdown)
  # logger.debug(f"\n\t{wtf_form.data=}")

  if request.method == 'POST':
    # Validate and count errors
    wtf_form.validate()
    _ = wtf_count_errors(wtf_form, log_errors=True)

    # Diagnostics of the model before updating with wtform values
    # Likely can comment out model_before and add_commit_and_log_model
    # if you want less diagnostics and redundant commits
    model_before = sa_model_to_dict(model_row)
    wtform_to_model(model_row, wtf_form, ignore_fields=["id_incidence"])
    add_commit_and_log_model(db,
                             model_row,
                             comment='call to wtform_to_model()',
                             model_before=model_before)

    # Determine the course of action for successful database update based on which button was submitted
    button = request.form.get('submit_button')

    # todo - change the button name to save?
    if button == 'validate_and_submit':
      logger.debug(f"validate_and_submit was pressed")
      if wtf_form.validate():
        return redirect(url_for('main.index'))

  error_count_dict = wtf_count_errors(wtf_form, log_errors=True)

  logger.debug(f"incidence_prep() about to render get template")

  return render_template(template_file,
                         wtf_form=wtf_form,
                         crud_type=crud_type,
                         error_count_dict=error_count_dict,
                         id_incidence=getattr(model_row, "id_incidence", None),
                         )
