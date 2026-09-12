# FastAPI server

A minimal Python API built with FastAPI and served by Uvicorn. It includes a welcome endpoint, a health check, and automatically generated API documentation.

Requires Python 3.10 or newer. Server setup and startup commands below are for Linux/macOS and should be run from the project directory. Windows instructions for running curl examples are included below.

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Using `.venv/bin/python` explicitly ensures installation and startup use the same Python environment. Shell activation is not required.

## Run

```bash
.venv/bin/python -m uvicorn main:app --reload
```

The server runs at http://127.0.0.1:8000. `--reload` is intended for local development.
Stop the server with `Ctrl+C`.

`main:app` tells Uvicorn to load the `app` object from `main.py`.

## Endpoints and documentation

- `GET /` redirects to the browser home page at `/page`.
- `GET /api/welcome` returns `{"message": "Hello, world!"}`.
- `GET /health` returns `{"status": "ok"}` for a quick server check outside the `/api` routes.
- Browser home page: http://127.0.0.1:8000/page
- Welcome message page: http://127.0.0.1:8000/page/welcome (calls `GET /api/welcome`).
- Server health page: http://127.0.0.1:8000/page/health (calls `GET /health`).
- Interactive API documentation: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

HTML routes use the `/page` router prefix; application API routes use `/api`. The quick server check stays at `/health`. For example, `@pages.get("/welcome")` registers `/page/welcome`, while `@api.get("/welcome")` registers `/api/welcome`. There is no standalone `/welcome` route. `/api/welcome` replaces the previous `/api` endpoint.

`@pages.get("")` uses an empty suffix, so its full path is the router prefix `/page` plus `""`, which equals `/page`. It serves the home page. `/page/` redirects to `/page` with FastAPI's default slash handling; `/` is a separate route that redirects to `/page`. `response_class=HTMLResponse` specifies an HTML response and does not affect the URL.

## HTTP errors

HTTP errors such as unknown routes and unsupported methods return JSON with an `Error` string combining the HTTP status code and standard description, for example `{"Error":"404 Not Found"}` or `{"Error":"405 Method Not Allowed"}`. Explicit HTTP exceptions with a custom detail append that detail after the standard description. The response keeps its HTTP status code and exception headers. Request validation errors retain FastAPI's default format.

## Template example

Open http://127.0.0.1:8000/page?name=Alex to see `Hello, Alex!`, or use the name form on the home page. The route passes Python values in a context dictionary to Jinja2, which merges them into `templates/home.html` using `{{ visitor }}`. HTML values are automatically escaped.

All pages extend `templates/base.html` for shared navigation and styling. The two subpages reuse `templates/api_result.html` with different titles, API URLs, and response fields. Browser JavaScript fetches the existing JSON endpoints on page load and when you click **Refresh**; loading and failure messages appear on the page.

After pulling these changes, rerun `.venv/bin/python -m pip install -r requirements.txt` to install Jinja2, then start the server as above.

## Quick check

With the server running, open another terminal and run:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## Running `/docs` examples on Windows

The **Try it out** → **Execute** buttons at http://127.0.0.1:8000/docs send requests directly from your browser; they do not require curl. You need curl only to run the generated **Curl** command in a terminal. Keep the server running while trying either option.

### PowerShell or Command Prompt

Modern Windows 10 and Windows 11 include curl. First check it in PowerShell or Command Prompt:

```powershell
curl.exe --version
```

If a version is displayed, no installation is needed. Use `curl.exe` explicitly in PowerShell to avoid the `curl` alias used by older PowerShell versions. See [Microsoft's curl documentation](https://learn.microsoft.com/en-us/windows/curl/).

```powershell
curl.exe -X GET "http://127.0.0.1:8000/api/welcome" -H "accept: application/json"
curl.exe "http://127.0.0.1:8000/health"
```

If `curl.exe` is not found:

1. Download the ZIP matching your Windows architecture from [curl for Windows](https://curl.se/windows/).
2. Extract it to a permanent folder, for example `C:\Tools\curl`.
3. Find the extracted `bin` folder containing `curl.exe` and add that folder's full path to your user **Path** using **Edit environment variables for your account** → **Path** → **Edit** → **New**.
4. Open a new terminal and run `curl.exe --version` again.

### Git Bash (for copying Bash-style examples)

Install [Git for Windows](https://git-scm.com/downloads/win), which provides Git Bash, using its installer. Alternatively, run this in PowerShell if Windows Package Manager is available:

```powershell
winget install --id Git.Git -e --source winget
```

Open **Git Bash** from the Start menu and check curl, then try the API:

```bash
curl --version
curl -X GET \
  'http://127.0.0.1:8000/api/welcome' \
  -H 'accept: application/json'
```

You can paste the Bash-style **Curl** examples generated by `/docs` into Git Bash. Their trailing backslashes (`\`) continue a command onto the next line. PowerShell and Command Prompt use different continuation syntax, so use the single-line `curl.exe` examples above in those terminals.

## Project files

- `main.py`: FastAPI application and route handlers. Add routes here as the API grows.
- [main_code_notes.md](main_code_notes.md): Code walkthrough, template roles, and request/response flow.
- `templates/`: Jinja2 templates with a shared layout, home page, and reusable API result page.
- `requirements.txt`: FastAPI, Uvicorn, and Jinja2 dependencies.
- `.gitignore`: Excludes the virtual environment, Python caches, and local `.env` files.

## Troubleshooting

If you see `ModuleNotFoundError: No module named 'fastapi'`, dependencies are missing from the Python environment you are using. Install them and start the server with the same interpreter:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn main:app --reload
```

If `.venv/bin/python` does not exist, run the setup steps first. Dependency installation requires access to your configured Python package index; resolve any network or DNS errors before retrying.

Running `python main.py` does not start the server. Use the Uvicorn command above.
