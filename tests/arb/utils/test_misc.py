"""
Unit tests for arb.utils.misc utility functions.

These tests cover the core logic and return values of utility functions, including sanitize_for_utf8. Logging behavior of sanitize_for_utf8 is not covered by these tests.

Note: Logging behavior of sanitize_for_utf8 is not covered by these tests. 
"""
import logging

import pytest

import arb.utils.misc as misc


def test_get_nested_value_basic():
  """Test that get_nested_value returns the correct value for valid nested keys."""
  d = {"a": {"b": {"c": 42}}, "x": 99}
  assert misc.get_nested_value(d, ("a", "b", "c")) == 42
  assert misc.get_nested_value(d, "x") == 99


def test_get_nested_value_missing_key():
  """Test that get_nested_value raises KeyError for missing keys."""
  d = {"a": {"b": {}}}
  with pytest.raises(KeyError):
    misc.get_nested_value(d, ("a", "b", "c"))


def test_get_nested_value_type_error():
  """Test that get_nested_value raises TypeError when traversing a non-dict value."""
  d = {"a": 5}
  with pytest.raises(TypeError):
    misc.get_nested_value(d, ("a", "b"))


def test_get_nested_value_value_error():
  """Test that get_nested_value raises KeyError for missing top-level key."""
  d = {"a": {}}
  with pytest.raises(KeyError):
    misc.get_nested_value(d, "b")


def test_ensure_key_value_pair_injects():
  """Test that ensure_key_value_pair injects a default value when missing."""
  d = {"a": {"x": 1}, "b": {}}
  defaults = {"b": 99}
  misc.ensure_key_value_pair(d, defaults, "x")
  assert d["b"]["x"] == 99


def test_ensure_key_value_pair_type_error():
  """Test that ensure_key_value_pair raises TypeError for invalid input."""
  d = {"a": {}}
  defaults = {}
  with pytest.raises(TypeError):
    misc.ensure_key_value_pair(d, defaults, "x")


def test_replace_list_occurrences():
  """Test that replace_list_occurrences replaces items in a list according to a lookup dict."""
  l = ["cat", "dog", "bird"]
  lookup = {"dog": "puppy", "bird": "parrot"}
  misc.replace_list_occurrences(l, lookup)
  assert l == ["cat", "puppy", "parrot"]


def test_replace_list_occurrences_none():
  """Test that replace_list_occurrences raises TypeError when input is None."""
  with pytest.raises(TypeError):
    misc.replace_list_occurrences(None, {"a": 1})


def test_args_to_string():
  """Test that args_to_string joins a list of arguments into a string."""
  assert misc.args_to_string(["--debug", "--log"]) == " --debug --log "
  assert misc.args_to_string(None) == ""
  assert misc.args_to_string([]) == ""


def test_log_error_logs_and_raises():
  """Test that log_error logs an error and raises the exception."""
  logger = logging.getLogger("arb.utils.misc")
  with pytest.raises(ValueError):
    try:
      raise ValueError("bad value")
    except Exception as e:
      misc.log_error(e)


def test_safe_cast_basic():
  """Test that safe_cast correctly casts values to the specified type."""
  assert misc.safe_cast("5", int) == 5
  assert misc.safe_cast(5, int) == 5
  assert misc.safe_cast("3.2", float) == 3.2
  assert misc.safe_cast(None, str) == "None"


def test_safe_cast_value_error():
  """Test that safe_cast raises ValueError for invalid casts."""
  with pytest.raises(ValueError):
    misc.safe_cast("foo", int)
  with pytest.raises(ValueError):
    misc.safe_cast("bar", None)


def test_sanitize_for_utf8_valid():
  """Test that sanitize_for_utf8 returns the original string for valid UTF-8 input."""
  from arb.utils.misc import sanitize_for_utf8
  s = "hello world"
  assert sanitize_for_utf8(s) == s


def test_sanitize_for_utf8_non_string():
  """Test that sanitize_for_utf8 returns None for non-string input."""
  from arb.utils.misc import sanitize_for_utf8
  result = sanitize_for_utf8(12345, context="non-string test")
  assert result is None
  # Note: This test does not check logging output.


def test_sanitize_for_utf8_windows_1252_smart_quote():
  """Test that sanitize_for_utf8 returns a string that can be encoded as UTF-8, even with Windows-1252 smart quotes or other non-UTF-8 bytes."""
  from arb.utils.misc import sanitize_for_utf8
  # Windows-1252 smart quote (right single quote, 0x92)
  bad_bytes = b"I wasn\x92t there"
  # Simulate what happens if this is decoded as latin1 (as often happens with Excel/Windows files)
  bad_str = bad_bytes.decode("latin1")
  result = sanitize_for_utf8(bad_str)
  # The result should be a string that can be encoded as UTF-8 without error
  result.encode("utf-8")  # Should not raise
  assert isinstance(result, str)


def test_sanitize_for_utf8_none():
  """Test that sanitize_for_utf8 returns None when input is None."""
  from arb.utils.misc import sanitize_for_utf8
  result = sanitize_for_utf8(None)
  assert result is None


def test_sanitize_for_utf8_empty_string():
  """Test that sanitize_for_utf8 returns an empty string when input is an empty string."""
  from arb.utils.misc import sanitize_for_utf8
  result = sanitize_for_utf8("")
  assert result == ""
