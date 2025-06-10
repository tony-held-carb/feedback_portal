document.addEventListener("DOMContentLoaded", function () {
    const formId = document.body.getAttribute("data-form-id");
    const form = document.querySelector(`#${formId}`);
    const indicator = document.getElementById("unsaved-indicator");

    if (!form || !indicator) {
        console.warn("Unsaved changes script: missing form or indicator");
        return;
    }

    let isDirty = false;

    const markDirty = () => {
        if (!isDirty) {
            indicator.classList.remove("d-none");
            isDirty = true;
        }
    };

    const fields = form.querySelectorAll("input, textarea, select");
    fields.forEach(field => {
        field.addEventListener("change", markDirty);
        field.addEventListener("input", markDirty);
    });

    window.addEventListener("beforeunload", function (e) {
        if (isDirty) {
            e.preventDefault();
            e.returnValue = "";
        }
    });

    form.addEventListener("submit", function () {
        isDirty = false;
        indicator.classList.add("d-none");
        window.removeEventListener("beforeunload", () => {
        });
    });
});
