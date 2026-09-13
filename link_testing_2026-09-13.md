# Visible link testing — 2026-09-13

## Scope and method

Fresh test using actual visible Chrome controlled by Playwright MCP against `http://127.0.0.1:8000`. Inspected rendered visible anchors on `/page`, `/page/welcome`, `/page/health`, `/docs`, and `/redoc`. Clicked each link from its source page, including repeated navigation links and self-links. Reloaded the source before each check. Verified destination URLs, navigation responses, and relevant rendered content. This was browser interaction, not a curl-only check.

Coverage: 16 application-page link instances and 7 documentation-page link instances. External coverage stops at the linked GitHub repository; links within GitHub were not crawled. Buttons, forms, and links revealed only after additional documentation interactions are outside this link inventory; earlier interaction tests are recorded separately.

## Application links — 16 passed

1. **/page — navigation — Home** → `/page`: PASS, HTTP 200.
2. **/page — navigation — Welcome message** → `/page/welcome`: PASS, HTTP 200.
3. **/page — navigation — Server health** → `/page/health`: PASS, HTTP 200.
4. **/page — content — Welcome message** → `/page/welcome`: PASS, HTTP 200.
5. **/page — content — Server health** → `/page/health`: PASS, HTTP 200.
6. **/page — content — API documentation** → `/docs`: PASS, HTTP 200.
7. **/page — content — API documentation (alternative)** → `/redoc`: PASS, HTTP 200.
8. **/page — content — GitHub repo** → `https://github.com/ljgww/FastApiServer`: PASS, HTTP 200.
9. **/page/welcome — navigation — Home** → `/page`: PASS, HTTP 200.
10. **/page/welcome — navigation — Welcome message** → `/page/welcome`: PASS, HTTP 200.
11. **/page/welcome — navigation — Server health** → `/page/health`: PASS, HTTP 200.
12. **/page/welcome — content — http://127.0.0.1:8000/api/welcome** → `/api/welcome`: PASS, HTTP 200.
13. **/page/health — navigation — Home** → `/page`: PASS, HTTP 200.
14. **/page/health — navigation — Welcome message** → `/page/welcome`: PASS, HTTP 200.
15. **/page/health — navigation — Server health** → `/page/health`: PASS, HTTP 200.
16. **/page/health — content — http://127.0.0.1:8000/health** → `/health`: PASS, HTTP 200.

Home destinations rendered `Hello, Visitor!`. Welcome destinations completed JavaScript loading and displayed `message: Hello, world!`; health destinations displayed `status: ok`. Direct endpoint links rendered the expected JSON. Swagger and ReDoc rendered their documentation. GitHub returned the public `ljgww/FastApiServer` repository with the expected repository title.

## Documentation links — 6 passed, 1 discrepancy

1. **Swagger `/openapi.json`: PASS.** Click opened schema JSON in a new tab; verified its contents and closed the extra tab.
2. **Swagger `default`: PASS.** Click collapsed the group to zero visible operations; another click restored both operations. The fragment changed with the expanded/collapsed state.
3. **Swagger `/health`: PASS.** Click updated the URL to `/docs#/default/health_health_get`.
4. **Swagger `/api/welcome`: PASS.** Click updated the URL to `/docs#/default/api_welcome_api_welcome_get`.
5. **ReDoc `Download`: PASS.** Click completed an `openapi.json` download with no download failure. Local artifact: `.playwright-mcp/openapi.json`.
6. **ReDoc health operation anchor: PASS.** Click reached `/redoc#operation/health_health_get` after waiting for the fragment update.
7. **ReDoc welcome operation anchor: DISCREPANCY.** The anchor href was `#operation/api_welcome_api_welcome_get`. After clicking, the welcome section appeared in the viewport, but the URL remained `/redoc#operation/health_health_get`. Waiting 30 seconds for the intended fragment timed out. Follow-up DOM inspection found the welcome section 188 pixels from the viewport top and the health section 505 pixels above it. Section navigation visibly occurred, but the expected URL fragment was not confirmed. Cause not determined; no fix made.

## Test execution notes

An initial application-link pass encountered a test-script error because the Playwright execution environment did not provide the global `URL` constructor. Replaced that use with a page-context pathname read and reran all 16 checks successfully. The initial pass is not counted as successful validation.

Immediate ReDoc URL reads were insufficient to establish anchor results, so explicit fragment waits and viewport inspection were added. The welcome fragment discrepancy above remained after that follow-up.

No application code was changed. Existing manual edits were preserved. Chrome was left on Swagger with the default group expanded. The server remained available throughout the run.

## Result

22 of 23 inventoried visible link instances passed their checks; one ReDoc fragment discrepancy remains. All 16 links on the application's own three template pages passed. This run does not replace the earlier HTTP, form, Refresh, or simulated-error checks documented in [the testing record](testing_record_2026-09-13.md).
