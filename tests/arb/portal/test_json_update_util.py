import pytest
import arb.portal.json_update_util as json_update_util
from unittest.mock import MagicMock, patch
from flask import Flask
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

@pytest.fixture
def mock_model():
    model = MagicMock()
    model.id_incidence = 123
    model.misc_json = {"foo": "bar", "id_incidence": 123}
    return model

@pytest.fixture
def mock_db(monkeypatch):
    db = MagicMock()
    monkeypatch.setattr(json_update_util, "db", db)
    return db

@pytest.fixture
def mock_portal_update(monkeypatch):
    patcher = patch("arb.portal.json_update_util.PortalUpdate")
    yield patcher.start()
    patcher.stop()

@pytest.fixture
def mock_flag_modified(monkeypatch):
    patcher = patch("arb.portal.json_update_util.flag_modified")
    yield patcher.start()
    patcher.stop()

@pytest.fixture
def mock_object_session(monkeypatch):
    patcher = patch("arb.portal.json_update_util.object_session", return_value=MagicMock())
    yield patcher.start()
    patcher.stop()

def test_apply_json_patch_and_log_basic(mock_model, mock_db, mock_portal_update, mock_flag_modified, mock_object_session):
    updates = {"foo": "baz", "bar": 1}
    mock_model.misc_json = {"foo": "bar", "id_incidence": 123}
    mock_model.id_incidence = 123
    session = MagicMock()
    mock_object_session.return_value = session
    session.__contains__.return_value = True
    mock_db.session = session
    json_update_util.db = mock_db
    json_update_util.PortalUpdate = mock_portal_update
    json_update_util.flag_modified = mock_flag_modified
    json_update_util.object_session = mock_object_session
    
    # Should not raise
    json_update_util.apply_json_patch_and_log(mock_model, updates)
    assert mock_db.session.commit.called
    assert mock_flag_modified.called
    assert mock_portal_update.called

def test_apply_json_patch_and_log_no_changes(mock_model, mock_db, mock_portal_update, mock_flag_modified, mock_object_session):
    updates = {"foo": "bar"}  # No change
    mock_model.misc_json = {"foo": "bar", "id_incidence": 123}
    mock_model.id_incidence = 123
    session = MagicMock()
    mock_object_session.return_value = session
    session.__contains__.return_value = True
    mock_db.session = session
    json_update_util.db = mock_db
    json_update_util.PortalUpdate = mock_portal_update
    json_update_util.flag_modified = mock_flag_modified
    json_update_util.object_session = mock_object_session
    
    json_update_util.apply_json_patch_and_log(mock_model, updates)
    # Should not add a PortalUpdate for unchanged field
    assert mock_portal_update.call_count == 0
    assert mock_db.session.commit.called

def test_apply_json_patch_and_log_handles_id_incidence_conflict(mock_model, mock_db, mock_portal_update, mock_flag_modified, mock_object_session):
    updates = {"id_incidence": 999, "foo": "baz"}
    mock_model.misc_json = {"foo": "bar", "id_incidence": 123}
    mock_model.id_incidence = 123
    session = MagicMock()
    mock_object_session.return_value = session
    session.__contains__.return_value = True
    mock_db.session = session
    json_update_util.db = mock_db
    json_update_util.PortalUpdate = mock_portal_update
    json_update_util.flag_modified = mock_flag_modified
    json_update_util.object_session = mock_object_session
    
    json_update_util.apply_json_patch_and_log(mock_model, updates)
    # id_incidence should be removed from updates, so only 'foo' is updated
    assert mock_portal_update.call_count >= 1
    assert mock_db.session.commit.called

# --- Integration Tests with Real Database ---
@pytest.fixture
def test_app():
    """Create a test Flask app with SQLite in-memory database."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    from arb.portal.extensions import db
    db.init_app(app)
    
    return app

@pytest.fixture
def test_db(test_app):
    """Get the database instance from the test app."""
    with test_app.app_context():
        from arb.portal.extensions import db
        return db

@pytest.fixture
def test_model_class():
    """Create a test model class with JSON field."""
    Base = declarative_base()
    
    class TestModel(Base):
        __tablename__ = 'test_models'
        
        id_incidence = Column(Integer, primary_key=True)
        misc_json = Column(JSON)
        name = Column(String)
    
    return TestModel

@pytest.fixture
def test_session(test_app, test_db, test_model_class):
    """Create a test session with tables created."""
    with test_app.app_context():
        from arb.portal.extensions import db
        test_model_class.__table__.create(db.engine)
        
        # Create PortalUpdate table
        from arb.portal.sqla_models import PortalUpdate
        db.create_all()  # This will create all tables including PortalUpdate
        
        return db.session

def test_apply_json_patch_and_log_integration_basic(test_app, test_db, test_model_class, test_session):
    """Integration test for basic JSON patch and log functionality."""
    with test_app.app_context():
        # Create a test model instance
        model = test_model_class(id_incidence=123, misc_json={"foo": "bar"}, name="test")
        test_session.add(model)
        test_session.commit()
        
        # Apply updates
        updates = {"foo": "baz", "new_field": "value"}
        json_update_util.apply_json_patch_and_log(model, updates, user="test_user")
        
        # Verify model was updated
        test_session.refresh(model)
        assert model.misc_json["foo"] == "baz"
        assert model.misc_json["new_field"] == "value"
        
        # Verify PortalUpdate entries were created
        from arb.portal.sqla_models import PortalUpdate
        updates = test_session.query(PortalUpdate).filter_by(id_incidence=123).all()
        assert len(updates) == 2  # Two changes logged
        
        # Verify specific update entries
        foo_update = next(u for u in updates if u.key == "foo")
        assert foo_update.old_value == "bar"
        assert foo_update.new_value == "baz"
        assert foo_update.user == "test_user"

def test_apply_json_patch_and_log_integration_no_changes(test_app, test_db, test_model_class, test_session):
    """Integration test for no-change scenarios."""
    with test_app.app_context():
        # Create a test model instance
        model = test_model_class(id_incidence=124, misc_json={"foo": "bar"}, name="test")
        test_session.add(model)
        test_session.commit()
        
        # Apply updates that don't change anything
        updates = {"foo": "bar"}  # Same value
        json_update_util.apply_json_patch_and_log(model, updates, user="test_user")
        
        # Verify no PortalUpdate entries were created
        from arb.portal.sqla_models import PortalUpdate
        updates = test_session.query(PortalUpdate).filter_by(id_incidence=124).all()
        assert len(updates) == 0

def test_apply_json_patch_and_log_integration_filter_placeholders(test_app, test_db, test_model_class, test_session):
    """Integration test for filtering out placeholder values."""
    with test_app.app_context():
        # Create a test model instance
        model = test_model_class(id_incidence=125, misc_json={"foo": "bar"}, name="test")
        test_session.add(model)
        test_session.commit()
        
        # Apply updates with placeholder values
        updates = {
            "foo": "bar",  # No change
            "new_field": None,  # Should be filtered
            "empty_field": "",  # Should be filtered
            "please_select": "Please Select",  # Should be filtered
            "valid_change": "new_value"  # Should be logged
        }
        json_update_util.apply_json_patch_and_log(model, updates, user="test_user")
        
        # Verify only valid changes were logged
        from arb.portal.sqla_models import PortalUpdate
        updates = test_session.query(PortalUpdate).filter_by(id_incidence=125).all()
        assert len(updates) == 1  # Only valid_change should be logged
        
        # Verify the logged change
        valid_update = updates[0]
        assert valid_update.key == "valid_change"
        assert valid_update.old_value == "None"  # None becomes "None" when converted to string
        assert valid_update.new_value == "new_value"

def test_apply_json_patch_and_log_integration_id_incidence_conflict(test_app, test_db, test_model_class, test_session):
    """Integration test for ID incidence conflict handling."""
    with test_app.app_context():
        # Create a test model instance
        model = test_model_class(id_incidence=126, misc_json={"foo": "bar", "id_incidence": 126}, name="test")
        test_session.add(model)
        test_session.commit()
        
        # Apply updates with conflicting id_incidence
        updates = {
            "id_incidence": 999,  # Should be removed from updates
            "foo": "baz"  # Should be applied
        }
        json_update_util.apply_json_patch_and_log(model, updates, user="test_user")
        
        # Verify model was updated correctly
        test_session.refresh(model)
        assert model.misc_json["foo"] == "baz"
        assert model.misc_json["id_incidence"] == 126  # Should remain unchanged
        
        # Verify only the foo change was logged
        from arb.portal.sqla_models import PortalUpdate
        updates = test_session.query(PortalUpdate).filter_by(id_incidence=126).all()
        assert len(updates) == 1
        assert updates[0].key == "foo"

def test_apply_json_patch_and_log_integration_new_model(test_app, test_db, test_model_class, test_session):
    """Integration test for new model with None misc_json."""
    with test_app.app_context():
        # Create a test model instance with None misc_json
        model = test_model_class(id_incidence=127, misc_json=None, name="test")
        test_session.add(model)
        test_session.commit()
        
        # Apply updates to new model
        updates = {"foo": "bar", "baz": "qux"}
        json_update_util.apply_json_patch_and_log(model, updates, user="test_user")
        
        # Verify model was updated
        test_session.refresh(model)
        assert model.misc_json["foo"] == "bar"
        assert model.misc_json["baz"] == "qux"
        
        # Verify both changes were logged
        from arb.portal.sqla_models import PortalUpdate
        updates = test_session.query(PortalUpdate).filter_by(id_incidence=127).all()
        assert len(updates) == 2 