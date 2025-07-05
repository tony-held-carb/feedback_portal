"""
Centralized definition of Flask extension instances used throughout the portal.

This module avoids circular imports by creating extension objects (e.g., `db`, `csrf`)
at the top level, without initializing them until `app.init_app()` is called elsewhere.

Extensions Defined:
  - db (SQLAlchemy): SQLAlchemy instance shared across all models and routes.
  - csrf (CSRFProtect): CSRF protection used for form validation.

Notes:
  - `geoalchemy2.Geometry` must be imported for spatial field introspection,
    even if not directly referenced in code.
  - Use `with app.app_context():` when accessing `db` outside a Flask route.

"""

import logging
from pathlib import Path

from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
# noinspection PyUnresolvedReferences
from geoalchemy2 import Geometry  # <= not used but must be imported for introspection


logger = logging.getLogger(__name__)
_, pp_log = get_pretty_printer()
logger.debug(f'Loading File: "{Path(__file__).name}". Full Path: "{Path(__file__)}"')

db = SQLAlchemy()
"""SQLAlchemy: Flask SQLAlchemy instance for managing ORM and schema."""
# print(f"{type(db)=}")

csrf = CSRFProtect()
"""CSRFProtect: Flask-WTF extension for CSRF form protection."""
