/**
 * @fileoverview Automatically displays and hides Bootstrap modals with content
 *
 * This script automatically shows a Bootstrap modal when the page loads if the modal
 * contains content. It's used to display messages, notifications, or other content
 * that should be shown to users immediately upon page load.
 *
 * Features:
 * - Automatically shows modal if it contains content
 * - Auto-hides modal after 2 seconds
 * - Uses Bootstrap's modal API for smooth animations
 *
 * Requirements:
 * - Bootstrap 5.x must be loaded
 * - Modal element must have ID "routeModal"
 * - Modal must have a .modal-body element
 */
document.addEventListener('DOMContentLoaded', function () {
    // Find the modal element by ID
    const modalElement = document.getElementById('routeModal');

    // Check if modal exists and has content in the modal body
    if (modalElement && modalElement.querySelector('.modal-body').textContent.trim() !== "") {
        // Create Bootstrap modal instance and show it
        const modal = new bootstrap.Modal(modalElement);
        modal.show();

        // Auto-hide modal after 2 seconds for better user experience
        // This prevents modals from staying open indefinitely
        setTimeout(() => {
            modal.hide();
        }, 2000);
    }
});
