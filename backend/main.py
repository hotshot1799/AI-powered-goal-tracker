from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings
from api.v1.router import api_router
from database import Base, engine, get_db
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")

# Templates configuration
templates = Jinja2Templates(directory=templates_dir)

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

    # Static files
    app.mount("/static/styles", StaticFiles(directory=os.path.join(static_dir, "styles")), name="styles")
    app.mount("/static/script", StaticFiles(directory=os.path.join(static_dir, "script")), name="scripts")
    
    # Template Routes
    @app.get("/")
    async def root(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})
    
    @app.get("/login")
    async def login_page(request: Request):
        if request.session.get('user_id'):
            return RedirectResponse(url="/dashboard")
        return templates.TemplateResponse("login.html", {"request": request})
    
    @app.get("/register")
    async def register_page(request: Request):
        return templates.TemplateResponse("register.html", {"request": request})
    
    @app.get("/dashboard")
    async def dashboard_page(request: Request):
        if not request.session.get('user_id'):
            return RedirectResponse(url="/login")
        return templates.TemplateResponse(
            "dashboard.html", 
            {
                "request": request,
                "username": request.session.get('username', 'User')
            }
        )

    @app.get("/goal/{goal_id}")
    async def goal_details_page(
        goal_id: int,
        request: Request,
        db: AsyncSession = Depends(get_db)
    ):
        try:
            if not request.session.get("user_id"):
                return RedirectResponse(url="/login")
            return templates.TemplateResponse(
                "goal_details.html",
                {"request": request, "goal_id": goal_id}
            )
        except Exception as e:
            logger.error(f"Error loading goal details: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    @app.on_event("startup")
    async def startup():
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables recreated successfully")
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
