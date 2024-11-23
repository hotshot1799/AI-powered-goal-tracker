from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.v1.router import api_router
from database import Base, engine
import logging
import os  # Add this import

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the absolute path to the static and templates directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")

# Move templates outside the function to make it globally accessible
templates = Jinja2Templates(directory=templates_dir)  # Use templates_dir here

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    
    # Mount static files with specific subdirectories
    app.mount("/static/styles", StaticFiles(directory=os.path.join(static_dir, "styles")), name="styles")
    app.mount("/static/script", StaticFiles(directory=os.path.join(static_dir, "script")), name="scripts")
    
    # Remove duplicate templates initialization
    # templates = Jinja2Templates(directory="templates")  # Remove this line
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})
    
    @app.get("/login")
    async def login_page(request: Request):
        return templates.TemplateResponse("login.html", {"request": request})
    
    @app.post("/login")
    async def login(request: Request):
        try:
            data = await request.json()
            # Return JSON response instead of redirect
            return JSONResponse(
                content={
                    "success": True,
                    "message": "Login successful",
                    "redirect": "/dashboard"
                }
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/dashboard")  # Add this route
    async def dashboard_page(request: Request):
        return templates.TemplateResponse("dashboard.html", {"request": request})
        
    @app.get("/register")
    async def register(request: Request):
        logger.info("Accessing register endpoint")
        return templates.TemplateResponse("register.html", {"request": request})
        
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "api_version": settings.VERSION}

    # Global exception handler
    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc: Exception):
        logger.error(f"Internal Server Error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "message": str(exc)}
        )

    @app.exception_handler(404)
    async def not_found_error_handler(request: Request, exc: Exception):
        logger.error(f"Not Found Error: {str(exc)}")
        return JSONResponse(
            status_code=404,
            content={"detail": "Not Found", "path": str(request.url)}
        )
        
    # Include API router with debug logging
    logger.info(f"Mounting API router at {settings.API_V1_STR}")
    app.include_router(
        api_router, 
        prefix=settings.API_V1_STR
    )
    
    @app.on_event("startup")
    async def startup():
        try:
             async with engine.begin() as conn:
                # Drop all tables
                await conn.run_sync(Base.metadata.drop_all)
                # Create all tables
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables recreated successfully")
        except Exception as e:
            logger.error(f"Error during startup: {str(e)}")
            raise

    @app.on_event("shutdown")
    async def shutdown():
        logger.info("Application shutting down...")
            
    return app

# Create the application instance
app = create_application()
wsgi_app = app

# Add middleware to log all requests
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

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting development server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
