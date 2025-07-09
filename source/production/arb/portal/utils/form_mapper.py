"""
  Filtering logic for querying the portal_updates table in the feedback portal.

  This module provides functions to parse and apply filters from request arguments,
  including ID ranges, substrings, and date filters, to SQLAlchemy queries.

  Args:
    None

  Returns:
    None

  Attributes:
    apply_portal_update_filters (function): Applies user-defined filters to a portal_updates query.
    logger (logging.Logger): Logger instance for this module.

  Examples:
    from arb.portal.utils.form_mapper import apply_portal_update_filters
    filtered_query = apply_portal_update_filters(query, PortalUpdate, request.args)

  Notes:
    - Used by the feedback portal interface for advanced filtering of update logs.
    - Supports flexible ID and date range parsing.
"""
import logging
from datetime import datetime
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Query
from sqlalchemy.orm import DeclarativeMeta

logger = logging.getLogger(__name__)

def apply_portal_update_filters(query: Query,
                                portal_update_model: DeclarativeMeta | type[Any],
                                args: dict):
  """
  Apply user-defined filters to a `PortalUpdate` SQLAlchemy query.

  Args:
    query (Query): Query to be filtered.
    portal_update_model (DeclarativeMeta | type[Any]): ORM model class for the portal_updates table.
    args (dict): Typically from `request.args`, containing filter values.

  Returns:
    Query: Modified SQLAlchemy query with filters applied.

  Examples:
    filtered_query = apply_portal_update_filters(query, PortalUpdate, request.args)
    # Applies filters for key, user, comments, ID ranges, and date ranges

  Notes:
    - Supported filters: substring matches (key, user, comments), ID exact/range, date range.
    - ID formats: '123', '100-200', '-250', '300-', '123,150-200,250-'.
    - Invalid or malformed filter parts are ignored.
    - Date filters expect 'YYYY-MM-DD' format; invalid dates are ignored.

  Additional notes on supported ID formats (via filter_id_incidence):
  ------------------------------------------------
    - "123"                  → Matches ID 123 exactly
    - "100-200"              → Matches IDs from 100 to 200 inclusive
    - "-250"                 → Matches all IDs ≤ 250
    - "300-"                 → Matches all IDs ≥ 300
    - "123,150-200,250-"     → Mixed exacts and ranges
    - "abc, 100-xyz, 222"    → Invalid parts are ignored
  """
  filter_key = args.get("filter_key", "").strip()
  filter_user = args.get("filter_user", "").strip()
  filter_comments = args.get("filter_comments", "").strip()
  filter_id_incidence = args.get("filter_id_incidence", "").strip()
  start_date_str = args.get("start_date", "").strip()
  end_date_str = args.get("end_date", "").strip()

  if filter_key:
    # noinspection PyUnresolvedReferences
    query = query.filter(portal_update_model.key.ilike(f"%{filter_key}%")) # type: ignore
  if filter_user:
    # noinspection PyUnresolvedReferences
    query = query.filter(portal_update_model.user.ilike(f"%{filter_user}%")) # type: ignore
  if filter_comments:
    # noinspection PyUnresolvedReferences
    query = query.filter(portal_update_model.comments.ilike(f"%{filter_comments}%"))  # type: ignore

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
              # noinspection PyUnresolvedReferences
              id_range_clauses.append(portal_update_model.id_incidence.between(start_val, end_val))  # type: ignore
          elif start:
            start_val = int(start)
            # noinspection PyUnresolvedReferences
            id_range_clauses.append(portal_update_model.id_incidence >= start_val)  # type: ignore
          elif end:
            end_val = int(end)
            # noinspection PyUnresolvedReferences
            id_range_clauses.append(portal_update_model.id_incidence <= end_val)  # type: ignore
        except ValueError:
          continue  # Ignore malformed part
      elif part.isdigit():
        id_exact.add(int(part))

    clause_list = []
    if id_exact:
      # noinspection PyUnresolvedReferences
      clause_list.append(portal_update_model.id_incidence.in_(sorted(id_exact)))  # type: ignore
    clause_list.extend(id_range_clauses)

    if clause_list:
      query = query.filter(or_(*clause_list))

  try:
    if start_date_str:
      start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
      # noinspection PyUnresolvedReferences
      query = query.filter(portal_update_model.timestamp >= start_dt)  # type: ignore
    if end_date_str:
      end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
      end_dt = end_dt.replace(hour=23, minute=59, second=59)
      # noinspection PyUnresolvedReferences
      query = query.filter(portal_update_model.timestamp <= end_dt)  # type: ignore
  except ValueError:
    pass  # Silently ignore invalid date inputs

  return query
