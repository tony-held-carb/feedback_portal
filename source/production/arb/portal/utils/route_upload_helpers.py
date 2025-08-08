"""
Shared helper functions for upload routes.

This module contains helper functions that are shared between different upload routes
to eliminate code duplication and ensure consistent behavior.

Module_Attributes:
  logger (logging.Logger): Logger instance for this module.

Examples:
  from arb.portal.utils.route_upload_helpers import validate_upload_request
  result = validate_upload_request(request_file)
"""

import logging
from pathlib import Path
from typing import Union
from flask import Response, render_template, request
from werkzeug.datastructures import FileStorage

from arb.portal.wtf_upload import UploadForm

logger = logging.getLogger(__name__)


def validate_upload_request(request_file: FileStorage | None) -> tuple[bool, str | None]:
    """
    Validate that a file was uploaded in the request.

    Args:
        request_file: The uploaded file from the request

    Returns:
        tuple[bool, str | None]: (is_valid, error_message)
        - is_valid: True if file is valid, False otherwise
        - error_message: Error message if validation failed, None if successful

    Examples:
        is_valid, error = validate_upload_request(request_file)
        if not is_valid:
            return render_template('upload.html', form=form, upload_message=error)
    """
    if not request_file or not request_file.filename:
        logger.warning("POST received with no file selected.")
        return False, "No file selected. Please choose a file."
    
    return True, None


def get_error_message_for_type(error_type: str, result) -> str:
    """
    Get user-friendly error message for specific error types.

    Args:
        error_type: Type of error that occurred
        result: Result object containing error details

    Returns:
        str: User-friendly error message

    Examples:
        message = get_error_message_for_type("missing_id", result)
        return render_template('upload.html', form=form, upload_message=message)
    """
    if error_type == "missing_id":
        return (
            "This file is missing a valid 'Incidence/Emission ID' (id_incidence). "
            "Please add a positive integer id_incidence to your spreadsheet before uploading."
        )
    elif error_type == "conversion_failed":
        return "Unsupported file format. Please upload Excel (.xlsx) file."
    elif error_type == "file_error":
        return f"Error processing uploaded file: {result.error_message}"
    elif error_type == "database_error":
        return f"Database error occurred: {result.error_message}"
    else:
        return f"An unexpected error occurred: {result.error_message}"


def get_success_message_for_upload(result, filename: str, upload_type: str) -> str:
    """
    Get success message for upload (direct vs staged).

    Args:
        result: Result object containing upload details
        filename: Original filename that was uploaded
        upload_type: Type of upload ("direct" or "staged")

    Returns:
        str: Success message for the upload

    Examples:
        message = get_success_message_for_upload(result, "data.xlsx", "staged")
        flash(message, "success")
    """
    if upload_type == "staged":
        return (
            f"✅ File '{filename}' staged successfully!\n"
            f"📋 ID: {result.id_}\n"
            f"🏭 Sector: {result.sector}\n"
            f"📁 Staged as: {result.staged_filename}\n"
            f"🔍 Ready for review and confirmation."
        )
    else:
        return f"✅ File '{filename}' uploaded successfully! ID: {result.id_}, Sector: {result.sector}"


def render_upload_form(form: UploadForm, message: str | None, template_name: str) -> str:
    """
    Render upload form with consistent message handling.

    Args:
        form: UploadForm instance
        message: Optional message to display
        template_name: Name of the template to render

    Returns:
        str: Rendered HTML

    Examples:
        return render_upload_form(form, "Upload successful!", "upload.html")
    """
    return render_template(template_name, form=form, upload_message=message)


def render_upload_error(form: UploadForm, message: str, template_name: str) -> str:
    """
    Render upload error with consistent error display.

    Args:
        form: UploadForm instance
        message: Error message to display
        template_name: Name of the template to render

    Returns:
        str: Rendered HTML

    Examples:
        return render_upload_error(form, "File upload failed", "upload.html")
    """
    return render_template(template_name, form=form, upload_message=message)
