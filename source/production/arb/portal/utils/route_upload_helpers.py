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
from flask import Response, render_template, request, url_for
from werkzeug.datastructures import FileStorage

from arb.portal.wtf_upload import UploadForm
from arb.portal.utils.route_util import format_diagnostic_message

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


def handle_upload_error(result, form: UploadForm, template_name: str, request_file=None) -> str:
    """
    Handle upload errors with appropriate error messages and logging.

    Args:
        result: Result object containing error information
        form: UploadForm instance
        template_name: Name of the template to render
        request_file: Optional uploaded file for diagnostic information

    Returns:
        str: Rendered HTML with error message

    Examples:
        return handle_upload_error(result, form, 'upload.html', request_file)
    """
    # Get user-friendly error message
    error_message = get_error_message_for_type(result.error_type, result)
    
    # Determine upload type from template name
    upload_type = "staged" if "staged" in template_name else "direct"
    
    # Handle conversion_failed specially for detailed diagnostics
    if result.error_type == "conversion_failed":
        logger.warning(f"Upload failed file conversion: {result.file_path=}")
        # Note: Detailed diagnostics would be handled by the calling route
        # since we don't have access to generate_upload_diagnostics here
        return render_upload_error_page(form, error_message, template_name, upload_type)
    
    # Log the error for debugging
    logger.error(f"Upload error - Type: {result.error_type}, Message: {result.error_message}")
    
    return render_upload_error_page(form, error_message, template_name, upload_type)


def handle_upload_exception(e: Exception, form: UploadForm, template_name: str, 
                          request_file=None, result=None, diagnostic_func=None) -> str:
    """
    Handle exceptions during upload processing with enhanced error handling.

    Args:
        e: The exception that occurred
        form: UploadForm instance
        template_name: Name of the template to render
        request_file: Optional uploaded file for diagnostic information
        result: Optional result object if available
        diagnostic_func: Optional function to generate detailed diagnostics

    Returns:
        str: Rendered HTML with detailed error message

    Examples:
        return handle_upload_exception(e, form, 'upload.html', request_file, result)
    """
    logger.exception("Exception occurred during upload processing.")
    
    # Determine upload type from template name
    upload_type = "staged" if "staged" in template_name else "direct"
    
    # Generate detailed diagnostic information if diagnostic function is provided
    if diagnostic_func and request_file:
        try:
            file_path = result.file_path if result else None
            error_details = diagnostic_func(request_file, file_path)
            detailed_message = format_diagnostic_message(error_details)
            return render_upload_error_page(form, detailed_message, template_name, upload_type, error_details)
        except Exception as diagnostic_error:
            logger.error(f"Error generating diagnostics: {diagnostic_error}")
    
    # Fallback to generic error message
    generic_message = "An unexpected error occurred during upload processing. Please try again."
    return render_upload_error_page(form, generic_message, template_name, upload_type)


def handle_upload_success(result, request_file, upload_type: str = "direct") -> tuple[str, str]:
    """
    Handle successful upload processing with appropriate success messages and logging.

    Args:
        result: Result object containing success information
        request_file: Uploaded file for filename information
        upload_type: Type of upload ("direct" or "staged")

    Returns:
        tuple[str, str]: (success_message, redirect_url)
        - success_message: User-friendly success message
        - redirect_url: URL to redirect to after successful upload

    Examples:
        message, redirect_url = handle_upload_success(result, request_file, "staged")
        flash(message, "success")
        return redirect(redirect_url)
    """
    # Generate success message
    success_message = get_success_message_for_upload(result, request_file.filename, upload_type)
    
    # Log the successful upload
    logger.info(f"Upload successful - Type: {upload_type}, ID: {result.id_}, Sector: {result.sector}")
    
    # Determine redirect URL based on upload type
    if upload_type == "staged":
        redirect_url = url_for('main.review_staged', id_=result.id_, filename=result.staged_filename)
    else:
        redirect_url = url_for('main.incidence_update', id_=result.id_)
    
    return success_message, redirect_url


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


def render_upload_page(form: UploadForm, message: str | None, template_name: str, 
                      upload_type: str = "direct") -> str:
    """
    Render upload page with consistent template handling and user experience.

    Args:
        form: UploadForm instance
        message: Optional message to display on the page
        template_name: Name of the template to render
        upload_type: Type of upload ("direct" or "staged")

    Returns:
        str: Rendered HTML for the upload page

    Examples:
        return render_upload_page(form, message, 'upload.html', "direct")
        return render_upload_page(form, message, 'upload_staged.html', "staged")
    """
    # Add upload type context for template customization
    template_context = {
        'form': form,
        'upload_message': message,
        'upload_type': upload_type,
        'page_title': f"{upload_type.title()} Upload" if upload_type else "Upload"
    }
    
    return render_template(template_name, **template_context)


def render_upload_success_page(form: UploadForm, success_message: str, template_name: str,
                             upload_type: str = "direct") -> str:
    """
    Render upload success page with consistent success handling.

    Args:
        form: UploadForm instance
        success_message: Success message to display
        template_name: Name of the template to render
        upload_type: Type of upload ("direct" or "staged")

    Returns:
        str: Rendered HTML for the success page

    Examples:
        return render_upload_success_page(form, "Upload successful!", 'upload.html', "direct")
    """
    # Add success-specific context
    template_context = {
        'form': form,
        'upload_message': success_message,
        'upload_type': upload_type,
        'is_success': True,
        'page_title': f"{upload_type.title()} Upload - Success"
    }
    
    return render_template(template_name, **template_context)


def render_upload_error_page(form: UploadForm, error_message: str, template_name: str,
                           upload_type: str = "direct", error_details: dict | None = None) -> str:
    """
    Render upload error page with consistent error handling and user experience.

    Args:
        form: UploadForm instance
        error_message: Error message to display
        template_name: Name of the template to render
        upload_type: Type of upload ("direct" or "staged")
        error_details: Optional detailed error information for debugging

    Returns:
        str: Rendered HTML for the error page

    Examples:
        return render_upload_error_page(form, "File upload failed", 'upload.html', "direct")
    """
    # Add error-specific context
    template_context = {
        'form': form,
        'upload_message': error_message,
        'upload_type': upload_type,
        'is_error': True,
        'error_details': error_details,
        'page_title': f"{upload_type.title()} Upload - Error"
    }
    
    return render_template(template_name, **template_context)
