from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from core.config import settings
from api.v1.router import api_router
from database import Base, engine
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Middleware setup
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="session",
        same_site="lax",
        https_only=True,
        max_age=1800
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check route
    @app.get("/")
    async def root():
        return {"status": "healthy", "message": "API is running"}

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    @app.on_event("startup")
    async def startup():
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Startup error: {str(e)}")
            raise

    return app

# Create application instance
app = create_application()

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response Status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise

# WSGI application
wsgi_app = app

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting development server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)