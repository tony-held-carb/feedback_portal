"""
Unit tests for io_wrappers.py

Coverage philosophy:
- All functions are tested with valid, edge, and error inputs
- Filesystem operations use tmp_path for isolation
- JSON/text read/write and copy are tested for correctness and error handling

This suite provides robust coverage for file I/O wrappers.
"""
import json
import sys
from pathlib import Path

import pytest

from arb.utils.path_utils import find_repo_root
sys.path.insert(0, str(find_repo_root(Path(__file__)) / 'source' / 'production'))
from arb.utils.io_wrappers import save_json_safely, read_json_file, write_text_file, copy_file_safe


# --- save_json_safely ---

def test_save_json_safely_basic(tmp_path):
  data = {"a": 1, "b": 2}
  file = tmp_path / "test.json"
  save_json_safely(data, file)
  assert file.exists()
  loaded = json.loads(file.read_text())
  assert loaded == data


def test_save_json_safely_none_data(tmp_path):
  file = tmp_path / "null.json"
  save_json_safely(None, file)
  assert file.read_text().strip() == "null"


def test_save_json_safely_with_options(tmp_path):
  data = {"a": 1}
  file = tmp_path / "opt.json"
  save_json_safely(data, file, json_options={"indent": 4})
  text = file.read_text()
  assert "    " in text  # indented


def test_save_json_safely_creates_parents(tmp_path):
  file = tmp_path / "a" / "b" / "c.json"
  save_json_safely({"x": 1}, file)
  assert file.exists()


def test_save_json_safely_none_path():
  with pytest.raises(ValueError):
    save_json_safely({"a": 1}, None)


# --- read_json_file ---

def test_read_json_file_basic(tmp_path):
  file = tmp_path / "test.json"
  file.write_text('{"a": 1, "b": 2}')
  result = read_json_file(file)
  assert result == {"a": 1, "b": 2}


def test_read_json_file_with_options(tmp_path):
  file = tmp_path / "test.json"
  file.write_text('{"a": 1}')

  def hook(d):
    d["hooked"] = True
    return d

  result = read_json_file(file, json_options={"object_hook": hook})
  assert result["hooked"] is True


def test_read_json_file_file_not_found(tmp_path):
  file = tmp_path / "nofile.json"
  with pytest.raises(FileNotFoundError):
    read_json_file(file)


def test_read_json_file_invalid_json(tmp_path):
  file = tmp_path / "bad.json"
  file.write_text("not json")
  with pytest.raises(json.JSONDecodeError):
    read_json_file(file)


def test_read_json_file_none_path():
  with pytest.raises(ValueError):
    read_json_file(None)


# --- write_text_file ---

def test_write_text_file_basic(tmp_path):
  file = tmp_path / "hello.txt"
  write_text_file("Hello, world!", file)
  assert file.read_text() == "Hello, world!"


def test_write_text_file_none_text(tmp_path):
  file = tmp_path / "empty.txt"
  write_text_file(None, file)
  assert file.read_text() == ""


def test_write_text_file_creates_parents(tmp_path):
  file = tmp_path / "a" / "b" / "c.txt"
  write_text_file("abc", file)
  assert file.exists()


def test_write_text_file_none_path():
  with pytest.raises(ValueError):
    write_text_file("hi", None)


# --- copy_file_safe ---

def test_copy_file_safe_basic(tmp_path):
  src = tmp_path / "src.txt"
  dst = tmp_path / "a" / "b" / "dst.txt"
  src.write_text("copy me")
  copy_file_safe(src, dst)
  assert dst.exists()
  assert dst.read_text() == "copy me"


def test_copy_file_safe_missing_src(tmp_path):
  src = tmp_path / "nope.txt"
  dst = tmp_path / "dst.txt"
  with pytest.raises(FileNotFoundError):
    copy_file_safe(src, dst)


def test_copy_file_safe_none_args(tmp_path):
  src = tmp_path / "src.txt"
  src.write_text("hi")
  with pytest.raises(ValueError):
    copy_file_safe(None, src)
  with pytest.raises(ValueError):
    copy_file_safe(src, None)
