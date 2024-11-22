from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.v1.router import api_router
from database import Base, engine

# Move templates outside the function to make it globally accessible
templates = Jinja2Templates(directory="templates")

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
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
    async def login(request: Request):
        return templates.TemplateResponse("login.html", {"request": request})
    
    @app.get("/register")
    async def register(request: Request):
        return templates.TemplateResponse("register.html", {"request": request})
        
    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
        
    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    @app.on_event("startup")
    async def startup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
    return app

app = create_application()
wsgi_app = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
