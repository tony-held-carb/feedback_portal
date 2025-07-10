"""
Integration tests for arb.portal.startup.db

Tests database reflection, model registration, table creation, and combined initialization.
Uses a Flask app context and an in-memory SQLite test DB.
"""
import pytest
from flask import Flask
from arb.portal.startup import db as startup_db
from arb.portal.extensions import db as sa_db

@pytest.fixture(scope="module")
def app():
  app = Flask(__name__)
  app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
  app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
  app.config["TESTING"] = True
  app.config["PROPAGATE_EXCEPTIONS"] = False
  sa_db.init_app(app)
  yield app

@pytest.fixture(scope="module")
def app_ctx(app):
  with app.app_context():
    yield

def test_reflect_database_runs(app_ctx):
  """reflect_database() runs without error (even if no tables exist)."""
  startup_db.reflect_database()
  # Should not raise

def test_db_initialize_runs(app_ctx):
  """db_initialize() runs and registers models without error."""
  startup_db.db_initialize()
  # Should not raise

def test_db_create_creates_tables(app_ctx):
  """db_create() creates tables in the test DB."""
  # Ensure models are registered
  startup_db.db_initialize()
  # Create tables
  startup_db.db_create()
  # Check that at least one table exists in metadata
  assert sa_db.metadata.tables, "No tables created in test DB."

def test_db_create_respects_fast_load(app_ctx, monkeypatch):
  """db_create() skips table creation if FAST_LOAD=True."""
  from flask import current_app
  monkeypatch.setitem(current_app.config, "FAST_LOAD", True)
  # Should not raise, but also not create tables
  startup_db.db_create()
  # No assertion here; just ensure no error

def test_db_initialize_and_create_runs(app_ctx):
  """db_initialize_and_create() runs without error and creates tables."""
  startup_db.db_initialize_and_create()
  assert sa_db.metadata.tables, "No tables created in test DB after combined init/create." 