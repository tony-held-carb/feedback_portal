"""
sqla_models.py stores the SQLAlchemy class/models to allow for python interaction with databases.

Notes:
  * Since SQLite to Postgres migration, the most DB models have been found through introspection rather than
    explicit python class specification.
  * classes defined below that inherit from db.Model will be created in the database.
"""

from sqlalchemy.sql import func

import arb.__get_logger as get_logger
from arb.portal.extensions import db

# from portal.globals import Globals
logger, pp_log = get_logger.get_logger(__name__, __file__)


class UploadedFile(db.Model):
  """
  Database table to store information about uploaded files.
  """
  __tablename__ = "uploaded_files"
  id_ = db.Column(db.Integer, primary_key=True)
  path = db.Column(db.Text, nullable=False)
  description = db.Column(db.Text, nullable=True)
  status = db.Column(db.Text, nullable=True)
  created_timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
  modified_timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

  def __repr__(self):
    return f'<Uploaded File: {self.id_}, Path: {self.path}, Description: {self.description}, Status: {self.status}>'
