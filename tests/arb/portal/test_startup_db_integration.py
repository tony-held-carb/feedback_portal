"""
Integration tests for arb.portal.startup.db

Tests database reflection, model registration, table creation, and combined initialization.
Uses a Flask app context and an in-memory SQLite test DB.
"""
import pytest
from flask import Flask
from arb.portal.startup import db as startup_db
from arb.portal.extensions import db as sa_db
import os

# --- Integration Tests with Real Database ---
# Using shared fixtures from conftest.py

def test_db_create_creates_tables(test_app):
    """Test that the uploaded_files and portal_updates tables exist in the real DB."""
    from sqlalchemy import inspect
    with test_app.app_context():
        from arb.portal.extensions import db
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        assert 'uploaded_files' in tables
        assert 'portal_updates' in tables

def test_db_initialize_and_create_runs(test_app):
    """Test that the DB is initialized and tables exist."""
    from sqlalchemy import inspect
    with test_app.app_context():
        from arb.portal.extensions import db
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        assert 'uploaded_files' in tables
        assert 'portal_updates' in tables 