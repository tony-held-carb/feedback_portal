document.addEventListener("DOMContentLoaded", function () {
    const dropZone = document.getElementById("drop_zone");
    const fileInput = document.querySelector('input[type="file"]');
    const form = document.querySelector("form");

    if (!dropZone || !fileInput || !form) {
        console.warn("Drop zone, file input, or form not found.");
        return;
    }

    function highlight(event) {
        event.preventDefault();
        dropZone.classList.add("dragging");
    }

    function unhighlight(event) {
        event.preventDefault();
        dropZone.classList.remove("dragging");
    }

    function handleDrop(event) {
        event.preventDefault();
        unhighlight(event);

        const files = event.dataTransfer.files;

        if (files.length > 0) {
            fileInput.files = files;

            const overlay = document.getElementById("upload-spinner-overlay");
            if (overlay) {
                overlay.classList.remove("d-none");
            }

            requestAnimationFrame(() => {
                setTimeout(() => {
                    const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                    if (submitBtn) {
                        submitBtn.click();
                    } else {
                        form.submit();  // Fallback if button not found
                    }
                }, 0);
            });
        }
    }

    ["dragenter", "dragover", "dragleave", "drop"].forEach(eventType => {
        dropZone.addEventListener(eventType, event => event.preventDefault());
        document.body.addEventListener(eventType, event => event.preventDefault());
    });

    dropZone.addEventListener("dragenter", highlight);
    dropZone.addEventListener("dragover", highlight);
    dropZone.addEventListener("dragleave", unhighlight);
    dropZone.addEventListener("drop", handleDrop);
});
