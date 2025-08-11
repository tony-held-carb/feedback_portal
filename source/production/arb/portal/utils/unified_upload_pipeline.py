"""
Unified Upload Processing Pipeline - Phase 9 Implementation.

This module implements Phase 9 of the upload refactor, providing a single,
configuration-driven processing pipeline that eliminates code duplication
between different upload types while maintaining full functionality.

Phase 9: Unified Processing Pipeline - COMPLETED
- Single processing pipeline for all upload types
- Configuration-driven behavior without code duplication
- Uses completed core logic functions from Phase 8
- Achieves significant code deduplication
- Enables Phase 10 (Route Consolidation)
"""

import logging
from pathlib import Path
from typing import Union, Optional, Dict, Any
from dataclasses import dataclass
from werkzeug.datastructures import FileStorage
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import AutomapBase

from arb.portal.upload_logic import (
    upload_file_logic,
    upload_file_refactored_logic,
    upload_file_staged_logic,
    upload_file_staged_refactored_logic,
    UploadLogicResult
)

logger = logging.getLogger(__name__)


@dataclass
class UnifiedUploadConfig:
    """
    Configuration for unified upload processing.
    
    This class extends the existing UploadConfiguration to support
    the unified processing pipeline with core logic function selection.
    """
    upload_type: str  # "direct" or "staged"
    template_name: str  # Template to render
    core_logic_function: str  # Which core logic function to use
    description: str  # Human-readable description
    is_refactored: bool  # Whether to use refactored logic
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.upload_type not in ["direct", "staged"]:
            raise ValueError(f"Invalid upload_type: {self.upload_type}. Must be 'direct' or 'staged'")
        
        if self.core_logic_function not in ["original", "refactored"]:
            raise ValueError(f"Invalid core_logic_function: {self.core_logic_function}. Must be 'original' or 'refactored'")
        
        # Validate logical consistency
        if self.upload_type == "staged" and self.core_logic_function == "original":
            if not hasattr(self, '_allow_staged_original'):
                logger.warning("Using original logic for staged uploads may not provide optimal error handling")


def get_core_logic_function(config: UnifiedUploadConfig):
    """
    Get the appropriate core logic function based on configuration.
    
    Args:
        config: UnifiedUploadConfig specifying the upload type and logic version
        
    Returns:
        Function reference to the appropriate core logic function
        
    Raises:
        ValueError: If configuration is invalid
    """
    if config.upload_type == "direct":
        if config.core_logic_function == "original":
            return upload_file_logic
        elif config.core_logic_function == "refactored":
            return upload_file_refactored_logic
        else:
            raise ValueError(f"Invalid core_logic_function for direct upload: {config.core_logic_function}")
    
    elif config.upload_type == "staged":
        if config.core_logic_function == "original":
            return upload_file_staged_logic
        elif config.core_logic_function == "refactored":
            return upload_file_staged_refactored_logic
        else:
            raise ValueError(f"Invalid core_logic_function for staged upload: {config.core_logic_function}")
    
    else:
        raise ValueError(f"Invalid upload_type: {config.upload_type}")


def process_upload_unified(
    db: SQLAlchemy,
    upload_folder: Union[str, Path],
    request_file: FileStorage,
    base: AutomapBase,
    config: UnifiedUploadConfig
) -> UploadLogicResult:
    """
    Unified upload processing pipeline for all upload types.
    
    This function provides a single, configuration-driven processing pipeline
    that eliminates code duplication between different upload types while
    maintaining full functionality and backward compatibility.
    
    Args:
        db: SQLAlchemy database instance
        upload_folder: Directory where files should be uploaded
        request_file: File uploaded via Flask request
        base: SQLAlchemy automap base for database reflection
        config: UnifiedUploadConfig specifying processing behavior
        
    Returns:
        UploadLogicResult with the result of the upload operation
        
    Examples:
        # Direct upload with original logic
        config = UnifiedUploadConfig(
            upload_type="direct",
            template_name="upload.html",
            core_logic_function="original",
            description="Direct upload using original logic",
            is_refactored=False
        )
        result = process_upload_unified(db, upload_folder, request_file, base, config)
        
        # Staged upload with refactored logic
        config = UnifiedUploadConfig(
            upload_type="staged",
            template_name="upload_staged.html",
            core_logic_function="refactored",
            description="Staged upload using refactored logic",
            is_refactored=True
        )
        result = process_upload_unified(db, upload_folder, request_file, base, config)
        
    Notes:
        - This function eliminates the need for separate processing logic in each route
        - All upload types use the same processing pipeline with configuration-driven behavior
        - Core logic functions are selected based on configuration, not hardcoded
        - Maintains full backward compatibility with existing functionality
        - Achieves significant code deduplication (target: 75%)
    """
    logger.info(f"Unified upload processing for {config.upload_type} upload using {config.core_logic_function} logic")
    
    try:
        # Get the appropriate core logic function based on configuration
        core_logic_func = get_core_logic_function(config)
        
        # Process the upload using the selected core logic function
        result = core_logic_func(db, upload_folder, request_file, base)
        
        # Log the result for debugging and monitoring
        if result.success:
            logger.info(f"Unified {config.upload_type} upload successful: {result.processed_data}")
        else:
            logger.warning(f"Unified {config.upload_type} upload failed: {result.error_type} - {result.error_message}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in unified upload processing: {e}")
        
        # Return a standardized error result
        return UploadLogicResult(
            success=False,
            status_code=500,
            flash_messages=[f"Unified upload processing failed: {str(e)}"],
            redirect_url=None,
            validation_errors={"processing_error": str(e)},
            processed_data=None,
            error_message=f"Unified upload processing error: {str(e)}",
            error_type="processing_error"
        )


def get_standard_configurations() -> Dict[str, UnifiedUploadConfig]:
    """
    Get standard configurations for common upload scenarios.
    
    Returns:
        Dictionary mapping configuration names to UnifiedUploadConfig instances
        
    Examples:
        configs = get_standard_configurations()
        direct_original = configs["direct_original"]
        staged_refactored = configs["staged_refactored"]
    """
    return {
        "direct_original": UnifiedUploadConfig(
            upload_type="direct",
            template_name="upload.html",
            core_logic_function="original",
            description="Direct upload using original logic (working route)",
            is_refactored=False
        ),
        
        "direct_refactored": UnifiedUploadConfig(
            upload_type="direct",
            template_name="upload.html",
            core_logic_function="refactored",
            description="Direct upload using refactored logic (enhanced error handling)",
            is_refactored=True
        ),
        
        "staged_original": UnifiedUploadConfig(
            upload_type="staged",
            template_name="upload_staged.html",
            core_logic_function="original",
            description="Staged upload using original logic (working route)",
            is_refactored=False
        ),
        
        "staged_refactored": UnifiedUploadConfig(
            upload_type="staged",
            template_name="upload_staged.html",
            core_logic_function="refactored",
            description="Staged upload using refactored logic (enhanced error handling)",
            is_refactored=True
        )
    }


def create_custom_configuration(
    upload_type: str,
    template_name: str,
    core_logic_function: str,
    description: str,
    is_refactored: bool
) -> UnifiedUploadConfig:
    """
    Create a custom upload configuration.
    
    Args:
        upload_type: Type of upload ("direct" or "staged")
        template_name: Template to render
        core_logic_function: Which core logic function to use ("original" or "refactored")
        description: Human-readable description
        is_refactored: Whether to use refactored logic
        
    Returns:
        UnifiedUploadConfig instance
        
    Examples:
        config = create_custom_configuration(
            upload_type="direct",
            template_name="custom_upload.html",
            core_logic_function="refactored",
            description="Custom direct upload with enhanced features",
            is_refactored=True
        )
    """
    return UnifiedUploadConfig(
        upload_type=upload_type,
        template_name=template_name,
        core_logic_function=core_logic_function,
        description=description,
        is_refactored=is_refactored
    )


def validate_configuration(config: UnifiedUploadConfig) -> tuple[bool, str | None]:
    """
    Validate a unified upload configuration.
    
    Args:
        config: UnifiedUploadConfig to validate
        
    Returns:
        tuple[bool, str | None]: (is_valid, error_message)
        - is_valid: True if configuration is valid, False otherwise
        - error_message: Error message if validation failed, None if successful
        
    Examples:
        is_valid, error = validate_configuration(config)
        if not is_valid:
            logger.error(f"Configuration validation failed: {error}")
    """
    try:
        # Test that the configuration can be used to get a core logic function
        core_logic_func = get_core_logic_function(config)
        
        # Verify the function exists and is callable
        if not callable(core_logic_func):
            return False, f"Core logic function is not callable: {core_logic_func}"
        
        # Validate template name (basic check)
        if not config.template_name or not isinstance(config.template_name, str):
            return False, "Template name must be a non-empty string"
        
        # Validate description
        if not config.description or not isinstance(config.description, str):
            return False, "Description must be a non-empty string"
        
        return True, None
        
    except Exception as e:
        return False, f"Configuration validation error: {str(e)}"


def get_configuration_summary() -> str:
    """
    Get a summary of all available configurations.
    
    Returns:
        String containing summary of all configurations
        
    Examples:
        summary = get_configuration_summary()
        print(summary)
    """
    configs = get_standard_configurations()
    
    summary = "Available Unified Upload Configurations:\n"
    summary += "=" * 50 + "\n"
    
    for name, config in configs.items():
        summary += f"\n{name}:\n"
        summary += f"  Upload Type: {config.upload_type}\n"
        summary += f"  Template: {config.template_name}\n"
        summary += f"  Logic: {config.core_logic_function}\n"
        summary += f"  Refactored: {config.is_refactored}\n"
        summary += f"  Description: {config.description}\n"
        summary += "-" * 30 + "\n"
    
    return summary
