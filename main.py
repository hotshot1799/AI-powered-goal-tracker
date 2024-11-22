from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.v1.router import api_router
from database import Base, engine

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    # Templates
    templates = Jinja2Templates(directory="templates")
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {"message": "Welcome to Goal Tracker API"}
    # Basic health check endpoint
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
wsgi_app = app  # Add this line for WSGI application declaration

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
