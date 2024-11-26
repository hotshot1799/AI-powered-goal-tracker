from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserCreate, UserResponse, Token
from services.auth import AuthService
from database import get_db
from core.security import create_access_token
from typing import Dict, Any

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    try:
        result = await auth_service.create_user(user_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Dict[str, Any])
async def login(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        data = await request.json()
        auth_service = AuthService(db)
        
        user = await auth_service.authenticate_user(
            data.get("username"),
            data.get("password")
        )
        
        if user:
            # Set session data
            request.session["user_id"] = int(user.id)  # Store as integer
            request.session["username"] = user.username
            
            # Generate JWT token for API access
            access_token = create_access_token(data={"sub": user.username})
            
            return {
                "success": True,
                "user_id": user.id,
                "username": user.username,
                "access_token": access_token,
                "token_type": "bearer",
                "redirect": "/dashboard"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/logout")
async def logout(request: Request) -> Dict[str, bool]:
    request.session.clear()
    return {"success": True}
