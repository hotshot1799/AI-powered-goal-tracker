# backend/main.py

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import JSONResponse
from core.config import settings
import logging

logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
    )

    allowed_origins = [
        "http://localhost:4000",
        "http://localhost:5173",
        "http://localhost:19006",  # React Native Expo default
        "http://localhost:19000",  # React Native Expo alternative
        "http://10.0.2.2:8000",   # Android Emulator
        "capacitor://localhost",   # Capacitor mobile app
        "https://ai-powered-goal-tracker-z0co.onrender.com",
        "http://ai-powered-goal-tracker-z0co.onrender.com",
        "https://ai-powered-goal-tracker.onrender.com",
        "http://ai-powered-goal-tracker.onrender.com"
    ]

    # Session middleware (must be added before CORS)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="session",
        same_site="none",
        https_only=True,
        max_age=86400,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for mobile app
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )

    @app.get("/")
    async def root():
        """Root endpoint for health checks"""
        return JSONResponse({
            "status": "healthy",
            "message": "AI-Powered Goal Tracker API is running",
            "version": settings.VERSION
        })

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return JSONResponse({
            "status": "ok",
            "uptime": "available",
            "services": {
                "api": "healthy",
                "database": "connected"
            }
        })

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        logger.info(f"Origin: {request.headers.get('origin')}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        try:
            response = await call_next(request)
            logger.info(f"Response Status: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting application...")
        try:
            # Add any startup tasks here
            logger.info("Application started successfully")
        except Exception as e:
            logger.error(f"Startup error: {str(e)}")
            raise

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down application...")
        try:
            # Add any cleanup tasks here
            logger.info("Application shutdown completed")
        except Exception as e:
            logger.error(f"Shutdown error: {str(e)}")
            raise

    # Include API router
    from api.v1.router import api_router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app

app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")