# How this FastAPI server works

This document explains the current [main.py](main.py), the templates it renders, and how the application answers HTTP requests. See [README.md](README.md) for installation and terminal commands.

## Overall structure

Uvicorn listens for HTTP requests and passes them to the FastAPI application. FastAPI selects a handler using the request method and URL path. That handler returns a redirect, JSON data, or rendered HTML.

The application has three groups of routes:

- `/page` and `/page/...` serve browser pages.
- `/api/...` serves application data as JSON.
- `/health` provides a quick server check outside the API prefix.

The root path `/` redirects to the home page at `/page`.

There is no database or stored application state. The welcome message and health status are fixed values. A personalized greeting comes from the current request's query string.

## Startup: how `main.py` becomes a server

Run this from the project directory:

```bash
.venv/bin/python -m uvicorn main:app --reload
```

`main:app` means “import the Python module `main` and use its object named `app`.” Uvicorn implements ASGI, the interface through which it exchanges request and response events with FastAPI. `--reload` restarts the application when development source changes are detected.

When Python imports `main.py`, it executes the module-level statements: imports, application creation, template and router setup, route decorators, and router registration. The handler function bodies run later, when matching requests arrive. Running `python main.py` alone does not start Uvicorn or open a listening port.

## Imports and application setup

```python
from pathlib import Path

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
```

- `Path` builds the filesystem path to the templates directory.
- `FastAPI` creates the application object used by Uvicorn.
- `APIRouter` groups handlers under a common URL prefix.
- `Request` provides details about the incoming request and supports named URL generation.
- `HTMLResponse` identifies responses containing HTML.
- `RedirectResponse` tells the client to request another URL.
- `Jinja2Templates` connects Jinja2 template rendering to the application.

`app = FastAPI(...)` sets the title, description, and version used in the generated API documentation. These metadata values do not set a URL prefix or start the server.

```python
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
```

`__file__` identifies `main.py`; its parent is the containing directory. The expression locates the sibling `templates` folder relative to this module, rather than assuming templates are in the terminal's current directory. Template filenames are filesystem resources, not automatically exposed web paths.

## Routers, decorators, and full paths

```python
pages = APIRouter(prefix="/page", include_in_schema=False)
api = APIRouter(prefix="/api")
```

A router prefix is prepended to each route declared on that router:

```python
@pages.get("")          # GET /page
@pages.get("/welcome")  # GET /page/welcome
@pages.get("/health")   # GET /page/health
@api.get("/welcome")    # GET /api/welcome
```

These lines illustrate the decorators used above their corresponding functions; they are not a separate code block to add to the application.

The empty string in `@pages.get("")` is an empty suffix: `/page` + `""` = `/page`. It does not match every URL or represent the application root. With the current default slash handling, a request to `/page/` redirects to `/page`.

Routes declared directly on `app`, such as `@app.get("/health")`, have no router prefix. There are no handlers at `/welcome`, `/pages`, `/api`, or `/api/health`.

The `.get(...)` decorator registers the function below it as a handler for the HTTP GET method. `response_class=HTMLResponse` describes the response format; it does not affect URL matching. `include_in_schema=False` omits the page routes from OpenAPI and `/docs`; it does not disable them or restrict access.

At the end of `main.py`:

```python
app.include_router(pages)
app.include_router(api)
```

These statements attach the routers' registered routes to the application. The direct `app` routes are already registered.

## Each handler in `main.py`

### `root`: redirect from `/`

```python
@app.get("/", include_in_schema=False)
async def root(request: Request) -> RedirectResponse:
    return RedirectResponse(url=request.url_for("page_home"))
```

FastAPI supplies the `Request` object. `request.url_for("page_home")` finds the route named after the `page_home` function and builds its URL using the request context. This avoids hardcoding `/page` into the redirect.

`RedirectResponse` defaults to HTTP 307 and includes the destination in the `Location` header. The browser follows that redirect with a separate request to `/page`. This function does not itself render the home template. Plain curl shows the redirect response; `curl -L` follows it.

### `api_welcome`: JSON at `/api/welcome`

This handler returns the Python dictionary `{"message": "Hello, world!"}`. FastAPI serializes it to a JSON response with status 200 and content type `application/json`.

The return annotation `dict[str, str]` declares a dictionary whose keys and values are strings. FastAPI uses the declared return type for response validation, serialization, and schema generation. No HTML template is involved in this handler.

### `health`: JSON at `/health`

This handler returns `{"status": "ok"}` as JSON with status 200. It stays directly on `app`, outside `/api`, for a quick server check.

It confirms that the application can answer this request. It does not check a database, external service, or other dependency.

### `page_home`: HTML at `/page`

```python
async def page_home(request: Request, name: str = "Visitor") -> HTMLResponse:
```

FastAPI injects `request`. Because `name` is a simple parameter that is not part of the path, FastAPI reads it from the query string. If it is absent, the default is `"Visitor"`.

For `/page?name=Alex`, the handler passes this context to `home.html`:

```python
{"title": "Home", "visitor": "Alex"}
```

`templates.TemplateResponse(...)` renders the chosen template using that context and returns HTML. Jinja2 replaces `{{ visitor }}` with the supplied name, while `title` is used by the shared layout. The browser receives the rendered greeting, not the Jinja2 source.

### `page_welcome`: HTML at `/page/welcome`

This handler renders `api_result.html` with a title, explanatory text, the URL of `api_welcome`, and `field="message"`.

The Python handler generates the page but does not call `api_welcome`. After the browser receives the HTML, the template's JavaScript makes a separate request to `/api/welcome` and displays its JSON result.

### `page_health`: HTML at `/page/health`

This handler reuses `api_result.html` with health-specific text, the URL of `health`, and `field="status"`. The browser then requests `/health`.

`/page/health` is the human-facing display; `/health` is the lightweight server check. The shared template's variable `api_url` holds the endpoint to fetch, including `/health`; that variable name does not assign the endpoint to the `/api` router.

### Why the handlers use `async def`

These functions are asynchronous handlers that FastAPI awaits. The current Python handler bodies contain no asynchronous I/O to await: they return small dictionaries, redirects, or template responses. Declaring a function `async` does not move its work to a separate thread or make blocking work nonblocking.

## Templates and browser behavior

### [templates/base.html](templates/base.html)

This is the shared HTML document. It defines the language, character encoding, mobile viewport, page title, inline CSS, and navigation links. `{% block content %}` marks the place where each child template supplies its page content.

Template calls such as `url_for('page_welcome')` generate links from registered route names. Links remain tied to the handler names even when their URL paths change.

### [templates/home.html](templates/home.html)

`{% extends "base.html" %}` reuses the shared document, and `{% block content %}` supplies the greeting, form, and links. `{{ ... }}` inserts values; `{% ... %}` controls template structure.

The form uses `method="get"`. Submitting a name navigates to `/page?name=...`, so FastAPI runs `page_home` again and renders a new greeting. This interaction does not call the JSON API or require custom JavaScript.

The links open the welcome page, health page, automatic `/docs` UI, and the external GitHub repository. The docs link uses FastAPI's built-in route name `swagger_ui_html`.

Jinja2's HTML autoescaping renders characters such as `<` safely in inserted text and attributes. For example, a supplied name containing HTML is displayed as text instead of becoming an HTML element.

### [templates/api_result.html](templates/api_result.html)

This reusable HTML view displays an endpoint's JSON response. Its filename does not define a URL or replace an API handler. Both page handlers explicitly select it through `TemplateResponse`.

The template first renders a heading, description, endpoint link, loading message, response area, and Refresh button. Its script then:

1. Reads the endpoint URL and field name inserted by Jinja2's `tojson` filter. This filter produces safely encoded JavaScript values instead of manually constructing quoted strings.
2. Runs `load()` immediately and also registers it for Refresh clicks.
3. Disables Refresh, displays `Loading…`, and clears the previous JSON output.
4. Calls `fetch()` with `cache: "no-store"` and a 10-second timeout signal.
5. Checks the HTTP result. An unsuccessful status becomes an error; a successful response is parsed as JSON.
6. Displays `data[field]`, such as the welcome message or health status, and a formatted copy of the complete JSON response.
7. Shows an error message if the request, timeout, or JSON parsing fails, and re-enables Refresh in `finally`.

The browser uses `textContent` to display returned data, so the data is treated as text rather than inserted HTML. A `<noscript>` message directs users without JavaScript to the endpoint link. HTML rendering happens on the server; this script runs in the browser.

## Complete request examples

### Opening the site root

1. The browser sends `GET /` to Uvicorn.
2. FastAPI selects `root`, which returns a 307 redirect to `/page`.
3. The browser sends `GET /page`.
4. FastAPI selects `page_home` and uses `name="Visitor"`.
5. Jinja2 renders `home.html` within `base.html`.
6. The server sends a 200 HTML response, and the browser displays `Hello, Visitor!`.

### Opening the welcome page

1. The browser sends `GET /page/welcome`.
2. `page_welcome` renders `api_result.html` within `base.html`, setting the fetch URL to `/api/welcome`.
3. The server returns 200 HTML.
4. The browser executes the included JavaScript and sends `GET /api/welcome`.
5. FastAPI selects `api_welcome`, which returns the welcome dictionary as 200 JSON.
6. The browser updates the result and JSON areas without navigating away from the page.

These are two separate HTTP requests: one for HTML and one for JSON. Clicking Refresh repeats only the JSON request.

### Running a direct health check

`curl http://127.0.0.1:8000/health` sends one request. FastAPI calls `health` and returns `{"status":"ok"}`. There is no redirect, template rendering, or browser JavaScript in this flow.

### Unmatched paths and methods

An unknown path such as `/pages` returns HTTP 404. An unsupported method on an existing route, such as `POST /api/welcome`, returns HTTP 405. The current application relies on FastAPI's default handling for these responses.

## Automatic API documentation

FastAPI provides `/openapi.json` for the machine-readable API schema, `/docs` for Swagger UI, and `/redoc` for an alternative documentation UI. These routes are created by `FastAPI(...)`; they do not need handlers in `main.py`.

The schema includes `/api/welcome` and `/health`. The root redirect and page routes are excluded by `include_in_schema=False`. In `/docs`, **Try it out** and **Execute** send requests from the browser. curl is needed only when copying a generated curl command into a terminal.

## Other files consulted

- [requirements.txt](requirements.txt) declares FastAPI, Uvicorn with its standard extras, and Jinja2. Installing it supplies the application framework, HTTP server, and template engine. The version ranges allow compatible candidate releases within the stated bounds; they do not lock an exact environment.
- [.gitignore](.gitignore) excludes the virtual environment, Python caches, `.env`, and pytest cache from normal Git tracking. It does not configure server behavior or load environment variables.
- [README.md](README.md) documents setup, routes, template examples, curl usage on Windows, and troubleshooting. It is an operating guide; this file explains the implementation.

## Where to make future changes

Add application JSON handlers to `api` with `@api.get("/...")`, and HTML handlers to `pages` with `@pages.get("/...")`, before the corresponding `app.include_router(...)` calls. Keep the quick server check on `/health`.

Change shared navigation or styling in `base.html`, the home form and links in `home.html`, and the common JSON result display in `api_result.html`. For a different page layout, create another template and select it from an HTML handler. A new template file alone does not create a route.
