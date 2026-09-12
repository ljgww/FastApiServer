"""Minimal FastAPI application."""

from pathlib import Path

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(
    title="FastAPI Server",
    description="A minimal API skeleton.",
    version="0.1.0",
)

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
pages = APIRouter(prefix="/page", include_in_schema=False)
api = APIRouter(prefix="/api")


@app.get("/", include_in_schema=False)
async def root(request: Request) -> RedirectResponse:
    return RedirectResponse(url=request.url_for("page_home"))


@api.get("/welcome")
async def api_welcome() -> dict[str, str]:
    return {"message": "Hello, world!"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@pages.get("", response_class=HTMLResponse)
async def page_home(request: Request, name: str = "Visitor") -> HTMLResponse:
    """Serve /page: the empty route suffix adds nothing to the router prefix."""
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"title": "Home", "visitor": name},
    )


@pages.get("/welcome", response_class=HTMLResponse)
async def page_welcome(request: Request) -> HTMLResponse:
    """Serve /page/welcome; browser JavaScript fetches /api/welcome."""
    return templates.TemplateResponse(
        request=request,
        name="api_result.html",
        context={
            "title": "Welcome message",
            "description": "Fetch the welcome message from the API.",
            "api_url": str(request.url_for("api_welcome")),
            "field": "message",
        },
    )


@pages.get("/health", response_class=HTMLResponse)
async def page_health(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="api_result.html",
        context={
            "title": "Server health",
            "description": "Run a quick server check using /health.",
            "api_url": str(request.url_for("health")),
            "field": "status",
        },
    )


app.include_router(pages)
app.include_router(api)
