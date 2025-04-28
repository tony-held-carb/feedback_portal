const dropArea = document.getElementById('drop-area');
const progressBar = document.getElementById('progress-bar');
const alertMessage = document.getElementById('alert-message');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

dropArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

function handleFiles(files) {
    ([...files]).forEach(uploadFile);
}

function uploadFile(file) {
    const url = '/upload';
    const formData = new FormData();
    formData.append('file', file);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);

    xhr.upload.addEventListener("progress", function (e) {
        const percent = (e.loaded / e.total) * 100;
        progressBar.style.width = percent + '%';
    });

    xhr.onload = function () {
        if (xhr.status === 200) {
            showAlert(JSON.parse(xhr.responseText).message, 'success');
        } else {
            showAlert(JSON.parse(xhr.responseText).message, 'error');
        }
    };

    xhr.send(formData);
}

function showAlert(message, status) {
    alertMessage.textContent = message;
    alertMessage.className = status === 'success' ? 'alert success' : 'alert error';
    setTimeout(() => {
        alertMessage.textContent = '';
        progressBar.style.width = '0%';
    }, 3000);
}
