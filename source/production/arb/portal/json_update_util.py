"""
Utility functions to apply updates to a SQLAlchemy model's JSON field and
log each change to the portal_updates table for auditing purposes.
"""
import datetime

from sqlalchemy.orm.attributes import flag_modified

from arb.__get_logger import get_logger
from arb.portal.extensions import db
from arb.portal.sqla_models import PortalUpdate
from arb.utils.constants import PLEASE_SELECT

logger, pp_log = get_logger()


def apply_json_patch_and_log(model,
                             updates: dict,
                             json_field: str = "misc_json",
                             user: str = "anonymous",
                             comments: str = "") -> None:
  """
  Applies updates to a model's JSON field and logs each changed key-value pair.

  This function compares the existing values in a model's JSON field (usually
  `misc_json`) to a provided dictionary of updates. If a key's value differs,
  the function:
    - Updates the model's JSON field
    - Flags the field as modified for SQLAlchemy tracking
    - Writes a record to the portal_updates audit table

  Args:
    model (SQLAlchemy model): An instance of a SQLAlchemy model with a JSON column.
    updates (dict): Dictionary of key-value pairs to apply.
    json_field (str): Name of the JSON field in the model (default is "misc_json").
    user (str): Identifier for the user making the change (default is "anonymous").
    comments (str): Optional comment or description for the update.

  Returns:
    None

  Raises:
    AttributeError: If the specified JSON field does not exist on the model.

  Example:
    >>> apply_json_patch_and_log(incidence, {"status": "resolved"}, user="admin")
  """
  # In the future, may want to handle new rows differently
  json_data = getattr(model, json_field)
  if json_data is None:
    json_data = {}
    is_new_row = True
  else:
    is_new_row = False

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

  for key, new_value in updates.items():

    old_value = json_data.get(key)
    json_data[key] = new_value

    # Filter out non-useful updates
    if old_value is None and new_value is None:
      continue
    if old_value is None and new_value == "":
      continue
    # Note, on the rare situation that "Please Select" is a valid entry in a string field, it will be filtered out
    if old_value is None and new_value == PLEASE_SELECT:
      continue

    if old_value != new_value:
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

  setattr(model, json_field, json_data)
  flag_modified(model, json_field)
  db.session.commit()
