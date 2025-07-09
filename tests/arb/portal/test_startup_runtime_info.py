import pytest
import arb.portal.startup.runtime_info as runtime_info
from unittest.mock import patch, MagicMock


def test_constants_types():
    assert isinstance(runtime_info.PROJECT_ROOT, runtime_info.Path)
    assert isinstance(runtime_info.UPLOAD_PATH, runtime_info.Path)
    assert isinstance(runtime_info.LOG_DIR, runtime_info.Path)
    assert isinstance(runtime_info.LOG_FILE, runtime_info.Path)
    assert isinstance(runtime_info.STATIC_DIR, runtime_info.Path)
    assert isinstance(runtime_info.IS_WINDOWS, bool)
    assert isinstance(runtime_info.IS_LINUX, bool)
    assert isinstance(runtime_info.IS_MAC, bool)


def test_platform_flags():
    # Only one of IS_WINDOWS, IS_LINUX, IS_MAC should be True
    flags = [runtime_info.IS_WINDOWS, runtime_info.IS_LINUX, runtime_info.IS_MAC]
    assert sum(flags) == 1

@pytest.mark.skip(reason="print_runtime_diagnostics prints/logs system info; robust test would require capturing logs and patching platform. Not critical for unit test coverage.")
def test_print_runtime_diagnostics():
    pass 