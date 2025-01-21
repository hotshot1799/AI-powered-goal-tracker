from fastapi import APIRouter
from api.v1.endpoints import auth, goals, progress, health

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(email_verification.router, prefix="/email", tags=["email_verification"])