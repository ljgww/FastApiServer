# Testing record — 2026-09-13

Follow-up: [Visible link testing](link_testing_2026-09-13.md) records a fresh browser run across all five HTML pages, including the GitHub destination and documentation anchors/download.

## Earlier HTTP checks (reported in the handoff)

The preceding session reported 18 passing HTTP checks covering pages, personalized greetings, API responses, documentation, redirects, 404 responses, and 405 responses with the `Allow` header. The individual assertions and full output were not supplied in the handoff, so this record preserves that result as reported, not as a fresh rerun of all 18 checks.

At handoff, form submission, browser JavaScript, refresh behavior, and Swagger execution remained untested in a browser.

## Browser connection and server startup

The handoff reported that built-in CUA failed with `CUA_REPL_ENABLED_SURFACES is required`, prompting installation of Playwright MCP. Its earlier direct verification launched visible isolated Chrome and opened `about:blank`.

In this session, after the VS Code reload, Playwright MCP tools were discovered and successfully used. The first navigation to `http://127.0.0.1:8000/` returned `ERR_CONNECTION_REFUSED`: the application was not running. Starting Uvicorn initially hit a sandbox socket permission error. A retry with escalated access succeeded, and Uvicorn reported application startup complete on port 8000.

## Actual Chrome browser results

- **Home redirect: passed.** Navigating to `/` reached `/page`, titled `Home · FastAPI demo`.
- **Name form: passed.** Filled **Your name** with `Alex`, clicked **Say hello**, and observed `/page?name=Alex` and `Hello, Alex!`.
- **Welcome page: passed.** Followed the navigation link; browser JavaScript rendered `message: Hello, world!` and the JSON payload. Clicking **Refresh** returned the same successful result.
- **Health page: passed.** Loaded `/page/health`; browser JavaScript rendered `status: ok` and its JSON payload. Clicking **Refresh** succeeded.
- **Swagger execution: passed.** Opened `/docs`, expanded `/api/welcome`, used **Try it out** and **Execute**, and observed HTTP 200 with `{"message":"Hello, world!"}`.
- **Direct welcome JSON: passed.** Browser navigation to `/api/welcome` returned HTTP 200 and `{"message":"Hello, world!"}`.
- **Direct health JSON: passed.** Browser navigation to `/health` returned HTTP 200 and `{"status":"ok"}`.
- **Absent API health route: passed.** Browser navigation to `/api/health` returned HTTP 404 and `{"Error":"404 Not Found"}`.
- **OpenAPI: passed.** Browser navigation to `/openapi.json` returned HTTP 200 and the schema JSON.
- **ReDoc: passed.** `/redoc` returned HTTP 200 and rendered the FastAPI Server documentation.
- **Loading state: passed.** Held the welcome API request using browser interception; observed `Loading…` and a disabled Refresh button.
- **Error display: passed with a simulated response.** Released the intercepted request with HTTP 503; observed `Could not load the API response (HTTP 503). Try refreshing.` and an enabled Refresh button. This was not an actual server outage.
- **Recovery: passed.** Removed interception and clicked Refresh; the real API returned and rendered `message: Hello, world!`.

## Observations and testing corrections

- The previously reported `/redocs` description typo was already corrected to `/redoc` in `templates/home.html` when inspected.
- Chrome requested `/favicon.ico`, which returned 404. This did not prevent the tested workflows from passing.
- An initial welcome-link click matched two links. The test was corrected to target the main navigation link and then passed; this was a test locator issue.
- An initial simulated-delay test used `setTimeout`, which was unavailable in the Playwright execution environment. It was replaced with a promise gate; loading, error, and recovery checks then passed.
- Expected console errors also occurred for the deliberately requested 404 and simulated 503.

## Evidence and final state

Tool results recorded page URLs, rendered text, JSON payloads, HTTP statuses, and Swagger's response output. Local Playwright artifacts included:

- `.playwright-mcp/page-2026-09-13T20-05-33-528Z.yml` — home page snapshot.
- `.playwright-mcp/page-2026-09-13T20-05-57-006Z.yml` — health page snapshot.
- `.playwright-mcp/page-2026-09-13T20-06-16-853Z.yml` — Swagger snapshot.
- `.playwright-mcp/console-2026-09-13T20-05-33-381Z.log` — favicon 404.

No application source files were changed during these tests. An existing user change to `templates/home.html` was preserved. The server was left running and Chrome was left on `/page/welcome` at the end of testing.

Browser testing is operational through Playwright MCP. This run did not establish cross-browser coverage, mobile layout coverage, timeout-specific behavior, or a new verification of every earlier HTTP assertion. See [TESTING.md](TESTING.md) for the repeatable workflow.
