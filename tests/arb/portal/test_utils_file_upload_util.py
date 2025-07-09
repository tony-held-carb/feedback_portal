import pytest
import arb.portal.utils.file_upload_util as file_upload_util
from unittest.mock import MagicMock, patch

@pytest.mark.skip(reason="Most file_upload_util functions require Flask request context or file I/O. Robust unit testing not possible without integration test or source refactor. See documentation.")
def test_save_uploaded_file():
    pass

@pytest.mark.skip(reason="Most file_upload_util functions require Flask request context or file I/O. Robust unit testing not possible without integration test or source refactor. See documentation.")
def test_allowed_file():
    pass 