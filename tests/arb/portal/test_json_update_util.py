import pytest
import arb.portal.json_update_util as json_update_util
from unittest.mock import MagicMock, patch

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