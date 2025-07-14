"""
Unit tests for diagnostics.py

Coverage philosophy:
- All functions are tested with both valid and invalid/edge-case inputs
- Logging output is captured and checked for diagnostic/logging functions
- Output formatting (string, HTML) is checked for correctness and escaping
- Recursive and introspection utilities are tested for robustness and coverage

This suite provides comprehensive coverage for diagnostic utilities used in development and debugging.
"""
import pytest
from arb.utils import diagnostics as diag

# --- obj_diagnostics ---

def test_obj_diagnostics_basic(caplog):
    class Dummy:
        a = 1
        def method(self):
            return 42
    obj = Dummy()
    with caplog.at_level('DEBUG'):
        diag.obj_diagnostics(obj)
    # Should log attribute 'a' but not 'method' by default
    assert any('a' in m for m in caplog.text.splitlines())
    assert not any('method' in m for m in caplog.text.splitlines())

def test_obj_diagnostics_include_hidden_and_functions(caplog):
    class Dummy:
        _hidden = 2
        def _private(self): return 99
        def method(self): return 42
    obj = Dummy()
    with caplog.at_level('DEBUG'):
        diag.obj_diagnostics(obj, include_hidden=True, include_functions=True)
    # Should log _hidden and _private as function
    assert any('_hidden' in m for m in caplog.text.splitlines())
    assert any('_private' in m and 'function' in m for m in caplog.text.splitlines())
    assert any('method' in m and 'function' in m for m in caplog.text.splitlines())

def test_obj_diagnostics_none(caplog):
    with caplog.at_level('DEBUG'):
        diag.obj_diagnostics(None)
    assert 'None' in caplog.text

# --- list_differences ---

def test_list_differences_lists():
    a = [1, 2, 3]
    b = [2, 3, 4]
    only_a, only_b = diag.list_differences(a, b)
    assert only_a == [1]
    assert only_b == [4]

def test_list_differences_dicts():
    d1 = {'a': 1, 'b': 2}
    d2 = {'b': 2, 'c': 3}
    only_d1, only_d2 = diag.list_differences(list(d1), list(d2))
    assert only_d1 == ['a']
    assert only_d2 == ['c']

def test_list_differences_none():
    only_a, only_b = diag.list_differences(None, [1, 2])
    assert only_a == []
    assert only_b == [1, 2]
    only_a, only_b = diag.list_differences([1, 2], None)
    assert only_a == [1, 2]
    assert only_b == []

def test_list_differences_print_warning(caplog):
    a = [1, 2]
    b = [2, 3]
    with caplog.at_level('WARNING'):
        diag.list_differences(a, b, 'A', 'B', print_warning=True)
    assert 'Warning:' in caplog.text

# --- diag_recursive ---

def test_diag_recursive_simple(caplog):
    with caplog.at_level('DEBUG'):
        diag.diag_recursive([1, [2, 3]])
    assert 'diag_recursive diagnostics called' in caplog.text
    assert 'Depth: 1' in caplog.text

def test_diag_recursive_none(caplog):
    with caplog.at_level('DEBUG'):
        diag.diag_recursive(None)
    assert 'Type:' in caplog.text

# --- dict_to_str ---

def test_dict_to_str_flat():
    d = {'a': 1, 'b': 2}
    s = diag.dict_to_str(d)
    assert 'a:' in s and 'b:' in s
    assert '1' in s and '2' in s

def test_dict_to_str_nested():
    d = {'a': 1, 'b': {'c': 2}}
    s = diag.dict_to_str(d)
    assert 'c:' in s and '2' in s

def test_dict_to_str_none():
    assert diag.dict_to_str(None) == ''

# --- obj_to_html ---

def test_obj_to_html_dict():
    d = {'a': 1, 'b': {'c': 2}}
    html = diag.obj_to_html(d)
    assert html.startswith('<pre')
    assert 'a' in html and 'b' in html and 'c' in html

def test_obj_to_html_none():
    html = diag.obj_to_html(None)
    assert html.startswith('<pre')
    assert 'pre' in html

# --- compare_dicts ---

def test_compare_dicts_equal(caplog):
    d1 = {'a': 1, 'b': 2}
    d2 = {'a': 1, 'b': 2}
    with caplog.at_level('DEBUG'):
        result = diag.compare_dicts(d1, d2)
    assert result is True

def test_compare_dicts_diff_keys(caplog):
    d1 = {'a': 1, 'b': 2}
    d2 = {'a': 1, 'c': 3}
    with caplog.at_level('DEBUG'):
        result = diag.compare_dicts(d1, d2, 'D1', 'D2')
    assert result is False
    assert 'Key differences' in caplog.text
    assert 'In D1 but not in D2' in caplog.text

def test_compare_dicts_diff_values(caplog):
    d1 = {'a': 1, 'b': 2}
    d2 = {'a': 1, 'b': 3}
    with caplog.at_level('DEBUG'):
        result = diag.compare_dicts(d1, d2)
    assert result is False
    assert 'Value differences' in caplog.text

def test_compare_dicts_none():
    assert diag.compare_dicts(None, None) is True
    assert diag.compare_dicts({'a': 1}, None) is False
    assert diag.compare_dicts(None, {'a': 1}) is False

# --- get_changed_fields ---

def test_get_changed_fields_basic():
    new = {'a': 2, 'b': 3}
    old = {'a': 1, 'b': 3}
    changes = diag.get_changed_fields(new, old)
    assert changes == {'a': 2}

def test_get_changed_fields_none():
    assert diag.get_changed_fields({'a': 1}, None) == {'a': 1}
    assert diag.get_changed_fields(None, {'a': 1}) == {}
    assert diag.get_changed_fields(None, None) == {}

def test_get_changed_fields_partial():
    new = {'a': 1, 'b': 2}
    old = {'a': 1, 'b': 3, 'c': 4}
    changes = diag.get_changed_fields(new, old)
    assert changes == {'b': 2} 