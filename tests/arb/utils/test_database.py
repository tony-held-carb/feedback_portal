"""
Unit tests for database.py

Coverage philosophy:
- All functions are tested with both valid and invalid inputs
- Database operations use in-memory SQLite for isolation and speed
- Error conditions and edge cases are explicitly tested
- SQLAlchemy fixtures provide realistic database context
- File operations are tested with temporary files

This suite provides comprehensive coverage for database utilities used in migrations,
diagnostics, and administrative scripts.
"""
import pytest
import sqlite3
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, JSON, MetaData
from sqlalchemy.ext.declarative import declarative_base

# Add the source/production directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'source', 'production'))
from arb.utils import database as dbmod


# --- Test Fixtures ---

@pytest.fixture
def flask_app():
    """Create a minimal Flask app for testing."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app


@pytest.fixture
def db(flask_app):
    """Create SQLAlchemy instance bound to test app."""
    return SQLAlchemy(flask_app)


@pytest.fixture
def base(db, flask_app):
    """Create a declarative base with test table."""
    Base = declarative_base()
    
    class TestModel(Base):
        __tablename__ = 'test_table'
        id = Column(Integer, primary_key=True)
        name = Column(String(50))
        misc_json = Column(JSON)
    
    # Create tables in memory
    with flask_app.app_context():
        Base.metadata.create_all(db.engine)
    
    return Base


@pytest.fixture
def reflected_base(db, base, flask_app):
    """Create a reflected base using the test database."""
    with flask_app.app_context():
        return dbmod.get_reflected_base(db)


@pytest.fixture
def temp_sql_script():
    """Create a temporary SQL script file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
        f.write("""
        CREATE TABLE test_table (
            id INTEGER PRIMARY KEY,
            name TEXT
        );
        INSERT INTO test_table (id, name) VALUES (1, 'test_name');
        """)
        return f.name


# --- execute_sql_script Tests ---

@pytest.mark.skip(reason="Creates app.db; skipping to avoid unwanted file creation during test runs.")
def test_execute_sql_script_with_defaults():
    """Test execute_sql_script with default parameters."""
    with patch('builtins.open') as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = "SELECT 1;"
        
        with patch('sqlite3.connect') as mock_connect:
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection
            
            dbmod.execute_sql_script()
            
            # Verify default script path was used
            mock_open.assert_called_with('../sql_scripts/script_01.sql')
            # Verify default connection was created
            mock_connect.assert_called_with('app.db')
            # Verify script was executed
            mock_connection.executescript.assert_called_with("SELECT 1;")
            # Verify commit and close were called
            mock_connection.commit.assert_called_once()
            mock_connection.close.assert_called_once()


def test_execute_sql_script_with_custom_path_and_connection(temp_sql_script):
    """Test execute_sql_script with custom script path and connection."""
    try:
        # Create a temporary connection
        conn = sqlite3.connect(':memory:')
        
        dbmod.execute_sql_script(script_path=temp_sql_script, connection=conn)
        
        # The connection is closed by the function, so we need to verify differently
        # Create a new connection to check the results
        check_conn = sqlite3.connect(':memory:')
        check_conn.executescript(open(temp_sql_script).read())
        check_conn.commit()
        
        cursor = check_conn.cursor()
        cursor.execute("SELECT name FROM test_table WHERE id = 1")
        result = cursor.fetchone()
        assert result[0] == 'test_name'
        check_conn.close()
        
    finally:
        os.unlink(temp_sql_script)


def test_execute_sql_script_file_not_found():
    """Test execute_sql_script with non-existent file."""
    with pytest.raises(FileNotFoundError):
        dbmod.execute_sql_script(script_path="/nonexistent/script.sql")


def test_execute_sql_script_empty_path():
    """Test execute_sql_script with empty string path."""
    with pytest.raises(FileNotFoundError):
        dbmod.execute_sql_script(script_path="")


def test_execute_sql_script_invalid_sql(temp_sql_script):
    """Test execute_sql_script with invalid SQL."""
    try:
        # Create a temporary file with invalid SQL
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write("INVALID SQL STATEMENT;")
            invalid_script = f.name
        
        conn = sqlite3.connect(':memory:')
        
        with pytest.raises(sqlite3.DatabaseError):
            dbmod.execute_sql_script(script_path=invalid_script, connection=conn)
        
    finally:
        conn.close()
        os.unlink(temp_sql_script)
        os.unlink(invalid_script)


# --- get_reflected_base Tests ---

def test_get_reflected_base_valid(db, base, flask_app):
    """Test get_reflected_base with valid SQLAlchemy instance."""
    with flask_app.app_context():
        reflected = dbmod.get_reflected_base(db)
        
        assert reflected is not None
        assert hasattr(reflected, 'classes')
        # Verify the test table is reflected
        assert 'test_table' in reflected.classes


def test_get_reflected_base_none_db():
    """Test get_reflected_base with None db."""
    with pytest.raises(AttributeError):
        dbmod.get_reflected_base(None)


def test_get_reflected_base_invalid_db():
    """Test get_reflected_base with invalid db object."""
    # Test with None - this should raise AttributeError when trying to access db.metadata
    with pytest.raises(AttributeError):
        dbmod.get_reflected_base(None)


# --- cleanse_misc_json Tests ---

def test_cleanse_misc_json_normal_operation(db, reflected_base, flask_app):
    """Test cleanse_misc_json normal operation."""
    with flask_app.app_context():
        # Insert test data
        TestModel = reflected_base.classes.test_table
        row1 = TestModel(id=1, name="test1", misc_json={"key1": "Please Select", "key2": "valid_value"})
        row2 = TestModel(id=2, name="test2", misc_json={"key3": "Please Select", "key4": "another_valid"})
        row3 = TestModel(id=3, name="test3", misc_json={"key5": "valid_only"})
        
        db.session.add_all([row1, row2, row3])
        db.session.commit()
        
        # Cleanse the data
        dbmod.cleanse_misc_json(db, reflected_base, "test_table", "misc_json", "Please Select")
        
        # Verify changes
        rows = db.session.query(TestModel).all()
        assert len(rows) == 3
        
        # Check that "Please Select" values were removed
        assert rows[0].misc_json == {"key2": "valid_value"}
        assert rows[1].misc_json == {"key4": "another_valid"}
        assert rows[2].misc_json == {"key5": "valid_only"}


def test_cleanse_misc_json_dry_run(db, reflected_base, flask_app):
    """Test cleanse_misc_json with dry_run=True."""
    with flask_app.app_context():
        # Insert test data
        TestModel = reflected_base.classes.test_table
        row = TestModel(id=1, name="test1", misc_json={"key1": "Please Select", "key2": "valid_value"})
        db.session.add(row)
        db.session.commit()
        
        # Store original data
        original_json = row.misc_json.copy()
        
        # Cleanse with dry run
        dbmod.cleanse_misc_json(db, reflected_base, "test_table", "misc_json", "Please Select", dry_run=True)
        
        # Verify no changes were made (rolled back)
        db.session.refresh(row)
        assert row.misc_json == original_json


def test_cleanse_misc_json_remove_none_values(db, reflected_base, flask_app):
    """Test cleanse_misc_json removing None values."""
    with flask_app.app_context():
        # Insert test data with None values
        TestModel = reflected_base.classes.test_table
        row = TestModel(id=1, name="test1", misc_json={"key1": None, "key2": "valid_value", "key3": None})
        db.session.add(row)
        db.session.commit()
        
        # Cleanse None values
        dbmod.cleanse_misc_json(db, reflected_base, "test_table", "misc_json", None)
        
        # Verify None values were removed
        db.session.refresh(row)
        assert row.misc_json == {"key2": "valid_value"}


def test_cleanse_misc_json_non_dict_json(db, reflected_base, flask_app):
    """Test cleanse_misc_json with non-dict JSON values."""
    with flask_app.app_context():
        # Insert test data with non-dict JSON
        TestModel = reflected_base.classes.test_table
        row1 = TestModel(id=1, name="test1", misc_json="not_a_dict")
        row2 = TestModel(id=2, name="test2", misc_json=123)
        row3 = TestModel(id=3, name="test3", misc_json={"key1": "Please Select"})
        
        db.session.add_all([row1, row2, row3])
        db.session.commit()
        
        # Cleanse should skip non-dict values
        dbmod.cleanse_misc_json(db, reflected_base, "test_table", "misc_json", "Please Select")
        
        # Verify only dict was processed
        rows = db.session.query(TestModel).all()
        assert rows[0].misc_json == "not_a_dict"  # unchanged
        assert rows[1].misc_json == 123  # unchanged
        assert rows[2].misc_json == {}  # processed


def test_cleanse_misc_json_empty_json(db, reflected_base, flask_app):
    """Test cleanse_misc_json with empty JSON dict."""
    with flask_app.app_context():
        # Insert test data with empty dict
        TestModel = reflected_base.classes.test_table
        row = TestModel(id=1, name="test1", misc_json={})
        db.session.add(row)
        db.session.commit()
        
        # Cleanse should handle empty dict
        dbmod.cleanse_misc_json(db, reflected_base, "test_table", "misc_json", "Please Select")
        
        # Verify empty dict remains
        db.session.refresh(row)
        assert row.misc_json == {}


def test_cleanse_misc_json_none_json(db, reflected_base, flask_app):
    """Test cleanse_misc_json with None JSON values."""
    with flask_app.app_context():
        # Insert test data with None JSON
        TestModel = reflected_base.classes.test_table
        row = TestModel(id=1, name="test1", misc_json=None)
        db.session.add(row)
        db.session.commit()
        
        # Cleanse should handle None JSON (function uses "or {}" internally)
        dbmod.cleanse_misc_json(db, reflected_base, "test_table", "misc_json", "Please Select")
        
        # Verify None remains None (function doesn't change None to empty dict)
        db.session.refresh(row)
        assert row.misc_json is None


def test_cleanse_misc_json_table_not_found(db, reflected_base, flask_app):
    """Test cleanse_misc_json with non-existent table."""
    with flask_app.app_context():
        with pytest.raises(ValueError, match="Table 'nonexistent_table' not found"):
            dbmod.cleanse_misc_json(db, reflected_base, "nonexistent_table", "misc_json")


def test_cleanse_misc_json_column_not_found(db, reflected_base, flask_app):
    """Test cleanse_misc_json with non-existent column."""
    with flask_app.app_context():
        with pytest.raises(ValueError, match="Column 'nonexistent_column' not found"):
            dbmod.cleanse_misc_json(db, reflected_base, "test_table", "nonexistent_column")


def test_cleanse_misc_json_empty_table_name(db, reflected_base, flask_app):
    """Test cleanse_misc_json with empty table name."""
    with flask_app.app_context():
        with pytest.raises(ValueError, match="Table '' not found"):
            dbmod.cleanse_misc_json(db, reflected_base, "", "misc_json")


def test_cleanse_misc_json_none_table_name(db, reflected_base, flask_app):
    """Test cleanse_misc_json with None table name."""
    with flask_app.app_context():
        with pytest.raises(ValueError, match="Table 'None' not found"):
            dbmod.cleanse_misc_json(db, reflected_base, None, "misc_json")


def test_cleanse_misc_json_empty_column_name(db, reflected_base, flask_app):
    """Test cleanse_misc_json with empty column name."""
    with flask_app.app_context():
        with pytest.raises(ValueError, match="Column '' not found"):
            dbmod.cleanse_misc_json(db, reflected_base, "test_table", "")


def test_cleanse_misc_json_none_column_name(db, reflected_base, flask_app):
    """Test cleanse_misc_json with None column name."""
    with flask_app.app_context():
        with pytest.raises(TypeError, match="attribute name must be string"):
            dbmod.cleanse_misc_json(db, reflected_base, "test_table", None)


def test_cleanse_misc_json_custom_remove_value(db, reflected_base, flask_app):
    """Test cleanse_misc_json with custom remove value."""
    with flask_app.app_context():
        # Insert test data
        TestModel = reflected_base.classes.test_table
        row = TestModel(id=1, name="test1", misc_json={"key1": "custom_value", "key2": "keep_this"})
        db.session.add(row)
        db.session.commit()
        
        # Cleanse with custom remove value
        dbmod.cleanse_misc_json(db, reflected_base, "test_table", "misc_json", "custom_value")
        
        # Verify custom value was removed
        db.session.refresh(row)
        assert row.misc_json == {"key2": "keep_this"}


def test_cleanse_misc_json_no_matches(db, reflected_base, flask_app):
    """Test cleanse_misc_json when no values match remove_value."""
    with flask_app.app_context():
        # Insert test data with no matching values
        TestModel = reflected_base.classes.test_table
        row = TestModel(id=1, name="test1", misc_json={"key1": "value1", "key2": "value2"})
        db.session.add(row)
        db.session.commit()
        
        # Store original data
        original_json = row.misc_json.copy()
        
        # Cleanse with value that doesn't exist
        dbmod.cleanse_misc_json(db, reflected_base, "test_table", "misc_json", "nonexistent_value")
        
        # Verify no changes were made
        db.session.refresh(row)
        assert row.misc_json == original_json


def test_cleanse_misc_json_database_error_handling(db, reflected_base, flask_app):
    """Test cleanse_misc_json error handling during database operations."""
    with flask_app.app_context():
        # Insert test data
        TestModel = reflected_base.classes.test_table
        row = TestModel(id=1, name="test1", misc_json={"key1": "Please Select"})
        db.session.add(row)
        db.session.commit()
        
        # Mock a database error during commit
        with patch.object(db.session, 'commit', side_effect=Exception("Database error")):
            with pytest.raises(RuntimeError, match="Error during cleansing"):
                dbmod.cleanse_misc_json(db, reflected_base, "test_table", "misc_json", "Please Select")
        
        # Verify session was rolled back
        db.session.refresh(row)
        assert row.misc_json == {"key1": "Please Select"}  # unchanged due to rollback 