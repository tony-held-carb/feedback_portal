"""
SQLAlchemy related utilities.
"""
from sqlalchemy import desc, inspect

import arb.__get_logger as get_logger
from arb.utils.misc import log_error

__version__ = "1.0.0"
logger, pp_log = get_logger.get_logger(__name__, __file__)


def sa_model_diagnostics(model, comment=""):
  """
  Log diagnostic information about an SQLAlchemy model.

  Args:
    model: SQLAlchemy model
    comment (str): header for logging purposes
  """
  logger.debug(f"Diagnostics for model of type {type(model)=}")
  if comment:
    logger.debug(f"{comment}")
  logger.debug(f"{model=}\n")

  fields = get_sa_fields(model)
  for key in fields:
    value = getattr(model, key)
    logger.debug(f"{key} {type(value)} = ({value})")


def get_sa_fields(model):
  """
  Return the sorted field names (i.e. column names) associated with a sqlalchemy model.

  Args:
    model (db.Model): sqlalchemy model

  Returns (list): field names (i.e. column names) associated with a sqlalchemy model.

  """
  inst = inspect(model)
  model_fields = [c_attr.key for c_attr in inst.mapper.column_attrs]

  model_fields.sort()
  return model_fields


def get_sa_column_types(model, is_instance=True):
  """
  Get the column name and datatype of a sqlalchemy model.

  Args:
    model (db.Model): SQLAlchemy model
    is_instance (bool): if True, the model is an instance (not the class)
  Returns (dict): column names are the key, values are a dict with sql and python types

  """

  # Get the table inspector for the model
  if is_instance:
    inspector = inspect(type(model))
  else:
    inspector = inspect(model)

  logger.debug(f"\n\t{model=}")
  logger.debug(f"\n\t{inspector=}")

  columns_info = {}
  for column in inspector.columns:
    col_name = column.name
    sqlalchemy_type = column.type
    python_type = column.type.python_type

    columns_info[col_name] = {
      'sqlalchemy_type': sqlalchemy_type,
      'python_type': python_type
    }

  return columns_info


def get_sa_automap_types(engine, base):
  """
  Return the automap types associated with a sqlalchemy model to determine underlying DB, SQLAlchemy, and python
  data types associated with each column's data.

  Args:
    engine (sqlalchemy.engine.Engine): SQLAlchemy engine instance
    base (DeclarativeMeta): SQLAlchemy declarative base

  Notes:
    base likely created with:
      base = automap_base()
      base.prepare(db.engine, reflect=True)

  Returns (dict): Dictionary of database table names, columns names, and datatypes with the structure:
    result[table_name][column_name][kind] = type
    where: kind can be 'database_type', 'sqlalchemy_type', or 'python_type',
  """
  result = {}

  inspector = inspect(engine)

  # Loop through all the mapped classes (tables)
  # print(f"{type(base)=}")
  # print(f"{type(base.classes)=}")
  for class_name, mapped_class in base.classes.items():
    # print(f"Table: {class_name}")
    result[class_name] = {}

    # Get the table columns
    columns = mapped_class.__table__.columns

    # Loop through columns to get types
    for column in columns:
      # print(f"Column: {column.name}")
      result[class_name][column.name] = {}
      db_type = None
      sa_type = None
      py_type = None

      # Database (SQL) column type
      db_column_type = inspector.get_columns(class_name)
      for col in db_column_type:
        if col['name'] == column.name:
          db_type = col['type']
          # print(f"  Database type (SQL): {db_type}")

          # SQLAlchemy type
          sa_type = type(db_type).__name__
          # print(f"  SQLAlchemy type: {sa_type}")

      # Python type
      try:
        py_type = column.type.python_type
      except Exception as e:
        msg = f"{column.name} is of type: {sa_type} that is not implemented in python.  Setting python type to None."
        logger.warning(msg)
        logger.warning(e)

      # print(f"  Python type: {py_type}")
      result[class_name][column.name]["python_type"] = py_type
      result[class_name][column.name]["database_type"] = db_type
      result[class_name][column.name]["sqlalchemy_type"] = sa_type

  return result


def sa_model_dict_compare(model_before, model_after):
  """
  Compare two dictionary representations of an SQLAlchemy model to determine the changes.

  Args:
    model_before (dict): dictionary representation of an SQLAlchemy model before changes
    model_after (dict): dictionary representation of an SQLAlchemy model after changes

  Returns (dict): key value pairs of new items associated with a model dictionary
  """
  changes = {}
  for field in model_after:
    if field not in model_before or model_before[field] != model_after[field]:
      changes[field] = model_after[field]
  return changes


def sa_model_to_dict(model):
  """
  Convert a sqlalchemy model to a python dictionary.

  Args:
    model: SQLAlchemy model

  Returns (dict): python dictionary with model column names as keys and column values as values.
  """
  model_as_dict = {}
  fields = get_sa_fields(model)
  for field in fields:
    value = getattr(model, field)
    model_as_dict[field] = value

  return model_as_dict


def table_to_list(base, session, table_name) -> list:
  """
  Extract content of a table a list of rows where each row is a dictionary
  with the column name as the key and the value as the content

  Args:
    base (sqlalchemy.orm.decl_api.DeclarativeMeta): base associated with database
    session:
    table_name (str):

  Returns:

  """
  result = []

  # Retrieve the table class dynamically
  table = base.classes.get(table_name)

  if table:
    logger.debug(f"Selecting data from: {table_name}")
    # Query all rows in the table
    rows = session.query(table).all()

    # Print each row and its column values
    for i, row in enumerate(rows):
      # Use the __table__.columns property to get column names
      column_names = table.__table__.columns.keys()
      row_data = {col: getattr(row, col) for col in column_names}
      result.append(row_data)
  else:
    logger.debug(f"Table '{table_name}' not found in the database.")

  return result


def get_class_from_table_name(base, table_name):
  """
  Retrieves the table from SQLAlchemy's metadata by the table_name.
  If the table is not mapped, this returns None.

  Args:
    base (DeclarativeMeta): SQLAlchemy declarative base
    table_name (str): database table name

  Returns (Mapper): table as mapped class of database

  Notes:
    To access the class mapped to a specific table name in SQLAlchemy without directly using _class_registry,
    you can use the Base.metadata object, which stores information about all mapped tables.
  """
  try:
    # Look up the table in metadata and find its mapped class
    table = base.metadata.tables.get(table_name)
    if table is not None:
      for mapper in base.registry.mappers:
        if mapper.local_table == table:
          return mapper.class_
    return None
  except Exception as e:
    msg = f"Exception occurred when trying to get table named {table_name}"
    logger.error(msg, exc_info=True)
    logger.error(f"exception info: {e}")

  return None


def get_rows_by_table_name(db,
                           base,
                           table_name,
                           colum_name_pk=None,
                           ascending=True):
  """
  Return all table rows.  If colum_name_pk is provided, sort by that column.

  Args:
    db (SQLAlchemy): SQLAlchemy db
    base (DeclarativeMeta): SQLAlchemy declarative base
    table_name (str): table of interest
    colum_name_pk (str): name of the column to sort rows
    ascending (bool): True for ascending, False for descending (only used if colum_name_pk is specified).

  Returns (SQLAlchemy.Model): rows
  """
  # table = base.classes[table_name]
  # table = base.registry._class_registry.get(table_name)
  table = get_class_from_table_name(base, table_name)
  logger.info(f"{type(table)=}")

  if colum_name_pk:
    column_pk = getattr(table, colum_name_pk)
    if ascending:
      rows = db.session.query(table).order_by(column_pk).all()
    else:
      rows = db.session.query(table).order_by(desc(column_pk)).all()
  else:
    rows = db.session.query(table).all()

  logger.debug(f"Query result type: {type(rows)=}")
  return rows


def delete_commit_and_log_model(db,
                                model_row,
                                comment=''):
  """
  Delete model from db, commit, and log contents before.

  Args:
    db (SQLAlchemy): SQLAlchemy db
    model_row (SQLAlchemy.Model): row that will potentially be transformed and commited
    comment (str): comment for logging the commit

  Returns:

  """
  row_as_dict = sa_model_to_dict(model_row)  # save contents for logging
  logger.info(f"Deleting model {comment=}: model contents={row_as_dict}")

  try:
    db.session.delete(model_row)
    db.session.commit()
  except Exception as e:
    log_error(e)


def add_commit_and_log_model(db,
                             model_row,
                             comment='',
                             model_before=None):
  """
  Add model to db, commit, and log contents before and after (if possible).

  Args:
    db (SQLAlchemy): SQLAlchemy db
    model_row (SQLAlchemy.Model): row that will potentially be transformed and commited
    comment (str): comment for logging the commit
    model_before (dict): optional dictionary (created with sa_model_to_dict) before a transformation
  """
  if model_before is not None:
    logger.info(f"model before commit {comment=}: {model_before}")

  try:
    db.session.add(model_row)
    db.session.commit()
    model_after = sa_model_to_dict(model_row)
    logger.info(f"model value after commit (all values): {model_after}")
    if model_before is not None:
      changes = sa_model_dict_compare(model_before, model_after)
      logger.info(f"model value after commit (changed values only): {changes}")
  except Exception as e:
    log_error(e)


def get_table_row_and_column(db, base, table_name, column_name, id_):
  """
  Given a table and column name, return the fields value given a primary key.


  Args:
    db (SQLAlchemy): SQLAlchemy db
    base (DeclarativeMeta): SQLAlchemy declarative base
    table_name (str): name of primary table
    column_name (str): name of the column with data of interest
    id_ (int): value of the primary key of table

  Returns:
    tuple: A tuple containing row and column value where id_ matches the primary key in a table.
      - row (SQLAlchemy.Model): Single row from a SQLAlchemy model of table_name
      - column_value: value of column_name in row.
  """
  logger.debug(f"Finding table {table_name}'s value in column {column_name} for primary key of {id_}.")
  column_value = None

  table = get_class_from_table_name(base, table_name)
  row = db.session.query(table).get(id_)

  if row:
    column_value = getattr(row, column_name)

  logger.debug(f"{row=}")
  logger.debug(f"{column_value=}")

  return row, column_value


def get_foreign_value(db,
                      base,
                      primary_table_name,
                      foreign_table_name,
                      primary_table_fk_name,
                      foreign_table_column_name,
                      primary_table_pk_value,
                      primary_table_pk_name=None,
                      foreign_table_pk_name=None,
                      ):
  """
  Look up the value of a foreign key given the primary and foreign table names and target column.

  Args:
    db (SQLAlchemy): SQLAlchemy db
    base (DeclarativeMeta): SQLAlchemy declarative base
    primary_table_name (str): name of primary table
    foreign_table_name (str): name of foreign table
    primary_table_pk_value (int): primary table's primary key value
    primary_table_fk_name (str): column name of foreign key in primary table
    foreign_table_column_name (str): column with desired data in foreign table
    primary_table_pk_name (str|None): name of primary key column in primary table
    foreign_table_pk_name (str|None): name of primary key column in foreign table

  Returns (str|None): foreign key value

  Notes:
    If multiple rows match the key value, only the first will be returned.
  """

  logger.debug(f"Determining value in foreign table: {primary_table_name=}, {foreign_table_name=}, "
               f"{primary_table_fk_name=}, {foreign_table_column_name=}, {primary_table_pk_name=}, {foreign_table_pk_name=},")
  result = None

  # incidences_with_json is not connected to the other tables, so you have to use incidences to get the sector
  primary_table = get_class_from_table_name(base, primary_table_name)
  foreign_table = get_class_from_table_name(base, foreign_table_name)

  if primary_table_pk_name is not None:
    column = getattr(primary_table, primary_table_pk_name)
    # Perform the query with a filter
    primary_row = db.session.query(primary_table).filter(column == primary_table_pk_value).first()
  else:
    primary_row = db.session.query(primary_table).get(primary_table_pk_value)

  if primary_row:
    primary_table_fk_value: int = getattr(primary_row, primary_table_fk_name)
    if foreign_table_pk_name is not None:
      column = getattr(foreign_table, foreign_table_pk_name)
      # Perform the query with a filter
      foreign_row = db.session.query(foreign_table).filter(column == primary_table_fk_value).first()
    else:
      foreign_row = db.session.query(foreign_table).get(primary_table_fk_value)
    if foreign_row:
      result = getattr(foreign_row, foreign_table_column_name)

  logger.debug(f"Foreign key lookup found to be: {result}")
  return result


def find_auto_increment_value(db, table_name, column_name):
  """
  Given a SQLAlchemy database, find the next auto increment value for a table given a column name.

  Args:
    db (SQLAlchemy): SQLAlchemy db
    table_name (str): name of table
    column_name (str): name of column

  Returns (str): diagnostic information about next primary key auto increment

  """
  from sqlalchemy import text

  # Connect to the database
  with db.engine.connect() as connection:
    # Query to get the next value of the sequence (next auto-increment value)
    # result = connection.execute(text(f"SELECT pg_get_serial_sequence('incidences', 'id_incidence')"))
    sql_text = f"SELECT pg_get_serial_sequence('{table_name}', '{column_name}')"
    result = connection.execute(text(sql_text))
    sequence_name = result.scalar()

    # print(f"{type(result)=}, {result=}")
    # print(f"{type(sequence_name)=}, {sequence_name=}")

    sql_text = f"SELECT nextval('{sequence_name}')"
    result = connection.execute(text(sql_text))
    next_val = result.scalar()

    # print(f"{type(result)=}, {result=}")
    # print(f"{type(next_val)=}, {next_val=}")

    result = f"Table '{table_name}' column '{column_name}' sequence '{sequence_name}' next value is '{next_val}'"

  return result
