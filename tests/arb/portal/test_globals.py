import pytest
try:
  import arb.portal.globals as portal_globals
except ModuleNotFoundError:
  import sys, os
  sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
  import arb.portal.globals as portal_globals
from unittest.mock import patch, MagicMock
import datetime
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base

# NOTE: Some functions in globals.py import dependencies inside the function body to avoid circular imports.
# This makes them impossible to patch/mock robustly in unit tests. As a result, tests for these functions are skipped.
# See documentation/docstring_update_for_testing.md for details and rationale.
#
# IMPORTANT: The imported functions are fully tested elsewhere:
# - get_excel_dropdown_data (from arb.portal.db_hardcoded) is tested in tests/arb/portal/test_db_hardcoded.py
# - get_sa_automap_types (from arb.utils.sql_alchemy) is tested in tests/arb/utils/test_sql_alchemy.py
# This provides high confidence that the core logic in load_drop_downs and load_type_mapping is correct.

def test_globals_initial_state():
  assert isinstance(portal_globals.Globals.db_column_types, dict)
  assert isinstance(portal_globals.Globals.drop_downs, dict)
  assert isinstance(portal_globals.Globals.drop_downs_contingent, dict)

@pytest.mark.skip(reason="Cannot robustly mock get_excel_dropdown_data because it is imported inside the method. See docstring_update_for_testing.md for details. Requires source change to test fully.")
def test_load_drop_downs_sets_globals():
  pass

@pytest.mark.skip(reason="Cannot robustly mock get_sa_automap_types because it is imported inside the method. See docstring_update_for_testing.md for details. Requires source change to test fully.")
def test_load_type_mapping_sets_db_column_types():
  pass

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
def test_base(test_app, test_db):
  """Create a reflected base from the test database."""
  with test_app.app_context():
    from arb.utils.database import get_reflected_base
    return get_reflected_base(test_db)

def test_load_drop_downs_integration(test_app, test_db):
  """Integration test for load_drop_downs using real database and app context."""
  with test_app.app_context():
    # Clear any existing data
    portal_globals.Globals.drop_downs = {}
    portal_globals.Globals.drop_downs_contingent = {}
    
    # Call the method
    portal_globals.Globals.load_drop_downs(test_app, test_db)
    
    # Verify that the globals were populated
    assert isinstance(portal_globals.Globals.drop_downs, dict)
    assert isinstance(portal_globals.Globals.drop_downs_contingent, dict)
    
    # Verify that dropdown data was loaded (should contain the expected keys)
    expected_keys = {
      "venting_exclusion", "ogi_performed", "ogi_result", "method21_performed", 
      "method21_result", "equipment_at_source", "component_at_source",
      "emission_identified_flag_fk", "emission_type_fk", "emission_location",
      "emission_cause", "emission_cause_secondary", "emission_cause_tertiary",
      "included_in_last_lmr", "planned_for_next_lmr"
    }
    
    for key in expected_keys:
      assert key in portal_globals.Globals.drop_downs, f"Missing dropdown key: {key}"
    
    # Verify contingent dropdowns were loaded
    assert "emission_cause_contingent_on_emission_location" in portal_globals.Globals.drop_downs_contingent

def test_load_type_mapping_integration(test_app, test_db, test_base):
  """Integration test for load_type_mapping using real database and app context."""
  with test_app.app_context():
    # Clear any existing data
    portal_globals.Globals.db_column_types = {}
    
    # Call the method
    portal_globals.Globals.load_type_mapping(test_app, test_db, test_base)
    
    # Verify that the globals were populated
    assert isinstance(portal_globals.Globals.db_column_types, dict)
    
    # The database might be empty, but the method should still work
    # and populate the dict (even if empty)

def test_globals_integration_with_real_data(test_app, test_db, test_base):
  """Integration test that loads both dropdowns and type mappings together."""
  with test_app.app_context():
    # Clear all globals
    portal_globals.Globals.drop_downs = {}
    portal_globals.Globals.drop_downs_contingent = {}
    portal_globals.Globals.db_column_types = {}
    
    # Load both types of data
    portal_globals.Globals.load_type_mapping(test_app, test_db, test_base)
    portal_globals.Globals.load_drop_downs(test_app, test_db)
    
    # Verify all globals are populated
    assert isinstance(portal_globals.Globals.drop_downs, dict)
    assert isinstance(portal_globals.Globals.drop_downs_contingent, dict)
    assert isinstance(portal_globals.Globals.db_column_types, dict)
    
    # Verify dropdown data is accessible
    assert len(portal_globals.Globals.drop_downs) > 0
    assert len(portal_globals.Globals.drop_downs_contingent) > 0

def test_globals_persistence_across_calls(test_app, test_db, test_base):
  """Test that globals persist correctly across multiple calls."""
  with test_app.app_context():
    # First call
    portal_globals.Globals.load_drop_downs(test_app, test_db)
    first_drop_downs = portal_globals.Globals.drop_downs.copy()
    first_contingent = portal_globals.Globals.drop_downs_contingent.copy()
    
    # Second call
    portal_globals.Globals.load_drop_downs(test_app, test_db)
    second_drop_downs = portal_globals.Globals.drop_downs
    second_contingent = portal_globals.Globals.drop_downs_contingent
    
    # Should be the same (idempotent)
    assert first_drop_downs == second_drop_downs
    assert first_contingent == second_contingent 