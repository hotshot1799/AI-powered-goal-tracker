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

@router.post("/login")
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    try:
        data = await request.json()
        username = data.get('username')
        password = data.get('password')

        # Get user
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if user and user.verify_password(password):
            # Store user_id as integer in session
            request.session['user_id'] = user.user_id_int  # Use the property we added
            request.session['username'] = user.username

            return {
                "success": True,
                "user_id": user.id,
                "username": user.username,
                "redirect": "/dashboard"
            }
        else:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/logout")
async def logout(request: Request) -> Dict[str, bool]:
    request.session.clear()
    return {"success": True}
