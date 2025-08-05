"""
Unit tests for file_io.py

Coverage philosophy:
- All functions are tested with valid, edge, and error inputs
- Filesystem operations use tmp_path for isolation
- Time and external dependencies are mocked as needed
- Project root resolution is tested with temp directory structures
- File reading is tested with temp files and mocks

This suite provides robust coverage for file and path utilities.
"""
from pathlib import Path
from unittest.mock import patch

import pytest

from arb.utils import file_io


# --- ensure_parent_dirs ---

def test_ensure_parent_dirs_creates_parents(tmp_path):
  file_path = tmp_path / "a" / "b" / "file.txt"
  assert not file_path.parent.exists()
  file_io.ensure_parent_dirs(file_path)
  assert file_path.parent.exists()
  assert file_path.parent.is_dir()


def test_ensure_parent_dirs_noop_for_empty():
  # Should not raise
  file_io.ensure_parent_dirs("")
  file_io.ensure_parent_dirs(None)


def test_ensure_parent_dirs_existing_dir(tmp_path):
  file_path = tmp_path / "file.txt"
  file_io.ensure_parent_dirs(file_path)
  assert file_path.parent.exists()


# --- ensure_dir_exists ---

def test_ensure_dir_exists_creates(tmp_path):
  dir_path = tmp_path / "x" / "y"
  assert not dir_path.exists()
  file_io.ensure_dir_exists(dir_path)
  assert dir_path.exists() and dir_path.is_dir()


def test_ensure_dir_exists_existing(tmp_path):
  dir_path = tmp_path / "z"
  dir_path.mkdir()
  file_io.ensure_dir_exists(dir_path)
  assert dir_path.exists()


def test_ensure_dir_exists_file_raises(tmp_path):
  file_path = tmp_path / "file.txt"
  file_path.write_text("hi")
  with pytest.raises(ValueError):
    file_io.ensure_dir_exists(file_path)


def test_ensure_dir_exists_noop_for_empty():
  # Should not raise
  file_io.ensure_dir_exists("")
  file_io.ensure_dir_exists(None)


# --- get_secure_timestamped_file_name ---

def test_get_secure_timestamped_file_name_basic(tmp_path):
  with patch("arb.utils.file_io.datetime") as mock_dt:
    mock_dt.now.return_value = mock_dt.strptime("2025-05-05T12:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
    mock_dt.now.return_value.strftime.return_value = "2025-05-05T12-30-00Z"
    mock_dt.now.return_value.tzinfo = None
    directory = tmp_path
    file_name = "user report.xlsx"
    result = file_io.get_secure_timestamped_file_name(directory, file_name)
    assert result.name.startswith("user_report_ts_2025-05-05T12-30-00Z")
    assert result.suffix == ".xlsx"
    assert result.parent == tmp_path


def test_get_secure_timestamped_file_name_empty_dir(tmp_path):
  with patch("arb.utils.file_io.datetime") as mock_dt:
    mock_dt.now.return_value = mock_dt.strptime("2025-05-05T12:30:00+00:00", "%Y-%m-%dT%H:%M:%S%z")
    mock_dt.now.return_value.strftime.return_value = "2025-05-05T12-30-00Z"
    mock_dt.now.return_value.tzinfo = None
    file_name = "user report.xlsx"
    result = file_io.get_secure_timestamped_file_name("", file_name)
    assert Path.home() in result.parents


def test_get_secure_timestamped_file_name_empty_file():
  with pytest.raises(ValueError):
    file_io.get_secure_timestamped_file_name("/tmp", "")
  with pytest.raises(ValueError):
    file_io.get_secure_timestamped_file_name("/tmp", None)


# --- resolve_project_root & get_project_root_dir ---

def test_get_project_root_dir_success(tmp_path):
  # Create a fake structure: tmp_path/foo/bar/baz/file.txt
  root = tmp_path / "foo"
  d = root / "bar" / "baz"
  d.mkdir(parents=True)
  file = d / "file.txt"
  file.write_text("hi")
  match_parts = ["foo", "bar", "baz"]
  result = file_io.get_project_root_dir(file, match_parts)
  assert result == root


def test_get_project_root_dir_no_match(tmp_path):
  file = tmp_path / "a" / "b" / "file.txt"
  file.parent.mkdir(parents=True)
  file.write_text("hi")
  with pytest.raises(ValueError):
    file_io.get_project_root_dir(file, ["not", "found"])


def test_get_project_root_dir_empty_args(tmp_path):
  file = tmp_path / "file.txt"
  file.write_text("hi")
  with pytest.raises(ValueError):
    file_io.get_project_root_dir("", ["foo"])
  with pytest.raises(ValueError):
    file_io.get_project_root_dir(file, [])


def test_resolve_project_root_success(tmp_path):
  # Use a custom structure
  root = tmp_path / "proj" / "src" / "arb" / "utils"
  d = root / "excel"
  d.mkdir(parents=True)
  file = d / "file.txt"
  file.write_text("hi")
  candidate_structures = [["proj", "src", "arb", "utils", "excel"]]
  result = file_io.resolve_project_root(file, candidate_structures)
  # The function returns the parent of the matched structure
  assert result == tmp_path / "proj"


def test_resolve_project_root_not_found(tmp_path):
  file = tmp_path / "file.txt"
  file.write_text("hi")
  with pytest.raises(file_io.ProjectRootNotFoundError):
    file_io.resolve_project_root(file, [["not", "found"]])


def test_resolve_project_root_empty_args(tmp_path):
  with pytest.raises(ValueError):
    file_io.resolve_project_root("", [["foo"]])


# --- read_file_reverse ---

def test_read_file_reverse_basic(tmp_path):
  file = tmp_path / "log.txt"
  lines = [f"line {i}" for i in range(10)]
  file.write_text("\n".join(lines))
  with patch("file_read_backwards.FileReadBackwards") as mock_frb:
    mock_frb.return_value.__enter__.return_value = reversed(lines)
    result = file_io.read_file_reverse(file, n=5)
    assert result == lines[-5:]


def test_read_file_reverse_empty_file(tmp_path):
  file = tmp_path / "empty.txt"
  file.write_text("")
  with patch("file_read_backwards.FileReadBackwards") as mock_frb:
    mock_frb.return_value.__enter__.return_value = iter([])
    result = file_io.read_file_reverse(file, n=10)
    assert result == []


def test_read_file_reverse_file_not_found(tmp_path):
  file = tmp_path / "nofile.txt"
  with pytest.raises(FileNotFoundError):
    file_io.read_file_reverse(file, n=5)
