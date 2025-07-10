"""
First pass tests for arb.portal.startup.runtime_info

Tests what can be tested with minimal context: constants are defined, platform detection works.
Skips complex context-dependent features for future follow-up testing.
"""
import pytest
from arb.portal.startup import runtime_info

def test_platform_constants_defined():
  """Platform detection constants are defined."""
  assert hasattr(runtime_info, 'PLATFORM')
  assert hasattr(runtime_info, 'IS_WINDOWS')
  assert hasattr(runtime_info, 'IS_LINUX')
  assert hasattr(runtime_info, 'IS_MAC')
  assert isinstance(runtime_info.PLATFORM, str)
  assert isinstance(runtime_info.IS_WINDOWS, bool)
  assert isinstance(runtime_info.IS_LINUX, bool)
  assert isinstance(runtime_info.IS_MAC, bool)

def test_path_constants_defined():
  """Path constants are defined."""
  assert hasattr(runtime_info, 'PROJECT_ROOT')
  assert hasattr(runtime_info, 'UPLOAD_PATH')
  assert hasattr(runtime_info, 'LOG_DIR')
  assert hasattr(runtime_info, 'LOG_FILE')
  assert hasattr(runtime_info, 'STATIC_DIR')

def test_platform_detection_logic():
  """Platform detection logic is consistent."""
  # Only one platform should be True
  platforms = [runtime_info.IS_WINDOWS, runtime_info.IS_LINUX, runtime_info.IS_MAC]
  assert sum(platforms) <= 1, "Only one platform should be detected as True"

def test_path_structure():
  """Path structure follows expected pattern."""
  assert runtime_info.UPLOAD_PATH.name == 'portal_uploads'
  assert runtime_info.LOG_DIR.name == 'logs'
  assert runtime_info.LOG_FILE.name == 'arb_portal.log'

@pytest.mark.skip(reason="Requires complex file system operations and runtime conditions. Will be addressed in follow-up context testing.")
def test_print_runtime_diagnostics():
  """print_runtime_diagnostics() function works correctly."""
  pass

@pytest.mark.skip(reason="Requires complex file system operations and runtime conditions. Will be addressed in follow-up context testing.")
def test_directory_creation():
  """Required directories are created correctly."""
  pass 