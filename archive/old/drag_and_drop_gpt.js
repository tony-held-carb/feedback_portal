document.addEventListener('DOMContentLoaded', function () {
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');
  const uploadForm = document.getElementById('upload-form');

  if (!dropZone || !fileInput || !uploadForm) {
    console.error("Required elements not found: drop-zone, file-input, or upload-form.");
    return;
  }

  // Highlight drop zone on drag enter
  dropZone.addEventListener('dragover', function (e) {
    e.preventDefault();
    dropZone.classList.add('drag-over');
  });

  dropZone.addEventListener('dragleave', function (e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
  });

  // Handle dropped files
  dropZone.addEventListener('drop', function (e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    console.log("Drop event triggered. files =", files);

    if (files.length > 0) {
      fileInput.files = files;
      console.log("File dropped:", files[0]);

      // Optional: auto-submit the form
      uploadForm.requestSubmit();
    } else {
      alert("⚠️ No file detected. Please ensure the file is closed (e.g., not open in Excel) before uploading.");
      console.warn("Drag-and-drop failed: no readable file.");
    }
  });

  // Click drop zone to open file dialog
  dropZone.addEventListener('click', function () {
    fileInput.click();
  });

  // Handle manual file selection
  fileInput.addEventListener('change', function (e) {
    const file = fileInput.files[0];
    if (!file) {
      alert("⚠️ No file selected. Please ensure the file is not open or locked.");
      console.warn("Manual file selection failed: FileList is empty.");
    } else {
      console.log("File manually selected:", file.name);
      uploadForm.requestSubmit();
    }
  });
});
