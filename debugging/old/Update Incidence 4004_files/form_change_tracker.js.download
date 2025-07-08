/**
 * @fileoverview Tracks unsaved changes in forms and warns users before leaving the page
 * 
 * This script monitors form fields for changes and provides visual feedback to users
 * when they have unsaved data. It prevents accidental data loss by showing a warning
 * when users try to leave the page with unsaved changes.
 * 
 * Features:
 * - Tracks changes to all form inputs (text, textarea, select)
 * - Shows visual indicator when form has unsaved changes
 * - Warns users before leaving page with unsaved data
 * - Automatically clears dirty state when form is submitted
 * 
 * Functions:
 * - markDirty() - Marks form as having unsaved changes and shows indicator
 * - (beforeunload event handler) - Warns user before leaving page
 * - (submit event handler) - Clears dirty state on form submission
 * - (change/input event handlers) - Monitor form field changes
 * 
 * Requirements:
 * - Form must have an ID matching the data-form-id attribute on the body
 * - Page must have an element with ID "unsaved-indicator"
 */
document.addEventListener("DOMContentLoaded", function () {
    // Get the form ID from the body data attribute and find the corresponding form
    const formId = document.body.getAttribute("data-form-id");
    const form = document.querySelector(`#${formId}`);
    const indicator = document.getElementById("unsaved-indicator");

    if (!form || !indicator) {
        console.warn("Unsaved changes script: missing form or indicator");
        return;
    }

    /**
     * Tracks whether the form has unsaved changes
     * @type {boolean}
     */
    let isDirty = false;

    /**
     * Marks the form as having unsaved changes
     * Shows the unsaved indicator and sets the dirty flag
     */
    const markDirty = () => {
        if (!isDirty) {
            indicator.classList.remove("d-none");
            isDirty = true;
        }
    };

    // Monitor all form fields for changes
    const fields = form.querySelectorAll("input, textarea, select");
    fields.forEach(field => {
        // Mark form as dirty when user changes any field value
        field.addEventListener("change", markDirty);
        // Also mark as dirty during typing (for immediate feedback)
        field.addEventListener("input", markDirty);
    });

    /**
     * Warns user before leaving page if they have unsaved changes
     * Shows browser's default "Leave Site?" dialog
     * @param {BeforeUnloadEvent} e - The beforeunload event
     */
    window.addEventListener("beforeunload", function (e) {
        if (isDirty) {
            e.preventDefault();
            e.returnValue = ""; // Shows browser's default warning message
        }
    });

    /**
     * Clears the dirty state when form is successfully submitted
     * Hides the unsaved indicator and removes the beforeunload warning
     */
    form.addEventListener("submit", function () {
        isDirty = false;
        indicator.classList.add("d-none");
        // Remove the beforeunload event listener to prevent warnings after submission
        window.removeEventListener("beforeunload", () => {
        });
    });
});
