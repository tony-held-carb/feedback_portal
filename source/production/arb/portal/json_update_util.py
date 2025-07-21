"""
  Utility functions to apply updates to an SQLAlchemy model's JSON field and
  log each change to the portal_updates table for auditing purposes.

  Features:
    - Compares current vs. new values in a model's JSON field
    - Logs only meaningful changes to a structured audit table
    - Excludes no-op or default placeholders (e.g., None, "")

  Args:
    None

  Returns:
    None

  Attributes:
    logger (logging.Logger): Logger instance for this module.

  Examples:
    from arb.portal.json_update_util import apply_json_patch_and_log
    apply_json_patch_and_log(model, updates)

  Notes:
    - Called when a form submission modifies a feedback record, with changes
      applied to the model and written to the database via SQLAlchemy.
    - The logger emits diagnostic messages for auditing and debugging.
"""

import datetime
import logging

from sqlalchemy.orm import object_session
from sqlalchemy.orm.attributes import flag_modified

from arb.portal.extensions import db
from arb.portal.sqla_models import PortalUpdate
from arb.utils.constants import PLEASE_SELECT

logger = logging.getLogger(__name__)


def apply_json_patch_and_log(model,
                             updates: dict,
                             json_field: str = "misc_json",
                             user: str = "anonymous",
                             comments: str = "") -> None:
  """
  Apply updates to a model's JSON field and log each change in portal_updates.

  This function performs a key-by-key comparison between the current JSON field
  (`model.misc_json` by default) and the proposed `updates`. For each key where
  the value has changed:
    - The field is updated
    - The change is logged to `portal_updates` with a timestamp and user info
    - Redundant or placeholder updates are skipped (e.g., None → None)

  Args:
    model (SQLAlchemy model): A SQLAlchemy ORM instance with a JSON column.
    updates (dict): Dictionary of key-value updates to apply.
    json_field (str): Name of the JSON field (default: 'misc_json').
    user (str): Identifier of the user performing the change (default: 'anonymous').
    comments (str): Optional comment for the log entry.

  Returns:
    None

  Raises:
    AttributeError: If the specified JSON field does not exist on the model.

  Examples:
    apply_json_patch_and_log(model, {"field1": "new_value"}, user="alice")

  Notes:
    - Filters out non-useful updates (e.g., None → None, None → "", None → PLEASE_SELECT).
    - Logs all changes to the portal_updates table for auditing.
    - Commits the session after applying changes and logging.
    - Raises and logs exceptions on commit failure.
  """

  # 🆕 DIAGNOSTIC: Log function entry and model state
  logger.info(f"[apply_json_patch_and_log] ENTRY: model={type(model).__name__}, "
              f"model.id_incidence={getattr(model, 'id_incidence', 'N/A')}, "
              f"updates={len(updates)} fields, json_field={json_field}")

  # Check if model is in session
  session = object_session(model)
  logger.info(f"[apply_json_patch_and_log] Model session: {session is not None}, "
              f"Model in session: {model in session if session else False}")

  # In the future, may want to handle new rows differently
  json_data = getattr(model, json_field)
  if json_data is None:
    json_data = {}
    is_new_row = True
  else:
    is_new_row = False

  logger.info(f"[apply_json_patch_and_log] Initial json_data: {json_data}, is_new_row: {is_new_row}")

  # Consistency check
  if "id_incidence" in json_data and json_data["id_incidence"] != model.id_incidence:
    logger.warning(f"[apply_json_patch_and_log] MISMATCH: model.id_incidence={model.id_incidence} "
                   f"!= misc_json['id_incidence']={json_data['id_incidence']}")

  # Remove id_incidence from updates to avoid contaminating misc_json
  if "id_incidence" in updates:
    if updates["id_incidence"] != model.id_incidence:
      logger.warning(f"[json_update] Removing conflicting id_incidence from updates: "
                     f"{updates['id_incidence']}")
      del updates["id_incidence"]

  changes_made = 0
  for key, new_value in updates.items():

    old_value = json_data.get(key)
    json_data[key] = new_value

    # Filter out non-useful updates
    if old_value is None and new_value is None:
      continue
    if old_value is None and new_value == "":
      continue
    # Note, on the rare situation that "Please Select" is a valid entry in a string field - it will be filtered out
    if old_value is None and new_value == PLEASE_SELECT:
      continue

    if old_value != new_value:
      changes_made += 1
      log_entry = PortalUpdate(
        timestamp=datetime.datetime.now(datetime.UTC),
        key=key,
        old_value=str(old_value),
        new_value=str(new_value),
        user=user,
        comments=comments or "",
        id_incidence=model.id_incidence,
      )
      db.session.add(log_entry)
      logger.debug(f"[apply_json_patch_and_log] Added log entry for {key}: {old_value} -> {new_value}")

  logger.info(f"[apply_json_patch_and_log] Applied {changes_made} changes to json_data")

  setattr(model, json_field, json_data)
  flag_modified(model, json_field)

  # 🆕 DIAGNOSTIC: Log before commit
  logger.info(f"[apply_json_patch_and_log] Before commit: model.{json_field}={getattr(model, json_field)}")
  logger.info(f"[apply_json_patch_and_log] About to commit {changes_made} changes to database")

  try:
    db.session.commit()
    logger.info(f"[apply_json_patch_and_log] ✅ COMMIT SUCCESSFUL: {changes_made} changes committed")

    # 🆕 DIAGNOSTIC: Verify model state after commit
    logger.info(f"[apply_json_patch_and_log] After commit: model.{json_field}={getattr(model, json_field)}")

    # Check if model is still in session after commit
    session_after = object_session(model)
    logger.info(f"[apply_json_patch_and_log] Model session after commit: {session_after is not None}")

  except Exception as e:
    logger.error(f"[apply_json_patch_and_log] ❌ COMMIT FAILED: {e}")
    logger.exception(f"[apply_json_patch_and_log] Full exception details:")
    raise
