# Testing guide

> Visibility correction: Chrome automation executed successfully, but the user reported that no browser testing was visible to them. A headed/visible launch configuration does not establish that its window is on the user’s current desktop. User-visible testing remains unconfirmed; the results below establish automated browser execution only.

The project has been checked using HTTP requests and an actual Chrome browser controlled through Playwright MCP. These are separate kinds of verification: HTTP checks do not execute page JavaScript or exercise forms and buttons.

See [the testing record](testing_record_2026-09-13.md) for completed checks, evidence, and limitations.

See [the visible link test record](link_testing_2026-09-13.md) for the fresh per-link results across application, Swagger, and ReDoc pages (22 passed, one ReDoc fragment discrepancy).

## Start the application

From the project directory (`/opt/dev/private/fastapi`, previously accessed as `/home/lj/dev/private/fastapi`):

```bash
.venv/bin/python -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000/. If the browser reports connection refused, check that Uvicorn is running. An agent sandbox may require additional access to bind the local server socket.

## Browser setup used

The session used Playwright MCP with Chrome in visible, isolated mode. The registration command reported in the previous session was:

```bash
codex mcp add playwright -- npx -y @playwright/mcp@0.0.80 --browser chrome --isolated
```

The user enabled the server in Codex settings and reloaded the VS Code window. After that reload, Playwright navigation and interaction tools were available and successfully controlled Chrome. This records the setup used; registration does not need to be repeated for each test.

## Repeatable browser checks

1. Open `/` and verify it redirects to `/page`.
2. Enter `Alex` in **Your name**, click **Say hello**, and verify `/page?name=Alex` displays `Hello, Alex!`.
3. Follow **Welcome message**. Verify `message: Hello, world!` and the matching JSON. Click **Refresh** and verify the result returns.
4. Open `/page/health`. Verify `status: ok` and the matching JSON. Click **Refresh** and verify the result returns.
5. Open `/docs`, expand `/api/welcome`, click **Try it out**, then **Execute**. Verify HTTP 200 and `{"message":"Hello, world!"}`.
6. Open `/redoc` and verify the documentation renders. Open `/openapi.json` and verify the schema loads.
7. Navigate directly to `/api/welcome` and `/health`; verify their JSON responses. Open `/api/health` and verify HTTP 404 with `{"Error":"404 Not Found"}`. Keep the health endpoint outside `/api`.
8. With Playwright request interception, temporarily hold the `/api/welcome` response. Verify **Loading…** and a disabled **Refresh** button. Release it as HTTP 503 and verify an error message and an enabled button. Remove interception, click **Refresh**, and verify successful recovery. Always remove interception even if the test fails.

The main navigation and home content both contain a **Welcome message** link. Scope automated clicks to the navigation or content area to avoid an ambiguous locator.

## Scope

These were interactive, agent-driven checks, not a committed automated test suite. Browser snapshots and console logs may be present in `.playwright-mcp/`; they are local session artifacts. Recheck server and tool availability in a new session rather than assuming processes persisted.
