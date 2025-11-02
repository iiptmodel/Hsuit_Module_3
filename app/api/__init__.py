# app/api/__init__.py - API Router configuration
from fastapi import APIRouter
from app.api.endpoints import reports

api_router = APIRouter()
# No authentication required - app is accessible directly
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])

