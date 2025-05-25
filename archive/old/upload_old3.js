document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("upload-form");
  const dropZone = document.getElementById("drop_zone");
  const fileInput = document.getElementById("hidden-file-input");
  const overlay = document.getElementById("spinner-overlay");

  if (!form || !fileInput || !dropZone || !overlay) {
    console.warn("Upload: missing DOM elements.");
    return;
  }

  // ✅ Defensive: Always hide overlay on initial load
  overlay.classList.add("d-none");

  // ✅ Unified form submission with validation and spinner
  function handleValidatedSubmit(event) {
    event.preventDefault();

    if (!form.checkValidity()) {
      form.classList.add("was-validated");
      return;
    }

    overlay.classList.remove("d-none");

    requestAnimationFrame(() => {
      setTimeout(() => {
        form.submit();
      }, 0);
    });
  }

  // ✅ Form submit via button or JS
  form.addEventListener("submit", handleValidatedSubmit);

  // ✅ Click-to-open file browser
  dropZone.addEventListener("click", () => {
    fileInput.click();
  });

  // ✅ Auto-submit after choosing file
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

  // ✅ Hide spinner if returning via browser Back button
  window.addEventListener("pageshow", function (event) {
    if (event.persisted || (window.performance && performance.navigation.type === 2)) {
      overlay.classList.add("d-none");
    }
  });
});
