/*
===============================================================================
JavaScript Diagnostics Utility (java_script_diagnostics.js)
===============================================================================

Purpose:
--------
This file provides a simple, robust way to log JavaScript diagnostics and debug
messages both to the browser (via a persistent overlay) and to the backend server
(via a POST endpoint). It is designed for use in development, E2E testing, and
troubleshooting hard-to-reproduce frontend issues.

Features:
---------
1. Diagnostics Overlay:
   - Displays log messages at the bottom of every page.
   - Messages persist across navigation and reloads (if the overlay is not removed).
   - Useful for seeing what happened even after a redirect or modal.

2. Backend Logging:
   - Sends diagnostic messages to the backend via /js_diagnostic_log.
   - Messages are written to the backend log file with a [JS_DIAG] prefix.
   - Allows correlation of frontend/browser events with backend activity.

3. Example Usage (see diagnostics test page):
   - Log on page load, button clicks, modal events, etc.
   - Use logToDiagnostics(msg) for overlay, sendJsDiagnostic(msg, extra) for backend.

How to Use:
-----------
- Include this file in your template using:
    <script src="{{ url_for('static', filename='js/java_script_diagnostics.js') }}"></script>
- Call logToDiagnostics('message') to log to the overlay.
- Call sendJsDiagnostic('message', {extra: 'data'}) to log to the backend.
- You can use both for maximum visibility.

Limitations & Caveats:
----------------------
- The overlay is visible to all users; do not log sensitive data.
- Backend logging is only as reliable as the /js_diagnostic_log endpoint.
- Overlay messages are not persisted if the user navigates away or reloads (unless you add localStorage support).
- This file is intended for development and diagnostics, not for production user-facing notifications.
- If the overlay is not visible, check that the <div id="js-diagnostics"> exists in the DOM.
- If backend logs are missing, check network requests and backend route.

===============================================================================
*/
// Diagnostics overlay logger
function logToDiagnostics(msg) {
    let diag = document.getElementById('js-diagnostics');
    if (!diag) {
        diag = document.createElement('div');
        diag.id = 'js-diagnostics';
        diag.style = 'position:fixed;bottom:0;left:0;z-index:9999;background:#fff;color:#000;padding:4px;font-size:12px;max-width:100vw;overflow:auto;opacity:0.95;box-shadow:0 0 8px #888;pointer-events:auto;';
        document.body.appendChild(diag);
    }
    diag.innerText += msg + '\n';
}

// Backend logger
function sendJsDiagnostic(msg, extra) {
    try {
        fetch('/js_diagnostic_log', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({msg, ts: new Date().toISOString(), ...extra})
        });
    } catch (e) {
        logToDiagnostics('[ERROR] Failed to send diagnostic to backend: ' + e);
    }
}

// On page load
window.addEventListener('DOMContentLoaded', function() {
    logToDiagnostics('[JS_DIAG] Page loaded');
    sendJsDiagnostic('Page loaded', {page: 'java_script_diagnostic_test'});

    // Send Diagnostic button
    document.getElementById('sendDiagnosticBtn').addEventListener('click', function() {
        const val = document.getElementById('diagnosticText').value;
        logToDiagnostics('[JS_DIAG] Send Diagnostic clicked: ' + val);
        sendJsDiagnostic('Send Diagnostic clicked', {value: val});
    });

    // Return to Homepage button
    document.getElementById('returnHomeBtn').addEventListener('click', function() {
        logToDiagnostics('[JS_DIAG] Return to Homepage button clicked (showing modal)');
        sendJsDiagnostic('Return to Homepage button clicked (showing modal)');
        // Show Bootstrap modal
        const modal = new bootstrap.Modal(document.getElementById('confirmReturnModal'));
        modal.show();
    });

    // Modal confirm/cancel
    document.getElementById('confirmReturnBtn').addEventListener('click', function() {
        logToDiagnostics('[JS_DIAG] Confirmed return to homepage');
        sendJsDiagnostic('Confirmed return to homepage');
        window.location.href = '/';
    });
    document.getElementById('cancelReturnBtn').addEventListener('click', function() {
        logToDiagnostics('[JS_DIAG] Cancelled return to homepage');
        sendJsDiagnostic('Cancelled return to homepage');
        // Hide modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('confirmReturnModal'));
        modal.hide();
    });
}); 