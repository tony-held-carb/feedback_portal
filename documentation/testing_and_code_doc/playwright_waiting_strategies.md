# Playwright Waiting & Synchronization Strategies for E2E Testing

## **Context: Why This Matters for Our Project**

- Our Excel upload portal uses modals, overlays, and backend redirects for file review and discard workflows.
- E2E tests (using Playwright) often fail or flake due to asynchronous UI/backend updates—tests may check for results before the app has finished updating.
- Manual testing works because humans naturally wait for the UI to reload, but E2E scripts are much faster and need explicit waits.

## **Common Asynchrony Problems in E2E Testing**
- UI/network/backend operations are not instant.
- Tests may click a button and immediately check for a result, before the UI/backend is ready.
- This leads to false negatives and unreliable tests.

## **Playwright's Waiting/Synchronization Tools**

| Tool/Method                          | When to Use                                      |
|---------------------------------------|--------------------------------------------------|
| `wait_for_navigation()`               | After actions that trigger a full page reload     |
| `wait_for_load_state("networkidle")` | After actions that trigger network requests or reloads |
| `expect(locator).to_be_visible()`     | Waiting for modals, overlays, or UI changes      |
| `wait_for_response()`                 | Waiting for specific backend API calls           |
| `wait_for_timeout(ms)`                | Only as a last resort for slow/unstable systems  |

### **Practical Examples**

**After clicking a modal confirm that submits a form:**
```python
confirm_btn.click()
page.wait_for_navigation()  # or page.wait_for_load_state("networkidle")
# Now check that the file is gone
assert filename not in page.content()
```

**Waiting for a modal to appear:**
```python
expect(page.locator('#discardConfirmModal')).to_be_visible()
```

**Waiting for a specific backend response:**
```python
with page.expect_response("**/discard_staged_update/**"):
    confirm_btn.click()
```

## **Using `with page.expect_navigation(): ...` for Navigation-triggering Actions**

### **When to Use**
- Use `with page.expect_navigation(): ...` whenever you perform an action (like clicking a button or submitting a form) that you expect will trigger a full page navigation or redirect.
- This is especially important for:
  - Modal confirm buttons that submit forms
  - Submit buttons on forms that redirect
  - Any action that causes the browser to load a new page

### **How to Use**
```python
# Correct usage for modal confirm that triggers a redirect
with page.expect_navigation():
    confirm_btn.click()
# Now the test will only proceed after the navigation is complete
assert filename not in page.content()
```
- The context manager ensures Playwright waits for the navigation event to finish before moving to the next line.
- This prevents race conditions where the test checks the page before the new content is loaded.

### **Why This is Preferred**
- It is more robust than simply calling `page.wait_for_load_state()` after a click, because it directly ties the wait to the navigation event triggered by the action.
- It avoids flakiness and makes tests more reliable, especially for workflows involving modals and backend redirects (like our discard/confirm flows).

## **Recommendations for Our Project**
- Always wait for navigation or network idle after actions that trigger backend changes and UI reloads.
- Use `expect(locator).to_be_visible()` for modals and overlays.
- Avoid `wait_for_timeout` unless absolutely necessary.
- Scrape overlays/logs **before** navigation if you want to capture transient frontend state.
- Use `with page.expect_navigation(): ...` for any action that triggers a redirect or full page reload.

## **Summary**
- Robust E2E tests require explicit waits to synchronize with the app's real state.
- Playwright provides a rich suite of tools to handle this.
- Applying these best practices will make our diagnostics and discard tests reliable and maintainable. 