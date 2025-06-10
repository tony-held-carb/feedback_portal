"""Db Patch Util - Auto-split from app_util."""

# Imports

from datetime import datetime
from pathlib import Path

from flask import redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy.ext.automap import AutomapBase
from sqlalchemy.ext.declarative import DeclarativeMeta
from werkzeug.datastructures import FileStorage

from arb.__get_logger import get_logger
from arb.portal.constants import PLEASE_SELECT
from arb.portal.db_hardcoded import LANDFILL_SECTORS, OIL_AND_GAS_SECTORS
from arb.portal.extensions import db
from arb.utils.excel.xl_parse import get_json_file_name
from arb.utils.json import json_load_with_meta
from arb.utils.sql_alchemy import add_commit_and_log_model, get_class_from_table_name, get_foreign_value, get_table_row_and_column, \
  sa_model_diagnostics, sa_model_to_dict
from arb.utils.web_html import upload_single_file
from arb.utils.wtf_forms_util import (
  initialize_drop_downs, model_to_wtform,
  validate_no_csrf, wtf_count_errors, wtform_to_model
)

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')



def dict_to_database(db,
                     base,
                     data_dict: dict,
                     table_name="incidences",
                     primary_key="id_incidence",
                     json_field="misc_json") -> int:
  """
  Insert or update a row in the specified table using a dictionary payload.

  The payload is merged into a model instance and committed to the database.

  Args:
    db (SQLAlchemy): SQLAlchemy database instance.
    base (AutomapBase): Reflected SQLAlchemy base metadata.
    data_dict (dict): Dictionary containing payload data.
    table_name (str): Table name to modify. Defaults to 'incidences'.
    primary_key (str): Name of the primary key field. Defaults to 'id_incidence'.
    json_field (str): Name of the JSON field to update. Defaults to 'misc_json'.

  Returns:
    int: Final value of the primary key for the affected row.

  Raises:
    ValueError: If data_dict is empty.
    AttributeError: If the resulting model does not expose the primary key.
  """

  from arb.utils.wtf_forms_util import update_model_with_payload

  if not data_dict:
    msg = "Attempt to add empty entry to database"
    logger.warning(msg)
    raise ValueError(msg)

  id_ = data_dict.get(primary_key)

  model, id_, is_new_row = get_ensured_row(
    db=db,
    base=base,
    table_name=table_name,
    primary_key_name=primary_key,
    id_=id_
  )

  # Backfill generated primary key into payload if it was not supplied
  if is_new_row:
    logger.debug(f"Backfilling {primary_key} = {id_} into payload")
    data_dict[primary_key] = id_

  update_model_with_payload(model, data_dict, json_field=json_field)

  session = db.session
  session.add(model)
  session.commit()

  # Final safety: extract final PK from model
  try:
    return getattr(model, primary_key)
  except AttributeError as e:
    logger.error(f"Model has no attribute '{primary_key}': {e}")
    raise

