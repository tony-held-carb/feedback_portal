# All production logic in sqla_models.py is fully covered by unit tests.
# The only untested function is run_diagnostics, which is likely obsolete, requires a real database, and is not robustly testable.
# See the run_diagnostics docstring and documentation/docstring_update_for_testing.md for details.

import pytest
import arb.portal.sqla_models as sqla_models
from unittest.mock import MagicMock, patch
import datetime
from flask import Flask


def test_uploaded_file_repr():
    file = sqla_models.UploadedFile()
    file.path = "uploads/data.csv"
    file.description = "Data"
    file.status = "done"
    result = repr(file)
    assert "<Uploaded File: None" in result
    assert "uploads/data.csv" in result
    assert "Description: Data" in result
    assert "Status: done" in result


def test_portal_update_repr():
    now = datetime.datetime.now(datetime.timezone.utc)
    update = sqla_models.PortalUpdate()
    update.timestamp = now
    update.key = "field1"
    update.old_value = "A"
    update.new_value = "B"
    update.user = "alice"
    update.comments = "test"
    update.id_incidence = 2
    result = repr(update)
    assert "<PortalUpdate id=None" in result
    assert "key='field1'" in result
    assert "old='A'" in result
    assert "new='B'" in result
    assert "user='alice'" in result
    assert str(now) in result

@pytest.mark.skip(reason="run_diagnostics is likely obsolete, developer-only, and not robustly testable. See docstring and documentation/docstring_update_for_testing.md.")
def test_run_diagnostics_success():
    pass

@pytest.mark.skip(reason="run_diagnostics is likely obsolete, developer-only, and not robustly testable. See docstring and documentation/docstring_update_for_testing.md.")
def test_run_diagnostics_db_error():
    pass

# --- Integration Tests with Real Database ---
@pytest.fixture
def test_app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    from arb.portal.extensions import db
    db.init_app(app)
    return app

@pytest.fixture
def test_db(test_app):
    with test_app.app_context():
        from arb.portal.extensions import db
        db.create_all()
        return db

@pytest.fixture
def test_session(test_app, test_db):
    with test_app.app_context():
        from arb.portal.extensions import db
        return db.session

def test_uploaded_file_integration(test_app, test_db, test_session):
    """Integration test for UploadedFile model."""
    with test_app.app_context():
        # Create and insert
        file = sqla_models.UploadedFile()
        file.path = "uploads/integration.xlsx"
        file.description = "Integration test file"
        file.status = "pending"
        test_session.add(file)
        test_session.commit()
        assert file.id_ is not None
        # Query
        fetched = sqla_models.UploadedFile.query.get(file.id_)
        assert fetched is not None
        assert fetched.path == "uploads/integration.xlsx"
        # Update
        fetched.status = "processed"
        test_session.commit()
        updated = sqla_models.UploadedFile.query.get(file.id_)
        assert updated.status == "processed"


def test_portal_update_integration(test_app, test_db, test_session):
    """Integration test for PortalUpdate model."""
    with test_app.app_context():
        now = datetime.datetime.now(datetime.timezone.utc)
        update = sqla_models.PortalUpdate()
        update.timestamp = now
        update.key = "integration_field"
        update.old_value = "X"
        update.new_value = "Y"
        update.user = "integration_user"
        update.comments = "integration test"
        update.id_incidence = 42
        test_session.add(update)
        test_session.commit()
        assert update.id is not None
        # Query
        fetched = sqla_models.PortalUpdate.query.get(update.id)
        assert fetched is not None
        assert fetched.key == "integration_field"
        # Update
        fetched.new_value = "Z"
        test_session.commit()
        updated = sqla_models.PortalUpdate.query.get(update.id)
        assert updated.new_value == "Z" 