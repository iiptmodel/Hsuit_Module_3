from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

page_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@page_router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Redirect root to chat interface."""
    return RedirectResponse("/chat")


@page_router.get("/chat", response_class=HTMLResponse)
async def read_chat(request: Request):
    """Serve the main chat interface with all features."""
    return templates.TemplateResponse("chat.html", {"request": request})
