"""
Flask/Database configuration settings and routines to create
and initialize a Flask database connection.

Refactored to:
  - Use modern Python syntax
  - Use Google-style docstrings
  - Add clarity and documentation for team maintainability

This module supports:
  - App configuration with custom Jinja filters
  - PostgreSQL connection setup
  - SQLAlchemy reflection and model registration
  - Development vs production-safe secrets
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
from arb.utils.date_and_time import date_to_string, repr_datetime_to_string
from arb.utils.diagnostics import diag_recursive
from arb.utils.file_io import get_project_root_dir
from arb.utils.misc import args_to_string

logger, pp_log = get_logger.get_logger(__name__, __file__)


class Config:
  """
  Flask and SQLAlchemy configuration class.

  This class determines the directory structure of the project, establishes paths
  for file uploads, and sets up database URIs and Jinja environment behavior.

  Notes:
      - Secrets like the Flask secret key should be defined via environment variables in production.
      - Upload path is hardcoded but designed to be safely adjusted via class attributes or parameters.
  """


  # ----------------------------------------------------
  # Database and Flask Config
  # ----------------------------------------------------
  POSTGRES_DB_URI = (
    'postgresql+psycopg2://methane:methaneCH4@prj-bus-methane-aurora-postgresql-instance-1'
    '.cdae8kkz3fpi.us-west-2.rds.amazonaws.com/plumetracker'
  )

  SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key-goes-here'
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or POSTGRES_DB_URI
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  # When enabled, Flask will log detailed information about templating files
  # consider setting to True if you're getting TemplateNotFound errors.
  EXPLAIN_TEMPLATE_LOADING = False  # Recommended setting for most use cases.

  @classmethod
  def configure_flask_app(cls,
                          flask_app: Flask,
                          secret_key=SECRET_KEY,
                          sqlalchemy_database_uri=SQLALCHEMY_DATABASE_URI,
                          sqlalchemy_track_modifications=SQLALCHEMY_TRACK_MODIFICATIONS,
                          explain_template_loading=EXPLAIN_TEMPLATE_LOADING,
                          upload_folder=UPLOAD_PATH) -> None:
    """
    Configure a Flask app instance with database, security, Jinja, and logging settings.

    Args:
        flask_app (Flask): The Flask app instance to configure.
        secret_key (str): Application secret key.
        sqlalchemy_database_uri (str): Database URI.
        sqlalchemy_track_modifications (bool): Enable SQLAlchemy modification tracking.
        explain_template_loading (bool): Enable Jinja template load diagnostics.
        upload_folder (Path): Folder to store uploaded files.

    Returns:
        None

    Example:
        >>> app = Flask(__name__)
        >>> Config.configure_flask_app(app)
    """
    flask_app.config['SECRET_KEY'] = secret_key
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = sqlalchemy_database_uri
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = sqlalchemy_track_modifications
    flask_app.config['EXPLAIN_TEMPLATE_LOADING'] = explain_template_loading

    flask_app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
      'connect_args': {
        'options': '-c search_path=satellite_tracker_demo1,public -c timezone=UTC'
      }
    }

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
    flask_app.config['UPLOAD_FOLDER'] = upload_folder
    flask_app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload


def db_initialize(flask_app: Flask, db: SQLAlchemy) -> None:
  """
  Initialize the Flask app's SQLAlchemy extension.

  Args:
      flask_app (Flask): The application instance.
      db (SQLAlchemy): SQLAlchemy object to initialize.

  Returns:
      None
  """
  diag_recursive("Initializing database")
  db.init_app(flask_app)


def db_create(flask_app: Flask, db: SQLAlchemy) -> None:
  """
  Create database tables for the Flask app using SQLAlchemy models.

  Args:
      flask_app (Flask): The application instance.
      db (SQLAlchemy): SQLAlchemy object used to manage the database.

  Notes:
      - You must import your model modules so that SQLAlchemy registers them.
      - This is only safe to run if you trust the models and database.
  """
  # Warning.  You must import models below (even if they are not used) so registration works properly
  # noinspection PyUnresolvedReferences
  import arb.portal.sqla_models as models

  diag_recursive("Creating database")

  with flask_app.app_context():
    db.create_all()


def db_initialize_and_create(flask_app: Flask, db: SQLAlchemy) -> None:
  """
  Initialize SQLAlchemy and optionally create tables for the Flask app.

  Args:
      flask_app (Flask): The Flask application instance.
      db (SQLAlchemy): SQLAlchemy object to initialize and use.

  Returns:
      None

  Warning:
      Uncomment `db_drop_all()` to wipe all tables, but use with extreme caution.
  """
  db_initialize(flask_app, db)
  # Uncomment next line if you wish to delete all tables and their data
  # Danger danger danger # db_drop_all(flask_app)
  db_create(flask_app, db)


def reflect_database(flask_app: Flask, db: SQLAlchemy) -> DeclarativeMeta:
  """
  Reflect the structure of an existing database into a SQLAlchemy base.

  Args:
      flask_app (Flask): The application instance.
      db (SQLAlchemy): SQLAlchemy object with a bound engine.

  Returns:
      DeclarativeMeta: Reflected database schema wrapped in an automapped base.

  Example:
      >>> base = reflect_database(app, db)
      >>> print(base.classes.keys())
  """
  with flask_app.app_context():
    base = automap_base()
    base.prepare(db.engine, reflect=True)
    # print(f"{type(base)=}")

  return base
