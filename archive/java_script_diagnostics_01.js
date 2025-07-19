/*
===============================================================================
Generalized JavaScript Diagnostics Utility (java_script_diagnostics.js)
===============================================================================

Purpose:
--------
This file provides a robust, reusable way to log JavaScript diagnostics and debug
messages both to the browser (via a persistent overlay) and to the backend server
(via a POST endpoint). It supports multiple diagnostics blocks per page, each with
its own context, and is designed for use in development, E2E testing, and
troubleshooting hard-to-reproduce frontend issues.

How to Use (Beginner-Friendly):
------------------------------
1. **Wrap your diagnostics section in a block:**
   - Use: `<div class="js-diagnostics-block" data-page="my_page"> ... </div>`
   - The `data-page` attribute is optional but recommended; it labels logs with the page or section name for easier debugging.

2. **Add required child elements with these classes:**
   - Input for message: `.js-diagnostic-text`
   - Send button: `.js-send-diagnostic-btn`
   - Return button: `.js-return-home-btn`
   - Modal: `.js-confirm-return-modal`
   - Modal confirm: `.js-confirm-return-btn`
   - Modal cancel: `.js-cancel-return-btn`
   - See `java_script_diagnostic_test.html` for a full example.

3. **Automatic Logging:**
   - Each diagnostics block logs a `[JS_DIAG] Page loaded` message on page load.
   - Clicking the send button logs the input value to both the overlay and backend.
   - The return button and modal also log actions.

4. **Multiple Inputs:**
   - Only the first `.js-diagnostic-text` input in a block is used by default. For more, extend the JS as needed.

5. **Backend Logging:**
   - `log_to_server` sends logs to the backend `/js_diagnostic_log` route. If the route is missing, an error is shown in the overlay.

6. **Overlay Requirements:**
   - The overlay is created automatically if missing, but is included in `base.html` for consistent styling and presence.

General-Purpose Logging:
------------------------
You can use `log_to_client` and `log_to_server` anywhere in your JS code—not just in event handlers or page loads. This is useful for:
- Logging from custom functions
- Error handlers
- AJAX callbacks
- E2E test hooks
- Any business logic

**How to Import:**
- In your HTML template, include this file at the end of the body (inside `{% block scripts %}` if using Jinja):
  ```html
  <script src="{{ url_for('static', filename='js/java_script_diagnostics.js') }}"></script>
  ```
- Make sure the overlay div (`<div id="js-diagnostics">...</div>`) is present, or let the JS create it automatically.

**Examples:**
-------------
// Log a custom message to the overlay (client only)
log_to_client("Custom client-side log message");

// Log a custom message to the backend (server)
log_to_server("Custom server-side log message", {context: "my_custom_context"});

// Log from a custom function
function myCustomFunction() {
    log_to_client("Custom function executed with value: " + someValue);
    log_to_server("Custom function executed", {value: someValue, page: "my_page"});
}

// Log from an AJAX callback
fetch('/api/data').then(response => response.json()).then(data => {
    log_to_client("AJAX success: " + JSON.stringify(data));
    log_to_server("AJAX success", {data, page: "my_page"});
}).catch(error => {
    log_to_client("AJAX error: " + error);
    log_to_server("AJAX error", {error: error.toString(), page: "my_page"});
});

// Log from an error handler
try {
    // some code that may throw
} catch (e) {
    log_to_client("Caught error: " + e);
    log_to_server("Caught error", {error: e.toString(), page: "my_page"});
}

// Log from E2E test hooks (if injecting JS via Playwright or similar)
// page.evaluate(() => log_to_client('E2E test step reached'));
// page.evaluate(() => log_to_server('E2E test step', {step: 'after login'}));

See Also:
---------
- `base.html` (for overlay div and global inclusion)
- `java_script_diagnostic_test.html` (for a complete example usage)
- `/js_diagnostic_log` backend route (for server-side logging)

===============================================================================
*/

// log_to_client: creates or appends to a floating overlay at the bottom of the page
function log_to_client(msg) {
    let diag = document.getElementById('js-diagnostics');
    // If the overlay doesn't exist, create it
    if (!diag) {
        diag = document.createElement('div');
        diag.id = 'js-diagnostics';
        diag.style = 'position:fixed;bottom:0;left:0;z-index:9999;background:#fff;color:#000;padding:4px;font-size:12px;max-width:100vw;overflow:auto;opacity:0.95;box-shadow:0 0 8px #888;pointer-events:auto;';
        document.body.appendChild(diag);
    }
    // Append the message
    diag.innerText += msg + '\n';
}

// log_to_server: sends a POST request to the backend diagnostics route
function log_to_server(msg, extra) {
    try {
        fetch('/js_diagnostic_log', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({msg, ts: new Date().toISOString(), ...extra})
        });
    } catch (e) {
        // If the backend route is missing or fails, log an error to the overlay
        log_to_client('[ERROR] Failed to send diagnostic to backend: ' + e);
    }
}

// Main diagnostics block handler: runs after the DOM is loaded
window.addEventListener('DOMContentLoaded', function() {
    // For each diagnostics block on the page...
    document.querySelectorAll('.js-diagnostics-block').forEach(function(block) {
        // Get the page/section context for logging
        const page = block.dataset.page || 'unknown_page';
        // Find the first input, send button, return button, and modal elements within the block
        const input = block.querySelector('.js-diagnostic-text');
        const sendBtn = block.querySelector('.js-send-diagnostic-btn');
        const returnBtn = block.querySelector('.js-return-home-btn');
        const modal = block.querySelector('.js-confirm-return-modal');
        const confirmBtn = block.querySelector('.js-confirm-return-btn');
        const cancelBtn = block.querySelector('.js-cancel-return-btn');

        // Log page load for this block
        log_to_client(`[JS_DIAG] Page loaded (${page})`);
        log_to_server('Page loaded', {page});

        // Send Diagnostic button: logs the input value to overlay and backend
        if (sendBtn) {
            sendBtn.addEventListener('click', function() {
                const val = input?.value || '';
                log_to_client(`[JS_DIAG] Send Diagnostic clicked: ${val} (${page})`);
                log_to_server('Send Diagnostic clicked', {value: val, page});
            });
        }

        // Return to Homepage button: shows the confirmation modal and logs the action
        if (returnBtn && modal) {
            returnBtn.addEventListener('click', function() {
                log_to_client(`[JS_DIAG] Return to Homepage button clicked (showing modal) (${page})`);
                log_to_server('Return to Homepage button clicked (showing modal)', {page});
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            });
        }

        // Modal confirm: logs and redirects to homepage
        if (confirmBtn && modal) {
            confirmBtn.addEventListener('click', function() {
                log_to_client(`[JS_DIAG] Confirmed return to homepage (${page})`);
                log_to_server('Confirmed return to homepage', {page});
                window.location.href = '/';
            });
        }
        // Modal cancel: logs and hides the modal
        if (cancelBtn && modal) {
            cancelBtn.addEventListener('click', function() {
                log_to_client(`[JS_DIAG] Cancelled return to homepage (${page})`);
                log_to_server('Cancelled return to homepage', {page});
                const bsModal = bootstrap.Modal.getInstance(modal);
                bsModal.hide();
            });
        }
    });
}); 