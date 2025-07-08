"""
Unit tests for json.py (ARB Feedback Portal JSON utilities)

Coverage philosophy:
- All public functions are tested for normal, edge, and error cases.
- File I/O is tested using temporary files/directories to avoid side effects.
- Type safety, error handling, and contract compliance are verified.
- Tests are self-contained and do not require external dependencies beyond pytest and the standard library.

This suite provides strong confidence for current and future usage.
"""
import pytest
import tempfile
import shutil
import os
import decimal
import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from arb.utils import json as jsonmod

# --- json_serializer / json_deserializer ---
def test_json_serializer_and_deserializer_datetime():
    dt = datetime.datetime(2025, 1, 1, 12, 0, tzinfo=ZoneInfo("UTC"))
    ser = jsonmod.json_serializer(dt)
    assert ser["__type__"] == "datetime.datetime"
    deser = jsonmod.json_deserializer(ser)
    assert deser == dt

def test_json_serializer_and_deserializer_decimal():
    dec = decimal.Decimal("123.45")
    ser = jsonmod.json_serializer(dec)
    assert ser["__type__"] == "decimal.Decimal"
    deser = jsonmod.json_deserializer(ser)
    assert deser == dec

def test_json_serializer_type_error():
    class Foo: pass
    with pytest.raises(TypeError):
        jsonmod.json_serializer(Foo())

def test_json_deserializer_type_error():
    with pytest.raises(TypeError):
        jsonmod.json_deserializer({"__class__": "unknown"})

# --- json_save / json_load ---
def test_json_save_and_load(tmp_path):
    data = {"a": 1, "b": decimal.Decimal("2.5"), "dt": datetime.datetime(2025, 1, 1, 12, 0, tzinfo=ZoneInfo("UTC"))}
    file_path = tmp_path / "test.json"
    jsonmod.json_save(file_path, data)
    loaded = jsonmod.json_load(file_path)
    assert loaded["a"] == 1
    assert decimal.Decimal(str(loaded["b"])) == decimal.Decimal("2.5")
    assert "dt" in loaded

# --- json_save_with_meta / json_load_with_meta ---
def test_json_save_with_meta_and_load_with_meta(tmp_path):
    data = {"foo": "bar"}
    meta = {"source": "test"}
    file_path = tmp_path / "meta.json"
    jsonmod.json_save_with_meta(file_path, data, metadata=meta)
    loaded_data, loaded_meta = jsonmod.json_load_with_meta(file_path)
    assert loaded_data == data
    assert "source" in loaded_meta
    assert "File created at" in loaded_meta

# --- add_metadata_to_json ---
def test_add_metadata_to_json(tmp_path):
    data = {"x": 42}
    file_in = tmp_path / "plain.json"
    file_out = tmp_path / "meta.json"
    jsonmod.json_save(file_in, data)
    jsonmod.add_metadata_to_json(file_in, file_out)
    loaded_data, loaded_meta = jsonmod.json_load_with_meta(file_out)
    assert loaded_data == data
    assert "File created at" in loaded_meta

# --- compare_json_files (just check no error) ---
def test_compare_json_files(tmp_path):
    data1 = {"a": 1}
    data2 = {"a": 1}
    file1 = tmp_path / "f1.json"
    file2 = tmp_path / "f2.json"
    jsonmod.json_save(file1, data1)
    jsonmod.json_save(file2, data2)
    # Should not raise
    jsonmod.compare_json_files(file1, file2)

# --- cast_model_value ---
def test_cast_model_value_basic_types():
    assert jsonmod.cast_model_value("123", int) == 123
    assert jsonmod.cast_model_value("123.45", float) == 123.45
    assert jsonmod.cast_model_value("true", bool) is True or jsonmod.cast_model_value("True", bool) is True
    assert jsonmod.cast_model_value("foo", str) == "foo"
    assert jsonmod.cast_model_value("123.45", decimal.Decimal) == decimal.Decimal("123.45")

def test_cast_model_value_datetime():
    dt_str = "2025-01-01T12:00:00+00:00"
    dt = jsonmod.cast_model_value(dt_str, datetime.datetime)
    assert isinstance(dt, datetime.datetime)
    assert dt.tzinfo is not None

def test_cast_model_value_datetime_to_ca():
    dt_str = "2025-01-01T12:00:00+00:00"
    ca_dt = jsonmod.cast_model_value(dt_str, datetime.datetime, convert_time_to_ca=True)
    assert isinstance(ca_dt, datetime.datetime)
    assert ca_dt.tzinfo is None  # naive CA time

def test_cast_model_value_unsupported_type():
    with pytest.raises(ValueError):
        jsonmod.cast_model_value("foo", list)

def test_cast_model_value_invalid():
    with pytest.raises(ValueError):
        jsonmod.cast_model_value("notanint", int)

# --- wtform_types_and_values ---
class DummyField:
    def __init__(self, data):
        self.data = data
class DummyForm:
    def __init__(self):
        self._fields = {
            "a": DummyField(1),
            "b": DummyField("foo"),
        }
def test_wtform_types_and_values():
    form = DummyForm()
    type_map, field_data = jsonmod.wtform_types_and_values(form)
    assert "a" in type_map and "b" in type_map
    assert "a" in field_data and "b" in field_data

# --- make_dict_serializeable / deserialize_dict ---
def test_make_dict_serializeable_and_deserialize_dict():
    dt = datetime.datetime(2025, 1, 1, 12, 0)
    d = {"dt": dt, "n": decimal.Decimal("1.5"), "s": "foo"}
    type_map = {"dt": datetime.datetime, "n": decimal.Decimal, "s": str}
    ser = jsonmod.make_dict_serializeable(d, type_map)
    assert isinstance(ser["dt"], str)
    deser = jsonmod.deserialize_dict(ser, type_map)
    assert isinstance(deser["dt"], datetime.datetime)
    assert deser["n"] == decimal.Decimal("1.5")
    assert deser["s"] == "foo"

def test_make_dict_serializeable_type_error():
    with pytest.raises(TypeError):
        jsonmod.make_dict_serializeable({1: "badkey"})

def test_make_dict_serializeable_value_error():
    with pytest.raises(ValueError):
        jsonmod.make_dict_serializeable({"n": "notanumber"}, {"n": decimal.Decimal})

# --- safe_json_loads ---
def test_safe_json_loads_valid():
    d = {"a": 1}
    assert jsonmod.safe_json_loads(d) == d
    s = '{"a": 1}'
    assert jsonmod.safe_json_loads(s) == {"a": 1}

def test_safe_json_loads_empty():
    assert jsonmod.safe_json_loads("") == {}
    assert jsonmod.safe_json_loads(None) == {}

def test_safe_json_loads_invalid():
    assert jsonmod.safe_json_loads("notjson") == {}
    with pytest.raises(TypeError):
        jsonmod.safe_json_loads(123)

# --- extract_id_from_json / extract_tab_payload ---
def test_extract_id_from_json_and_tab_payload():
    json_data = {"tab_contents": {"Feedback Form": {"id_incidence": "42", "foo": "bar"}}}
    assert jsonmod.extract_id_from_json(json_data) == 42
    assert jsonmod.extract_tab_payload(json_data) == {"id_incidence": "42", "foo": "bar"}
    assert jsonmod.extract_id_from_json({}, tab_name="Missing") is None
    assert jsonmod.extract_tab_payload({}, tab_name="Missing") == {}

# --- normalize_value ---
def test_normalize_value():
    assert jsonmod.normalize_value(None) == ""
    assert jsonmod.normalize_value("") == ""
    dt = datetime.datetime(2025, 1, 1, 12, 0)
    assert "2025-01-01T12:00:00" in jsonmod.normalize_value(dt)
    assert jsonmod.normalize_value(123) == "123"

# --- compute_field_differences ---
def test_compute_field_differences():
    new = {"a": 1, "b": "foo"}
    old = {"a": 2, "b": "foo"}
    diffs = jsonmod.compute_field_differences(new, old)
    assert isinstance(diffs, list)
    assert any(d["changed"] for d in diffs)
    assert any(d["is_same"] for d in diffs) 