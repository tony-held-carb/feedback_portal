"""
Utility to apply updates to a model's JSON field and log each change to the portal_updates table.
"""
import datetime

from sqlalchemy.orm.attributes import flag_modified

from arb.__get_logger import get_logger
from arb.portal.extensions import db
from arb.portal.sqla_models import PortalUpdate

logger, pp_log = get_logger()


def apply_json_patch_and_log(model,
                             updates: dict,
                             json_field: str = "misc_json",
                             user: str = "anonymous",
                             comments: str = "") -> None:
  """
  Applies updates to a model's JSON field and logs each key/value change in the portal_updates table.

  Args:
      model: SQLAlchemy model instance with a JSON column like 'misc_json'.
      updates (dict): Dictionary of key/value pairs to apply.
      json_field (str): Name of the JSON column on the model.
      user (str): Current user (or 'anonymous').
      comments (str): Optional comment for the update.
  """
  json_data = getattr(model, json_field) or {}

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
    if old_value != new_value:
      log_entry = PortalUpdate(
        timestamp=datetime.datetime.now(datetime.UTC),
        key=key,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value),
        user=user,
        comments=comments or "",
        id_incidence=model.id_incidence,
      )
      db.session.add(log_entry)

    json_data[key] = new_value

  setattr(model, json_field, json_data)
  flag_modified(model, json_field)
