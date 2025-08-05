import logging
import pprint
from unittest.mock import patch

import arb.logging.arb_logging as arb_logging


def test_get_pretty_printer_basic():
  pp, pp_log = arb_logging.get_pretty_printer()
  data = {"foo": [1, 2, 3], "bar": {"baz": "qux"}}
  result = pp_log(data)
  assert isinstance(result, str)
  assert "foo" in result and "bar" in result
  assert isinstance(pp, pprint.PrettyPrinter)


def test_get_pretty_printer_kwargs():
  _, pp_log = arb_logging.get_pretty_printer(indent=4, width=40)
  data = {"a": [1, 2, 3]}
  result = pp_log(data)
  assert result.startswith("{")


def test_resolve_log_dir_creates_dir(tmp_path):
  with patch("arb.logging.arb_logging.get_project_root_dir", return_value=tmp_path):
    log_dir = arb_logging._resolve_log_dir("logs", app_dir_structure=["foo"])
    assert log_dir.exists()
    assert log_dir.name == "logs"


def test_setup_standalone_logging_prints(monkeypatch, tmp_path):
  with patch("arb.logging.arb_logging.get_project_root_dir", return_value=tmp_path):
    monkeypatch.setattr(logging, "basicConfig", lambda **kwargs: None)
    with patch("builtins.print") as mock_print:
      arb_logging.setup_standalone_logging("testlog", log_dir="logs", app_dir_structure=["foo"])
      assert mock_print.called


def test_setup_app_logging_prints(monkeypatch, tmp_path):
  with patch("arb.logging.arb_logging.get_project_root_dir", return_value=tmp_path):
    monkeypatch.setattr(logging, "basicConfig", lambda **kwargs: None)
    with patch("builtins.print") as mock_print:
      arb_logging.setup_app_logging("testlog", log_dir="logs", app_dir_structure=["foo"])
      assert mock_print.called
