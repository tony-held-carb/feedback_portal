/**
 * @fileoverview Generic deletion confirmation system for all modals rendered via confirm_macros.jinja
 *
 * This script provides a secure confirmation system for dangerous operations like deletions.
 * It requires users to type a specific confirmation phrase before allowing the form submission
 * to proceed, preventing accidental deletions.
 *
 * Features:
 * - Requires exact text confirmation before form submission
 * - Case-insensitive matching for user convenience
 * - Works with any form that includes the confirmation input
 * - Prevents accidental submissions with browser alert
 *
 * Requirements:
 * - Form must have an ID ending with "Form" (e.g., "deleteForm", "removeForm")
 * - Form must contain an input with class "confirm-input"
 * - Input must have a "data-expected" attribute with the required confirmation text
 *
 * Usage:
 * <form id="deleteForm">
 *   <input class="confirm-input" data-expected="DELETE" type="text" required>
 *   <button type="submit">Delete</button>
 * </form>
 */
document.addEventListener("DOMContentLoaded", function () {
    // Find all forms that end with "Form" (convention for forms that need confirmation)
    document.querySelectorAll("form[id$='Form']").forEach(form => {
        /**
         * Handles form submission and validates confirmation text
         * Prevents submission if user hasn't typed the exact required text
         * @param {Event} event - The form submit event
         */
        form.addEventListener("submit", function (event) {
            // Find the confirmation input field
            const input = form.querySelector(".confirm-input");
            // Get the expected confirmation text from the data attribute
            const expected = input.getAttribute("data-expected").trim().toLowerCase();
            // Get what the user actually typed (normalized to lowercase)
            const actual = input.value.trim().toLowerCase();

            // If the user didn't type the exact required text, prevent submission
            if (actual !== expected) {
                alert(`You must type "${expected}" to confirm.`);
                event.preventDefault();
            }
        });
    });
});
