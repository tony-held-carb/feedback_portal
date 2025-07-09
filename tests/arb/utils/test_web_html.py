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

def test_selector_list_to_tuples():
    result = web_html.selector_list_to_tuples(["Red", "Green"])
    assert result[0][0] == "Please Select"
    assert ("Red", "Red") in result
    assert ("Green", "Green") in result
    assert web_html.selector_list_to_tuples([])[0][0] == "Please Select"
    with pytest.raises(TypeError):
        web_html.selector_list_to_tuples(None)

def test_list_to_triple_tuple():
    result = web_html.list_to_triple_tuple(["A", "B"])
    assert result == [("A", "A", {}), ("B", "B", {})]
    assert web_html.list_to_triple_tuple([]) == []
    with pytest.raises(TypeError):
        web_html.list_to_triple_tuple(None)

def test_update_triple_tuple_dict():
    tuples = [("A", "A", {}), ("B", "B", {})]
    match_list = ["A"]
    match_update = {"disabled": True}
    unmatch_update = {"class": "available"}
    result = web_html.update_triple_tuple_dict(tuples, match_list, match_update, unmatch_update)
    assert result[0][2]["disabled"] is True
    assert result[1][2]["class"] == "available"

def test_update_selector_dict():
    d = {"colors": ["Red", "Blue"]}
    result = web_html.update_selector_dict(d)
    assert "colors" in result
    assert result["colors"][0][0] == "Please Select"
    assert ("Red", "Red") in result["colors"]
    assert ("Blue", "Blue") in result["colors"] 