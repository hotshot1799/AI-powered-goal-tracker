# backend/api/v1/endpoints/health.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """API health check endpoint"""
    try:
        # Test database connection
        await db.execute("SELECT 1")
        
        return JSONResponse({
            "status": "healthy",
            "services": {
                "database": "connected",
                "api": "running"
            },
            "details": {
                "database_connection": "ok",
                "api_status": "ok"
            }
        })
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "services": {
                    "database": str(e),
                    "api": "running"
                },
                "details": {
                    "database_connection": "failed",
                    "api_status": "ok"
                }
            }
        )