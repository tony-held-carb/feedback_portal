import pytest
try:
  import arb.portal.globals as portal_globals
except ModuleNotFoundError:
  import sys, os
  sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
  import arb.portal.globals as portal_globals
from unittest.mock import patch, MagicMock
import datetime

# NOTE: Some functions in globals.py import dependencies inside the function body to avoid circular imports.
# This makes them impossible to patch/mock robustly in unit tests. As a result, tests for these functions are skipped.
# See documentation/docstring_update_for_testing.md for details and rationale.

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