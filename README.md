# FastAPI server

A minimal Python API built with FastAPI and served by Uvicorn. It includes a welcome endpoint, a health check, and automatically generated API documentation.

Requires Python 3.10 or newer. The commands below are for Linux/macOS and should be run from the project directory.

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
- `GET /api` returns `{"message": "Hello, world!"}`.
- `GET /health` returns `{"status": "ok"}`.
- Browser home page: http://127.0.0.1:8000/page
- Welcome message page: http://127.0.0.1:8000/page/welcome (calls `GET /api`).
- Server health page: http://127.0.0.1:8000/page/health (calls `GET /health`).
- Interactive API documentation: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

## Template example

Open http://127.0.0.1:8000/page?name=Alex to see `Hello, Alex!`, or use the name form on the home page. The route passes Python values in a context dictionary to Jinja2, which merges them into `templates/home.html` using `{{ visitor }}`. HTML values are automatically escaped.

All pages extend `templates/base.html` for shared navigation and styling. The two subpages reuse `templates/api.html` with different titles, API URLs, and response fields. Browser JavaScript fetches the existing JSON endpoints on page load and when you click **Refresh**; loading and failure messages appear on the page.

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

## Project files

- `main.py`: FastAPI application and route handlers. Add routes here as the API grows.
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
