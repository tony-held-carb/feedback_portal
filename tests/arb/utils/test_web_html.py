import pytest
from unittest.mock import MagicMock, patch
import arb.utils.web_html as web_html

def test_upload_single_file(tmp_path):
    file_storage = MagicMock()
    file_storage.filename = "test.txt"
    file_storage.save = MagicMock()
    with patch("arb.utils.web_html.get_secure_timestamped_file_name", return_value=tmp_path/"secure.txt"):
        result = web_html.upload_single_file(tmp_path, file_storage)
    file_storage.save.assert_called()
    assert result.name == "secure.txt"

def test_upload_single_file_no_filename():
    file_storage = MagicMock()
    file_storage.filename = ""
    with pytest.raises(ValueError):
        web_html.upload_single_file("/tmp", file_storage)

def test_upload_single_file_none_filename():
    file_storage = MagicMock()
    file_storage.filename = None
    with pytest.raises(ValueError):
        web_html.upload_single_file("/tmp", file_storage)

def test_selector_list_to_tuples():
    result = web_html.selector_list_to_tuples(["Red", "Green"])
    assert result[0][0] == "Please Select"
    assert ("Red", "Red") in result
    assert ("Green", "Green") in result
    assert web_html.selector_list_to_tuples([])[0][0] == "Please Select"

def test_selector_list_to_tuples_empty_list():
    result = web_html.selector_list_to_tuples([])
    assert len(result) == 1
    assert result[0][0] == "Please Select"
    # The first element is a 3-tuple with disabled dict
    assert len(result[0]) == 3
    assert result[0][2]["disabled"] is True

def test_selector_list_to_tuples_single_item():
    result = web_html.selector_list_to_tuples(["Single"])
    assert len(result) == 2
    assert result[0][0] == "Please Select"
    assert result[1] == ("Single", "Single")

def test_list_to_triple_tuple():
    result = web_html.list_to_triple_tuple(["A", "B"])
    assert result == [("A", "A", {}), ("B", "B", {})]
    assert web_html.list_to_triple_tuple([]) == []

def test_list_to_triple_tuple_empty_list():
    result = web_html.list_to_triple_tuple([])
    assert result == []

def test_list_to_triple_tuple_single_item():
    result = web_html.list_to_triple_tuple(["Single"])
    assert result == [("Single", "Single", {})]

def test_update_triple_tuple_dict():
    tuples = [("A", "A", {}), ("B", "B", {})]
    match_list = ["A"]
    match_update = {"disabled": True}
    unmatch_update = {"class": "available"}
    result = web_html.update_triple_tuple_dict(tuples, match_list, match_update, unmatch_update)
    assert result[0][2]["disabled"] is True
    assert result[1][2]["class"] == "available"

def test_update_triple_tuple_dict_empty_list():
    result = web_html.update_triple_tuple_dict([], ["A"], {"disabled": True})
    assert result == []

def test_update_triple_tuple_dict_empty_match_list():
    tuples = [("A", "A", {}), ("B", "B", {})]
    result = web_html.update_triple_tuple_dict(tuples, [], {"disabled": True}, {"class": "default"})
    assert result[0][2]["class"] == "default"
    assert result[1][2]["class"] == "default"

def test_update_triple_tuple_dict_none_unmatch_update():
    tuples = [("A", "A", {}), ("B", "B", {})]
    result = web_html.update_triple_tuple_dict(tuples, ["A"], {"disabled": True}, None)
    assert result[0][2]["disabled"] is True
    assert result[1][2] == {}

def test_update_selector_dict():
    d = {"colors": ["Red", "Blue"]}
    result = web_html.update_selector_dict(d)
    assert "colors" in result
    assert result["colors"][0][0] == "Please Select"
    assert ("Red", "Red") in result["colors"]
    assert ("Blue", "Blue") in result["colors"]

def test_update_selector_dict_empty_dict():
    result = web_html.update_selector_dict({})
    assert result == {}

def test_ensure_placeholder_option():
    tuples = [("A", "A", {}), ("B", "B", {})]
    result = web_html.ensure_placeholder_option(tuples)
    assert result[0][0] == "Please Select"
    assert result[0][2]["disabled"] is True
    assert ("A", "A", {}) in result
    assert ("B", "B", {}) in result

def test_ensure_placeholder_option_custom_item():
    tuples = [("A", "A", {}), ("B", "B", {})]
    result = web_html.ensure_placeholder_option(tuples, item="Custom", item_dict={"selected": True})
    assert result[0][0] == "Custom"
    assert result[0][2]["selected"] is True

def test_ensure_placeholder_option_ensure_first_false():
    tuples = [("A", "A", {}), ("B", "B", {})]
    result = web_html.ensure_placeholder_option(tuples, ensure_first=False)
    # Should still be first due to default behavior
    assert result[0][0] == "Please Select"

def test_ensure_placeholder_option_empty_list():
    result = web_html.ensure_placeholder_option([])
    assert len(result) == 1
    assert result[0][0] == "Please Select"

def test_remove_items_single_string():
    tuples = [("A", "A", {}), ("B", "B", {}), ("C", "C", {})]
    result = web_html.remove_items(tuples, "B")
    assert len(result) == 2
    assert ("A", "A", {}) in result
    assert ("C", "C", {}) in result
    assert ("B", "B", {}) not in result

def test_remove_items_list():
    tuples = [("A", "A", {}), ("B", "B", {}), ("C", "C", {})]
    result = web_html.remove_items(tuples, ["A", "C"])
    assert len(result) == 1
    assert result[0] == ("B", "B", {})

def test_remove_items_empty_list():
    tuples = [("A", "A", {}), ("B", "B", {})]
    result = web_html.remove_items(tuples, [])
    assert result == tuples

def test_remove_items_empty_tuples():
    result = web_html.remove_items([], "A")
    assert result == []

def test_remove_items_item_not_found():
    tuples = [("A", "A", {}), ("B", "B", {})]
    result = web_html.remove_items(tuples, "C")
    assert result == tuples

def test_run_diagnostics(caplog):
    """Test the run_diagnostics function."""
    web_html.run_diagnostics()
    # Check that diagnostics ran without errors
    # The function prints to stdout, so we can't easily capture it in tests
    # But we can verify it doesn't raise any exceptions
    assert True  # If we get here, no exceptions were raised 