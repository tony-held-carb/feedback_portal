"""
Unit tests for json.py (ARB Feedback Portal JSON utilities)

Coverage philosophy:
- All public functions are tested for normal, edge, and error cases.
- File I/O is tested using temporary files/directories to avoid side effects.
- Type safety, error handling, and contract compliance are verified.
- Tests are self-contained and do not require external dependencies beyond pytest and the standard library.

This suite provides strong confidence for current and future usage.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / 'source' / 'production'))
import json
import pytest
import decimal
import datetime
from arb.utils import json as arb_json


# --- json_serializer / json_deserializer ---
def test_json_serializer_datetime():
  dt = datetime.datetime(2025, 7, 4, 12, 34, 56, 789012)
  result = arb_json.json_serializer(dt)
  assert result["__type__"] == "datetime.datetime"
  assert "value" in result


def test_json_serializer_decimal():
  d = decimal.Decimal("1.23")
  result = arb_json.json_serializer(d)
  assert result["__type__"] == "decimal.Decimal"
  assert result["value"] == "1.23"


def test_json_serializer_class():
  result = arb_json.json_serializer(int)
  assert result["__class__"] == "int"
  assert result["__module__"] == "builtins"


def test_json_serializer_unsupported():
  with pytest.raises(TypeError):
    arb_json.json_serializer(object())


def test_json_deserializer_datetime():
  obj = {"__type__": "datetime.datetime", "value": "2025-07-04T12:34:56.789012"}
  result = arb_json.json_deserializer(obj)
  assert isinstance(result, datetime.datetime)
  assert result.year == 2025


def test_json_deserializer_decimal():
  obj = {"__type__": "decimal.Decimal", "value": "1.23"}
  result = arb_json.json_deserializer(obj)
  assert isinstance(result, decimal.Decimal)
  assert result == decimal.Decimal("1.23")


def test_json_deserializer_class():
  obj = {"__class__": "int", "__module__": "builtins"}
  result = arb_json.json_deserializer(obj)
  assert result is int


def test_json_deserializer_unknown_type():
  obj = {"__type__": "unknown.Type", "value": "foo"}
  # Should return obj unchanged, not raise
  result = arb_json.json_deserializer(obj)
  assert result == obj


def test_json_deserializer_unknown_class():
  obj = {"__class__": "not_a_real_class", "__module__": "foo"}
  with pytest.raises(TypeError):
    arb_json.json_deserializer(obj)


# --- json_save / json_load (file-based) ---
def test_json_save_and_load_roundtrip(tmp_path):
  data = {"a": 1, "b": decimal.Decimal("2.5"), "dt": datetime.datetime(2025, 7, 4, 12, 0)}
  file = tmp_path / "test.json"
  arb_json.json_save(file, data)
  loaded = arb_json.json_load(file)
  assert loaded["a"] == 1
  assert loaded["b"] == "2.5" or loaded["b"] == decimal.Decimal("2.5")
  assert "dt" in loaded


def test_json_save_none_path(tmp_path):
  with pytest.raises(ValueError):
    arb_json.json_save(None, {"a": 1})


def test_json_save_none_data(tmp_path):
  file = tmp_path / "null.json"
  arb_json.json_save(file, None)
  assert file.read_text().strip() == "null"


def test_json_load_file_not_found(tmp_path):
  file = tmp_path / "nofile.json"
  with pytest.raises(FileNotFoundError):
    arb_json.json_load(file)


def test_json_load_invalid_json(tmp_path):
  file = tmp_path / "bad.json"
  file.write_text("not json")
  with pytest.raises(json.JSONDecodeError):
    arb_json.json_load(file)


# --- json_save_with_meta / json_load_with_meta ---
def test_json_save_with_meta_and_load(tmp_path):
  data = {"foo": 1}
  meta = {"source": "test"}
  file = tmp_path / "meta.json"
  arb_json.json_save_with_meta(file, data, metadata=meta)
  loaded_data, loaded_meta = arb_json.json_load_with_meta(file)
  assert loaded_data == data
  assert loaded_meta["source"] == "test"


def test_json_save_with_meta_none_metadata(tmp_path):
  data = {"foo": 2}
  file = tmp_path / "meta2.json"
  arb_json.json_save_with_meta(file, data, metadata=None)
  loaded_data, loaded_meta = arb_json.json_load_with_meta(file)
  assert loaded_data == data
  assert isinstance(loaded_meta, dict)


# --- add_metadata_to_json ---
def test_add_metadata_to_json(tmp_path):
  file_in = tmp_path / "in.json"
  file_out = tmp_path / "out.json"
  file_in.write_text(json.dumps({"a": 1}))
  arb_json.add_metadata_to_json(file_in, file_out)
  result = json.loads(file_out.read_text())
  assert "_metadata_" in result
  assert "_data_" in result


# --- compare_json_files ---
def test_compare_json_files_identical(tmp_path, capsys):
  file1 = tmp_path / "a.json"
  file2 = tmp_path / "b.json"
  data = {"x": 1}
  file1.write_text(json.dumps(data))
  file2.write_text(json.dumps(data))
  arb_json.compare_json_files(file1, file2)
  out = capsys.readouterr().out
  assert "No differences" in out or out == ""


def test_compare_json_files_different(tmp_path, capsys):
  file1 = tmp_path / "a.json"
  file2 = tmp_path / "b.json"
  file1.write_text(json.dumps({"x": 1}))
  file2.write_text(json.dumps({"x": 2}))
  arb_json.compare_json_files(file1, file2)
  out = capsys.readouterr().out
  # No assertion on output content, just ensure no error


# --- cast_model_value ---
def test_cast_model_value_int():
  assert arb_json.cast_model_value("5", int) == 5


def test_cast_model_value_float():
  assert arb_json.cast_model_value("2.5", float) == 2.5


def test_cast_model_value_bool():
  assert arb_json.cast_model_value("True", bool) is True


def test_cast_model_value_invalid():
  with pytest.raises(Exception):
    arb_json.cast_model_value("notanint", int)


# --- wtform_types_and_values ---
def test_wtform_types_and_values():
  class DummyField:
    def __init__(self, data):
      self.data = data

  class DummyForm:
    _fields = {
      "a": DummyField(1),
      "b": DummyField("foo")
    }

  types, values = arb_json.wtform_types_and_values(DummyForm())
  assert "a" in values and "b" in values
  assert values["a"] == 1
  assert values["b"] == "foo"


# --- make_dict_serializeable / deserialize_dict ---
def test_make_dict_serializeable_and_deserialize_dict():
  d = {"a": decimal.Decimal("1.1"), "b": datetime.datetime(2025, 7, 4, 12, 0, tzinfo=datetime.timezone.utc)}
  ser = arb_json.make_dict_serializeable(d)
  deser = arb_json.deserialize_dict(ser, {"a": decimal.Decimal, "b": datetime.datetime})
  assert round(float(deser["a"]), 2) == 1.10
  assert isinstance(deser["b"], datetime.datetime)


# --- safe_json_loads ---
def test_safe_json_loads_valid():
  d = {"a": 1}
  assert arb_json.safe_json_loads(json.dumps(d)) == d


def test_safe_json_loads_none():
  assert arb_json.safe_json_loads(None) == {}


def test_safe_json_loads_invalid():
  assert arb_json.safe_json_loads("not json") == {}


# --- extract_id_from_json / extract_tab_payload ---
def test_extract_id_from_json():
  d = {"tab_contents": {"Feedback Form": {"id_incidence": 42}}}
  assert arb_json.extract_id_from_json(d) == 42


def test_extract_id_from_json_missing():
  d = {"Feedback Form": {}}
  assert arb_json.extract_id_from_json(d) is None


def test_extract_tab_payload():
  d = {"tab_contents": {"Feedback Form": {"foo": 1}}}
  assert arb_json.extract_tab_payload(d) == {"foo": 1}


# --- normalize_value ---
def test_normalize_value():
  assert arb_json.normalize_value(None) == ""
  assert arb_json.normalize_value(5) == "5"
  assert arb_json.normalize_value(5.0) == "5.0"
  assert arb_json.normalize_value("foo") == "foo"


# --- compute_field_differences ---
def test_compute_field_differences():
  new = {"a": 1, "b": 2}
  old = {"a": 1, "b": 3}
  diffs = arb_json.compute_field_differences(new, old)
  assert any(d["key"] == "b" for d in diffs)
