/**
 * e2e_testing_related.js
 * -----------------------
 * This script defines a general-purpose readiness signal for end-to-end (E2E) testing.
 * It injects a stable, cross-page flag into the DOM that signals when the page is likely
 * ready for Playwright or similar test automation tools to interact with it safely.
 *
 * Usage:
 * ------
 * 1. Include this script in your base.html template (typically near the bottom of <body>):
 *
 *     <script src="{{ url_for('static', filename='js/e2e_testing_related.js') }}"></script>
 *
 * 2. In your Playwright tests, replace fragile load-state or timeout waits with:
 *
 *     page.goto(url, wait_until="load")
 *     page.wait_for_selector("html[data-e2e-ready='true']", timeout=7000)
 *
 *    You can then optionally follow this with:
 *
 *     page.wait_for_selector("#upload-form", timeout=3000)
 *
 *    This allows you to use a general readiness gate first, and a specific one afterward.
 *
 * Rationale:
 * ----------
 * In modern web applications, especially those using JavaScript enhancements (date pickers,
 * modals, async widgets), simply waiting for the browser's 'load' event or using
 * `page.wait_for_load_state("networkidle")` is unreliable:
 *
 * - `window.onload` only signals that static assets (HTML, JS, CSS, images) are downloaded.
 * - `networkidle` can hang indefinitely if there are background polling or analytics beacons.
 * - Arbitrary timeouts (`wait_for_timeout`) introduce flakiness and fragility.
 *
 * Instead, this script provides a *unified readiness signal* that layers multiple
 * browser signals:
 *
 *     window.onload
 *       ↳ requestAnimationFrame (wait for next paint frame)
 *         ↳ requestIdleCallback (wait for JS to finish initializing)
 *           ↳ SET ATTRIBUTE: <html data-e2e-ready="true">
 *
 * Strengths:
 * ----------
 * ✅ General-purpose — no per-page customization required.
 * ✅ Framework-agnostic — works with Flask, vanilla JS, or enhanced apps.
 * ✅ Avoids Playwright flake — no fragile timeouts or `networkidle` stalls.
 * ✅ Reliable test anchor — single attribute to signal full readiness.
 * ✅ Lightweight — no external libraries required.
 *
 * Limitations:
 * ------------
 * ❌ Does not guarantee async data (e.g. AJAX API calls) are complete.
 * ❌ Does not wait for long-running animations or intentionally deferred DOM changes.
 * ❌ Assumes the app becomes idle shortly after initial load (which is typically true in server-rendered apps).
 *
 * Placement in base.html:
 * ------------------------
 * ✅ Place the script near the **bottom of <body>**, *before* any optional footer JS blocks.
 * ✅ Do NOT defer or async this script — it must run as soon as the page's load event fires.
 * ✅ Avoid placing it after `{% block footer_js %}` or `{% block scripts %}` unless you
 *    explicitly want it to depend on page-specific logic.
 *
 *
 * Why this order matters:
 * ------------------------
 * - Footer blocks are usually for page-specific scripts (widgets, analytics, charts).
 * - Those scripts may fail or delay unexpectedly.
 * - The E2E marker should run after core rendering, but not be blocked by optional content.
 *

 * Deeper Context and FAQ:
 * -----------------------
 *
 * Q1: Why is the Playwright timeout set to 7000ms?
 * ------------------------------------------------
 * This is a practical, not strict, value. While many pages settle in 2–4 seconds,
 * we’ve observed that 7 seconds provides headroom for slow CI environments or pages with
 * mild JS delays. It's a balance between test stability and failure responsiveness.
 *
 * Adjust per test if needed. For fast pages, 3000–5000ms is often sufficient.
 *
 * Q2: Can I wait for additional elements after this?
 * --------------------------------------------------
 * Yes. In fact, it's common and encouraged. This script gives you a general readiness
 * flag. For any page-specific widgets (e.g. "#upload-form", ".chart-container"),
 * simply add a follow-up wait:
 *
 *     page.wait_for_selector("html[data-e2e-ready='true']", timeout=7000)
 *     page.wait_for_selector("#upload-form", timeout=3000)
 *
 * Q3: What happens if this readiness check is inadequate?
 * --------------------------------------------------------
 * If the readiness attribute is never set (e.g. broken script or browser error), Playwright
 * will raise:
 *
 *     TimeoutError: page.wait_for_selector: Timeout 7000ms exceeded.
 *     Selector 'html[data-e2e-ready="true"]' was not found
 *
 * If it is set too early and DOM elements are still initializing, subsequent selectors
 * may fail with:
 *
 *     TimeoutError: Selector '#upload-form' was not found
 *     or
 *     ElementHandleError: Element is not visible
 *
 * In either case, adjust your test to wait for a more specific signal, increase the timeout,
 * or inspect whether the `data-e2e-ready` script executed successfully (e.g. log to console).
 *
 */

(function () {
    if (typeof window === "undefined" || typeof document === "undefined") return;

    // Check if we're already marked as ready (prevent duplicate marking)
    if (document.documentElement.hasAttribute("data-e2e-ready")) return;

    // Layered readiness signal using onload → rAF → idle callback
    window.addEventListener("load", () => {
        requestAnimationFrame(() => {
            if ("requestIdleCallback" in window) {
                requestIdleCallback(() => {
                    document.documentElement.setAttribute("data-e2e-ready", "true");
                });
            } else {
                // Fallback for older browsers
                setTimeout(() => {
                    document.documentElement.setAttribute("data-e2e-ready", "true");
                }, 50);
            }
        });
    });
})();
  