"""
app_util.py has utility functions specific to the feedback_portal app.

Notes:
   * General purpose utility functions that are not tightly coupled with feedback_portal
     app should be in arb.util so they can be used in other projects.
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.attributes import flag_modified

import arb.__get_logger as get_logger
from arb.utils.excel.xl_parse import get_json_file_name
from arb.utils.json import json_load_with_meta
from arb.utils.sql_alchemy import add_commit_and_log_model, get_class_from_table_name, get_foreign_value, get_table_row_and_column, \
  sa_model_to_dict
from arb.utils.web_html import upload_single_file

logger, pp_log = get_logger.get_logger(__name__, __file__)


def get_sector_info(db, base, id_):
  """
  Given an incidence primary key, return the sector and sector type associated with the incidence.

  Args:
    db (SQLAlchemy): SQLAlchemy database associated with a flask app
    base (DeclarativeMeta): SQLAlchemy declarative base
    id_ (int): primary key of the incidences table

  Returns
    tuple: A tuple containing the sector and sector type associated with the incidence.
      - sector (str): Sector name.
      - sector_type (str): Sector type (Oil & Gas, or Landfill).
  """
  logger.debug(f"get_sector_info() called to determining sector & sector type for {id_=}")
  primary_table_name = 'incidences'
  json_column = 'misc_json'

  sector_by_foreign_key = get_foreign_value(db,
                                            base,
                                            primary_table_name=primary_table_name,
                                            foreign_table_name='sources',
                                            primary_table_fk_name='source_id',
                                            foreign_table_column_name='sector',
                                            primary_table_pk_value=id_,
                                            )

  row, misc_json = get_table_row_and_column(db,
                                            base,
                                            table_name=primary_table_name,
                                            column_name=json_column,
                                            id_=id_)
  if misc_json is None:
    misc_json = {}

  row_before = sa_model_to_dict(row)  # save contents for logging
  _ = resolve_sector(sector_by_foreign_key, row, misc_json)
  sector, sector_type = resolve_sector_type(row, misc_json)

  add_commit_and_log_model(db,
                           row,
                           comment='resolving sector and sector_type',
                           model_before=row_before)

  logger.debug(f"get_sector_info() returning {sector=} {sector_type=}")

  return sector, sector_type


def resolve_sector_type(row, misc_json):
  """
  Find the sector type associated with an incidence.

  Args:
    row (SQLAlchemy.Model): row associated with incidence matching id_
    misc_json (dict): dictionary of json column

  Returns:
    tuple: A tuple containing sector, sector_type.
      - sector (str): Sector associated with the incidence.
      - sector_type (str): Sector type associated with the incidence.
  """
  logger.debug(f"resolve_sector_type() called with {row=}, {misc_json}")
  # Find the corresponding sector_type associated with the sector
  sector = misc_json['sector']
  sector_type = get_sector_type(sector)

  if 'sector_type' not in misc_json:
    misc_json['sector_type'] = sector_type
    flag_modified(row, "misc_json")
    logger.debug(f"sector_type initialized to: {sector_type}")
  elif misc_json['sector_type'] != sector_type:
    logger.warning(f"Sector Type mismatch, JSON data will not be adjusted from {misc_json['sector_type']} to"
                   f"{sector_type=}")

  logger.debug(f"resolve_sector_type() returning with {sector=}, {sector_type}")

  return sector, sector_type


def resolve_sector(sector_by_foreign_key, row, misc_json):
  """
  There may be a mismatch between foreign key sector and json sector during early prototyping routines.
  This function tries to align the data mismatches.  Note, mismatches should only be present during prototyping, and once
  the json formulation and data schema are updated, there should not be mismatches.

  Args:
    sector_by_foreign_key (str): sector as determined by foreign key lookup
    row (SQLAlchemy.Model): row associated with incidence matching id_
    misc_json (dict): dictionary of json column

  Returns (str): sector associated with the incidence.
  """
  logger.debug(f"resolve_sector() called with {sector_by_foreign_key=}, {row=}, {misc_json=}")
  default_sector = 'Oil & Gas'  # for prototyping assume incidences without sector information are 'Oil & Gas'

  if sector_by_foreign_key is None:
    logger.warning(f"sector column value in sources table is None.")
  else:
    if 'sector' not in misc_json:
      logger.warning(f"Sector mismatch.  Sector currently undefined in json data and will be set to {sector_by_foreign_key=}")
      misc_json['sector'] = sector_by_foreign_key
      flag_modified(row, "misc_json")
    else:
      if sector_by_foreign_key != misc_json['sector']:
        logger.warning(f"Sector mismatch, JSON data will not be adjusted.  {sector_by_foreign_key=}, {misc_json['sector']=}")

  # Ensure json entry for sector
  if 'sector' not in misc_json:
    misc_json['sector'] = default_sector
    flag_modified(row, "misc_json")

  logger.debug(f"resolve_sector() returning {misc_json['sector']=}")

  return misc_json['sector']


def get_sector_type(sector):
  """
  Returns the sector (e.g. "Oil & Gas" or "Landfill") based on a sector name
  (e.g. "Industrial: Power Generation" or "Anaerobic Digester").

  Args:
    sector (str): Sector name.

  Returns (str): Sector type.  Currently only 'Oil & Gas' and 'Landfill' are implemented.
  """
  # todo - add ValueError: Unknown sector type: 'Recycling & Waste: Landfills'.

  if sector in [
    "Industrial - Other",
    "Industrial: Other",
    "Industrial: Oil & Gas",
    "Industrial: Power Generation",
    "Oil and Gas",
    "Oil & Gas",
  ]:
    sector_type = "Oil & Gas"
  elif sector in [
    "Agriculture: Dairy (Enteric Fermentation or Manure Management)",
    "Agriculture: Dairy Digester",
    "Agriculture: Other",
    "Anaerobic Digester",
    "Compost",
    "Landfill",
    "Landfills",
    "Livestock",
    "Recycling & Waste: Compost",
    "Recycling & Waste: Anaerobic Digester",
    "Recycling & Waste: Landfills",
    "Recycling & Waste: Other",
  ]:
    sector_type = "Landfill"
  else:
    raise ValueError(f"Unknown sector type: '{sector}'.")
  return sector_type


def upload_and_update_db(db, upload_dir, request_file, base):
  """
  Save a file uploaded from a html post request and parse the contents and add to the database if possible.

  Args:
    db (SQLAlchemy): SQLAlchemy database associated with a flask app
    request_file:
      - request_file likely created with: request_file = request.files['file']
    upload_dir (str|Path):
      - Path to server directory for file uploads
    base (DeclarativeMeta): SQLAlchemy declarative base

  Returns:
    tuple: A tuple containing the file_name, id_incidence and sector.
    - file_name (Path): filename associated with json data
    - id_ (int): id_incidence.
    - sector (str): feedback sector.

  Notes:
  """
  logger.debug(f"upload_and_update_db() called with {request_file=}")

  # Feedback form ID associated with upload
  id_ = None
  sector = None

  file_name = upload_single_file(upload_dir, request_file)
  add_file_to_upload_table(db, file_name, status="File Added", description=None)

  # if file is xl and can be converted to json,
  # save a json version of the file and return the filename
  json_file_name = get_json_file_name(file_name)

  if json_file_name:
    id_, sector = json_file_to_db(db, json_file_name, base)

  return file_name, id_, sector


def json_file_to_db(db, file_name, base):
  """
  Update database with contents of a json file.

  Args:
    db (SQLAlchemy): SQLAlchemy database associated with a flask app
    file_name (Path): path to .json file on server
    base (DeclarativeMeta): SQLAlchemy declarative base

  Returns:
      tuple: A tuple containing the id_incidence and sector.
      - id_ (int): id_incidence.
      - sector (str): feedback sector.

  """
  json_as_dict, metadata = json_load_with_meta(file_name)
  id_, sector = xl_dict_to_database(db, base, json_as_dict, 'Feedback Form')

  return id_, sector


def xl_dict_to_database(db, base, xl_dict, tab_name='Feedback Form'):
  """
  Add spreadsheet contents represented by xl_dict to the database.

  Args:
    db (SQLAlchemy): SQLAlchemy database associated with a flask app
    base (DeclarativeMeta): SQLAlchemy declarative base
    xl_dict (dict): dictionary of column names and values to update database row
    tab_name (str): key name of tab_contents dictionary with html key/values
  Returns:
      tuple: A tuple containing the id_incidence and sector.
      - id_ (int): id_incidence.
      - sector (str): feedback sector.
  """
  logger.debug(f"dict_to_model() called with {xl_dict=}")

  metadata = xl_dict['metadata']
  sector = metadata['sector']
  tab_data = xl_dict['tab_contents'][tab_name]

  # add the sector type to the tab contents
  tab_data['sector'] = sector

  id_ = dict_to_database(db, base, tab_data)

  return id_, sector


def dict_to_database(db,
                     base,
                     data_dict,
                     table_name='incidences',
                     json_field='misc_json'
                     ):
  """
  Update json field in a table with the contents of a data dict.

  Args:
    db (SQLAlchemy): SQLAlchemy database associated with a flask app
    base (DeclarativeMeta): SQLAlchemy declarative base
    data_dict (dict): data to add to json table column
    table_name (str): table to update
    json_field (str): column with json data field

  Notes:
    - If the dict_ has an id_incidence that is already in the database,
      that row will be updated with dict_ contents.  If dict_ has an id_incidence that is not in the database,
      a new row with that id will be created.  if dict_ does not have id_incidence a new row will be created with
      an auto generated id.
  """
  from arb.utils.wtf_forms_util import update_model_with_payload

  table = get_class_from_table_name(base, table_name)
  session = db.session

  if data_dict:
    # Try to lookup off id_incidence
    if "id_incidence" in data_dict:
      id_ = data_dict["id_incidence"]
      logger.debug(f"Payload detected with id_incidence: {id_}")
      model = db.session.query(table).filter_by(id_incidence=id_).first()
      if model is None:
        logger.debug(f"Creating new record with id_incidence: {id_}")
        model = table(id_incidence=id_)
    else:
      # todo - the json field will not have a id_incidence value so it is out of synch from that model row column
      logger.debug(f"Creating new record with auto generated id_incidence since payload did not have an id_incidence")
      model = table(id_incidence=None)

    update_model_with_payload(model, data_dict, json_field)

    # todo - use the payload routine submit_and_log_model
    session.add(model)
    session.commit()

    # commit will create new id_ if it was not already in the database
    id_ = getattr(model, 'id_incidence')

    # todo (consider) - move id_incidence to its own routine?
    logger.debug(f"updating incidence id in the json field initially matches postgres column value: {id_=}")
    model_json_dict = getattr(model, json_field)
    if model_json_dict is None:
      model_json_dict = {}

    # todo (consider) - the o&g feedback form does not include a id_plume field,
    #  in subsequent source, it can be looked up, but for now, it must be hard coded.
    if model_json_dict['sector'] in ['Oil and Gas', 'Oil & Gas']:
      if 'id_plume' not in model_json_dict or model_json_dict['id_plume'] is None:
        model_json_dict['id_plume'] = 123456

    model_json_dict['id_incidence'] = id_
    setattr(model, json_field, model_json_dict)
    flag_modified(model, json_field)
    session.add(model)
    session.commit()

  else:
    msg = f"Attempt to add empty entry to database"
    logger.warning(msg)
    raise ValueError(msg)

  return id_


def add_file_to_upload_table(db, file_name, status=None, description=None) -> None:
  """
  Add row to uploaded_files table with filename, description, and status.

  Args:
    db (SQLAlchemy): SQLAlchemy database associated with a flask app
    file_name (Path): Path to file once uploaded to the server
    status (str|None): Status code associated with file upload
    description (str|None): Description associated with file upload
  """
  # todo to wrap commit in log?
  from arb.portal.sqla_models import UploadedFile
  logger.debug(f"Adding uploaded file to upload table: {file_name=}")
  model_uploaded_file = UploadedFile(path=str(file_name), status=status, description=description)
  db.session.add(model_uploaded_file)
  db.session.commit()
  logger.debug(f"{model_uploaded_file=}")
