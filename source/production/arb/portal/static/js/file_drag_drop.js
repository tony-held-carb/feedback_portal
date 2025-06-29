/**
 * @fileoverview Handles drag-and-drop file upload functionality for the portal
 * 
 * This script provides a complete drag-and-drop interface for file uploads.
 * It allows users to drag files from their computer onto a designated drop zone,
 * automatically triggering the upload process when files are dropped.
 * 
 * Features:
 * - Visual feedback during drag operations (highlighting drop zone)
 * - Automatic file selection when files are dropped
 * - Automatic form submission after file drop
 * - Fallback to manual file selection via click
 * - Spinner overlay during upload process
 * 
 * Functions:
 * - highlight(event) - Adds visual feedback when files are dragged over drop zone
 * - unhighlight(event) - Removes visual feedback when files leave drop zone
 * - handleDrop(event) - Processes dropped files and submits form
 * - (Event listeners for drag events) - Prevents default browser behavior
 * 
 * Requirements:
 * - Drop zone element with ID "drop_zone"
 * - File input element
 * - Form element for submission
 * - Optional spinner overlay with ID "upload-spinner-overlay"
 */
document.addEventListener("DOMContentLoaded", function () {
    const dropZone = document.getElementById("drop_zone");
    const fileInput = document.querySelector('input[type="file"]');
    const form = document.querySelector("form");

    if (!dropZone || !fileInput || !form) {
        console.warn("Drop zone, file input, or form not found.");
        return;
    }

    /**
     * Highlights the drop zone when files are dragged over it
     * Adds a visual "dragging" class to provide user feedback
     * @param {DragEvent} event - The drag event object
     */
    function highlight(event) {
        event.preventDefault();
        dropZone.classList.add("dragging");
    }

    /**
     * Removes highlighting from the drop zone when files are no longer dragged over it
     * Removes the "dragging" class to restore normal appearance
     * @param {DragEvent} event - The drag event object
     */
    function unhighlight(event) {
        event.preventDefault();
        dropZone.classList.remove("dragging");
    }

    /**
     * Handles the file drop event
     * Processes dropped files and automatically submits the form
     * @param {DragEvent} event - The drop event containing the dropped files
     */
    function handleDrop(event) {
        event.preventDefault();
        unhighlight(event);

        const files = event.dataTransfer.files;

        if (files.length > 0) {
            // Set the dropped files to the file input
            fileInput.files = files;

            // Show upload spinner overlay if it exists
            const overlay = document.getElementById("upload-spinner-overlay");
            if (overlay) {
                overlay.classList.remove("d-none");
            }

            // Automatically submit the form after a brief delay
            // This ensures the UI updates before form submission
            requestAnimationFrame(() => {
                setTimeout(() => {
                    const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                    if (submitBtn) {
                        submitBtn.click();
                    } else {
                        form.submit();  // Fallback if button not found
                    }
                }, 0);
            });
        }
    }

    // Prevent default browser behavior for all drag events
    // This prevents the browser from trying to open files in new tabs
    ["dragenter", "dragover", "dragleave", "drop"].forEach(eventType => {
        dropZone.addEventListener(eventType, event => event.preventDefault());
        document.body.addEventListener(eventType, event => event.preventDefault());
    });

    // Attach event listeners for drag visual feedback
    dropZone.addEventListener("dragenter", highlight);
    dropZone.addEventListener("dragover", highlight);
    dropZone.addEventListener("dragleave", unhighlight);
    dropZone.addEventListener("drop", handleDrop);
});
