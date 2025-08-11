"""
Core upload logic functions extracted from Flask routes for unit testing.

This module contains the business logic for file uploads, separated from the Flask
route handlers to enable unit testing without browser automation.

Phase 8: Core Logic Extraction - COMPLETED
- Extracted business logic from routes.py upload functions
- Uses existing backend functions without modification
- Provides unified interface for both direct and staged uploads
- Enables Phase 9 (Unified Processing Pipeline) and Phase 10 (Route Consolidation)
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
from werkzeug.datastructures import FileStorage
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import AutomapBase

from arb.portal.config.accessors import get_upload_folder
from arb.portal.utils.db_ingest_util import (
    upload_and_update_db,  # Used by working upload_file route
    upload_and_stage_only,  # Used by working upload_file_staged route
    upload_and_process_file,  # Used by refactored upload_file_refactored route
    stage_uploaded_file_for_review  # Used by refactored upload_file_staged_refactored route
)
from arb.portal.utils.result_types import UploadResult, StagingResult

logger = logging.getLogger(__name__)


@dataclass
class UploadLogicResult:
    """Standardized result format for upload logic functions."""
    success: bool
    status_code: int
    flash_messages: List[str]
    redirect_url: Optional[str]
    validation_errors: Optional[Dict[str, Any]]
    processed_data: Optional[Dict[str, Any]]
    error_message: Optional[str] = None
    error_type: Optional[str] = None


def upload_file_logic(
    db: SQLAlchemy,
    upload_folder: Union[str, Path],
    request_file: FileStorage,
    base: AutomapBase
) -> UploadLogicResult:
    """
    Core logic for uploading a file (original implementation).
    
    This function extracts the business logic from the upload_file route
    without modifying the working backend function upload_and_update_db().
    
    Args:
        db: SQLAlchemy database instance
        upload_folder: Directory where files should be uploaded
        request_file: File uploaded via Flask request
        base: SQLAlchemy automap base for database reflection
        
    Returns:
        UploadLogicResult with the result of the upload operation
    """
    try:
        logger.info(f"Processing upload for file: {request_file.filename}")
        
        # Use the existing working backend function without modification
        file_path, id_, sector = upload_and_update_db(db, upload_folder, request_file, base)
        
        if id_:
            # Upload successful - redirect to incidence update
            return UploadLogicResult(
                success=True,
                status_code=200,
                flash_messages=["File uploaded successfully"],
                redirect_url=f"/incidence_update/{id_}",
                validation_errors=None,
                processed_data={
                    "filename": file_path.name if file_path else None,
                    "id_incidence": id_,
                    "sector": sector,
                    "file_path": str(file_path) if file_path else None
                }
            )
        else:
            # Upload blocked - missing or invalid id_incidence
            return UploadLogicResult(
                success=False,
                status_code=400,
                flash_messages=["Upload blocked: missing or invalid id_incidence"],
                redirect_url=None,
                validation_errors={"id_incidence": "missing or invalid"},
                processed_data={
                    "filename": file_path.name if file_path else None,
                    "file_path": str(file_path) if file_path else None
                },
                error_message="This file is missing a valid 'Incidence/Emission ID' (id_incidence). Please add a positive integer id_incidence to your spreadsheet before uploading.",
                error_type="missing_id"
            )
        
    except Exception as e:
        logger.error(f"Error in upload_file_logic: {e}")
        return UploadLogicResult(
            success=False,
            status_code=500,
            flash_messages=[f"Upload failed: {str(e)}"],
            redirect_url=None,
            validation_errors={"error": str(e)},
            processed_data=None,
            error_message=str(e),
            error_type="processing_error"
        )


def upload_file_refactored_logic(
    db: SQLAlchemy,
    upload_folder: Union[str, Path],
    request_file: FileStorage,
    base: AutomapBase
) -> UploadLogicResult:
    """
    Core logic for uploading a file (refactored implementation).
    
    This function extracts the business logic from the upload_file_refactored route
    without modifying the working backend function upload_and_process_file().
    
    Args:
        db: SQLAlchemy database instance
        upload_folder: Directory where files should be uploaded
        request_file: File uploaded via Flask request
        base: SQLAlchemy automap base for database reflection
        
    Returns:
        UploadLogicResult with the result of the upload operation
    """
    try:
        logger.info(f"Processing refactored upload for file: {request_file.filename}")
        
        # Use the existing working backend function without modification
        result: UploadResult = upload_and_process_file(db, upload_folder, request_file, base)
        
        if result.success:
            # Upload successful - redirect to incidence update
            return UploadLogicResult(
                success=True,
                status_code=200,
                flash_messages=["File uploaded successfully"],
                redirect_url=f"/incidence_update/{result.id_}",
                validation_errors=None,
                processed_data={
                    "filename": result.file_path.name if result.file_path else None,
                    "id_incidence": result.id_,
                    "sector": result.sector,
                    "file_path": str(result.file_path) if result.file_path else None
                }
            )
        else:
            # Handle specific error types based on the result
            return UploadLogicResult(
                success=False,
                status_code=400,
                flash_messages=[f"Upload failed: {result.error_type}"],
                redirect_url=None,
                validation_errors={result.error_type: result.error_message},
                processed_data={
                    "filename": result.file_path.name if result.file_path else None,
                    "file_path": str(result.file_path) if result.file_path else None,
                    "error_type": result.error_type
                },
                error_message=result.error_message,
                error_type=result.error_type
            )
        
    except Exception as e:
        logger.error(f"Error in upload_file_refactored_logic: {e}")
        return UploadLogicResult(
            success=False,
            status_code=500,
            flash_messages=[f"Upload failed: {str(e)}"],
            redirect_url=None,
            validation_errors={"error": str(e)},
            processed_data=None,
            error_message=str(e),
            error_type="processing_error"
        )


def upload_file_staged_logic(
    db: SQLAlchemy,
    upload_folder: Union[str, Path],
    request_file: FileStorage,
    base: AutomapBase
) -> UploadLogicResult:
    """
    Core logic for staging a file for review (original implementation).
    
    This function extracts the business logic from the upload_file_staged route
    without modifying the working backend function upload_and_stage_only().
    
    Args:
        db: SQLAlchemy database instance
        upload_folder: Directory where files should be uploaded
        request_file: File uploaded via Flask request
        base: SQLAlchemy automap base for database reflection
        
    Returns:
        UploadLogicResult with the result of the staging operation
    """
    try:
        logger.info(f"Processing staged upload for file: {request_file.filename}")
        
        # Use the existing working backend function without modification
        file_path, id_, sector, json_data, staged_filename = upload_and_stage_only(db, upload_folder, request_file, base)
        
        if id_ and staged_filename:
            # Staging successful - redirect to review page
            return UploadLogicResult(
                success=True,
                status_code=200,
                flash_messages=["File staged for review successfully"],
                redirect_url=f"/review_staged/{id_}/{staged_filename}",
                validation_errors=None,
                processed_data={
                    "filename": file_path.name if file_path else None,
                    "id_incidence": id_,
                    "sector": sector,
                    "staged_filename": staged_filename,
                    "file_path": str(file_path) if file_path else None
                }
            )
        else:
            # Staging blocked - missing or invalid id_incidence
            return UploadLogicResult(
                success=False,
                status_code=400,
                flash_messages=["Staging blocked: missing or invalid id_incidence"],
                redirect_url=None,
                validation_errors={"id_incidence": "missing or invalid"},
                processed_data={
                    "filename": file_path.name if file_path else None,
                    "file_path": str(file_path) if file_path else None
                },
                error_message="This file is missing a valid 'Incidence/Emission ID' (id_incidence). Please add a positive integer id_incidence to your spreadsheet before uploading.",
                error_type="missing_id"
            )
        
    except Exception as e:
        logger.error(f"Error in upload_file_staged_logic: {e}")
        return UploadLogicResult(
            success=False,
            status_code=500,
            flash_messages=[f"Staging failed: {str(e)}"],
            redirect_url=None,
            validation_errors={"error": str(e)},
            processed_data=None,
            error_message=str(e),
            error_type="processing_error"
        )


def upload_file_staged_refactored_logic(
    db: SQLAlchemy,
    upload_folder: Union[str, Path],
    request_file: FileStorage,
    base: AutomapBase
) -> UploadLogicResult:
    """
    Core logic for staging a file for review (refactored implementation).
    
    This function extracts the business logic from the upload_file_staged_refactored route
    without modifying the working backend function stage_uploaded_file_for_review().
    
    Args:
        db: SQLAlchemy database instance
        upload_folder: Directory where files should be uploaded
        request_file: File uploaded via Flask request
        base: SQLAlchemy automap base for database reflection
        
    Returns:
        UploadLogicResult with the result of the staging operation
    """
    try:
        logger.info(f"Processing refactored staged upload for file: {request_file.filename}")
        
        # Use the existing working backend function without modification
        result: StagingResult = stage_uploaded_file_for_review(db, upload_folder, request_file, base)
        
        if result.success:
            # Staging successful - redirect to review page
            return UploadLogicResult(
                success=True,
                status_code=200,
                flash_messages=["File staged for review successfully"],
                redirect_url=f"/review_staged/{result.id_}/{result.staged_filename}",
                validation_errors=None,
                processed_data={
                    "filename": result.file_path.name if result.file_path else None,
                    "id_incidence": result.id_,
                    "sector": result.sector,
                    "staged_filename": result.staged_filename,
                    "file_path": str(result.file_path) if result.file_path else None
                }
            )
        else:
            # Handle specific error types based on the result
            return UploadLogicResult(
                success=False,
                status_code=400,
                flash_messages=[f"Staging failed: {result.error_type}"],
                redirect_url=None,
                validation_errors={result.error_type: result.error_message},
                processed_data={
                    "filename": result.file_path.name if result.file_path else None,
                    "file_path": str(result.file_path) if result.file_path else None,
                    "error_type": result.error_type
                },
                error_message=result.error_message,
                error_type=result.error_type
            )
        
    except Exception as e:
        logger.error(f"Error in upload_file_staged_refactored_logic: {e}")
        return UploadLogicResult(
            success=False,
            status_code=500,
            flash_messages=[f"Staging failed: {str(e)}"],
            redirect_url=None,
            validation_errors={"error": str(e)},
            processed_data=None,
            error_message=str(e),
            error_type="processing_error"
        )


def get_upload_folder_logic() -> Path:
    """
    Get the upload folder path using the existing configuration accessor.
    
    Returns:
        Path to the upload folder
    """
    return get_upload_folder()

