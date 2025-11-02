# app/api/__init__.py - API Router configuration
from fastapi import APIRouter
from app.api.endpoints import auth, reports

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])

