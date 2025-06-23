/**
 * confirm_delete.js
 * Generic deletion confirmation for all modals rendered via confirm_macros.jinja
 */
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("form[id$='Form']").forEach(form => {
        form.addEventListener("submit", function (event) {
            const input = form.querySelector(".confirm-input");
            const expected = input.getAttribute("data-expected").trim().toLowerCase();
            const actual = input.value.trim().toLowerCase();
            if (actual !== expected) {
                alert(`You must type "${expected}" to confirm.`);
                event.preventDefault();
            }
        });
    });
});
