"""Form Integration - Auto-split from app_util."""

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



def apply_portal_update_filters(query, PortalUpdate, args: dict):
  """
  Apply user-defined filters to a `PortalUpdate` SQLAlchemy query.

  Args:
    query (SQLAlchemy Query): Query to be filtered.
    PortalUpdate (Base): ORM model class for the portal_updates table.
    args (dict): Typically from `request.args`, containing filter values.

  Supported filters:
    - Substring matches on key, user, comments
    - ID exact match or range parsing (e.g. "100-200, 250")
    - Date range filtering via `start_date` and `end_date`

  Supported ID formats (via filter_id_incidence):
  ------------------------------------------------
  - "123"                  → Matches ID 123 exactly
  - "100-200"              → Matches IDs from 100 to 200 inclusive
  - "-250"                 → Matches all IDs ≤ 250
  - "300-"                 → Matches all IDs ≥ 300
  - "123,150-200,250-"     → Mixed exacts and ranges
  - "abc, 100-xyz, 222"    → Invalid parts are ignored

  Returns (SQLAlchemy Query):
    SQLAlchemy query: Modified query with filters applied.
  """
  filter_key = args.get("filter_key", "").strip()
  filter_user = args.get("filter_user", "").strip()
  filter_comments = args.get("filter_comments", "").strip()
  filter_id_incidence = args.get("filter_id_incidence", "").strip()
  start_date_str = args.get("start_date", "").strip()
  end_date_str = args.get("end_date", "").strip()

  if filter_key:
    query = query.filter(PortalUpdate.key.ilike(f"%{filter_key}%"))
  if filter_user:
    query = query.filter(PortalUpdate.user.ilike(f"%{filter_user}%"))
  if filter_comments:
    query = query.filter(PortalUpdate.comments.ilike(f"%{filter_comments}%"))

  if filter_id_incidence:
    id_exact = set()
    id_range_clauses = []

    for part in filter_id_incidence.split(","):
      part = part.strip()
      if not part:
        continue
      if "-" in part:
        try:
          start, end = part.split("-")
          start = start.strip()
          end = end.strip()
          if start and end:
            start_val = int(start)
            end_val = int(end)
            if start_val <= end_val:
              id_range_clauses.append(PortalUpdate.id_incidence.between(start_val, end_val))
          elif start:
            start_val = int(start)
            id_range_clauses.append(PortalUpdate.id_incidence >= start_val)
          elif end:
            end_val = int(end)
            id_range_clauses.append(PortalUpdate.id_incidence <= end_val)
        except ValueError:
          continue  # Ignore malformed part
      elif part.isdigit():
        id_exact.add(int(part))

    clause_list = []
    if id_exact:
      clause_list.append(PortalUpdate.id_incidence.in_(sorted(id_exact)))
    clause_list.extend(id_range_clauses)

    if clause_list:
      query = query.filter(or_(*clause_list))

  try:
    if start_date_str:
      start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
      query = query.filter(PortalUpdate.timestamp >= start_dt)
    if end_date_str:
      end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
      end_dt = end_dt.replace(hour=23, minute=59, second=59)
      query = query.filter(PortalUpdate.timestamp <= end_dt)
  except ValueError:
    pass  # Silently ignore invalid date inputs

  return query

