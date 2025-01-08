from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from core.config import settings
from api.v1.router import api_router
from database import Base, engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_allowed_origins():
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://ai-powered-goal-tracker-z0co.onrender.com",
        "http://ai-powered-goal-tracker-z0co.onrender.com"
    ]
    logger.info(f"Allowed origins: {origins}")
    return origins

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    allowed_origins = get_allowed_origins()

    # CORS middleware must be the first middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )
    
    # Session middleware
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="session",
        same_site="lax",
        https_only=True,
        max_age=1800
    )

    # Add CORS headers middleware
    @app.middleware("http")
    async def add_cors_headers(request: Request, call_next):
        response = await call_next(request)
        origin = request.headers.get("origin")
        
        if origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            
        return response

    # CORS preflight handler
    @app.options("/{full_path:path}")
    async def options_handler(request: Request, full_path: str):
        origin = request.headers.get("origin")
        if origin in allowed_origins:
            headers = {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "3600",
            }
            return Response(status_code=200, headers=headers)
        return Response(status_code=400)

    # Health check route
    @app.get("/")
    async def root():
        return {
            "status": "healthy",
            "message": "API is running",
            "allowed_origins": allowed_origins
        }

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

app = create_application()

# Request logging middleware
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

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting development server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)