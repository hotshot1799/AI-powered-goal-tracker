from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Goal Tracker"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "An AI-powered application for tracking and managing personal goals"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/dbname")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://ai-powered-goal-tracker-z0co.onrender.com")
    
    # AI Service settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()