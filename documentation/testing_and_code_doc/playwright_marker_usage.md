

1. You need message processing in the base.html to ensure that all pages process flash messages and they don't
build and double up over time.

2. flash_messaging.jinja has the flash message processing.  The key flag for detecting uploads is:
          {% if message == "_upload_attempted" %}
            <div class="upload-marker" data-upload-attempted="true" style="display: none;"></div>
          {% endif %}

3. In flash routes when you want to signal that a download attempt (be it successful or failed) has been attempted
you include the following flash message after the post:
    if request.method == 'POST':
        flash("_upload_attempted", "internal-marker")
You will likely want to put this right before the:
    try:
        request_file = request.files.get('file')


4. in your pytesting code, replace blocks of form:
        page.set_input_files("input[type='file']", file_path)
        upload_page.wait_for_timeout(1000)  # Wait for file processing to complete

   with:
        clear_upload_attempt_marker(upload_page)
        upload_file_and_wait_for_attempt_marker(upload_page, temp_file)

5.  clear_upload_attempt_marker
        clears all previous markers of form: '.upload-marker[data-upload-attempted="true"]'

6.  upload_file_and_wait_for_attempt_marker
        1. attempts a file upload
            page.set_input_files("input[type='file']", file_path)   
        2. waits until a page with a file upload attempted flag is loaded
           this may be the same route, or a redirected route
                UPLOAD_ATTEMPT_MARKER_SELECTOR = ".upload-marker[data-upload-attempted='true']"
                expect(page.locator(UPLOAD_ATTEMPT_MARKER_SELECTOR)).to_have_count(1, timeout=timeout)


