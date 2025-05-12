"""
Flask/Database configuration settings and routines to create
and initialize a flask database connection.
"""

import os

import werkzeug
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from jinja2 import StrictUndefined
from sqlalchemy.ext.automap import automap_base
# noinspection PyUnresolvedReferences
from sqlalchemy.orm import DeclarativeMeta

import arb.__get_logger as get_logger
import arb.utils.diagnostics
import arb.utils.misc
from arb.utils.date_and_time import repr_datetime_to_string
from arb.utils.file_io import get_project_root_dir

logger, pp_log = get_logger.get_logger(__name__, __file__)


class Config:
  """
  Class to hold flask & database configuration data.
  Initializes formatting for the app's logger.

  Notes:
    * When in production, the secret key should be stored as an environment variable.
      During prototyping, it is safe to use a hard coded value (as done below).
    *
  """
  # ----------------------------------------------------
  # Determine File Structure
  # ----------------------------------------------------

  # Get the platform independent project root directory knowing the apps directory structure is:
  # 'feedback_portal/source/production/arb/portal/'
  app_dir_structure = ['feedback_portal', 'source', 'production', 'arb', 'portal']
  PROJECT_ROOT = get_project_root_dir(__file__, app_dir_structure)
  logger.debug(f"PROJECT_ROOT={PROJECT_ROOT}")

  # Path to upload feedback forms and payloads
  # UPLOAD_PATH = PROJECT_ROOT / 'source/production/arb/portal/static/uploads'
  UPLOAD_PATH = PROJECT_ROOT / 'portal_uploads'

  # Ensure UPLOAD_PATH exists
  UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
  logger.debug(f"UPLOAD_PATH={UPLOAD_PATH}")

  # ----------------------------------------------------
  # Database Related
  # ----------------------------------------------------
  POSTGRES_DB_URI = 'postgresql+psycopg2://methane:methaneCH4@prj-bus-methane-aurora-postgresql-instance-1.cdae8kkz3fpi.us-west-2.rds.amazonaws.com/plumetracker'
  SECRET_KEY = (os.environ.get('SECRET_KEY') or 'secret-key-goes-here')
  SQLALCHEMY_DATABASE_URI = (os.environ.get('DATABASE_URI') or POSTGRES_DB_URI)
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  # ----------------------------------------------------
  # Misc
  # ----------------------------------------------------
  EXPLAIN_TEMPLATE_LOADING = False

  @classmethod
  def configure_flask_app(cls,
                          flask_app,
                          secret_key=SECRET_KEY,
                          sqlalchemy_database_uri=SQLALCHEMY_DATABASE_URI,
                          sqlalchemy_track_modifications=SQLALCHEMY_TRACK_MODIFICATIONS,
                          explain_template_loading=EXPLAIN_TEMPLATE_LOADING,
                          upload_folder=UPLOAD_PATH,
                          ):
    """
    Configures the Flask application.

    Args:
      flask_app (Flask): The Flask application instance.
      secret_key (str): The secret key for the application. Defaults to SECRET_KEY.
      sqlalchemy_database_uri (str): The database URI. Defaults to SQLALCHEMY_DATABASE_URI.
      sqlalchemy_track_modifications (bool): Whether to track modifications. Defaults to SQLALCHEMY_TRACK_MODIFICATIONS.
      explain_template_loading (bool): Whether to explain template loading. Defaults to EXPLAIN_TEMPLATE_LOADING.
      upload_folder (str): The upload folder path. Defaults to UPLOAD_PATH.

    Returns:
      None
    """
    from arb.utils.misc import args_to_string
    from arb.utils.diagnostics import diag_recursive
    from arb.utils.date_and_time import date_to_string

    flask_app.config['SECRET_KEY'] = secret_key
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = sqlalchemy_database_uri
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = sqlalchemy_track_modifications
    flask_app.config['EXPLAIN_TEMPLATE_LOADING'] = explain_template_loading

    # Consider - this is hard coded here, may want to make it global variable
    # todo - timezone=UTC added to connection so in theory, all times are utc
    # need to combine this with DateTime(timezone=True) in your SQLAlchemy models to ensure both Python and Postgres are handling timezones correctly.
    flask_app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
      'connect_args': {
        'options': '-c search_path=satellite_tracker_demo1,public -c timezone=UTC'
      }
    }

    # Jinja: Treat all undefined variables as errors
    flask_app.jinja_env.undefined = StrictUndefined

    # Jinja: Trim whitespace before/after {{ }} text injection
    flask_app.jinja_env.trim_blocks = True
    flask_app.jinja_env.lstrip_blocks = True

    # Jinja: custom filters for debugging and string manipulation
    flask_app.jinja_env.filters['debug'] = diag_recursive
    flask_app.jinja_env.filters['date_to_string'] = date_to_string
    # todo - repr_datetime_to_string modified and this may no longer work ...
    flask_app.jinja_env.filters['repr_datetime_to_string'] = repr_datetime_to_string
    flask_app.jinja_env.filters['args_to_string'] = args_to_string

    # Logging: Turn off color coding (avoids special terminal characters in log file)
    werkzeug.serving._log_add_style = False

    # Upload configuration
    flask_app.config['UPLOAD_FOLDER'] = Config.UPLOAD_PATH
    flask_app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16MB


def db_initialize(flask_app, db) -> None:
  """
  Initialize a flask app database connection.

  Args:
    flask_app (Flask): The Flask application instance.
    db (SQLAlchemy): SQLAlchemy database associated with a flask app
  """
  arb.utils.diagnostics.diag_recursive(f"Initializing database")
  db.init_app(flask_app)


def db_create(flask_app, db) -> None:
  """
  Create a database for a flask app.

  Args:
    flask_app (Flask): The Flask application instance.
    db (SQLAlchemy): SQLAlchemy database associated with a flask app

  Notes:
    * Make sure to import all your SQLAlchemy models in this routine.
      Your IDE may indicate that the imported models are not used,
      but they need to be imported for proper SQLAlchemy registration.
  """
  # Warning.  You must import models below (even if they are not used) so registration works properly
  # noinspection PyUnresolvedReferences
  import arb.portal.sqla_models as models

  arb.utils.diagnostics.diag_recursive(f"Creating database")

  # Create database within app context
  with flask_app.app_context():
    db.create_all()


def db_initialize_and_create(flask_app, db) -> None:
  """
  Initialize a flask app database connection and create the database if necessary.

  Args:
    flask_app (Flask): The Flask application instance.
    db (SQLAlchemy): SQLAlchemy database associated with a flask app
  """
  db_initialize(flask_app, db)
  # Uncomment next line if you wish to delete all tables and their data
  # Danger danger danger # db_drop_all(flask_app)
  db_create(flask_app, db)


def reflect_database(flask_app, db):
  """
  Determine structure of an existing database using reflection.

  Args:
    flask_app (Flask): The Flask application instance.
    db (SQLAlchemy): SQLAlchemy database associated with a flask app

  Returns (DeclarativeMeta): base associated with database
  """
  with flask_app.app_context():
    base = automap_base()
    base.prepare(db.engine, reflect=True)
    # print(f"{type(base)=}")

  return base
