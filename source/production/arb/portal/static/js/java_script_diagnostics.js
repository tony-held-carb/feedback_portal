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

Key Features:
-------------
- Event delegation: Works with dynamically created elements (modals, etc.)
- Dual logging: Client overlay + backend server logging
- Page load logging: Automatic logging when pages load
- Context-aware: Uses data attributes for meaningful log messages
- Production-ready: Can disable overlay for production environments

How to Use (Beginner-Friendly):
------------------------------
1. **Include the JS file in your template:**
   ```html
   <script src="{{ url_for('static', filename='js/java_script_diagnostics.js') }}"></script>
   ```

2. **Wrap your diagnostics section in a block:**
   ```html
   <div class="js-diagnostics-block" data-page="my_page_name">
     <!-- Your diagnostics content here -->
   </div>
   ```

3. **Add loggable buttons with these attributes:**
   ```html
   <button class="js-log-btn" data-js-logging-context="my-action">My Button</button>
   ```

4. **For diagnostic input + send functionality:**
   ```html
   <input type="text" class="js-diagnostic-text" value="Default message">
   <button class="js-log-btn" data-js-logging-context="send-diagnostic">Send Diagnostic</button>
   ```

5. **Automatic behavior:**
   - Page loads → logs "Page loaded: {page_name}"
   - Button clicks → logs "Button clicked: {context}"
   - Send diagnostic → logs "Button clicked: send-diagnostic: {input_value}"

Production vs Development Considerations:
----------------------------------------
IMPORTANT: The overlay is visible to users and should be hidden in production.

**Development (localhost/127.0.0.1):**
- Show overlay for immediate visual feedback
- Use both client and backend logging
- Accept timing differences between frontend/backend logs

**Production:**
- Hide overlay (users don't need to see diagnostics)
- Keep backend logging for debugging production issues
- Be aware of synchronization issues (see below)

**To conditionally show/hide overlay:**
```javascript
// Add this to your template or main JS
if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    // Production: hide overlay
    const overlay = document.getElementById('js-diagnostics');
    if (overlay) overlay.style.display = 'none';
}
```

Synchronization Issues:
----------------------
WARNING: Frontend and backend logging may not be perfectly synchronized.

**The Problem:**
- Frontend logging happens immediately in the browser
- Backend logging requires network request (POST to /js_diagnostic_log)
- Network latency can cause logs to arrive out of order
- Race conditions possible between rapid user actions

**Example Scenario:**
```
User clicks: "Send Diagnostic" → "Return to Homepage" → "Yes, Return"
Frontend logs: [immediate] Send → Return → Confirm
Backend logs: [network delay] Send → Return → Confirm (may arrive in different order)
```

**Best Practices:**
- Use timestamps in logs for correlation
- Accept that backend logs may be slightly out of order
- Frontend overlay provides real-time feedback
- Backend logs provide persistence and server-side analysis

Advanced Usage:
--------------
**Manual Logging from Custom Functions:**
```javascript
// Log to client overlay only
log_to_client("Custom client-side message");

// Log to backend server only
log_to_server("Custom server message", {context: "my_context"});

// Log to both
log_to_client("User action completed");
log_to_server("User action completed", {action: "save", userId: 123});
```

**Error Handling:**
```javascript
try {
    // Some risky operation
    riskyFunction();
} catch (e) {
    log_to_client("Error: " + e.message);
    log_to_server("Error occurred", {error: e.toString(), function: "riskyFunction"});
}
```

**AJAX Callbacks:**
```javascript
fetch('/api/data')
    .then(response => response.json())
    .then(data => {
        log_to_client("API success: " + JSON.stringify(data));
        log_to_server("API success", {data, endpoint: "/api/data"});
    })
    .catch(error => {
        log_to_client("API error: " + error);
        log_to_server("API error", {error: error.toString(), endpoint: "/api/data"});
    });
```

**E2E Testing Integration:**
```javascript
// In Playwright tests
await page.evaluate(() => log_to_client('E2E test step: login completed'));
await page.evaluate(() => log_to_server('E2E test step', {step: 'after_login'}));
```

**Modal Integration (Automatic):**
```html
<!-- Modal buttons automatically log when clicked -->
<button class="js-log-btn" data-js-logging-context="modal-confirm" data-bs-dismiss="modal">
    Confirm Action
</button>
<button class="js-log-btn" data-js-logging-context="modal-cancel" data-bs-dismiss="modal">
    Cancel
</button>
```

**Form Integration:**
```html
<!-- Form buttons automatically log when clicked -->
<form method="POST" action="/submit">
    <button type="submit" class="js-log-btn" data-js-logging-context="form-submit">
        Submit Form
    </button>
</form>
```

Configuration Options:
---------------------
**Custom Context Values:**
- `send-diagnostic`: Special handling for diagnostic input
- `page-load`: Automatic page load logging
- `modal-*`: Modal button actions
- `form-*`: Form submission actions
- `api-*`: API call actions
- Any custom value: Will be logged as "Button clicked: {your_value}"

**Required HTML Structure:**
```html
<!-- Required: Diagnostics block wrapper -->
<div class="js-diagnostics-block" data-page="page_name">
    
    <!-- Optional: Diagnostic input for send-diagnostic context -->
    <input type="text" class="js-diagnostic-text" value="Default message">
    
    <!-- Required: Loggable buttons -->
    <button class="js-log-btn" data-js-logging-context="action_name">Button Text</button>
    
    <!-- Optional: Modal with loggable buttons -->
    <div class="modal">
        <button class="js-log-btn" data-js-logging-context="modal-confirm">Confirm</button>
        <button class="js-log-btn" data-js-logging-context="modal-cancel">Cancel</button>
    </div>
</div>
```

**Backend Requirements:**
- POST endpoint: `/js_diagnostic_log`
- Accepts JSON: `{msg: "message", ts: "timestamp", context: "context", ...}`
- Returns: 200 OK (or handles errors gracefully)

Troubleshooting:
---------------
**Overlay not showing:**
- Check if `#js-diagnostics` element exists in DOM
- Verify `log_to_client()` function is called
- Check browser console for JavaScript errors

**Backend logs not appearing:**
- Verify `/js_diagnostic_log` route exists and works
- Check network tab for failed POST requests
- Verify server logs for any errors

**Buttons not logging:**
- Ensure buttons have `js-log-btn` class
- Verify `data-js-logging-context` attribute is present
- Check for JavaScript errors in console

**Modal buttons not working:**
- Ensure modal buttons have `js-log-btn` class
- Verify event delegation is working (check if other buttons log)
- Check Bootstrap modal initialization

**Double logging:**
- Remove any custom `log_to_client`/`log_to_server` calls
- Ensure buttons only have `js-log-btn` class (not multiple event handlers)

Performance Considerations:
--------------------------
- Event delegation is efficient for large numbers of buttons
- Backend logging is asynchronous (doesn't block UI)
- Overlay updates are synchronous (may impact performance with many logs)
- Consider limiting overlay log history for long-running pages

See Also:
---------
- `base.html` (for overlay div and global inclusion)
- `java_script_diagnostic_test.html` (for complete working example)
- `/js_diagnostic_log` backend route (for server-side logging)
- Bootstrap documentation (for modal integration)

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

// Initialize diagnostics system when DOM is ready
window.addEventListener('DOMContentLoaded', function() {
    // Log page load
    const diagnosticsBlock = document.querySelector('.js-diagnostics-block');
    const pageName = diagnosticsBlock?.getAttribute('data-page') || 'unknown-page';
    log_to_client(`[JS_DIAG] Page loaded: ${pageName}`);
    log_to_server(`Page loaded: ${pageName}`, { context: 'page-load', page: pageName });
});

// Use event delegation to handle all .js-log-btn clicks, including dynamically created elements
document.addEventListener('click', function(event) {
    // Check if the clicked element is a .js-log-btn
    if (event.target.matches('.js-log-btn')) {
        const btn = event.target;
        const context = btn.getAttribute('data-js-logging-context') || 'unknown-action';
        let message = `Button clicked: ${context}`;
        
        // If the button is a send-diagnostic, include the diagnostic text if present
        if (context === 'send-diagnostic') {
            const block = btn.closest('.js-diagnostics-block');
            let value = '';
            if (block) {
                const input = block.querySelector('.js-diagnostic-text');
                if (input) value = input.value;
            }
            message += `: ${value}`;
        }
        
        // Log the action for all buttons
        log_to_client(message);
        log_to_server(message, { context });
    }
}); 