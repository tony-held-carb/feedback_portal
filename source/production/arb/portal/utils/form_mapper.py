"""
form_mapper.py

Provides filtering logic for querying the portal_updates table.

Includes logic for parsing ID ranges, substrings, and date filters
from request arguments in the feedback portal interface.
"""
from datetime import datetime
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import DeclarativeMeta, Query


def apply_portal_update_filters(query: Query,
                                portal_update_model: DeclarativeMeta | type[Any],
                                args: dict):
  """
  Apply user-defined filters to a `PortalUpdate` SQLAlchemy query.

  Args:
    query (Query): Query to be filtered.
    portal_update_model (DeclarativeMeta | type[Any]): ORM model class for the portal_updates table.
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
    # noinspection PyUnresolvedReferences
    query = query.filter(portal_update_model.key.ilike(f"%{filter_key}%"))
  if filter_user:
    # noinspection PyUnresolvedReferences
    query = query.filter(portal_update_model.user.ilike(f"%{filter_user}%"))
  if filter_comments:
    # noinspection PyUnresolvedReferences
    query = query.filter(portal_update_model.comments.ilike(f"%{filter_comments}%"))

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
              id_range_clauses.append(portal_update_model.id_incidence.between(start_val, end_val))
          elif start:
            start_val = int(start)
            # noinspection PyUnresolvedReferences
            id_range_clauses.append(portal_update_model.id_incidence >= start_val)
          elif end:
            end_val = int(end)
            # noinspection PyUnresolvedReferences
            id_range_clauses.append(portal_update_model.id_incidence <= end_val)
        except ValueError:
          continue  # Ignore malformed part
      elif part.isdigit():
        id_exact.add(int(part))

    clause_list = []
    if id_exact:
      # noinspection PyUnresolvedReferences
      clause_list.append(portal_update_model.id_incidence.in_(sorted(id_exact)))
    clause_list.extend(id_range_clauses)

    if clause_list:
      query = query.filter(or_(*clause_list))

  try:
    if start_date_str:
      start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
      # noinspection PyUnresolvedReferences
      query = query.filter(portal_update_model.timestamp >= start_dt)
    if end_date_str:
      end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
      end_dt = end_dt.replace(hour=23, minute=59, second=59)
      # noinspection PyUnresolvedReferences
      query = query.filter(portal_update_model.timestamp <= end_dt)
  except ValueError:
    pass  # Silently ignore invalid date inputs

  return query
