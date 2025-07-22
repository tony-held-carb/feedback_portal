/**
 * delete_testing_range.js
 *
 * Handles dynamic UI and confirmation logic for the Delete Testing Range developer utility page.
 *
 * Features:
 * - Updates the submit button label (Preview/Delete) based on the Dry Run checkbox in real time.
 * - Shows a Bootstrap modal confirmation dialog when the user attempts to delete (not dry run).
 * - Modal allows user to Confirm Delete, Cancel, or Preview (switches to dry run and submits).
 * - Prevents accidental destructive actions and provides a safe workflow for test data cleanup.
 *
 * Usage:
 * - This script should be included only on the delete_testing_range.html page.
 * - Requires Bootstrap 5's JS for modal support.
 */

document.addEventListener('DOMContentLoaded', function () {
    // Elements
    const dryRunCheckbox = document.getElementById('dry_run');
    const submitBtn = document.getElementById('delete-preview-btn');
    const form = document.getElementById('delete-testing-range-form');
    const modal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
    const confirmBtn = document.getElementById('modal-confirm-delete');
    const previewBtn = document.getElementById('modal-preview');
    const cancelBtn = document.getElementById('modal-cancel');
    let skipModal = false;

    // Update the submit button label and style based on dry run checkbox
    function updateButton() {
        submitBtn.textContent = dryRunCheckbox.checked ? 'Preview' : 'Delete';
        submitBtn.classList.toggle('btn-danger', !dryRunCheckbox.checked);
        submitBtn.classList.toggle('btn-primary', dryRunCheckbox.checked);
    }

    dryRunCheckbox.addEventListener('change', updateButton);
    updateButton();

    // Intercept form submission to show modal if not a dry run
    form.addEventListener('submit', function (e) {
        if (!dryRunCheckbox.checked && !skipModal) {
            e.preventDefault();
            modal.show();
        }
        skipModal = false;
    });

    // Modal: Confirm Delete
    confirmBtn.addEventListener('click', function () {
        skipModal = true;
        modal.hide();
        form.submit();
    });

    // Modal: Preview (switch to dry run and submit)
    previewBtn.addEventListener('click', function () {
        dryRunCheckbox.checked = true;
        updateButton();
        skipModal = true;
        modal.hide();
        form.submit();
    });

    // Modal: Cancel
    cancelBtn.addEventListener('click', function () {
        modal.hide();
    });
}); 