import logging
from unittest.mock import MagicMock, patch

import pytest

import arb.utils.log_util as log_util


def test_log_function_parameters_basic(caplog):
  def dummy(a, b=2):
    log_util.log_function_parameters()
    return a + b

  with caplog.at_level(logging.DEBUG):
    result = dummy(1, b=3)
  assert "dummy(a=1, b=3)" in caplog.text
  assert result == 4


def test_log_function_parameters_custom_logger():
  logger = MagicMock()

  def dummy(x):
    log_util.log_function_parameters(logger=logger)

  dummy(5)
  logger.debug.assert_called()


def test_log_function_parameters_type_error():
  with pytest.raises(AttributeError):
    log_util.log_function_parameters(logger=123)


def test_log_parameters_decorator_logs(caplog):
  @log_util.log_parameters(print_to_console=False)
  def foo(x, y=2):
    return x + y

  with caplog.at_level(logging.DEBUG):
    result = foo(3, y=4)
  assert "foo(x=3, y=4)" in caplog.text
  assert result == 7


def test_log_parameters_decorator_custom_logger():
  logger = MagicMock()

  @log_util.log_parameters(logger=logger)
  def bar(z):
    return z

  bar(10)
  logger.debug.assert_called()


def test_log_parameters_type_error():
  with pytest.raises(AttributeError):
    @log_util.log_parameters(logger=123)
    def bad(x):
      return x

    bad(1)


def test_flask_user_context_filter_sets_user():
  filter_ = log_util.FlaskUserContextFilter()
  record = MagicMock()
  with patch("arb.utils.log_util.has_request_context", return_value=True), \
          patch("arb.utils.log_util.g", new=MagicMock(user="bob")):
    filter_.filter(record)
    assert record.user == "bob"


def test_flask_user_context_filter_no_user():
  filter_ = log_util.FlaskUserContextFilter()
  record = MagicMock()
  with patch("arb.utils.log_util.has_request_context", return_value=False):
    filter_.filter(record)
    assert record.user == "n/a"
