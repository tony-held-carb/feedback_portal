"""
Tests for the result_types module.

This module tests the StagingResult and UploadResult named tuples
that were moved from db_ingest_util.py to their own module for better organization.
"""

from pathlib import Path

import pytest

from arb.portal.utils.result_types import StagingResult, UploadResult


class TestStagingResult:
  """Test the StagingResult named tuple."""

  def test_staging_result_creation(self):
    """StagingResult can be created with all required fields."""
    result = StagingResult(
      file_path=Path("test.xlsx"),
      id_=123,
      sector="Dairy Digester",
      json_data={"id_incidence": 123, "sector": "Dairy Digester"},
      staged_filename="id_123_ts_20250101_120000.json",
      success=True,
      error_message=None,
      error_type=None
    )

    assert result.file_path == Path("test.xlsx")
    assert result.id_ == 123
    assert result.sector == "Dairy Digester"
    assert result.json_data == {"id_incidence": 123, "sector": "Dairy Digester"}
    assert result.staged_filename == "id_123_ts_20250101_120000.json"
    assert result.success is True
    assert result.error_message is None
    assert result.error_type is None

  def test_staging_result_error_case(self):
    """StagingResult can represent error cases."""
    result = StagingResult(
      file_path=Path("test.xlsx"),
      id_=None,
      sector="Dairy Digester",
      json_data={"sector": "Dairy Digester"},
      staged_filename=None,
      success=False,
      error_message="No valid id_incidence found in spreadsheet",
      error_type="missing_id"
    )

    assert result.file_path == Path("test.xlsx")
    assert result.id_ is None
    assert result.sector == "Dairy Digester"
    assert result.json_data == {"sector": "Dairy Digester"}
    assert result.staged_filename is None
    assert result.success is False
    assert result.error_message == "No valid id_incidence found in spreadsheet"
    assert result.error_type == "missing_id"

  def test_staging_result_immutability(self):
    """StagingResult is immutable (NamedTuple)."""
    result = StagingResult(
      file_path=Path("test.xlsx"),
      id_=123,
      sector="Dairy Digester",
      json_data={},
      staged_filename="test.json",
      success=True,
      error_message=None,
      error_type=None
    )

    # Attempting to modify should raise an error
    with pytest.raises(AttributeError):
      result.success = False


class TestUploadResult:
  """Test the UploadResult named tuple."""

  def test_upload_result_creation(self):
    """UploadResult can be created with all required fields."""
    result = UploadResult(
      file_path=Path("test.xlsx"),
      id_=123,
      sector="Dairy Digester",
      success=True,
      error_message=None,
      error_type=None
    )

    assert result.file_path == Path("test.xlsx")
    assert result.id_ == 123
    assert result.sector == "Dairy Digester"
    assert result.success is True
    assert result.error_message is None
    assert result.error_type is None

  def test_upload_result_error_case(self):
    """UploadResult can represent error cases."""
    result = UploadResult(
      file_path=Path("test.xlsx"),
      id_=None,
      sector="Dairy Digester",
      success=False,
      error_message="Database error occurred during insertion",
      error_type="database_error"
    )

    assert result.file_path == Path("test.xlsx")
    assert result.id_ is None
    assert result.sector == "Dairy Digester"
    assert result.success is False
    assert result.error_message == "Database error occurred during insertion"
    assert result.error_type == "database_error"

  def test_upload_result_immutability(self):
    """UploadResult is immutable (NamedTuple)."""
    result = UploadResult(
      file_path=Path("test.xlsx"),
      id_=123,
      sector="Dairy Digester",
      success=True,
      error_message=None,
      error_type=None
    )

    # Attempting to modify should raise an error
    with pytest.raises(AttributeError):
      result.success = False


class TestResultTypesModule:
  """Test the result_types module as a whole."""

  def test_module_import(self):
    """The result_types module can be imported successfully."""
    from arb.portal.utils import result_types

    assert hasattr(result_types, 'StagingResult')
    assert hasattr(result_types, 'UploadResult')
    assert result_types.StagingResult is StagingResult
    assert result_types.UploadResult is UploadResult

  def test_result_types_documentation(self):
    """Result types have proper documentation."""
    assert StagingResult.__doc__ is not None
    assert UploadResult.__doc__ is not None
    assert "Result of staging an uploaded file" in StagingResult.__doc__
    assert "Result of processing an uploaded file" in UploadResult.__doc__
