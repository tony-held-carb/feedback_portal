"""
Extensions.py has the centralized instance of SQLAlchemy database variable named
'db' that is common to the flask app and related routines.

Notes:
  * db will be initialized and associated with the flask app in different modules.
  * db is placed here to avoid circular references.
  * To use the db outside a flask route function, use a context of the form:
    with app.app_context():
      # Your code goes here.
      db.create_all()  # for example
  * the type hint for db is:
      db (SQLAlchemy): SQLAlchemy database associated with a flask app
"""
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

# noinspection PyUnresolvedReferences
from geoalchemy2 import Geometry  # <= not used but must be imported for introspection

import arb.__get_logger as get_logger

logger, pp_log = get_logger.get_logger(__name__, __file__)

db = SQLAlchemy()
# print(f"{type(db)=}")

csrf = CSRFProtect()