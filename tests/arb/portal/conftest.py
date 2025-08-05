"""
Test configuration and utilities for portal tests.
Provides database setup, isolation, and cleanup utilities.
"""

import os

import pytest
from flask import Flask


# Only import db and models for type hints and session, not for schema creation

def create_test_app():
  """Create a test Flask app with PostgreSQL database."""
  app = Flask(__name__)
  app.config['TESTING'] = True

  # Use DATABASE_URI if set, otherwise fall back to settings configuration
  database_uri = os.environ.get('DATABASE_URI')
  if database_uri:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
  else:
    # Import and use the database configuration from settings
    try:
      from arb.portal.config.settings import BaseConfig
      app.config['SQLALCHEMY_DATABASE_URI'] = BaseConfig.SQLALCHEMY_DATABASE_URI
      app.config['SQLALCHEMY_ENGINE_OPTIONS'] = BaseConfig.SQLALCHEMY_ENGINE_OPTIONS
    except ImportError:
      # Fallback to SQLite if settings import fails
      app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  from arb.portal.extensions import db
  db.init_app(app)
  return app


@pytest.fixture
def test_app():
  """Create a test Flask app with PostgreSQL database."""
  return create_test_app()


@pytest.fixture
def test_db(test_app):
  """Get the database instance from the test app."""
  with test_app.app_context():
    from arb.portal.extensions import db
    return db


@pytest.fixture
def test_session(test_app, test_db):
  """Create a test session with proper isolation. Does NOT create or alter tables."""
  with test_app.app_context():
    from arb.portal.extensions import db
    transaction = db.session.begin_nested()
    yield db.session
    transaction.rollback()
    db.session.close()
