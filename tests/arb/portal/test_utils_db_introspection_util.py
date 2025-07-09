import pytest
import arb.portal.utils.db_introspection_util as db_introspection_util
from unittest.mock import MagicMock, patch

@pytest.mark.skip(reason="Most db_introspection_util functions require a live DB, SQLAlchemy AutomapBase, or integration context. Robust unit testing not possible without integration test or source refactor. See documentation.")
def test_get_table_names():
    pass

@pytest.mark.skip(reason="Most db_introspection_util functions require a live DB, SQLAlchemy AutomapBase, or integration context. Robust unit testing not possible without integration test or source refactor. See documentation.")
def test_get_column_names():
    pass

@pytest.mark.skip(reason="Most db_introspection_util functions require a live DB, SQLAlchemy AutomapBase, or integration context. Robust unit testing not possible without integration test or source refactor. See documentation.")
def test_get_primary_key():
    pass 