/**
 * confirm_delete.js
 *
 * Provides a reusable modal-based deletion confirmation.
 * To trigger: add `data-confirm="shazam"` and `data-target-id="INCIDENCE_ID"` to any delete button.
 */

document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("deleteConfirmModal");
  const confirmInput = document.getElementById("deleteConfirmInput");
  const form = document.getElementById("deleteConfirmForm");
  const expectedPhrase = "shazam";

  window.setupDeleteModal = function (deleteUrl) {
    confirmInput.value = "";
    form.action = deleteUrl;
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
  };

  form.addEventListener("submit", function (event) {
    const typed = confirmInput.value.trim().toLowerCase();
    if (typed !== expectedPhrase) {
      alert(`You must type "${expectedPhrase}" to confirm deletion.`);
      event.preventDefault();
    }
  });
});
