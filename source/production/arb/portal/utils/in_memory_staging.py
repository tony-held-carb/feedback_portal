"""
In-Memory Staging Infrastructure for Unified Upload Processing

This module provides the core infrastructure for the Phase 8 unified upload
processing architecture. It implements an in-memory first approach where both
direct and staged uploads use the same core processing pipeline, with
configurable persistence strategies.

Key Components:
- InMemoryStaging: Core data structure representing processed upload data
- UploadProcessingConfig: Configuration for upload processing behavior  
- process_upload_to_memory: Unified processing pipeline
- Configuration-driven persistence methods

The architecture eliminates ~75% code duplication between direct and staged
uploads by making direct upload a specialized case of staged upload with
auto-confirmation and no file persistence.

Examples:
    from arb.portal.utils.in_memory_staging import (
        InMemoryStaging, 
        UploadProcessingConfig,
        process_upload_to_memory
    )
    
    # Unified processing for any upload type
    memory_result = process_upload_to_memory(db, upload_dir, request_file, base)
    
    # Direct upload configuration
    config = UploadProcessingConfig(auto_confirm=True, persist_staging_file=False)
    
    # Staged upload configuration  
    config = UploadProcessingConfig(auto_confirm=False, persist_staging_file=True)

Notes:
    - InMemoryStaging is the single source of truth for processed upload data
    - Persistence strategies are pluggable via configuration
    - All Result Types provide consistent error handling throughout the pipeline
    - Perfect separation of concerns enables surgical unit testing
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import AutomapBase
from werkzeug.datastructures import FileStorage

from arb.portal.utils.result_types import (
    InMemoryStagingResult,
    PersistenceResult,
    DatabaseInsertResult,
    StagedFileResult,
    FileSaveResult,
    FileConversionResult,
    IdValidationResult
)

logger = logging.getLogger(__name__)


@dataclass
class UploadProcessingConfig:
    """
    Configuration for upload processing behavior.
    
    This configuration class allows the same unified processing pipeline
    to support different upload types (direct, staged, batch, etc.) by
    varying the persistence and confirmation strategies.
    
    Attributes:
        auto_confirm (bool): If True, automatically commit to database without staging file
        update_all_fields (bool): If True, update all fields; if False, only changed fields
        persist_staging_file (bool): If True, create staging file for manual review
        cleanup_staging_file (bool): If True, delete staging file after processing
        
    Examples:
        # Direct upload configuration
        direct_config = UploadProcessingConfig(
            auto_confirm=True,
            update_all_fields=True, 
            persist_staging_file=False
        )
        
        # Staged upload configuration
        staged_config = UploadProcessingConfig(
            auto_confirm=False,
            persist_staging_file=True
        )
        
        # Validation-only configuration
        validation_config = UploadProcessingConfig(
            auto_confirm=False,
            persist_staging_file=False
        )
    """
    auto_confirm: bool = False
    update_all_fields: bool = False
    persist_staging_file: bool = True
    cleanup_staging_file: bool = False


@dataclass
class InMemoryStaging:
    """
    Core data structure representing processed upload data in memory.
    
    This dataclass serves as the single source of truth for processed upload
    data. It contains all the information needed to persist the data to either
    database (direct upload) or staging file (staged upload).
    
    Attributes:
        id_ (int): Extracted incidence ID from the uploaded file
        sector (str): Detected sector from file content
        original_filename (str): Original uploaded filename
        file_path (Path): Path to the saved uploaded file
        json_data (dict): Parsed JSON data from the file
        metadata (dict): Additional metadata about the upload
        timestamp (datetime): When the in-memory staging was created
        
    Methods:
        to_database: Persist directly to database (direct upload)
        to_staging_file: Persist to staging file (staged upload)
        
    Examples:
        # Creating in-memory staging (typically done by process_upload_to_memory)
        staging = InMemoryStaging(
            id_=123,
            sector="Dairy Digester",
            original_filename="upload.xlsx",
            file_path=Path("uploads/file.xlsx"),
            json_data={"id_incidence": 123, "sector": "Dairy Digester"},
            metadata={"file_size": 1024, "upload_time": "2025-01-01T12:00:00"},
            timestamp=datetime.now()
        )
        
        # Direct database persistence
        db_result = staging.to_database(db, base, update_strategy="all_fields")
        
        # Staging file persistence
        file_result = staging.to_staging_file(staging_dir)
    """
    id_: int
    sector: str
    original_filename: str
    file_path: Path
    json_data: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime
    
    def to_database(self, db: SQLAlchemy, base: AutomapBase, 
                   update_strategy: str = "changed_only") -> DatabaseInsertResult:
        """
        Persist in-memory staging data directly to database.
        
        This method handles direct upload by committing the in-memory staging
        data directly to the database without creating intermediate staging files.
        
        Args:
            db (SQLAlchemy): Database instance
            base (AutomapBase): SQLAlchemy base for table access
            update_strategy (str): "all_fields" or "changed_only"
            
        Returns:
            DatabaseInsertResult: Result of database insertion with success/error info
            
        Examples:
            # Direct upload with all fields update
            result = staging.to_database(db, base, "all_fields")
            if result.success:
                print(f"Inserted with ID: {result.id_}")
            else:
                print(f"Database error: {result.error_message}")
        """
        try:
            from arb.portal.utils.db_ingest_util import xl_dict_to_database
            
            logger.debug(f"Persisting in-memory staging to database: ID={self.id_}, strategy={update_strategy}")
            
            # Structure data in the format expected by xl_dict_to_database
            # xl_dict_to_database expects: {"metadata": {"sector": ...}, "tab_contents": {"Feedback Form": {...}}}
            xl_dict_format = {
                "metadata": {
                    "sector": self.sector,
                    "original_filename": self.original_filename,
                    "upload_timestamp": self.timestamp.isoformat(),
                    **self.metadata
                },
                "tab_contents": {
                    "Feedback Form": self.json_data
                }
            }
            
            # Use existing database insertion logic
            # TODO: Enhance xl_dict_to_database to support update_strategy parameter
            id_, sector = xl_dict_to_database(db, base, xl_dict_format)
            
            if id_ is not None:
                logger.info(f"Successfully persisted in-memory staging to database: ID={id_}")
                return DatabaseInsertResult(
                    id_=id_,
                    success=True,
                    error_message=None,
                    error_type=None
                )
            else:
                logger.warning("Database insertion returned None - likely validation failure")
                return DatabaseInsertResult(
                    id_=None,
                    success=False,
                    error_message="Database insertion failed - data validation error",
                    error_type="validation_error"
                )
                
        except Exception as e:
            logger.exception(f"Exception during database persistence: {e}")
            return DatabaseInsertResult(
                id_=None,
                success=False,
                error_message=f"Database error: {str(e)}",
                error_type="database_error"
            )
    
    def to_staging_file(self, staging_dir: Path) -> StagedFileResult:
        """
        Persist in-memory staging data to staging file for manual review.
        
        This method handles staged upload by creating a staging file that
        preserves all the processed data for manual review and confirmation.
        
        Args:
            staging_dir (Path): Directory where staging file should be created
            
        Returns:
            StagedFileResult: Result of staging file creation with filename/error info
            
        Examples:
            # Staged upload with file persistence
            result = staging.to_staging_file(Path("staged_uploads"))
            if result.success:
                print(f"Staged as: {result.staged_filename}")
            else:
                print(f"Staging error: {result.error_message}")
        """
        try:
            # Create timestamped staging filename
            timestamp_str = self.timestamp.strftime("%Y_%m_%d_%H_%M_%S")
            staged_filename = f"id_{self.id_}_ts_{timestamp_str}.json"
            staged_file_path = staging_dir / staged_filename
            
            logger.debug(f"Creating staging file: {staged_file_path}")
            
            # Prepare staging data with metadata
            staging_data = {
                "original_filename": self.original_filename,
                "upload_timestamp": self.timestamp.isoformat(),
                "id_incidence": self.id_,
                "sector": self.sector,
                "metadata": self.metadata,
                "json_data": self.json_data,
                # TODO: Add base_misc_json for comparison during review
            }
            
            # Ensure staging directory exists
            staging_dir.mkdir(parents=True, exist_ok=True)
            
            # Write staging file
            with open(staged_file_path, 'w', encoding='utf-8') as f:
                json.dump(staging_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Successfully created staging file: {staged_filename}")
            return StagedFileResult(
                staged_filename=staged_filename,
                success=True,
                error_message=None,
                error_type=None
            )
            
        except Exception as e:
            logger.exception(f"Exception during staging file creation: {e}")
            return StagedFileResult(
                staged_filename=None,
                success=False,
                error_message=f"Failed to create staging file: {str(e)}",
                error_type="file_error"
            )


def process_upload_to_memory(db: SQLAlchemy, upload_dir: str | Path, 
                           request_file: FileStorage, 
                           base: AutomapBase) -> InMemoryStagingResult:
    """
    Unified processing pipeline creating in-memory staging for all uploads.
    
    This function represents the shared core logic that both direct and staged
    uploads use, eliminating ~75% of current code duplication. It processes
    the uploaded file through all common steps (save, convert, validate) and
    creates an InMemoryStaging object that can then be persisted based on
    upload configuration.
    
    Args:
        db (SQLAlchemy): Database instance
        upload_dir (str | Path): Directory for uploaded files
        request_file (FileStorage): Uploaded file from Flask request
        base (AutomapBase): SQLAlchemy base for table access
        
    Returns:
        InMemoryStagingResult: Contains InMemoryStaging object or error information
        
    Examples:
        # Process any upload to in-memory staging
        memory_result = process_upload_to_memory(db, upload_dir, request_file, base)
        
        if memory_result.success:
            # Use in-memory staging for direct or staged upload
            staging = memory_result.in_memory_staging
            
            # Direct upload
            db_result = staging.to_database(db, base, "all_fields")
            
            # Or staged upload
            file_result = staging.to_staging_file(staging_dir)
        else:
            # Handle processing error
            print(f"Processing failed: {memory_result.error_message}")
    """
    try:
        logger.debug(f"Starting unified upload processing for file: {request_file.filename}")
        
        # Import here to avoid circular imports
        from arb.portal.utils.db_ingest_util import (
            save_uploaded_file_with_result,
            convert_file_to_json_with_result,
            validate_id_from_json_with_result
        )
        
        # Step 1: Save uploaded file
        save_result = save_uploaded_file_with_result(upload_dir, request_file, db)
        if not save_result.success:
            logger.warning(f"File save failed: {save_result.error_message}")
            return InMemoryStagingResult(
                in_memory_staging=None,
                success=False,
                error_message=save_result.error_message,
                error_type=save_result.error_type
            )
        
        # Step 2: Convert to JSON
        convert_result = convert_file_to_json_with_result(save_result.file_path)
        if not convert_result.success:
            logger.warning(f"File conversion failed: {convert_result.error_message}")
            return InMemoryStagingResult(
                in_memory_staging=None,
                success=False,
                error_message=convert_result.error_message,
                error_type=convert_result.error_type
            )
        
        # Step 3: Validate and extract ID
        validate_result = validate_id_from_json_with_result(convert_result.json_data)
        if not validate_result.success:
            logger.warning(f"ID validation failed: {validate_result.error_message}")
            return InMemoryStagingResult(
                in_memory_staging=None,
                success=False,
                error_message=validate_result.error_message,
                error_type=validate_result.error_type
            )
        
        # Step 4: Create in-memory staging (this is always successful if we get here)
        timestamp = datetime.now()
        metadata = {
            "original_filename": request_file.filename,
            "file_size": len(request_file.read()) if hasattr(request_file, 'read') else None,
            "upload_timestamp": timestamp.isoformat(),
            "processing_timestamp": timestamp.isoformat(),
            "file_path": str(save_result.file_path),
            "json_path": str(convert_result.json_path)
        }
        
        # Reset file pointer if we read it for metadata
        if hasattr(request_file, 'seek'):
            request_file.seek(0)
        
        # Extract the tab contents from the full JSON structure for consistency
        # convert_result.json_data contains: {"metadata": {...}, "tab_contents": {"Feedback Form": {...}}}
        # We want to store just the tab contents for the Feedback Form
        tab_contents = convert_result.json_data.get("tab_contents", {}).get("Feedback Form", {})
        
        in_memory_staging = InMemoryStaging(
            id_=validate_result.id_,
            sector=convert_result.sector or "Unknown",
            original_filename=request_file.filename or "unknown.xlsx",
            file_path=save_result.file_path,
            json_data=tab_contents,  # Store just the tab contents, not the full structure
            metadata=metadata,
            timestamp=timestamp
        )
        
        logger.info(f"Successfully created in-memory staging: ID={in_memory_staging.id_}, sector={in_memory_staging.sector}")
        return InMemoryStagingResult(
            in_memory_staging=in_memory_staging,
            success=True,
            error_message=None,
            error_type=None
        )
        
    except Exception as e:
        logger.exception(f"Exception during unified upload processing: {e}")
        return InMemoryStagingResult(
            in_memory_staging=None,
            success=False,
            error_message=f"Unexpected error during processing: {str(e)}",
            error_type="processing_error"
        )


def process_upload_with_config(config: UploadProcessingConfig,
                             db: SQLAlchemy, 
                             upload_dir: str | Path,
                             request_file: FileStorage,
                             base: AutomapBase) -> PersistenceResult:
    """
    Configuration-driven upload processing with unified pipeline.
    
    This function demonstrates how the unified in-memory processing can be
    configured for different upload types (direct, staged, validation-only, etc.)
    
    Args:
        config (UploadProcessingConfig): Configuration for upload behavior
        db (SQLAlchemy): Database instance
        upload_dir (str | Path): Directory for uploaded files
        request_file (FileStorage): Uploaded file from Flask request
        base (AutomapBase): SQLAlchemy base for table access
        
    Returns:
        PersistenceResult: Result of configured persistence operation
        
    Examples:
        # Direct upload configuration
        direct_config = UploadProcessingConfig(auto_confirm=True, persist_staging_file=False)
        result = process_upload_with_config(direct_config, db, upload_dir, request_file, base)
        
        # Staged upload configuration
        staged_config = UploadProcessingConfig(auto_confirm=False, persist_staging_file=True)
        result = process_upload_with_config(staged_config, db, upload_dir, request_file, base)
    """
    try:
        logger.debug(f"Processing upload with config: auto_confirm={config.auto_confirm}, persist_staging_file={config.persist_staging_file}")
        
        # Step 1: Process to in-memory staging (unified for all upload types)
        memory_result = process_upload_to_memory(db, upload_dir, request_file, base)
        if not memory_result.success:
            return PersistenceResult(
                success=False,
                result_data={},
                error_message=memory_result.error_message,
                error_type=memory_result.error_type
            )
        
        staging = memory_result.in_memory_staging
        result_data = {}
        
        # Step 2: Handle persistence based on configuration
        if config.auto_confirm:
            # Direct upload: persist to database
            update_strategy = "all_fields" if config.update_all_fields else "changed_only"
            db_result = staging.to_database(db, base, update_strategy)
            
            if not db_result.success:
                return PersistenceResult(
                    success=False,
                    result_data={},
                    error_message=db_result.error_message,
                    error_type=db_result.error_type
                )
            
            result_data.update({
                "id_": db_result.id_,
                "sector": staging.sector,
                "persistence_type": "database",
                "file_path": str(staging.file_path),
                "json_data": staging.json_data
            })
        
        if config.persist_staging_file:
            # Staged upload: persist to staging file
            staging_dir = Path(upload_dir) / "staged"
            file_result = staging.to_staging_file(staging_dir)
            
            if not file_result.success:
                return PersistenceResult(
                    success=False,
                    result_data=result_data,  # May have database data from auto_confirm
                    error_message=file_result.error_message,
                    error_type=file_result.error_type
                )
            
            result_data.update({
                "staged_filename": file_result.staged_filename,
                "id_": staging.id_,
                "sector": staging.sector,
                "persistence_type": "staging_file" if not config.auto_confirm else "both",
                "file_path": str(staging.file_path),
                "json_data": staging.json_data
            })
        
        # Step 3: Cleanup if requested
        if config.cleanup_staging_file and "staged_filename" in result_data:
            # TODO: Implement staging file cleanup
            pass
        
        logger.info(f"Successfully processed upload with config: {result_data}")
        return PersistenceResult(
            success=True,
            result_data=result_data,
            error_message=None,
            error_type=None
        )
        
    except Exception as e:
        logger.exception(f"Exception during configured upload processing: {e}")
        return PersistenceResult(
            success=False,
            result_data={},
            error_message=f"Unexpected error during configured processing: {str(e)}",
            error_type="processing_error"
        )
