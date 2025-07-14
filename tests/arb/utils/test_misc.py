import pytest
import logging
import arb.utils.misc as misc

def test_get_nested_value_basic():
    d = {"a": {"b": {"c": 42}}, "x": 99}
    assert misc.get_nested_value(d, ("a", "b", "c")) == 42
    assert misc.get_nested_value(d, "x") == 99

def test_get_nested_value_missing_key():
    d = {"a": {"b": {}}}
    with pytest.raises(KeyError):
        misc.get_nested_value(d, ("a", "b", "c"))

def test_get_nested_value_type_error():
    d = {"a": 5}
    with pytest.raises(TypeError):
        misc.get_nested_value(d, ("a", "b"))

def test_get_nested_value_value_error():
    d = {"a": {}}
    with pytest.raises(KeyError):
        misc.get_nested_value(d, "b")

def test_ensure_key_value_pair_injects():
    d = {"a": {"x": 1}, "b": {}}
    defaults = {"b": 99}
    misc.ensure_key_value_pair(d, defaults, "x")
    assert d["b"]["x"] == 99

def test_ensure_key_value_pair_type_error():
    d = {"a": {}}
    defaults = {}
    with pytest.raises(TypeError):
        misc.ensure_key_value_pair(d, defaults, "x")

def test_replace_list_occurrences():
    l = ["cat", "dog", "bird"]
    lookup = {"dog": "puppy", "bird": "parrot"}
    misc.replace_list_occurrences(l, lookup)
    assert l == ["cat", "puppy", "parrot"]

def test_replace_list_occurrences_none():
    with pytest.raises(TypeError):
        misc.replace_list_occurrences(None, {"a": 1})

def test_args_to_string():
    assert misc.args_to_string(["--debug", "--log"]) == " --debug --log "
    assert misc.args_to_string(None) == ""
    assert misc.args_to_string([]) == ""

def test_log_error_logs_and_raises():
    logger = logging.getLogger("arb.utils.misc")
    with pytest.raises(ValueError):
        try:
            raise ValueError("bad value")
        except Exception as e:
            misc.log_error(e)

def test_safe_cast_basic():
    assert misc.safe_cast("5", int) == 5
    assert misc.safe_cast(5, int) == 5
    assert misc.safe_cast("3.2", float) == 3.2
    assert misc.safe_cast(None, str) == "None"

def test_safe_cast_value_error():
    with pytest.raises(ValueError):
        misc.safe_cast("foo", int)
    with pytest.raises(ValueError):
        misc.safe_cast("bar", None) 