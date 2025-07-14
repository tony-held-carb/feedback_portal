"""
Comprehensive tests for arb.portal.utils.db_introspection_util

Tests all database introspection logic including row retrieval, creation, session management,
and error handling. Covers edge cases and integration scenarios with proper mocking.
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from arb.portal.utils import db_introspection_util
from arb.portal.utils.db_introspection_util import get_ensured_row

@pytest.fixture
def mock_db():
    """Create a mock SQLAlchemy database instance."""
    mock_db = MagicMock()
    mock_db.session = MagicMock(spec=Session)
    return mock_db

@pytest.fixture
def mock_base():
    """Create a mock AutomapBase instance."""
    return MagicMock()

@pytest.fixture
def mock_table_class():
    """Create a mock table class."""
    mock_class = MagicMock()
    mock_class.__name__ = "MockTable"
    return mock_class

def test_get_ensured_row_function_signature():
    """get_ensured_row function has correct signature."""
    assert hasattr(db_introspection_util, 'get_ensured_row')
    assert callable(db_introspection_util.get_ensured_row)

def test_get_ensured_row_retrieves_existing_row(mock_db, mock_base, mock_table_class):
    """get_ensured_row retrieves existing row when id_ is provided and row exists."""
    existing_model = MagicMock()
    existing_model.id_incidence = 123
    
    with patch('arb.portal.utils.db_introspection_util.get_class_from_table_name') as mock_get_class:
        with patch('arb.portal.utils.db_introspection_util.logger') as mock_logger:
            mock_get_class.return_value = mock_table_class
            mock_db.session.get.return_value = existing_model
            
            model, id_, is_new = get_ensured_row(mock_db, mock_base, "incidences", "id_incidence", 123)
            
            assert model == existing_model
            assert id_ == 123
            assert is_new is False
            mock_db.session.get.assert_called_once_with(mock_table_class, 123)

def test_get_ensured_row_creates_new_row_when_id_provided_but_not_found(mock_db, mock_base, mock_table_class):
    """get_ensured_row creates new row when id_ is provided but row doesn't exist."""
    new_model = MagicMock()
    new_model.id_incidence = 456
    
    with patch('arb.portal.utils.db_introspection_util.get_class_from_table_name') as mock_get_class:
        with patch('arb.portal.utils.db_introspection_util.logger') as mock_logger:
            mock_get_class.return_value = mock_table_class
            mock_db.session.get.return_value = None
            mock_table_class.return_value = new_model
            
            model, id_, is_new = get_ensured_row(mock_db, mock_base, "incidences", "id_incidence", 456)
            
            assert model == new_model
            assert id_ == 456
            assert is_new is True
            mock_table_class.assert_called_once_with(id_incidence=456)

def test_get_ensured_row_creates_new_row_with_auto_generated_id(mock_db, mock_base, mock_table_class):
    """get_ensured_row creates new row with auto-generated id when id_ is None."""
    new_model = MagicMock()
    new_model.id_incidence = 789
    
    with patch('arb.portal.utils.db_introspection_util.get_class_from_table_name') as mock_get_class:
        with patch('arb.portal.utils.db_introspection_util.logger') as mock_logger:
            mock_get_class.return_value = mock_table_class
            mock_table_class.return_value = new_model
            
            model, id_, is_new = get_ensured_row(mock_db, mock_base, "incidences", "id_incidence", None)
            
            assert model == new_model
            assert id_ == 789
            assert is_new is True
            mock_table_class.assert_called_once_with(id_incidence=None)
            mock_db.session.add.assert_called_once_with(new_model)
            mock_db.session.commit.assert_called_once()

def test_get_ensured_row_adds_to_session_when_requested(mock_db, mock_base, mock_table_class):
    """get_ensured_row adds new model to session when add_to_session=True."""
    new_model = MagicMock()
    new_model.id_incidence = 456
    
    with patch('arb.portal.utils.db_introspection_util.get_class_from_table_name') as mock_get_class:
        with patch('arb.portal.utils.db_introspection_util.logger') as mock_logger:
            mock_get_class.return_value = mock_table_class
            mock_db.session.get.return_value = None
            mock_table_class.return_value = new_model
            
            model, id_, is_new = get_ensured_row(mock_db, mock_base, "incidences", "id_incidence", 456, add_to_session=True)
            
            assert is_new is True
            mock_db.session.add.assert_called_once_with(new_model)

def test_get_ensured_row_does_not_add_to_session_by_default(mock_db, mock_base, mock_table_class):
    """get_ensured_row does not add new model to session by default."""
    new_model = MagicMock()
    new_model.id_incidence = 456
    
    with patch('arb.portal.utils.db_introspection_util.get_class_from_table_name') as mock_get_class:
        with patch('arb.portal.utils.db_introspection_util.logger') as mock_logger:
            mock_get_class.return_value = mock_table_class
            mock_db.session.get.return_value = None
            mock_table_class.return_value = new_model
            
            model, id_, is_new = get_ensured_row(mock_db, mock_base, "incidences", "id_incidence", 456, add_to_session=False)
            
            assert is_new is True
            mock_db.session.add.assert_not_called()

def test_get_ensured_row_handles_commit_failure(mock_db, mock_base, mock_table_class):
    """get_ensured_row handles commit failure when creating new row with auto-generated id."""
    new_model = MagicMock()
    new_model.id_incidence = 789
    
    with patch('arb.portal.utils.db_introspection_util.get_class_from_table_name') as mock_get_class:
        with patch('arb.portal.utils.db_introspection_util.logger') as mock_logger:
            mock_get_class.return_value = mock_table_class
            mock_table_class.return_value = new_model
            mock_db.session.commit.side_effect = SQLAlchemyError("Database error")
            
            with pytest.raises(SQLAlchemyError, match="Database error"):
                get_ensured_row(mock_db, mock_base, "incidences", "id_incidence", None)

def test_get_ensured_row_raises_error_for_invalid_table(mock_db, mock_base):
    """get_ensured_row raises ValueError for invalid table name."""
    with patch('arb.portal.utils.db_introspection_util.get_class_from_table_name') as mock_get_class:
        mock_get_class.return_value = None
        
        with pytest.raises(ValueError, match="Table 'invalid_table' not found"):
            get_ensured_row(mock_db, mock_base, "invalid_table", "id_incidence", 123)

def test_get_ensured_row_uses_custom_primary_key(mock_db, mock_base, mock_table_class):
    """get_ensured_row works with custom primary key names."""
    existing_model = MagicMock()
    existing_model.custom_id = 999
    
    with patch('arb.portal.utils.db_introspection_util.get_class_from_table_name') as mock_get_class:
        with patch('arb.portal.utils.db_introspection_util.logger') as mock_logger:
            mock_get_class.return_value = mock_table_class
            mock_db.session.get.return_value = existing_model
            
            model, id_, is_new = get_ensured_row(mock_db, mock_base, "custom_table", "custom_id", 999)
            
            assert model == existing_model
            assert id_ == 999
            assert is_new is False
            mock_db.session.get.assert_called_once_with(mock_table_class, 999)

def test_get_ensured_row_creates_new_row_with_custom_primary_key(mock_db, mock_base, mock_table_class):
    """get_ensured_row creates new row with custom primary key."""
    new_model = MagicMock()
    new_model.custom_id = 888
    
    with patch('arb.portal.utils.db_introspection_util.get_class_from_table_name') as mock_get_class:
        with patch('arb.portal.utils.db_introspection_util.logger') as mock_logger:
            mock_get_class.return_value = mock_table_class
            mock_db.session.get.return_value = None
            mock_table_class.return_value = new_model
            
            model, id_, is_new = get_ensured_row(mock_db, mock_base, "custom_table", "custom_id", 888)
            
            assert model == new_model
            assert id_ == 888
            assert is_new is True
            mock_table_class.assert_called_once_with(custom_id=888)

def test_get_ensured_row_logs_detailed_diagnostics(mock_db, mock_base, mock_table_class):
    """get_ensured_row logs detailed diagnostics for debugging."""
    existing_model = MagicMock()
    existing_model.id_incidence = 123
    
    with patch('arb.portal.utils.db_introspection_util.get_class_from_table_name') as mock_get_class:
        with patch('arb.portal.utils.db_introspection_util.logger') as mock_logger:
            mock_get_class.return_value = mock_table_class
            mock_db.session.get.return_value = existing_model
            
            get_ensured_row(mock_db, mock_base, "incidences", "id_incidence", 123)
            
            # Check that logging was called multiple times for diagnostics
            assert mock_logger.info.call_count >= 3

def test_get_ensured_row_handles_attribute_error_gracefully(mock_db, mock_base, mock_table_class):
    """get_ensured_row handles AttributeError when accessing primary key."""
    existing_model = MagicMock()
    # Simulate missing primary key attribute
    existing_model.id_incidence = None
    delattr(existing_model, 'id_incidence')
    
    with patch('arb.portal.utils.db_introspection_util.get_class_from_table_name') as mock_get_class:
        with patch('arb.portal.utils.db_introspection_util.logger') as mock_logger:
            mock_get_class.return_value = mock_table_class
            mock_db.session.get.return_value = existing_model
            
            model, id_, is_new = get_ensured_row(mock_db, mock_base, "incidences", "id_incidence", 123)
            
            assert model == existing_model
            assert id_ == 123
            assert is_new is False

def test_get_ensured_row_session_state_tracking(mock_db, mock_base, mock_table_class):
    """get_ensured_row properly tracks session state."""
    new_model = MagicMock()
    new_model.id_incidence = 456
    
    with patch('arb.portal.utils.db_introspection_util.get_class_from_table_name') as mock_get_class:
        with patch('arb.portal.utils.db_introspection_util.logger') as mock_logger:
            with patch('sqlalchemy.orm.object_session') as mock_object_session:
                mock_get_class.return_value = mock_table_class
                mock_db.session.get.return_value = None
                mock_table_class.return_value = new_model
                mock_object_session.return_value = mock_db.session
                
                get_ensured_row(mock_db, mock_base, "incidences", "id_incidence", 456)
                
                # Check that session state was logged
                mock_object_session.assert_called_once_with(new_model)

def test_get_ensured_row_default_parameters(mock_db, mock_base, mock_table_class):
    """get_ensured_row works with default parameters."""
    new_model = MagicMock()
    new_model.id_incidence = 789
    
    with patch('arb.portal.utils.db_introspection_util.get_class_from_table_name') as mock_get_class:
        with patch('arb.portal.utils.db_introspection_util.logger') as mock_logger:
            mock_get_class.return_value = mock_table_class
            mock_table_class.return_value = new_model
            
            model, id_, is_new = get_ensured_row(mock_db, mock_base)
            
            assert model == new_model
            assert id_ == 789
            assert is_new is True
            # Check default parameters were used
            mock_get_class.assert_called_once_with(mock_base, "incidences")
            mock_table_class.assert_called_once_with(id_incidence=None)

def test_get_ensured_row_returns_correct_tuple_structure(mock_db, mock_base, mock_table_class):
    """get_ensured_row returns correct tuple structure (model, id_, is_new_row)."""
    existing_model = MagicMock()
    existing_model.id_incidence = 123
    
    with patch('arb.portal.utils.db_introspection_util.get_class_from_table_name') as mock_get_class:
        with patch('arb.portal.utils.db_introspection_util.logger') as mock_logger:
            mock_get_class.return_value = mock_table_class
            mock_db.session.get.return_value = existing_model
            
            result = get_ensured_row(mock_db, mock_base, "incidences", "id_incidence", 123)
            
            assert isinstance(result, tuple)
            assert len(result) == 3
            model, id_, is_new = result
            assert model == existing_model
            assert id_ == 123
            assert isinstance(is_new, bool) 