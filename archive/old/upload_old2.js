document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("upload-form");
  const dropZone = document.getElementById("drop_zone");
  const fileInput = document.getElementById("hidden-file-input");
  const overlay = document.getElementById("spinner-overlay");

  if (!form || !fileInput || !dropZone || !overlay) {
    console.warn("Upload: missing DOM elements.");
    return;
  }

  // ✅ Unified form submission with validation and spinner
  function handleValidatedSubmit(event) {
    event.preventDefault();

    if (!form.checkValidity()) {
      form.classList.add("was-validated");  // Bootstrap validation styling
      return;
    }

    overlay.classList.remove("d-none");

    requestAnimationFrame(() => {
      setTimeout(() => {
        form.submit();  // Resume normal submission after spinner is visible
      }, 0);
    });
  }

  // ✅ Form submit via button or requestSubmit
  form.addEventListener("submit", handleValidatedSubmit);

  // ✅ Click-to-open file browser
  dropZone.addEventListener("click", () => {
    fileInput.click();
  });

  // ✅ Automatically submit form when file selected via file picker
  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      form.requestSubmit();
    }
  });

  // ✅ Drag-and-drop visuals
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

  // ✅ Handle dropped files
  dropZone.addEventListener("drop", function (event) {
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      fileInput.files = files;
      form.requestSubmit();
    }
  });
});
