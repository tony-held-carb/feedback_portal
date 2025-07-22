/**
 * Success Popup Management
 *
 * This module handles the display of success popups after form submissions.
 * It provides a clean, reusable way to show success feedback to users
 * without disrupting their workflow.
 *
 * @version 1.0.0
 * @author ARB Feedback Portal
 */

/**
 * Initialize success popup functionality
 *
 * This function should be called when the page loads to set up
 * any success popup behavior. It checks for the presence of
 * success popup flags and displays modals accordingly.
 */
function initializeSuccessPopup() {
    // Check if we should show a success popup
    // Look for a data attribute or global variable indicating success
    const shouldShowPopup = document.body.hasAttribute('data-show-success-popup') ||
        window.showSuccessPopup === true;

    if (shouldShowPopup) {
        const successModal = document.getElementById('successModal');
        if (successModal) {
            // Show the success modal using Bootstrap
            const modal = new bootstrap.Modal(successModal);
            modal.show();

            // Log success for debugging
            console.log('Success popup displayed');
        }
    }
}

/**
 * Show a success popup programmatically
 *
 * This function can be called from other JavaScript code to
 * display a success popup with custom messaging.
 *
 * @param {string} title - The modal title
 * @param {string} message - The success message
 * @param {string} modalId - Optional custom modal ID (defaults to 'successModal')
 */
function showSuccessPopup(title = 'Success', message = 'Operation completed successfully', modalId = 'successModal') {
    const modalElement = document.getElementById(modalId);
    if (!modalElement) {
        console.warn(`Modal with ID '${modalId}' not found`);
        return;
    }

    // Update modal content if custom values provided
    if (title !== 'Success') {
        const titleElement = modalElement.querySelector('.modal-title');
        if (titleElement) {
            titleElement.innerHTML = `<i class="fas fa-check-circle me-2"></i>${title}`;
        }
    }

    if (message !== 'Operation completed successfully') {
        const messageElement = modalElement.querySelector('.modal-body p');
        if (messageElement) {
            messageElement.textContent = message;
        }
    }

    // Show the modal
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
}

/**
 * Hide the success popup programmatically
 *
 * @param {string} modalId - Optional custom modal ID (defaults to 'successModal')
 */
function hideSuccessPopup(modalId = 'successModal') {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            modal.hide();
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    initializeSuccessPopup();
});

// Export functions for use in other modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeSuccessPopup,
        showSuccessPopup,
        hideSuccessPopup
    };
} 