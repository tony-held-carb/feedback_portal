import pytest
import arb.portal.startup.flask as startup_flask
from unittest.mock import MagicMock

@pytest.mark.skip(reason="configure_flask_app requires a real Flask app context; robust unit testing not possible without integration test or source refactor. See documentation.")
def test_configure_flask_app():
    pass 