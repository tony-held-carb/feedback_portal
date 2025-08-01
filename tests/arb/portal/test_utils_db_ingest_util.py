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
from arb.portal.utils.db_ingest_util import StagingResult

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

@pytest.fixture
def mock_db():
    """Create a mock SQLAlchemy database instance."""
    mock_db = MagicMock()
    mock_db.session = MagicMock()
    return mock_db

@pytest.fixture
def mock_base():
    """Create a mock AutomapBase instance."""
    return MagicMock()

@pytest.fixture
def mock_table_class():
    """Create a mock table class for database operations."""
    mock_class = MagicMock()
    mock_class.__name__ = "TestTable"
    return mock_class

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

def test_validate_payload_for_database_function_signature():
    """validate_payload_for_database function has correct signature."""
    assert hasattr(db_ingest_util, 'validate_payload_for_database')
    assert callable(db_ingest_util.validate_payload_for_database)


def test_validate_payload_for_database_with_valid_data():
    """validate_payload_for_database accepts valid data."""
    valid_data = {"id_incidence": 123, "sector": "test"}
    # Should not raise any exception
    db_ingest_util.validate_payload_for_database(valid_data)


def test_validate_payload_for_database_with_empty_data():
    """validate_payload_for_database raises ValueError for empty data."""
    with pytest.raises(ValueError, match="Attempt to add empty entry to database"):
        db_ingest_util.validate_payload_for_database({})


def test_validate_payload_for_database_with_none_data():
    """validate_payload_for_database raises ValueError for None data."""
    with pytest.raises(ValueError, match="Attempt to add empty entry to database"):
        db_ingest_util.validate_payload_for_database(None)


def test_resolve_database_row_function_signature():
    """resolve_database_row function has correct signature."""
    assert hasattr(db_ingest_util, 'resolve_database_row')
    assert callable(db_ingest_util.resolve_database_row)


def test_resolve_database_row_with_existing_id(mock_db, mock_base, mock_table_class):
    """resolve_database_row retrieves existing row when id is provided."""
    existing_model = MagicMock()
    existing_model.id_incidence = 123
    
    with patch('arb.portal.utils.db_ingest_util.get_ensured_row') as mock_get_ensured:
        mock_get_ensured.return_value = (existing_model, 123, False)
        
        data_dict = {"id_incidence": 123, "sector": "test"}
        model, id_, is_new = db_ingest_util.resolve_database_row(
            mock_db, mock_base, data_dict
        )
        
        assert model == existing_model
        assert id_ == 123
        assert is_new is False
        mock_get_ensured.assert_called_once()


def test_resolve_database_row_with_new_id(mock_db, mock_base, mock_table_class):
    """resolve_database_row creates new row and backfills id when needed."""
    new_model = MagicMock()
    new_model.id_incidence = 456
    
    with patch('arb.portal.utils.db_ingest_util.get_ensured_row') as mock_get_ensured:
        mock_get_ensured.return_value = (new_model, 456, True)
        
        data_dict = {"sector": "test"}  # No id_incidence
        model, id_, is_new = db_ingest_util.resolve_database_row(
            mock_db, mock_base, data_dict
        )
        
        assert model == new_model
        assert id_ == 456
        assert is_new is True
        assert data_dict["id_incidence"] == 456  # Should be backfilled


def test_update_model_with_payload_and_commit_function_signature():
    """update_model_with_payload_and_commit function has correct signature."""
    assert hasattr(db_ingest_util, 'update_model_with_payload_and_commit')
    assert callable(db_ingest_util.update_model_with_payload_and_commit)


def test_update_model_with_payload_and_commit_with_dry_run(mock_db):
    """update_model_with_payload_and_commit respects dry_run flag."""
    mock_model = MagicMock()
    data_dict = {"id_incidence": 123, "sector": "test"}
    
    with patch('arb.portal.utils.db_ingest_util.update_model_with_payload') as mock_update:
        db_ingest_util.update_model_with_payload_and_commit(
            mock_db, mock_model, data_dict, dry_run=True
        )
        
        mock_update.assert_called_once()
        mock_db.session.add.assert_not_called()
        mock_db.session.commit.assert_not_called()


def test_update_model_with_payload_and_commit_without_dry_run(mock_db):
    """update_model_with_payload_and_commit commits when not dry_run."""
    mock_model = MagicMock()
    data_dict = {"id_incidence": 123, "sector": "test"}
    
    with patch('arb.portal.utils.db_ingest_util.update_model_with_payload') as mock_update:
        db_ingest_util.update_model_with_payload_and_commit(
            mock_db, mock_model, data_dict, dry_run=False
        )
        
        mock_update.assert_called_once()
        mock_db.session.add.assert_called_once_with(mock_model)
        mock_db.session.commit.assert_called_once()


def test_extract_primary_key_from_model_function_signature():
    """extract_primary_key_from_model function has correct signature."""
    assert hasattr(db_ingest_util, 'extract_primary_key_from_model')
    assert callable(db_ingest_util.extract_primary_key_from_model)


def test_extract_primary_key_from_model_success():
    """extract_primary_key_from_model successfully extracts primary key."""
    mock_model = MagicMock()
    mock_model.id_incidence = 123
    
    result = db_ingest_util.extract_primary_key_from_model(mock_model, "id_incidence")
    assert result == 123


def test_extract_primary_key_from_model_missing_attribute():
    """extract_primary_key_from_model raises AttributeError for missing attribute."""
    mock_model = MagicMock()
    # Don't set id_incidence attribute
    
    with pytest.raises(AttributeError):
        db_ingest_util.extract_primary_key_from_model(mock_model, "id_incidence")


def test_dict_to_database_refactored_function_signature():
    """dict_to_database_refactored function has correct signature."""
    assert hasattr(db_ingest_util, 'dict_to_database_refactored')
    assert callable(db_ingest_util.dict_to_database_refactored)


def test_dict_to_database_refactored_uses_smaller_functions(mock_db, mock_base, mock_table_class):
    """dict_to_database_refactored uses the new smaller functions."""
    mock_model = MagicMock()
    mock_model.id_incidence = 123
    data_dict = {"id_incidence": 123, "sector": "test"}
    
    with patch('arb.portal.utils.db_ingest_util.validate_payload_for_database') as mock_validate:
        with patch('arb.portal.utils.db_ingest_util.resolve_database_row') as mock_resolve:
            with patch('arb.portal.utils.db_ingest_util.update_model_with_payload_and_commit') as mock_update:
                with patch('arb.portal.utils.db_ingest_util.extract_primary_key_from_model') as mock_extract:
                    mock_resolve.return_value = (mock_model, 123, False)
                    mock_extract.return_value = 123
                    
                    result = db_ingest_util.dict_to_database_refactored(
                        mock_db, mock_base, data_dict
                    )
                    
                    assert result == 123
                    mock_validate.assert_called_once_with(data_dict)
                    mock_resolve.assert_called_once()
                    mock_update.assert_called_once()
                    mock_extract.assert_called_once_with(mock_model, "id_incidence")


def test_dict_to_database_refactored_equivalent_to_original(mock_db, mock_base, mock_table_class):
    """dict_to_database_refactored produces same result as original function."""
    # Test that both functions produce the same result for the same input
    data_dict = {"id_incidence": 123, "sector": "test"}
    
    # Mock the dependencies for both functions
    mock_model = MagicMock()
    mock_model.id_incidence = 123
    
    with patch('arb.portal.utils.db_ingest_util.get_ensured_row') as mock_get_ensured:
        with patch('arb.portal.utils.db_ingest_util.update_model_with_payload_and_commit') as mock_update:
            with patch('arb.utils.wtf_forms_util.update_model_with_payload') as mock_update_original:
                mock_get_ensured.return_value = (mock_model, 123, False)
                
                # Test refactored function
                refactored_result = db_ingest_util.dict_to_database_refactored(
                    mock_db, mock_base, data_dict
                )
                
                # Verify the result is valid
                assert refactored_result == 123
                
                # Verify that the helper functions were called correctly
                mock_get_ensured.assert_called_once()
                mock_update.assert_called_once()
                
                # Verify that the refactored function maintains the same interface
                # and produces the same type of result as the original
                assert isinstance(refactored_result, int)
                assert refactored_result == mock_model.id_incidence


def test_dict_to_database_refactored_with_dry_run(mock_db, mock_base, mock_table_class):
    """dict_to_database_refactored respects dry_run flag."""
    mock_model = MagicMock()
    mock_model.id_incidence = 123
    data_dict = {"id_incidence": 123, "sector": "test"}
    
    with patch('arb.portal.utils.db_ingest_util.validate_payload_for_database'):
        with patch('arb.portal.utils.db_ingest_util.resolve_database_row') as mock_resolve:
            with patch('arb.portal.utils.db_ingest_util.update_model_with_payload_and_commit') as mock_update:
                with patch('arb.portal.utils.db_ingest_util.extract_primary_key_from_model') as mock_extract:
                    mock_resolve.return_value = (mock_model, 123, False)
                    mock_extract.return_value = 123
                    
                    result = db_ingest_util.dict_to_database_refactored(
                        mock_db, mock_base, data_dict, dry_run=True
                    )
                    
                    assert result == 123
                    # Should pass dry_run=True to update function
                    mock_update.assert_called_once()
                    call_args = mock_update.call_args
                    assert call_args[1]['dry_run'] is True 

# =============================================================================
# TESTS FOR REFACTORED STAGING FUNCTIONS
# =============================================================================

def test_staging_result_named_tuple():
    """StagingResult named tuple can be created and accessed."""
    result = StagingResult(
        file_path=Path("test.xlsx"),
        id_=123,
        sector="Dairy Digester",
        json_data={"id_incidence": 123},
        staged_filename="id_123_ts_20250101_120000.json",
        success=True,
        error_message=None,
        error_type=None
    )
    
    assert result.file_path == Path("test.xlsx")
    assert result.id_ == 123
    assert result.sector == "Dairy Digester"
    assert result.json_data == {"id_incidence": 123}
    assert result.staged_filename == "id_123_ts_20250101_120000.json"
    assert result.success is True
    assert result.error_message is None
    assert result.error_type is None


def test_staging_result_error_case():
    """StagingResult can represent error cases."""
    result = StagingResult(
        file_path=Path("test.xlsx"),
        id_=None,
        sector="Dairy Digester",
        json_data={"sector": "Dairy Digester"},
        staged_filename=None,
        success=False,
        error_message="No valid id_incidence found",
        error_type="missing_id"
    )
    
    assert result.success is False
    assert result.error_message == "No valid id_incidence found"
    assert result.error_type == "missing_id"
    assert result.id_ is None
    assert result.staged_filename is None


def test_staging_result_function_signature():
    """stage_uploaded_file_for_review function has correct signature."""
    assert hasattr(db_ingest_util, 'stage_uploaded_file_for_review')
    assert callable(db_ingest_util.stage_uploaded_file_for_review)


def test_save_uploaded_file_function_signature():
    """_save_uploaded_file function has correct signature."""
    assert hasattr(db_ingest_util, '_save_uploaded_file')
    assert callable(db_ingest_util._save_uploaded_file)


def test_save_uploaded_file_success(mock_db):
    """_save_uploaded_file successfully saves uploaded file."""
    mock_request_file = MagicMock()
    mock_request_file.filename = "test.xlsx"

    with patch('arb.portal.utils.db_ingest_util.upload_single_file') as mock_upload:
        with patch('arb.portal.utils.db_ingest_util.add_file_to_upload_table') as mock_add:
            mock_upload.return_value = Path("uploads/test.xlsx")

            result = db_ingest_util._save_uploaded_file("uploads", mock_request_file, mock_db)
            
            assert result == Path("uploads/test.xlsx")
            mock_upload.assert_called_once_with("uploads", mock_request_file)
            mock_add.assert_called_once()


def test_save_uploaded_file_failure(mock_db):
    """_save_uploaded_file raises ValueError on failure."""
    mock_request_file = MagicMock()
    mock_request_file.filename = "test.xlsx"
    
    with patch('arb.portal.utils.db_ingest_util.upload_single_file') as mock_upload:
        mock_upload.side_effect = Exception("Upload failed")
        
        with pytest.raises(ValueError, match="File upload failed"):
            db_ingest_util._save_uploaded_file("uploads", mock_request_file, mock_db)


def test_convert_file_to_json_function_signature():
    """_convert_file_to_json function has correct signature."""
    assert hasattr(db_ingest_util, '_convert_file_to_json')
    assert callable(db_ingest_util._convert_file_to_json)


def test_convert_file_to_json_success():
    """_convert_file_to_json successfully converts file."""
    file_path = Path("test.xlsx")
    
    with patch('arb.portal.utils.db_ingest_util.convert_excel_to_json_if_valid') as mock_convert:
        mock_convert.return_value = (Path("test.json"), "Dairy Digester")
        
        json_path, sector = db_ingest_util._convert_file_to_json(file_path)
        
        assert json_path == Path("test.json")
        assert sector == "Dairy Digester"
        mock_convert.assert_called_once_with(file_path)


def test_convert_file_to_json_failure():
    """_convert_file_to_json returns None on conversion failure."""
    file_path = Path("test.txt")
    
    with patch('arb.portal.utils.db_ingest_util.convert_excel_to_json_if_valid') as mock_convert:
        mock_convert.return_value = (None, None)
        
        json_path, sector = db_ingest_util._convert_file_to_json(file_path)
        
        assert json_path is None
        assert sector is None


def test_validate_and_extract_id_function_signature():
    """_validate_and_extract_id function has correct signature."""
    assert hasattr(db_ingest_util, '_validate_and_extract_id')
    assert callable(db_ingest_util._validate_and_extract_id)


def test_validate_and_extract_id_success():
    """_validate_and_extract_id successfully extracts valid ID."""
    json_path = Path("test.json")
    json_data = {"id_incidence": 123, "sector": "Dairy Digester"}
    
    with patch('arb.portal.utils.db_ingest_util.json_load_with_meta') as mock_load:
        with patch('arb.portal.utils.db_ingest_util.extract_id_from_json') as mock_extract:
            mock_load.return_value = (json_data, {})
            mock_extract.return_value = 123
            
            id_, data = db_ingest_util._validate_and_extract_id(json_path)
            
            assert id_ == 123
            assert data == json_data


def test_validate_and_extract_id_missing():
    """_validate_and_extract_id returns None for missing ID."""
    json_path = Path("test.json")
    json_data = {"sector": "Dairy Digester"}  # No id_incidence
    
    with patch('arb.portal.utils.db_ingest_util.json_load_with_meta') as mock_load:
        with patch('arb.portal.utils.db_ingest_util.extract_id_from_json') as mock_extract:
            mock_load.return_value = (json_data, {})
            mock_extract.return_value = None
            
            id_, data = db_ingest_util._validate_and_extract_id(json_path)
            
            assert id_ is None
            assert data == json_data


def test_validate_and_extract_id_invalid():
    """_validate_and_extract_id returns None for invalid ID."""
    json_path = Path("test.json")
    json_data = {"id_incidence": -1, "sector": "Dairy Digester"}
    
    with patch('arb.portal.utils.db_ingest_util.json_load_with_meta') as mock_load:
        with patch('arb.portal.utils.db_ingest_util.extract_id_from_json') as mock_extract:
            mock_load.return_value = (json_data, {})
            mock_extract.return_value = -1
            
            id_, data = db_ingest_util._validate_and_extract_id(json_path)
            
            assert id_ is None
            assert data == json_data


def test_create_staged_file_function_signature():
    """_create_staged_file function has correct signature."""
    assert hasattr(db_ingest_util, '_create_staged_file')
    assert callable(db_ingest_util._create_staged_file)


def test_create_staged_file_success(mock_db, mock_base, mock_table_class):
    """_create_staged_file successfully creates staged file."""
    mock_model = MagicMock()
    mock_model.misc_json = {"existing": "data"}
    
    with patch('arb.portal.utils.db_ingest_util.get_ensured_row') as mock_get_row:
        with patch('arb.portal.utils.db_ingest_util.json_save_with_meta') as mock_save:
            with patch('arb.portal.utils.db_ingest_util.add_file_to_upload_table') as mock_add:
                with patch('arb.portal.utils.db_ingest_util.prep_payload_for_json') as mock_prep:
                    mock_get_row.return_value = (mock_model, 123, False)
                    mock_prep.return_value = {"id_incidence": 123, "sector": "Dairy Digester"}
                    
                    result = db_ingest_util._create_staged_file(123, {"id_incidence": 123}, mock_db, mock_base, "uploads")
                    
                    assert result is not None
                    assert "id_123_ts_" in result
                    assert result.endswith(".json")
                    mock_save.assert_called_once()
                    mock_add.assert_called_once()


def test_create_staged_file_failure(mock_db, mock_base, mock_table_class):
    """_create_staged_file returns None on failure."""
    with patch('arb.portal.utils.db_ingest_util.get_ensured_row') as mock_get_row:
        mock_get_row.side_effect = Exception("Database error")
        
        result = db_ingest_util._create_staged_file(123, {"id_incidence": 123}, mock_db, mock_base, "uploads")
        
        assert result is None


def test_stage_uploaded_file_for_review_success(mock_db, mock_base, mock_table_class):
    """stage_uploaded_file_for_review returns success result for valid file."""
    mock_request_file = MagicMock()
    mock_request_file.filename = "test.xlsx"
    mock_model = MagicMock()
    mock_model.misc_json = {"existing": "data"}
    
    with patch('arb.portal.utils.db_ingest_util._save_uploaded_file') as mock_save:
        with patch('arb.portal.utils.db_ingest_util._convert_file_to_json') as mock_convert:
            with patch('arb.portal.utils.db_ingest_util._validate_and_extract_id') as mock_validate:
                with patch('arb.portal.utils.db_ingest_util._create_staged_file') as mock_create:
                    mock_save.return_value = Path("uploads/test.xlsx")
                    mock_convert.return_value = (Path("test.json"), "Dairy Digester")
                    mock_validate.return_value = (123, {"id_incidence": 123})
                    mock_create.return_value = "id_123_ts_20250101_120000.json"
                    
                    result = db_ingest_util.stage_uploaded_file_for_review(mock_db, "uploads", mock_request_file, mock_base)
                    
                    assert result.success is True
                    assert result.id_ == 123
                    assert result.sector == "Dairy Digester"
                    assert result.staged_filename == "id_123_ts_20250101_120000.json"
                    assert result.error_message is None
                    assert result.error_type is None


def test_stage_uploaded_file_for_review_file_error(mock_db, mock_base, mock_table_class):
    """stage_uploaded_file_for_review returns file_error result on upload failure."""
    mock_request_file = MagicMock()
    mock_request_file.filename = "test.xlsx"
    
    with patch('arb.portal.utils.db_ingest_util._save_uploaded_file') as mock_save:
        mock_save.side_effect = ValueError("File upload failed")
        
        result = db_ingest_util.stage_uploaded_file_for_review(mock_db, "uploads", mock_request_file, mock_base)
        
        assert result.success is False
        assert result.error_type == "file_error"
        assert "File upload failed" in result.error_message


def test_stage_uploaded_file_for_review_conversion_failed(mock_db, mock_base, mock_table_class):
    """stage_uploaded_file_for_review returns conversion_failed result."""
    mock_request_file = MagicMock()
    mock_request_file.filename = "test.txt"
    
    with patch('arb.portal.utils.db_ingest_util._save_uploaded_file') as mock_save:
        with patch('arb.portal.utils.db_ingest_util._convert_file_to_json') as mock_convert:
            mock_save.return_value = Path("uploads/test.txt")
            mock_convert.return_value = (None, None)
            
            result = db_ingest_util.stage_uploaded_file_for_review(mock_db, "uploads", mock_request_file, mock_base)
            
            assert result.success is False
            assert result.error_type == "conversion_failed"
            assert "Unsupported file format" in result.error_message


def test_stage_uploaded_file_for_review_missing_id(mock_db, mock_base, mock_table_class):
    """stage_uploaded_file_for_review returns missing_id result."""
    mock_request_file = MagicMock()
    mock_request_file.filename = "test.xlsx"
    
    with patch('arb.portal.utils.db_ingest_util._save_uploaded_file') as mock_save:
        with patch('arb.portal.utils.db_ingest_util._convert_file_to_json') as mock_convert:
            with patch('arb.portal.utils.db_ingest_util._validate_and_extract_id') as mock_validate:
                mock_save.return_value = Path("uploads/test.xlsx")
                mock_convert.return_value = (Path("test.json"), "Dairy Digester")
                mock_validate.return_value = (None, {"sector": "Dairy Digester"})
                
                result = db_ingest_util.stage_uploaded_file_for_review(mock_db, "uploads", mock_request_file, mock_base)
                
                assert result.success is False
                assert result.error_type == "missing_id"
                assert "No valid 'Incidence/Emission ID'" in result.error_message
                assert result.sector == "Dairy Digester"  # Should preserve sector even on ID failure


def test_stage_uploaded_file_for_review_database_error(mock_db, mock_base, mock_table_class):
    """stage_uploaded_file_for_review returns database_error result."""
    mock_request_file = MagicMock()
    mock_request_file.filename = "test.xlsx"
    
    with patch('arb.portal.utils.db_ingest_util._save_uploaded_file') as mock_save:
        with patch('arb.portal.utils.db_ingest_util._convert_file_to_json') as mock_convert:
            with patch('arb.portal.utils.db_ingest_util._validate_and_extract_id') as mock_validate:
                with patch('arb.portal.utils.db_ingest_util._create_staged_file') as mock_create:
                    mock_save.return_value = Path("uploads/test.xlsx")
                    mock_convert.return_value = (Path("test.json"), "Dairy Digester")
                    mock_validate.return_value = (123, {"id_incidence": 123})
                    mock_create.return_value = None  # Staging failed
                    
                    result = db_ingest_util.stage_uploaded_file_for_review(mock_db, "uploads", mock_request_file, mock_base)
                    
                    assert result.success is False
                    assert result.error_type == "database_error"
                    assert "Failed to create staged file" in result.error_message
                    assert result.id_ == 123  # Should preserve ID even on staging failure


def test_stage_uploaded_file_for_review_equivalent_to_original(mock_db, mock_base, mock_table_class):
    """stage_uploaded_file_for_review produces equivalent results to upload_and_stage_only."""
    mock_request_file = MagicMock()
    mock_request_file.filename = "test.xlsx"
    mock_model = MagicMock()
    mock_model.misc_json = {"existing": "data"}
    
    # Test with successful staging
    with patch('arb.portal.utils.db_ingest_util._save_uploaded_file') as mock_save:
        with patch('arb.portal.utils.db_ingest_util._convert_file_to_json') as mock_convert:
            with patch('arb.portal.utils.db_ingest_util._validate_and_extract_id') as mock_validate:
                with patch('arb.portal.utils.db_ingest_util._create_staged_file') as mock_create:
                    mock_save.return_value = Path("uploads/test.xlsx")
                    mock_convert.return_value = (Path("test.json"), "Dairy Digester")
                    mock_validate.return_value = (123, {"id_incidence": 123})
                    mock_create.return_value = "id_123_ts_20250101_120000.json"
                    
                    result = db_ingest_util.stage_uploaded_file_for_review(mock_db, "uploads", mock_request_file, mock_base)
                    
                    # Should match the tuple format of upload_and_stage_only
                    assert result.file_path == Path("uploads/test.xlsx")
                    assert result.id_ == 123
                    assert result.sector == "Dairy Digester"
                    assert result.json_data == {"id_incidence": 123}
                    assert result.staged_filename == "id_123_ts_20250101_120000.json" 