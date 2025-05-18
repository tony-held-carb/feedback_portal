document.addEventListener('DOMContentLoaded', function () {
  const modalElement = document.getElementById('routeModal');

  if (modalElement && modalElement.querySelector('.modal-body').textContent.trim() !== "") {
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    // Auto-hide modal after 2 seconds
    setTimeout(() => {
      modal.hide();
    }, 2000);
  }
});
