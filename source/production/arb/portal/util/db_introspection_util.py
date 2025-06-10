from pathlib import Path

from arb.__get_logger import get_logger
from arb.utils.sql_alchemy import get_class_from_table_name

logger, pp_log = get_logger()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')


def get_ensured_row(db, base, table_name="incidences", primary_key_name="id_incidence", id_=None) -> tuple:
  """
  Retrieve or create a row in the specified table using a primary key.

  If the row exists, it is returned. Otherwise, a new row is created and committed.

  Args:
    db (SQLAlchemy): SQLAlchemy database instance.
    base (AutomapBase): Reflected SQLAlchemy base metadata.
    table_name (str): Table name to operate on. Defaults to 'incidences'.
    primary_key_name (str): Name of the primary key column. Defaults to 'id_incidence'.
    id_ (int | None): Primary key value. If None, a new row is created.

  Returns:
    tuple: (model, id_, is_new_row)
      - model: SQLAlchemy ORM instance
      - id_: Primary key value
      - is_new_row: Whether a new row was created (True/False)

  Raises:
    AttributeError: If the model class lacks the specified primary key.
  """

  is_new_row = False

  session = db.session
  table = get_class_from_table_name(base, table_name)

  if id_ is not None:
    logger.debug(f"Retrieving {table_name} row with {primary_key_name}={id_}")
    model = session.get(table, id_)
    if model is None:
      is_new_row = True
      logger.debug(f"No existing row found; creating new {table_name} row with {primary_key_name}={id_}")
      model = table(**{primary_key_name: id_})
  else:
    is_new_row = True
    logger.debug(f"Creating new {table_name} row with auto-generated {primary_key_name}")
    model = table(**{primary_key_name: None})
    session.add(model)
    session.commit()
    id_ = getattr(model, primary_key_name)
    logger.debug(f"{table_name} row created with {primary_key_name}={id_}")

  return model, id_, is_new_row
