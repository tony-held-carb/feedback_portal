"""
Comprehensive tests for arb.portal.startup.runtime_info

Covers platform detection, path constants, directory creation, and print_runtime_diagnostics logging.
"""
import sys
from pathlib import Path

from arb.portal.startup import runtime_info


def test_platform_constants_defined():
  """Platform detection constants are defined and correct types."""
  assert hasattr(runtime_info, 'PLATFORM')
  assert hasattr(runtime_info, 'IS_WINDOWS')
  assert hasattr(runtime_info, 'IS_LINUX')
  assert hasattr(runtime_info, 'IS_MAC')
  assert isinstance(runtime_info.PLATFORM, str)
  assert isinstance(runtime_info.IS_WINDOWS, bool)
  assert isinstance(runtime_info.IS_LINUX, bool)
  assert isinstance(runtime_info.IS_MAC, bool)


def test_platform_detection_logic():
  """Platform detection logic is mutually exclusive and matches sys.platform."""
  platforms = [runtime_info.IS_WINDOWS, runtime_info.IS_LINUX, runtime_info.IS_MAC]
  assert sum(platforms) <= 1, "Only one platform should be detected as True"
  # Check that the detected platform matches the running platform
  plat = sys.platform
  if plat.startswith('win'):
    assert runtime_info.IS_WINDOWS
  elif plat.startswith('linux'):
    assert runtime_info.IS_LINUX
  elif plat.startswith('darwin'):
    assert runtime_info.IS_MAC


def test_path_constants_defined_and_types():
  """Path constants are defined and are Path objects."""
  for attr in ['PROJECT_ROOT', 'UPLOAD_PATH', 'LOG_DIR', 'LOG_FILE', 'STATIC_DIR']:
    val = getattr(runtime_info, attr)
    assert isinstance(val, Path)


def test_path_structure():
  """Path structure follows expected pattern and names."""
  assert runtime_info.UPLOAD_PATH.name == 'portal_uploads'
  assert runtime_info.LOG_DIR.name == 'logs'
  assert runtime_info.LOG_FILE.name == 'arb_portal.log'
  assert runtime_info.STATIC_DIR.name == 'static'
  # Check that LOG_FILE is inside LOG_DIR
  assert runtime_info.LOG_FILE.parent == runtime_info.LOG_DIR


def test_required_directories_exist():
  """UPLOAD_PATH and LOG_DIR exist and are directories."""
  assert runtime_info.UPLOAD_PATH.exists()
  assert runtime_info.UPLOAD_PATH.is_dir()
  assert runtime_info.LOG_DIR.exists()
  assert runtime_info.LOG_DIR.is_dir()


def test_directory_creation_idempotent(tmp_path, monkeypatch):
  """Directory creation is idempotent and does not raise if already exists."""
  # Patch PROJECT_ROOT to a temp dir and re-import
  test_root = tmp_path / "feedback_portal"
  test_root.mkdir(parents=True, exist_ok=True)
  monkeypatch.setattr(runtime_info, 'PROJECT_ROOT', test_root)
  monkeypatch.setattr(runtime_info, 'UPLOAD_PATH', test_root / 'portal_uploads')
  monkeypatch.setattr(runtime_info, 'LOG_DIR', test_root / 'logs')
  # Should not raise
  for d in [runtime_info.UPLOAD_PATH, runtime_info.LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)
    d.mkdir(parents=True, exist_ok=True)  # Call again to check idempotency
    assert d.exists() and d.is_dir()


def test_print_runtime_diagnostics_logs_all(monkeypatch):
  """print_runtime_diagnostics logs all expected info."""
  logs = []

  class DummyLogger:
    def info(self, msg):
      logs.append(msg)

  monkeypatch.setattr(runtime_info, 'logger', DummyLogger())
  runtime_info.print_runtime_diagnostics()
  # Check that all expected keys are in the logs
  expected_keys = [
    'PLATFORM', 'IS_WINDOWS', 'IS_LINUX', 'IS_MAC',
    'PROJECT_ROOT', 'UPLOAD_PATH', 'LOG_DIR', 'STATIC_DIR'
  ]
  for key in expected_keys:
    assert any(key in str(line) for line in logs)


def test_print_runtime_diagnostics_multiple_calls(monkeypatch):
  """print_runtime_diagnostics can be called multiple times without error."""
  logs = []

  class DummyLogger:
    def info(self, msg):
      logs.append(msg)

  monkeypatch.setattr(runtime_info, 'logger', DummyLogger())
  runtime_info.print_runtime_diagnostics()
  runtime_info.print_runtime_diagnostics()
  # Should have double the expected keys
  expected_keys = [
    'PLATFORM', 'IS_WINDOWS', 'IS_LINUX', 'IS_MAC',
    'PROJECT_ROOT', 'UPLOAD_PATH', 'LOG_DIR', 'STATIC_DIR'
  ]
  for key in expected_keys:
    assert sum(key in str(line) for line in logs) >= 2


def test_log_file_path_is_file():
  """LOG_FILE is a file path inside LOG_DIR."""
  assert runtime_info.LOG_FILE.parent == runtime_info.LOG_DIR
  assert runtime_info.LOG_FILE.name == 'arb_portal.log'
