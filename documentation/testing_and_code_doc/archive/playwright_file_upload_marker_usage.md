# Playwright Marker System for File Upload Testing

## Overview

The Playwright Marker System is a robust approach to testing file upload workflows without relying on arbitrary timeouts (`page.wait_for_timeout()`). Instead, it uses hidden DOM markers that are injected by the Flask backend to signal when upload attempts have occurred, regardless of success or failure.

## Core Components

### 1. Backend Marker Generation (`flash_messaging.jinja`)

The Flask backend creates hidden DOM markers when file uploads are attempted:

```jinja
{% if category == "internal-marker" %}
  {# 🪪 Internal test marker: invisible to users, visible to Playwright #}
  {% if message == "_upload_attempted" %}
    <div class="upload-marker" data-upload-attempted="true" style="display: none;"></div>
  {% endif %}
{% endif %}
```

### 2. Flask Route Integration

All upload routes flash the marker immediately when a POST request is received:

```python
if request.method == 'POST':
    flash("_upload_attempted", "internal-marker")
    try:
        request_file = request.files.get('file')
        # ... process file upload
```

### 3. Helper Functions (`upload_helpers.py`)

Three key functions provide different levels of control:

#### `upload_file_and_wait_for_attempt_marker(page, file_path, timeout=10000)`
**Purpose**: Complete upload workflow - sets file input AND waits for marker
**When to use**: When you want to upload a file and wait for the marker in one step
**Behavior**: 
- Calls `page.set_input_files("input[type='file']", file_path)`
- Waits for `.upload-marker[data-upload-attempted='true']` to appear

#### `wait_for_upload_attempt_marker(page, timeout=7000)`
**Purpose**: Wait-only function - does NOT upload the file
**When to use**: When `page.set_input_files()` causes immediate page navigation/redirect
**Behavior**: 
- Only waits for `.upload-marker[data-upload-attempted='true']` to appear
- Does NOT perform file upload

#### `clear_upload_attempt_marker(page)`
**Purpose**: Remove previous markers to prevent stale state
**When to use**: Before each new upload attempt in the same test session
**Behavior**: 
- Removes all `.upload-marker[data-upload-attempted='true']` elements from DOM

## Key Decision: Which Function to Use?

### Use `upload_file_and_wait_for_attempt_marker()` when:
- The upload form stays on the same page after file selection
- No immediate navigation/redirect occurs
- You want the simplest one-step approach

### Use `wait_for_upload_attempt_marker()` when:
- `page.set_input_files()` triggers immediate page navigation
- The file input element disappears after upload (redirects to `/review_staged/`)
- You need to handle the upload and wait separately

## Common Patterns and Examples

### Pattern 1: Simple Upload (No Navigation)
```python
# Clear any previous markers
clear_upload_attempt_marker(page)

# Upload and wait for marker in one step
upload_file_and_wait_for_attempt_marker(page, file_path)
```

### Pattern 2: Upload with Navigation
```python
# Clear any previous markers
clear_upload_attempt_marker(page)

# Upload file (causes navigation)
page.set_input_files("input[type='file']", file_path)

# Wait for marker on the new page
wait_for_upload_attempt_marker(page)
```

### Pattern 3: Using Page Locator
```python
# Clear any previous markers
clear_upload_attempt_marker(page)

# Get file input and upload
file_input = page.locator("input[type='file']")
file_input.set_input_files(file_path)

# Wait for marker (may be on redirected page)
wait_for_upload_attempt_marker(page)
```

## Multiple File Upload Scenarios

### How the Portal Handles Multiple Files

**Important**: The portal is designed for **single file uploads per request**. When examining the Flask routes:

1. **Single File Processing**: All routes use `request.files.get('file')` (singular)
2. **One Marker Per Request**: Each POST request generates exactly one `_upload_attempted` marker
3. **Sequential Uploads**: Multiple files must be uploaded in separate requests

### Testing Multiple File Uploads

The `two_staged_files` fixture demonstrates the correct approach:

```python
# Upload first file
navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged")
clear_upload_attempt_marker(page)
file_input = page.locator("input[type='file']")
file_input.set_input_files(file_path1)
wait_for_upload_attempt_marker(page)

# Navigate back and upload second file
navigate_and_wait_for_ready(page, f"{BASE_URL}/upload_staged")
clear_upload_attempt_marker(page)
file_input = page.locator("input[type='file']")
file_input.set_input_files(file_path2)
wait_for_upload_attempt_marker(page)
```

### Why This Works

1. **Each upload is a separate POST request** to the Flask route
2. **Each request generates its own marker** via `flash("_upload_attempted", "internal-marker")`
3. **Markers are cleared between uploads** to prevent interference
4. **Navigation between uploads** ensures clean state

## Migration Guide: Replacing `wait_for_timeout()`

### Before (Problematic):
```python
page.set_input_files("input[type='file']", file_path)
page.wait_for_timeout(1000)  # ❌ Arbitrary timeout
```

### After (Robust):
```python
# Clear any previous upload attempt markers
clear_upload_attempt_marker(page)

# Upload file using Playwright's set_input_files
page.set_input_files("input[type='file']", file_path)

# Wait for the upload attempt marker to appear (may be on redirected page)
wait_for_upload_attempt_marker(page)
```

## Common Pitfalls and Solutions

### Pitfall 1: Double Upload Attempts
**Problem**: Calling `upload_file_and_wait_for_attempt_marker()` after already calling `set_input_files()`
```python
# ❌ WRONG - Double upload attempt
file_input.set_input_files(file_path)
upload_file_and_wait_for_attempt_marker(page, file_path)  # Tries to upload again!
```

**Solution**: Use `wait_for_upload_attempt_marker()` after manual `set_input_files()`
```python
# ✅ CORRECT
file_input.set_input_files(file_path)
wait_for_upload_attempt_marker(page)
```

### Pitfall 2: Stale Markers
**Problem**: Previous test uploads leave markers that interfere with new tests
```python
# ❌ WRONG - May pick up old marker
page.set_input_files("input[type='file']", file_path)
wait_for_upload_attempt_marker(page)
```

**Solution**: Always clear markers before new uploads
```python
# ✅ CORRECT
clear_upload_attempt_marker(page)
page.set_input_files("input[type='file']", file_path)
wait_for_upload_attempt_marker(page)
```

### Pitfall 3: Missing Navigation Handling
**Problem**: Not accounting for page redirects after upload
```python
# ❌ WRONG - May fail if page navigates
upload_file_and_wait_for_attempt_marker(page, file_path)
page.locator("input[type='file']")  # Element may not exist after redirect
```

**Solution**: Use `wait_for_upload_attempt_marker()` for navigation scenarios
```python
# ✅ CORRECT
clear_upload_attempt_marker(page)
page.set_input_files("input[type='file']", file_path)
wait_for_upload_attempt_marker(page)  # Works even after navigation
```

## Best Practices

### 1. Always Clear Markers First
```python
clear_upload_attempt_marker(page)  # Prevent stale state
```

### 2. Choose the Right Function
- **Navigation expected**: Use `wait_for_upload_attempt_marker()`
- **No navigation**: Use `upload_file_and_wait_for_attempt_marker()`

### 3. Handle Multiple Files Sequentially
```python
for file_path in file_paths:
    clear_upload_attempt_marker(page)
    page.set_input_files("input[type='file']", file_path)
    wait_for_upload_attempt_marker(page)
    # Navigate back if needed for next upload
```

### 4. Use Descriptive Comments
```python
# Clear any previous upload attempt markers
clear_upload_attempt_marker(page)

# Upload file using Playwright's set_input_files
page.set_input_files("input[type='file']", file_path)

# Wait for the upload attempt marker to appear (may be on redirected page)
wait_for_upload_attempt_marker(page)
```

## Troubleshooting

### Marker Not Found
**Symptoms**: `TimeoutError` waiting for marker
**Causes**:
- Flask route not calling `flash("_upload_attempted", "internal-marker")`
- Page navigation before marker appears
- JavaScript errors preventing DOM updates

**Solutions**:
- Verify Flask route includes the flash call
- Increase timeout if needed
- Check browser console for JavaScript errors

### Multiple Markers Found
**Symptoms**: Test passes but may be unreliable
**Causes**: Previous uploads left markers in DOM
**Solutions**:
- Always call `clear_upload_attempt_marker(page)` before uploads
- Ensure proper test isolation

### Element Not Found After Upload
**Symptoms**: `TimeoutError` on `set_input_files()`
**Causes**: Page navigation after file selection
**Solutions**:
- Use `wait_for_upload_attempt_marker()` instead of `upload_file_and_wait_for_attempt_marker()`
- Handle navigation explicitly

## Summary

The Playwright Marker System provides a robust, timeout-free approach to testing file uploads by:

1. **Using DOM markers** instead of arbitrary timeouts
2. **Handling page navigation** gracefully
3. **Supporting multiple file uploads** through sequential requests
4. **Providing clear function separation** for different use cases

The key is understanding when to use `upload_file_and_wait_for_attempt_marker()` vs `wait_for_upload_attempt_marker()` based on whether page navigation occurs during the upload process.


