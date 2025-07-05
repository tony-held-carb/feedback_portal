/**
 * @fileoverview Comprehensive file upload handling with drag-and-drop, validation, and progress feedback
 * 
 * This script provides a complete file upload experience with multiple interaction methods.
 * It handles both drag-and-drop and click-to-select file uploads, with form validation
 * and visual feedback throughout the process.
 * 
 * Features:
 * - Drag-and-drop file upload with visual feedback
 * - Click-to-open file browser
 * - Automatic form submission after file selection
 * - Form validation with Bootstrap styling
 * - Upload progress spinner overlay
 * - Browser back button handling
 * - Defensive programming with element existence checks
 * - Upload progress notifications via ToastManager
 * 
 * Functions:
 * - handleValidatedSubmit(event) - Validates form and shows progress before submission
 * - (Event listeners for click, change, drag events)
 * - (Browser back button handling)
 * 
 * Requirements:
 * - Form must have ID "upload-form"
 * - Drop zone must have ID "drop_zone"
 * - Hidden file input must have ID "hidden-file-input"
 * - Spinner overlay must have ID "spinner-overlay"
 * - Bootstrap CSS classes for validation styling
 * - ToastManager must be available for notifications
 */
document.addEventListener("DOMContentLoaded", function () {
    // Get all required DOM elements
    const form = document.getElementById("upload-form");
    const dropZone = document.getElementById("drop_zone");
    const fileInput = document.getElementById("hidden-file-input");
    const overlay = document.getElementById("spinner-overlay");

    // Defensive check: ensure all required elements exist
    if (!form || !fileInput || !dropZone || !overlay) {
        console.warn("Upload: missing DOM elements.");
        return;
    }

    // ✅ Defensive: Always hide overlay on initial load
    overlay.classList.add("d-none");

    /**
     * Handles form submission with validation and spinner
     * Validates the form and shows spinner before submitting
     * @param {Event} event - The form submit event
     */
    function handleValidatedSubmit(event) {
        event.preventDefault();

        // Check if form is valid (required fields, file selected, etc.)
        if (!form.checkValidity()) {
            form.classList.add("was-validated");
            return;
        }

        // Show spinner overlay to indicate upload in progress
        overlay.classList.remove("d-none");

        // Show upload progress notification if ToastManager is available (disabled in old system)
        if (window.ToastManager) {
            window.ToastManager.showUploadProgress();
        } else {
            // Fallback to console logging for debugging
            console.info('Upload: Starting file upload process...');
        }

        // Submit form after a brief delay to ensure UI updates
        requestAnimationFrame(() => {
            setTimeout(() => {
                form.submit();
            }, 0);
        });
    }

    // ✅ Form submit via button or JS
    form.addEventListener("submit", handleValidatedSubmit);

    /**
     * Opens file browser when drop zone is clicked
     * Provides alternative to drag-and-drop for file selection
     */
    dropZone.addEventListener("click", () => {
        fileInput.click();
    });

    /**
     * Automatically submits form when a file is selected
     * Triggers upload process immediately after file selection
     */
    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            form.requestSubmit();
        }
    });

    // ✅ Drag-and-drop visuals
    // Add visual feedback when files are dragged over the drop zone
    ["dragenter", "dragover"].forEach(eventType => {
        dropZone.addEventListener(eventType, e => {
            e.preventDefault();
            dropZone.classList.add("dragging");
        });
    });

    // Remove visual feedback when files are no longer over the drop zone
    ["dragleave", "drop"].forEach(eventType => {
        dropZone.addEventListener(eventType, e => {
            e.preventDefault();
            dropZone.classList.remove("dragging");
        });
    });

    /**
     * Handles files dropped onto the drop zone
     * Sets the dropped files to the file input and submits the form
     * @param {DragEvent} event - The drop event containing the files
     */
    dropZone.addEventListener("drop", function (event) {
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            form.requestSubmit();
        }
    });

    // ✅ Hide spinner if returning via browser Back button
    // Prevents spinner from staying visible when user navigates back
    window.addEventListener("pageshow", function (event) {
        if (event.persisted || (window.performance && performance.navigation.type === 2)) {
            overlay.classList.add("d-none");
        }
    });
});
