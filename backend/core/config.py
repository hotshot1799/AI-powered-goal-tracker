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
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.SECRET_KEY:
            raise ValueError(
                "SECRET_KEY environment variable is required for security. "
                "Please set it to a strong random string (e.g., generated with: "
                "python -c 'import secrets; print(secrets.token_urlsafe(32))')"
            )
    
    # SendGrid settings
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "")  # Your verified sender email
    
    # Email settings (for SendGrid SMTP)
    SMTP_SERVER: str = "smtp.sendgrid.net"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "apikey"  # This is always "apikey" for SendGrid
    SMTP_PASSWORD: str = os.getenv("SENDGRID_API_KEY", "")  # Use the API key as password

    # CORS settings
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://ai-powered-goal-tracker-z0co.onrender.com")
    
    # AI Service settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()