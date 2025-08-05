"""
Comprehensive tests for arb.portal.utils.form_mapper

Covers all filter types, edge cases, error handling, and combinations for
apply_portal_update_filters using mocks for SQLAlchemy Query and model.
"""
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from arb.portal.utils import form_mapper
from arb.portal.utils.form_mapper import apply_portal_update_filters


@pytest.fixture
def mock_query():
  """Create a mock SQLAlchemy Query object."""
  return MagicMock(name="Query")


@pytest.fixture
def mock_portal_update_model():
  """Create a mock portal_update_model with required attributes."""
  model = MagicMock()
  # Simulate ORM columns for ilike, in_, between, >=, <=, etc.
  model.key.ilike = MagicMock(name="key.ilike")
  model.user.ilike = MagicMock(name="user.ilike")
  model.comments.ilike = MagicMock(name="comments.ilike")
  model.id_incidence.in_ = MagicMock(name="id_incidence.in_")
  model.id_incidence.between = MagicMock(name="id_incidence.between")
  model.id_incidence.__ge__ = MagicMock(name="id_incidence.__ge__")
  model.id_incidence.__le__ = MagicMock(name="id_incidence.__le__")
  model.timestamp.__ge__ = MagicMock(name="timestamp.__ge__")
  model.timestamp.__le__ = MagicMock(name="timestamp.__le__")
  return model


def test_apply_portal_update_filters_function_signature():
  """apply_portal_update_filters function has correct signature."""
  assert hasattr(form_mapper, 'apply_portal_update_filters')
  assert callable(form_mapper.apply_portal_update_filters)


def test_no_filters_returns_original_query(mock_query, mock_portal_update_model):
  """No filters: returns original query object."""
  args = {}
  result = apply_portal_update_filters(mock_query, mock_portal_update_model, args)
  assert result == mock_query


def test_filter_key_applies_ilike(mock_query, mock_portal_update_model):
  args = {"filter_key": "abc"}
  mock_query.filter.return_value = "filtered_query"
  result = apply_portal_update_filters(mock_query, mock_portal_update_model, args)
  mock_portal_update_model.key.ilike.assert_called_once_with("%abc%")
  mock_query.filter.assert_called_once()
  assert result == "filtered_query"


def test_filter_user_applies_ilike(mock_query, mock_portal_update_model):
  args = {"filter_user": "bob"}
  mock_query.filter.return_value = "filtered_query"
  result = apply_portal_update_filters(mock_query, mock_portal_update_model, args)
  mock_portal_update_model.user.ilike.assert_called_once_with("%bob%")
  mock_query.filter.assert_called_once()
  assert result == "filtered_query"


def test_filter_comments_applies_ilike(mock_query, mock_portal_update_model):
  args = {"filter_comments": "note"}
  mock_query.filter.return_value = "filtered_query"
  result = apply_portal_update_filters(mock_query, mock_portal_update_model, args)
  mock_portal_update_model.comments.ilike.assert_called_once_with("%note%")
  mock_query.filter.assert_called_once()
  assert result == "filtered_query"


def test_filter_id_incidence_exact_and_range(mock_query, mock_portal_update_model):
  args = {"filter_id_incidence": "123,100-200,300-400,-250,abc,500-xyz,222,300-"}
  mock_query.filter.return_value = mock_query
  from unittest.mock import patch
  with patch("arb.portal.utils.form_mapper.or_", return_value=MagicMock(name="or_clause")) as mock_or_:
    result = apply_portal_update_filters(mock_query, mock_portal_update_model, args)
    mock_portal_update_model.id_incidence.in_.assert_called_once_with([123, 222])
    mock_portal_update_model.id_incidence.between.assert_any_call(100, 200)
    mock_portal_update_model.id_incidence.between.assert_any_call(300, 400)
    mock_portal_update_model.id_incidence.__le__.assert_any_call(250)
    mock_portal_update_model.id_incidence.__ge__.assert_any_call(300)
    assert mock_query.filter.call_count >= 1
    assert result == mock_query


def test_filter_id_incidence_empty_and_invalid(mock_query, mock_portal_update_model):
  args = {"filter_id_incidence": "abc,,--,xyz-"}
  result = apply_portal_update_filters(mock_query, mock_portal_update_model, args)
  # No valid filters, so no calls to in_, between, etc.
  mock_portal_update_model.id_incidence.in_.assert_not_called()
  mock_portal_update_model.id_incidence.between.assert_not_called()
  mock_portal_update_model.id_incidence.__le__.assert_not_called()
  mock_portal_update_model.id_incidence.__ge__.assert_not_called()
  # Should not call filter
  mock_query.filter.assert_not_called()
  assert result == mock_query


def test_filter_id_incidence_open_ended(mock_query, mock_portal_update_model):
  args = {"filter_id_incidence": "-100,200-"}
  mock_query.filter.return_value = mock_query
  from unittest.mock import patch
  with patch("arb.portal.utils.form_mapper.or_", return_value=MagicMock(name="or_clause")) as mock_or_:
    result = apply_portal_update_filters(mock_query, mock_portal_update_model, args)
    mock_portal_update_model.id_incidence.__le__.assert_called_once_with(100)
    mock_portal_update_model.id_incidence.__ge__.assert_called_once_with(200)
    assert result == mock_query


def test_filter_id_incidence_spaces_and_commas(mock_query, mock_portal_update_model):
  args = {"filter_id_incidence": " 123 , 456-789 , -100 , 200- ", "filter_key": "foo"}
  mock_query.filter.return_value = mock_query
  from unittest.mock import patch
  with patch("arb.portal.utils.form_mapper.or_", return_value=MagicMock(name="or_clause")) as mock_or_:
    result = apply_portal_update_filters(mock_query, mock_portal_update_model, args)
    mock_portal_update_model.id_incidence.in_.assert_called_once_with([123])
    mock_portal_update_model.id_incidence.between.assert_any_call(456, 789)
    mock_portal_update_model.id_incidence.__le__.assert_any_call(100)
    mock_portal_update_model.id_incidence.__ge__.assert_any_call(200)
    assert result == mock_query


def test_filter_date_range_valid(mock_query, mock_portal_update_model):
  args = {"start_date": "2024-07-01", "end_date": "2024-07-10"}
  mock_query.filter.return_value = mock_query
  result = apply_portal_update_filters(mock_query, mock_portal_update_model, args)
  # Check that timestamp >= and <= were called with correct datetimes
  mock_portal_update_model.timestamp.__ge__.assert_called_once()
  mock_portal_update_model.timestamp.__le__.assert_called_once()
  start_dt = mock_portal_update_model.timestamp.__ge__.call_args[0][0]
  end_dt = mock_portal_update_model.timestamp.__le__.call_args[0][0]
  assert isinstance(start_dt, datetime)
  assert isinstance(end_dt, datetime)
  assert start_dt.strftime("%Y-%m-%d") == "2024-07-01"
  assert end_dt.strftime("%Y-%m-%d") == "2024-07-10"
  assert end_dt.hour == 23 and end_dt.minute == 59 and end_dt.second == 59
  assert result == mock_query


def test_filter_date_range_invalid(mock_query, mock_portal_update_model):
  args = {"start_date": "not-a-date", "end_date": "2024-07-10"}
  mock_query.filter.return_value = mock_query
  # Should ignore both dates if either is invalid due to single try block
  result = apply_portal_update_filters(mock_query, mock_portal_update_model, args)
  mock_portal_update_model.timestamp.__ge__.assert_not_called()
  mock_portal_update_model.timestamp.__le__.assert_not_called()
  assert result == mock_query


def test_filter_date_range_missing(mock_query, mock_portal_update_model):
  args = {"start_date": "", "end_date": ""}
  result = apply_portal_update_filters(mock_query, mock_portal_update_model, args)
  mock_portal_update_model.timestamp.__ge__.assert_not_called()
  mock_portal_update_model.timestamp.__le__.assert_not_called()
  assert result == mock_query


def test_combined_filters_all_types(mock_query, mock_portal_update_model):
  args = {
    "filter_key": "abc",
    "filter_user": "bob",
    "filter_comments": "note",
    "filter_id_incidence": "123,100-200",
    "start_date": "2024-07-01",
    "end_date": "2024-07-10"
  }
  mock_query.filter.return_value = mock_query
  from unittest.mock import patch
  with patch("arb.portal.utils.form_mapper.or_", return_value=MagicMock(name="or_clause")) as mock_or_:
    result = apply_portal_update_filters(mock_query, mock_portal_update_model, args)
    mock_portal_update_model.key.ilike.assert_called_once_with("%abc%")
    mock_portal_update_model.user.ilike.assert_called_once_with("%bob%")
    mock_portal_update_model.comments.ilike.assert_called_once_with("%note%")
    mock_portal_update_model.id_incidence.in_.assert_called_once_with([123])
    mock_portal_update_model.id_incidence.between.assert_any_call(100, 200)
    mock_portal_update_model.timestamp.__ge__.assert_called_once()
    mock_portal_update_model.timestamp.__le__.assert_called_once()
    assert result == mock_query


def test_apply_portal_update_filters_handles_missing_args(mock_query, mock_portal_update_model):
  """Handles missing args dict gracefully."""
  result = apply_portal_update_filters(mock_query, mock_portal_update_model, {})
  assert result == mock_query
