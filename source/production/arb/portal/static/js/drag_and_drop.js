document.addEventListener("DOMContentLoaded", function () {
  const dropZone = document.getElementById("drop_zone");
  const fileInput = document.querySelector('input[type="file"]');

  if (!dropZone || !fileInput) {
    console.warn("Drag-and-drop zone or file input not found.");
    return;
  }

  // 🔁 Highlight drop zone on drag events
  function highlight(event) {
    event.preventDefault();
    dropZone.classList.add("dragging");
  }

  function unhighlight(event) {
    event.preventDefault();
    dropZone.classList.remove("dragging");
  }

  // 📦 Handle file drop
  function handleDrop(event) {
    event.preventDefault();
    unhighlight(event);

    const files = event.dataTransfer.files;
    if (files.length > 0) {
      fileInput.files = files;

      // Optional: auto-submit form if only one file is expected
      const form = fileInput.closest("form");
      if (form) {
        form.submit();
      }
    }
  }

  // ⛔ Prevent default browser behavior
  ["dragenter", "dragover", "dragleave", "drop"].forEach(eventType => {
    dropZone.addEventListener(eventType, event => event.preventDefault());
    document.body.addEventListener(eventType, event => event.preventDefault());
  });

  // 🧲 Bind events
  dropZone.addEventListener("dragenter", highlight);
  dropZone.addEventListener("dragover", highlight);
  dropZone.addEventListener("dragleave", unhighlight);
  dropZone.addEventListener("drop", handleDrop);
});
