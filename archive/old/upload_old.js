document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("upload-form");
  const dropZone = document.getElementById("drop_zone");
  const fileInput = dropZone.querySelector('input[type="file"]');
  const overlay = document.getElementById("spinner-overlay");

  // ✅ Show spinner before submitting
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (overlay) overlay.classList.remove("d-none");

    requestAnimationFrame(() => {
      setTimeout(() => {
        form.submit();
      }, 0);
    });
  });

  // ✅ Drag styling
  ["dragenter", "dragover"].forEach(eventType => {
    dropZone.addEventListener(eventType, e => {
      e.preventDefault();
      dropZone.classList.add("dragging");
    });
  });

  ["dragleave", "drop"].forEach(eventType => {
    dropZone.addEventListener(eventType, e => {
      e.preventDefault();
      dropZone.classList.remove("dragging");
    });
  });

  // ✅ Handle dropped file
  dropZone.addEventListener("drop", function (event) {
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      fileInput.files = files;
      form.requestSubmit();
    }
  });
});
