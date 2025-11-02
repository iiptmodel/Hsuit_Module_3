from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

page_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@page_router.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    """Serve the dashboard to all visitors (no authentication)."""
    return templates.TemplateResponse("dashboard.html", {"request": request})
