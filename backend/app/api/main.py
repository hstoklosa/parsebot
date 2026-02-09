from fastapi import APIRouter

from app.api.routes import extract

api_router = APIRouter(
    prefix="/api",
    tags=["api"],
)

api_router.include_router(extract.router)