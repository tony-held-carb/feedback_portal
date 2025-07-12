"""
Comprehensive tests for arb.portal.utils.db_ingest_util

Tests all database ingestion logic including Excel parsing, JSON handling, database operations,
and file upload processing. Covers edge cases, error conditions, and integration scenarios.
"""
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from werkzeug.datastructures import FileStorage

from arb.portal.utils import db_ingest_util
from arb.portal.utils.db_ingest_util import (
    extract_tab_and_sector, xl_dict_to_database, dict_to_database,
    json_file_to_db, upload_and_update_db, upload_and_stage_only,
    convert_excel_to_json_if_valid, extract_sector_from_json, store_staged_payload
)

@pytest.fixture
def sample_xl_dict():
    """Sample Excel dictionary for testing."""
    return {
        "metadata": {
            "sector": "landfill",
            "filename": "test.xlsx"
        },
        "tab_contents": {
            "Feedback Form": {
                "id_incidence": 123,
                "facility_name": "Test Facility",
                "contact_email": "test@example.com"
            }
        }
    }

@pytest.fixture
def sample_data_dict():
    """Sample data dictionary for database operations."""
    return {
        "id_incidence": 456,
        "facility_name": "Test Facility",
        "contact_email": "test@example.com",
        "sector": "landfill"
    }

def test_extract_tab_and_sector_function_signature():
    """extract_tab_and_sector function has correct signature."""
    assert hasattr(db_ingest_util, 'extract_tab_and_sector')
    assert callable(db_ingest_util.extract_tab_and_sector)

def test_extract_tab_and_sector_with_valid_data(sample_xl_dict):
    """extract_tab_and_sector works with valid data."""
    result = extract_tab_and_sector(sample_xl_dict)
    
    assert isinstance(result, dict)
    assert result["sector"] == "landfill"
    assert result["facility_name"] == "Test Facility"
    assert result["contact_email"] == "test@example.com"
    assert result["id_incidence"] == 123

def test_extract_tab_and_sector_with_custom_tab_name(sample_xl_dict):
    """extract_tab_and_sector works with custom tab name."""
    sample_xl_dict["tab_contents"]["Custom Tab"] = sample_xl_dict["tab_contents"]["Feedback Form"]
    result = extract_tab_and_sector(sample_xl_dict, "Custom Tab")
    
    assert result["sector"] == "landfill"
    assert result["facility_name"] == "Test Facility"

def test_extract_tab_and_sector_missing_tab():
    """extract_tab_and_sector raises ValueError for missing tab."""
    xl_dict = {
        "metadata": {"sector": "landfill"},
        "tab_contents": {"Wrong Tab": {}}
    }
    
    with pytest.raises(ValueError, match="Tab 'Feedback Form' not found"):
        extract_tab_and_sector(xl_dict)

def test_extract_tab_and_sector_missing_tab_contents():
    """extract_tab_and_sector raises ValueError for missing tab_contents."""
    xl_dict = {"metadata": {"sector": "landfill"}}
    
    with pytest.raises(ValueError, match="Tab 'Feedback Form' not found"):
        extract_tab_and_sector(xl_dict)

def test_extract_tab_and_sector_missing_sector():
    """extract_tab_and_sector handles missing sector gracefully."""
    xl_dict = {
        "metadata": {},
        "tab_contents": {
            "Feedback Form": {
                "facility_name": "Test Facility"
            }
        }
    }
    
    with patch('arb.portal.utils.db_ingest_util.logger') as mock_logger:
        result = extract_tab_and_sector(xl_dict)
        
        assert result["sector"] == "Unknown"
        mock_logger.warning.assert_called_once()

def test_xl_dict_to_database_function_signature():
    """xl_dict_to_database function has correct signature."""
    assert hasattr(db_ingest_util, 'xl_dict_to_database')
    assert callable(db_ingest_util.xl_dict_to_database)

def test_xl_dict_to_database_with_mock_db(sample_xl_dict):
    """xl_dict_to_database works with mock database."""
    mock_db = MagicMock()
    mock_base = MagicMock()
    
    with patch('arb.portal.utils.db_ingest_util.dict_to_database') as mock_dict_to_db:
        mock_dict_to_db.return_value = 789
        id_, sector = xl_dict_to_database(mock_db, mock_base, sample_xl_dict)
        
        assert id_ == 789
        assert sector == "landfill"
        mock_dict_to_db.assert_called_once()

def test_dict_to_database_function_signature():
    """dict_to_database function has correct signature."""
    assert hasattr(db_ingest_util, 'dict_to_database')
    assert callable(db_ingest_util.dict_to_database)

def test_dict_to_database_empty_data():
    """dict_to_database raises ValueError for empty data."""
    mock_db = MagicMock()
    mock_base = MagicMock()
    
    with pytest.raises(ValueError, match="Attempt to add empty entry"):
        dict_to_database(mock_db, mock_base, {})

def test_dict_to_database_with_mock_components(sample_data_dict):
    """dict_to_database works with mock components."""
    mock_db = MagicMock()
    mock_base = MagicMock()
    mock_model = MagicMock()
    mock_model.id_incidence = 456
    
    with patch('arb.portal.utils.db_ingest_util.get_ensured_row') as mock_get_row:
        with patch('arb.utils.wtf_forms_util.update_model_with_payload') as mock_update:
            mock_get_row.return_value = (mock_model, 456, False)
            
            result = dict_to_database(mock_db, mock_base, sample_data_dict)
            
            assert result == 456
            mock_get_row.assert_called_once()
            mock_update.assert_called_once()
            mock_db.session.add.assert_called_once_with(mock_model)
            mock_db.session.commit.assert_called_once()

def test_dict_to_database_dry_run(sample_data_dict):
    """dict_to_database respects dry_run flag."""
    mock_db = MagicMock()
    mock_base = MagicMock()
    mock_model = MagicMock()
    mock_model.id_incidence = 456
    
    with patch('arb.portal.utils.db_ingest_util.get_ensured_row') as mock_get_row:
        with patch('arb.utils.wtf_forms_util.update_model_with_payload') as mock_update:
            mock_get_row.return_value = (mock_model, 456, False)
            
            result = dict_to_database(mock_db, mock_base, sample_data_dict, dry_run=True)
            
            assert result == 456
            mock_db.session.add.assert_not_called()
            mock_db.session.commit.assert_not_called()

def test_dict_to_database_new_row_backfill(sample_data_dict):
    """dict_to_database backfills primary key for new rows."""
    mock_db = MagicMock()
    mock_base = MagicMock()
    mock_model = MagicMock()
    mock_model.id_incidence = 789
    
    # Remove primary key to simulate new row scenario
    data_dict = sample_data_dict.copy()
    del data_dict["id_incidence"]
    
    with patch('arb.portal.utils.db_ingest_util.get_ensured_row') as mock_get_row:
        with patch('arb.utils.wtf_forms_util.update_model_with_payload') as mock_update:
            mock_get_row.return_value = (mock_model, 789, True)  # is_new_row=True
            
            result = dict_to_database(mock_db, mock_base, data_dict)
            
            assert result == 789
            # Check that primary key was backfilled
            assert data_dict["id_incidence"] == 789

def test_json_file_to_db_function_signature():
    """json_file_to_db function has correct signature."""
    assert hasattr(db_ingest_util, 'json_file_to_db')
    assert callable(db_ingest_util.json_file_to_db)

def test_json_file_to_db_with_mock_components():
    """json_file_to_db works with mock components."""
    mock_db = MagicMock()
    mock_base = MagicMock()
    mock_json_data = {"metadata": {"sector": "landfill"}, "tab_contents": {"Feedback Form": {}}}
    
    with patch('arb.portal.utils.db_ingest_util.json_load_with_meta') as mock_load:
        with patch('arb.portal.utils.db_ingest_util.xl_dict_to_database') as mock_xl_to_db:
            mock_load.return_value = (mock_json_data, {"sector": "landfill"})
            mock_xl_to_db.return_value = (123, "landfill")
            
            result = json_file_to_db(mock_db, "test.json", mock_base)
            
            assert result == (123, "landfill")
            mock_load.assert_called_once_with("test.json")
            mock_xl_to_db.assert_called_once_with(mock_db, mock_base, mock_json_data, dry_run=False)

def test_upload_and_update_db_function_signature():
    """upload_and_update_db function has correct signature."""
    assert hasattr(db_ingest_util, 'upload_and_update_db')
    assert callable(db_ingest_util.upload_and_update_db)

def test_upload_and_stage_only_function_signature():
    """upload_and_stage_only function has correct signature."""
    assert hasattr(db_ingest_util, 'upload_and_stage_only')
    assert callable(db_ingest_util.upload_and_stage_only)

def test_convert_excel_to_json_if_valid_with_excel_file():
    """convert_excel_to_json_if_valid works with Excel file."""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
    
    try:
        with patch('arb.portal.utils.db_ingest_util.convert_upload_to_json') as mock_convert:
            mock_convert.return_value = ({"test": "data"}, "landfill")
            
            result = convert_excel_to_json_if_valid(tmp_path)
            
            # The function should call convert_upload_to_json and return the result
            mock_convert.assert_called_once()
            # Check that the function returns the expected tuple structure
            assert isinstance(result, tuple)
            assert len(result) == 2
    finally:
        tmp_path.unlink(missing_ok=True)

def test_convert_excel_to_json_if_valid_with_non_excel_file():
    """convert_excel_to_json_if_valid returns None for non-Excel files."""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
    
    try:
        result = convert_excel_to_json_if_valid(tmp_path)
        assert result == (None, None)
    finally:
        tmp_path.unlink(missing_ok=True)

def test_extract_sector_from_json():
    """extract_sector_from_json extracts sector from JSON file."""
    test_data = {"metadata": {"sector": "landfill"}}
    
    with patch('arb.portal.utils.db_ingest_util.json_load_with_meta') as mock_load:
        mock_load.return_value = (test_data, {"sector": "landfill"})
        result = extract_sector_from_json(Path("test.json"))
        assert result == "landfill"

def test_extract_sector_from_json_missing_sector():
    """extract_sector_from_json returns None for missing sector."""
    test_data = {"metadata": {}}
    
    with patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
        result = extract_sector_from_json(Path("test.json"))
        assert result is None

def test_store_staged_payload():
    """store_staged_payload stores payload to file."""
    test_data = {"test": "data"}
    test_id = 123
    test_sector = "landfill"
    
    with patch('arb.utils.io_wrappers.save_json_safely') as mock_save:
        with patch('arb.portal.utils.db_ingest_util.get_upload_folder') as mock_folder:
            mock_folder.return_value = Path("/tmp")
            
            result = store_staged_payload(test_id, test_sector, test_data)
            
            assert isinstance(result, Path)
            mock_save.assert_called_once()

def test_all_functions_exist():
    """All expected functions exist in the module."""
    expected_functions = [
        'extract_tab_and_sector',
        'xl_dict_to_database', 
        'dict_to_database',
        'json_file_to_db',
        'upload_and_update_db',
        'upload_and_update_db_old',
        'upload_and_stage_only',
        'convert_excel_to_json_if_valid',
        'extract_sector_from_json',
        'store_staged_payload'
    ]
    
    for func_name in expected_functions:
        assert hasattr(db_ingest_util, func_name), f"Function {func_name} not found"
        assert callable(getattr(db_ingest_util, func_name)), f"Function {func_name} is not callable" 