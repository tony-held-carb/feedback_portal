document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("upload-form");
  const dropZone = document.getElementById("drop_zone");
  const fileInput = dropZone.querySelector('input[type="file"]');
  const overlay = document.getElementById("spinner-overlay");

  // ✅ Show spinner *before* redirecting
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (overlay) overlay.classList.remove("d-none");

    // Give the browser time to render the spinner before navigation
    requestAnimationFrame(() => {
      setTimeout(() => {
        form.submit();  // resume actual form submission
      }, 0);
    });
  });

  // ✅ Drag-and-drop styling
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

  // ✅ Handle dropped file and auto-submit
  dropZone.addEventListener("drop", function (event) {
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      fileInput.files = files;
      form.requestSubmit();  // triggers the above submit handler
    }
  });
});
