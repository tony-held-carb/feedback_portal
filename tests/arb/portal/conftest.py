"""
Test configuration and utilities for portal tests.
Provides database setup, isolation, and cleanup utilities.
"""

import pytest
from flask import Flask
import os

# Only import db and models for type hints and session, not for schema creation

def create_test_app():
    """Create a test Flask app with PostgreSQL database."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
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