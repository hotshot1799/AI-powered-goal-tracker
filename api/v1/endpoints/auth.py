from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserCreate, UserResponse
from services.auth import AuthService
from database import get_db
from typing import Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login")
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        data = await request.json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing username or password"
            )

        auth_service = AuthService(db)
        result = await auth_service.authenticate_user(username, password)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        # Set session data
        request.session["user_id"] = str(result["user_id"])
        request.session["username"] = result["username"]
        
        return {
            "success": True,
            "user_id": result["user_id"],
            "username": result["username"],
            "redirect": "/dashboard"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/logout")  # Changed from 'get' to 'post'
async def logout(request: Request) -> Dict[str, Any]:
    try:
        request.session.clear()
        return {
            "success": True,
            "redirect": "/login"
        }
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )
