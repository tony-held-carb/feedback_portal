const fileInput = document.getElementById('file-input');
const dragArea = document.getElementById('drag-area');
const fileBtn = document.getElementById('file-btn');
const progressBar = document.getElementById('progress');
const uploadedArea = document.getElementById('uploaded-area');

// When the button is clicked, trigger file input
fileBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', handleFileUpload);

// Drag and drop events
dragArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    dragArea.classList.add('active');
});

dragArea.addEventListener('dragleave', () => {
    dragArea.classList.remove('active');
});

dragArea.addEventListener('drop', (e) => {
    e.preventDefault();
    dragArea.classList.remove('active');
    const file = e.dataTransfer.files[0];
    handleFileUpload({target: {files: [file]}});
});

function handleFileUpload(event) {
    const file = event.target.files[0];

    if (file) {
        uploadFile(file);
    }
}

function uploadFile(file) {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append('file', file);

    xhr.open('POST', '/upload', true);

    xhr.upload.addEventListener('progress', (e) => {
        const percent = Math.round((e.loaded / e.total) * 100);
        progressBar.style.width = percent + '%';
    });

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            uploadedArea.innerHTML = `<p>File uploaded: ${file.name}</p>`;
        }
    };

    xhr.send(formData);
}
